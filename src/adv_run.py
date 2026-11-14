"""Run the advanced pipeline on the frozen advanced benchmark. Dev by default; test needs --final-test and runs once.

    python -m src.adv_run --config TEXT,VISUAL,PAGES              # dev
    python -m src.adv_run --config <chosen> --final-test           # test, after the criteria are frozen

The agent sees only the question. Gold is read after the agent finishes, to compute a FIRST-PASS grade:
  answerable    pass_auto = answered AND an LLM judge (strict, given the expected answer) says correct AND the cited chunks
                cover every gold page. The LLM judge only assists: dev selection uses it; every test question is also read and
                labelled by hand against the original page (src.adv_review).
  unanswerable  pass_auto = the system abstained (it returned no claim).
Provider errors, timeouts and missing results are recorded as failures and stay in the denominator.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

from . import config
from .adv_agent import CONFIGS, Responder, run_agent
from .adv_index import AdvIndex
from .embeddings import OpenAIEmbedder
from .textutil import sha256_lf

BENCH = config.BENCHMARK_DIR / "advanced"
OUT_DIR = config.RESULTS_DIR / "advanced"
CRITERIA = config.REPO_ROOT / "docs" / "ADVANCED_CRITERIA.md"
CRITERIA_FROZEN = config.REPO_ROOT / "docs" / "ADVANCED_CRITERIA_FROZEN.json"

JUDGE_SYSTEM = """You grade one answer from a retrieval system against the reference. Be strict.
Return ONLY JSON {"correct": true|false, "reason": "one sentence"}.
correct = true only if the answer states ALL parts of the reference answer: the same numbers (within the stated tolerance, same sign and unit), the same names/years, and any requested calculation result. Extra true detail is fine; a missing part, a wrong number, a wrong unit, a wrong entity or a contradiction makes it false. Do not grade citation formatting."""


def check_frozen() -> None:
    bench = json.loads((BENCH / "FROZEN.json").read_text(encoding="utf-8"))
    if sha256_lf(BENCH / "questions.json") != bench["sha256"]:
        raise SystemExit("benchmark/advanced/questions.json changed after it was frozen; refusing to run.")
    if not CRITERIA_FROZEN.exists():
        raise SystemExit("docs/ADVANCED_CRITERIA.md is not frozen yet; write and freeze it before running.")
    crit = json.loads(CRITERIA_FROZEN.read_text(encoding="utf-8"))
    if sha256_lf(CRITERIA) != crit["sha256"]:
        raise SystemExit("docs/ADVANCED_CRITERIA.md changed after it was frozen; refusing to run.")


def judge(judge_responder: Responder, question: dict, answer: str) -> tuple[bool, str]:
    prompt = (f"Question: {question['question']}\nReference answer: {question['expected_answer']}\n"
              f"Tolerance: {question.get('tolerance') or 'exact'}\nSystem answer: {answer}")
    response = judge_responder.create(instructions=JUDGE_SYSTEM, input=prompt, max_output_tokens=2000)
    text = next((c.text for o in response.output if o.type == "message" for c in o.content if c.type == "output_text"), "")
    try:
        data = json.loads(text[text.index("{"):text.rindex("}") + 1])
        return bool(data["correct"]), str(data.get("reason", ""))
    except (ValueError, KeyError):
        return False, f"unparseable judge output: {text[:120]!r}"


def pages_of(ids: list[str], by_id: dict[str, dict]) -> set[int]:
    return {by_id[i]["page"] for i in ids if i in by_id}


def grade(question: dict, trace: dict, by_id: dict, judge_responder: Responder) -> dict:
    searches = [e for e in trace["events"] if e["event"] == "search"]
    out: dict = {"n_searches": len(searches), "tool_use": bool(searches)}
    if trace["status"] == "error":
        return out | {"pass_auto": False, "why": "system error"}
    if not question["answerable"]:
        return out | {"pass_auto": trace["status"] == "abstain",
                      "why": "abstained" if trace["status"] == "abstain" else "answered an unanswerable question"}
    gold_pages = {g["page"] for g in question["gold"]}
    context_pages = pages_of(searches[-1]["context_ids"], by_id) if searches else set()
    out |= {"gold_pages": sorted(gold_pages), "context_has_gold_pages": gold_pages <= context_pages,
            "image_pages_have_gold": bool(searches) and gold_pages <= set(searches[-1]["image_pages"] or []) | set()}
    if trace["status"] != "answered":
        return out | {"pass_auto": False, "why": f"refused ({trace['events'][-1]['event']})"}
    cited_pages = pages_of(trace["citations"], by_id)
    correct, reason = judge(judge_responder, question, trace["answer"])
    out |= {"cited_pages": sorted(cited_pages), "citation_covers_gold_pages": gold_pages <= cited_pages,
            "judge_correct": correct, "judge_reason": reason}
    out["pass_auto"] = correct and gold_pages <= cited_pages
    out["why"] = "ok" if out["pass_auto"] else ("wrong or incomplete answer" if not correct else "citations do not cover every gold page")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="PAGES")
    parser.add_argument("--final-test", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out", default=str(OUT_DIR))
    args = parser.parse_args()
    split = "test" if args.final_test else "dev"
    if args.limit and args.final_test:
        raise SystemExit("--limit is for dev smoke tests only")
    check_frozen()
    names = args.config.split(",")
    unknown = [n for n in names if n not in CONFIGS]
    if unknown:
        raise SystemExit(f"unknown configuration(s) {unknown}; choose from {sorted(CONFIGS)}")
    out_root = Path(args.out) if os.path.isabs(args.out) else config.REPO_ROOT / args.out
    if args.final_test:
        done = [n for n in names if (out_root / "test" / n / "traces.json").exists()]
        if done:
            raise SystemExit(f"test already run for {done}; the test split is evaluated once.")
    load_dotenv(config.ENV_PATH)
    questions = [q for q in json.loads((BENCH / "questions.json").read_text(encoding="utf-8")) if q["split"] == split]
    if args.limit:
        questions = questions[:args.limit]
    embedder = OpenAIEmbedder()
    index = AdvIndex(embedder)
    by_id = {c["id"]: c for c in index.chunks}
    for name in names:
        cfg = CONFIGS[name]
        agent, judge_r = Responder(), Responder()
        traces = []
        for q in questions:
            before, emb_before, started = agent.snapshot(), embedder.total_tokens, time.perf_counter()
            try:
                result = run_agent(q["question"], index, cfg, agent)
            except Exception as exc:  # provider/retrieval failure: a failure that stays in the denominator
                result = {"status": "error", "answer": "", "citations": [], "events": [], "error": f"{type(exc).__name__}: {exc}"}
            after = agent.snapshot()
            trace = {"query_id": q["id"], "split": split, "config": name, "group": q["group"], "question": q["question"],
                     "elapsed_s": round(time.perf_counter() - started, 2),
                     "usage": {"input_tokens": after[0] - before[0], "output_tokens": after[1] - before[1],
                               "reasoning_tokens": after[2] - before[2], "llm_calls": after[3] - before[3],
                               "embedding_tokens": embedder.total_tokens - emb_before}, **result}
            trace["grade"] = grade(q, trace, by_id, judge_r)
            traces.append(trace)
            print(f"{name:7s} {q['id']:4s} {q['group']:8s} {trace['status']:8s} pass_auto={trace['grade']['pass_auto']!s:5s} "
                  f"{trace['elapsed_s']:5.1f}s {trace['grade']['why']}")
        folder = out_root / split / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "traces.json").write_text(json.dumps(traces, ensure_ascii=False, indent=2), encoding="utf-8")
        by_group = defaultdict(lambda: [0, 0])
        for t in traces:
            by_group[t["group"]][1] += 1
            by_group[t["group"]][0] += t["grade"]["pass_auto"]
        ok = [t for t in traces if t["status"] != "error"]
        summary = {"config": name, "split": split, "model": agent.model, "questions": len(traces),
                   "pass_auto": f"{sum(t['grade']['pass_auto'] for t in traces)}/{len(traces)}",
                   "by_group": {k: f"{a}/{b}" for k, (a, b) in sorted(by_group.items())},
                   "errors": [t["query_id"] for t in traces if t["status"] == "error"],
                   "failed": [t["query_id"] for t in traces if not t["grade"]["pass_auto"]],
                   "median_seconds": round(statistics.median(t["elapsed_s"] for t in ok), 1) if ok else None,
                   "tokens": {"agent_input": sum(t["usage"]["input_tokens"] for t in traces),
                              "agent_output": sum(t["usage"]["output_tokens"] for t in traces),
                              "agent_reasoning": sum(t["usage"]["reasoning_tokens"] for t in traces),
                              "judge_input": judge_r.input_tokens, "judge_output": judge_r.output_tokens,
                              "embedding": sum(t["usage"]["embedding_tokens"] for t in traces)},
                   "note": "pass_auto is a first-pass grade (LLM judge + citation pages); prices of gpt-6.1-terra are unknown, so cost is reported in tokens"}
        (folder / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
