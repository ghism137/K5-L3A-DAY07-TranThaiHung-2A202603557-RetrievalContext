"""Run the agent on the frozen benchmark. Dev by default; the test split needs --final-test and runs once.

    python -m src.run_agent --config R0,BASE,BASE+C1,BASE+C2         # dev
    python -m src.run_agent --config R0,<chosen> --final-test          # test, after the criteria are frozen

Gold (pages, key facts) is read only AFTER the agent has finished, to compute Context Evidence Rate and first-search
hits; it never enters the agent. Grounded answer, citation support and correct abstention are human labels
(see starter/agent_metrics.py); this script only counts what can be counted without judging content.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv

from . import config
from .agent import ASSUMED_CHAT_USD_PER_M, CONFIGS, Chat, ContextBuilder, Pipeline, Resources, run_agent
from .embeddings import ASSUMED_USD_PER_MILLION, OpenAIEmbedder
from .run_retrieval import is_hit
from .store import PgVectorStore
from .textutil import canon, sha256_lf

OUT_DIR = config.RESULTS_DIR / "agent"
CRITERIA = config.REPO_ROOT / "docs" / "SELECTION_CRITERIA.md"


def check_frozen() -> None:
    bench = json.loads((config.BENCHMARK_DIR / "FROZEN.json").read_text(encoding="utf-8"))
    if sha256_lf(config.BENCHMARK_DIR / "questions.json") != bench["sha256"]:
        raise SystemExit("benchmark/questions.json changed after it was frozen; refusing to run.")
    crit = json.loads((config.REPO_ROOT / "docs" / "CRITERIA_FROZEN.json").read_text(encoding="utf-8"))
    if sha256_lf(CRITERIA) != crit["sha256"]:
        raise SystemExit("docs/SELECTION_CRITERIA.md changed after it was frozen; refusing to run.")


def context_has_evidence(passages: list[dict], question: dict) -> bool:
    for page in {g["page"] for g in question["gold"]}:
        text = canon(" ".join(p["text"] for p in passages if p["page"] == page))
        if all(canon(k) in text for k in question["key_facts"]):
            return True
    return False


def evaluate_trace(trace: dict, question: dict, chunk_by_id: dict[str, dict]) -> dict:
    searches = [e for e in trace["events"] if e["event"] == "search"]
    out = {"n_searches": len(searches), "tool_use": bool(searches)}
    if question["answerable"]:
        out["context_has_evidence"] = bool(searches) and context_has_evidence(searches[-1]["passages"], question)
        first = searches[0]["seeds"] if searches else []
        out["first_search_hit_at_3"] = any(
            is_hit({"page": s["page"], "text": chunk_by_id[s["id"]]["text"]}, question) for s in first)
    return out


def summarize(name: str, split: str, traces: list[dict], chat: Chat, embedder: OpenAIEmbedder) -> dict:
    ans = [t for t in traces if t["answerable"] and t["status"] != "error"]
    una = [t for t in traces if not t["answerable"] and t["status"] != "error"]
    ok = [t for t in traces if t["status"] != "error"]
    n = len(ans)
    count = lambda xs, f: sum(1 for x in xs if f(x))
    return {
        "config": name, "split": split, "model": chat.model, "questions": len(traces),
        "provider_errors": [t["query_id"] for t in traces if t["status"] == "error"],
        "answerable": {
            "n": n,
            "context_evidence_rate": f"{count(ans, lambda t: t['eval']['context_has_evidence'])}/{n}",
            "first_search_hit_at_3": f"{count(ans, lambda t: t['eval']['first_search_hit_at_3'])}/{n}",
            "answered": count(ans, lambda t: t["status"] == "answered"),
            "abstained_false": count(ans, lambda t: t["status"] == "abstain"),
            "context_missed": [t["query_id"] for t in ans if not t["eval"]["context_has_evidence"]]},
        "unanswerable": {
            "n": len(una), "abstained": count(una, lambda t: t["status"] == "abstain"),
            "answered_anyway": [t["query_id"] for t in una if t["status"] == "answered"],
            "note": "status only; whether the abstention is correct is a human label"},
        "tool_use": f"{count(ok, lambda t: t['eval']['tool_use'])}/{len(ok)}",
        "searches_distribution": {str(k): count(ok, lambda t: t["eval"]["n_searches"] == k) for k in range(0, 5)},
        "median_seconds": round(statistics.median(t["elapsed_s"] for t in ok), 2) if ok else None,
        "tokens": {"llm_prompt": sum(t["usage"]["prompt_tokens"] for t in traces),
                   "llm_completion": sum(t["usage"]["completion_tokens"] for t in traces),
                   "embedding": sum(t["usage"]["embedding_tokens"] for t in traces)},
        "estimated_cost_usd": round(sum(t["usage"]["cost_usd"] or 0 for t in traces), 6),
        "cost_note": "list prices are assumptions (src/agent.py, src/embeddings.py); verify before quoting",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="BASE", help=f"comma list from {sorted(CONFIGS)}")
    parser.add_argument("--final-test", action="store_true", help="evaluate the test split (once per configuration)")
    parser.add_argument("--limit", type=int, default=0, help="first N questions (dev smoke tests only)")
    parser.add_argument("--out", default=str(OUT_DIR))
    args = parser.parse_args()
    split = "test" if args.final_test else "dev"
    if args.limit and args.final_test:
        raise SystemExit("--limit is for dev smoke tests; the test split is run in full")
    check_frozen()
    names = args.config.split(",")
    unknown = [n for n in names if n not in CONFIGS]
    if unknown:
        raise SystemExit(f"unknown configuration(s) {unknown}; choose from {sorted(CONFIGS)}")
    out_root = Path(args.out) if os.path.isabs(args.out) else config.REPO_ROOT / args.out
    if args.final_test:
        existing = [n for n in names if (out_root / "test" / n.replace("+", "_") / "traces.json").exists()]
        if existing:
            raise SystemExit(f"test already run for {existing}; the test split is evaluated once. "
                             "Delete the folder deliberately and record why if a system error forces a rerun.")

    load_dotenv(config.ENV_PATH)
    questions = [q for q in json.loads((config.BENCHMARK_DIR / "questions.json").read_text(encoding="utf-8"))
                 if q["split"] == split]
    if args.limit:
        questions = questions[:args.limit]
    embedder = OpenAIEmbedder()
    chat = Chat()
    store = PgVectorStore(os.environ["DATABASE_URL"], embedder.dimensions, embedder.model_name)
    res = Resources(store, embedder)
    chunk_by_id = {c["id"]: c for chunks in res.chunks.values() for c in chunks}

    for name in names:
        cfg = CONFIGS[name]
        pipeline, builder = Pipeline(cfg, res, chat), ContextBuilder(cfg, res)
        traces = []
        for q in questions:
            before, emb_before = chat.snapshot(), embedder.total_tokens
            started = time.perf_counter()
            try:
                result = run_agent(q["question"], q["filter"], pipeline, builder, chat)
            except Exception as exc:  # provider/retrieval failure: record it, never substitute a fake answer
                result = {"status": "error", "answer": "", "citations": [], "events": [], "error": f"{type(exc).__name__}: {exc}"}
            after = chat.snapshot()
            usage = {"prompt_tokens": after[0] - before[0], "completion_tokens": after[1] - before[1],
                     "llm_calls": after[2] - before[2], "embedding_tokens": embedder.total_tokens - emb_before}
            usage["cost_usd"] = None
            if chat.model in ASSUMED_CHAT_USD_PER_M:
                p_in, p_out = ASSUMED_CHAT_USD_PER_M[chat.model]
                usage["cost_usd"] = (usage["prompt_tokens"] * p_in + usage["completion_tokens"] * p_out) / 1e6 \
                    + usage["embedding_tokens"] / 1e6 * ASSUMED_USD_PER_MILLION[embedder.model_name]
            trace = {"query_id": q["id"], "split": split, "config": name, "question": q["question"], "filter": q["filter"],
                     "answerable": q["answerable"], "origin": q["origin"], "elapsed_s": round(time.perf_counter() - started, 3),
                     "usage": usage, **result}
            trace["eval"] = evaluate_trace(trace, q, chunk_by_id) if result["status"] != "error" else {}
            traces.append(trace)
            e = trace["eval"]
            print(f"{name:11s} {q['id']:4s} {trace['status']:8s} searches={e.get('n_searches', '-')} "
                  f"ctx_evidence={e.get('context_has_evidence', '-')} {trace['elapsed_s']:.1f}s"
                  + (f"  ERROR {result['error']}" if trace["status"] == "error" else ""))
        folder = out_root / split / name.replace("+", "_")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "traces.json").write_text(json.dumps(traces, ensure_ascii=False, indent=2), encoding="utf-8")
        summary = summarize(name, split, traces, chat, embedder)
        (folder / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
