"""Compare dense, BM25 and hybrid-RRF retrieval on the frozen benchmark. Retrieval only (no LLM).

    python -m src.run_retrieval                  # DEV only (default)
    python -m src.run_retrieval --final-test     # only after the configuration is chosen and written down

Same corpus, index and questions for every method; the original question text is the query.
Hit = a chunk on a gold page that contains every key fact (see benchmark/README.md).
Unanswerable questions are searched and traced but excluded from every retrieval metric.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from collections import defaultdict

from dotenv import load_dotenv

from . import config
from .embeddings import OpenAIEmbedder
from .retrieval import BM25Retriever, DenseRetriever, rrf
from .store import PgVectorStore
from .textutil import canon, sha256_lf

DEPTH = 20     # candidates each retriever contributes to fusion
RANK_CUT = 10  # ranked list kept per method for metrics
RRF_K = 60
OUT_DIR = config.RESULTS_DIR / "retrieval"


def check_frozen() -> None:
    frozen = json.loads((config.BENCHMARK_DIR / "FROZEN.json").read_text(encoding="utf-8"))
    if sha256_lf(config.BENCHMARK_DIR / "questions.json") != frozen["sha256"]:
        raise SystemExit("benchmark/questions.json changed after it was frozen; refusing to run.")


def is_hit(result: dict, question: dict) -> bool:
    pages = {g["page"] for g in question["gold"]}
    text = canon(result["text"])
    return result["page"] in pages and all(canon(k) in text for k in question["key_facts"])


def first_hit_rank(results: list[dict], question: dict) -> int | None:
    return next((r["rank"] for r in results if is_hit(r, question)), None)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-test", action="store_true", help="evaluate the test split (run once, after choosing)")
    parser.add_argument("--indexes", default="A,B")
    args = parser.parse_args()
    split = "test" if args.final_test else "dev"
    check_frozen()
    load_dotenv(config.ENV_PATH)
    questions = [q for q in json.loads((config.BENCHMARK_DIR / "questions.json").read_text(encoding="utf-8"))
                 if q["split"] == split]

    embedder = OpenAIEmbedder()
    store = PgVectorStore(os.environ["DATABASE_URL"], embedder.dimensions, embedder.model_name)
    vectors, embed_ms = {}, {}
    for q in questions:
        t = time.perf_counter()
        vectors[q["id"]] = embedder.embed_query(q["question"])
        embed_ms[q["id"]] = (time.perf_counter() - t) * 1000

    traces = []
    for index in args.indexes.split(","):
        chunks = json.loads((config.DATA_DIR / "index" / f"chunks_{index}.json").read_text(encoding="utf-8"))
        bm25, dense = BM25Retriever(chunks), DenseRetriever(store, embedder, index)
        for use_filter in (False, True):
            for q in questions:
                flt = q["filter"] if use_filter else None
                if use_filter and not flt:
                    continue  # the filtered variant only exists for questions that carry a user-given filter
                runs = {}
                t = time.perf_counter(); ranked = dense.search_vector(vectors[q["id"]], top_k=DEPTH, filters=flt)
                runs["dense"] = (ranked, (time.perf_counter() - t) * 1000 + embed_ms[q["id"]])
                t = time.perf_counter(); lex = bm25.search(q["question"], top_k=DEPTH, filters=flt)
                runs["bm25"] = (lex, (time.perf_counter() - t) * 1000)
                t = time.perf_counter(); fused = rrf([ranked, lex], k=RRF_K, top_k=RANK_CUT)
                runs["hybrid_rrf"] = (fused, (time.perf_counter() - t) * 1000 + runs["dense"][1] + runs["bm25"][1])
                for method, (results, ms) in runs.items():
                    results = results[:RANK_CUT]
                    traces.append({
                        "query_id": q["id"], "split": split, "answerable": q["answerable"], "index": index,
                        "method": method, "filter": flt, "query": q["question"], "elapsed_ms": round(ms, 2),
                        "first_hit_rank": first_hit_rank(results, q) if q["answerable"] else None,
                        "results": [{"rank": r["rank"], "id": r["id"], "page": r["page"], "score": round(r["score"], 6),
                                     "hit": is_hit(r, q) if q["answerable"] else None,
                                     "text": r["text"]} for r in results]})

    groups = defaultdict(list)
    for t in traces:
        if t["answerable"]:
            groups[(t["index"], t["method"], t["filter"] is not None)].append(t)
    summary = []
    for (index, method, filtered), items in sorted(groups.items()):
        ranks = [t["first_hit_rank"] for t in items]
        n = len(items)
        summary.append({
            "index": index, "method": method, "filter_applied_to_questions_that_have_one": filtered, "n": n,
            "hit_at_1": sum(r == 1 for r in ranks), "hit_at_3": sum(r is not None and r <= 3 for r in ranks),
            "hit_at_10": sum(r is not None for r in ranks),
            "mrr_at_10": round(sum(1 / r for r in ranks if r) / n, 4),
            "missed_at_3": [t["query_id"] for t in items if not (t["first_hit_rank"] and t["first_hit_rank"] <= 3)],
            "median_ms": round(statistics.median(t["elapsed_ms"] for t in items), 1)})
    config.RESULTS_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    tag = f"{split}"
    with open(OUT_DIR / f"traces_{tag}.jsonl", "w", encoding="utf-8") as fh:
        for t in traces:
            fh.write(json.dumps(t, ensure_ascii=False) + "\n")
    meta = {"split": split, "questions": len(questions), "answerable": sum(q["answerable"] for q in questions),
            "depth_for_fusion": DEPTH, "rank_cut": RANK_CUT, "rrf_k": RRF_K, "bm25": {"k1": 1.5, "b": 0.75},
            "embedding_model": embedder.model_name, "query_embedding_tokens": embedder.total_tokens,
            "estimated_cost_usd": round(embedder.estimated_cost_usd, 7)}
    (OUT_DIR / f"summary_{tag}.json").write_text(json.dumps({"config": meta, "rows": summary}, indent=2), encoding="utf-8")

    print(f"{split}: {meta['answerable']} answerable questions | query embedding {embedder.total_tokens} tokens")
    print(f"{'index':5s} {'method':11s} {'filter':6s} {'n':>3s} {'Hit@1':>6s} {'Hit@3':>6s} {'Hit@10':>7s} {'MRR@10':>7s} {'ms':>7s}  missed@3")
    for r in summary:
        print(f"{r['index']:5s} {r['method']:11s} {str(r['filter_applied_to_questions_that_have_one']):6s} {r['n']:>3d} "
              f"{r['hit_at_1']:>6d} {r['hit_at_3']:>6d} {r['hit_at_10']:>7d} {r['mrr_at_10']:>7.3f} {r['median_ms']:>7.1f}  {r['missed_at_3']}")


if __name__ == "__main__":
    main()
