"""Retrieval-only evaluation of C1 (query rewrite) and C2 (context merge/expand), DEV ONLY, original question as query.

    python -m src.run_retrieval_variants

Exploratory analysis added after the configuration was frozen and the test was run once: it is NOT used to choose or
change the configuration, and there is deliberately no test option. No agent is involved; the query is the benchmark
question itself, so the numbers are comparable with results/retrieval/summary_dev.json.

Part 1 (as specified in docs/SELECTION_CRITERIA.md): ranking metrics (Hit@1/3/10, MRR@10) and Context Evidence Rate
(all key facts of a gold page in the final context; seeds = top-3 packed into the 2400-character budget).
  + C1  adds BM25(rewritten query) as a third list to the RRF fusion (hybrid only)
  + C2  merges adjacent/overlapping chunks of a page and fills the rest of the budget with neighbours
Part 2 (controls, to interpret part 1):
  C1 control  "+ BM25 twice": the same extra list but with the ORIGINAL query, separating the effect of the rewritten
              text from the effect of weighting lexical evidence more
  C2 budget   C2 with 3200/4000 characters, and a "top-5 seeds, no merge" control with the same 4000 characters,
              separating neighbour merging from simply reading more text. The frozen 2400 budget is exactly 3 full chunks.
"""
from __future__ import annotations

import json
import os

from dotenv import load_dotenv

from . import config
from .agent import Chat, ContextBuilder, Pipeline, PipelineConfig, Resources
from .embeddings import OpenAIEmbedder
from .retrieval import rrf
from .run_agent import check_frozen, context_has_evidence
from .run_retrieval import DEPTH, RANK_CUT, RRF_K, first_hit_rank
from .store import PgVectorStore

OUT = config.RESULTS_DIR / "retrieval" / "variants_dev.json"
TOP_K = 3
BASES = [("dense", "A"), ("hybrid", "A"), ("hybrid", "B")]


def ranking_metrics(ranks: list[int | None]) -> dict:
    n = len(ranks)
    return {"hit_at_1": sum(r == 1 for r in ranks), "hit_at_3": sum(r is not None and r <= 3 for r in ranks),
            "hit_at_10": sum(r is not None for r in ranks), "mrr_at_10": round(sum(1 / r for r in ranks if r) / n, 4)}


def main() -> None:
    check_frozen()
    load_dotenv(config.ENV_PATH)
    questions = [q for q in json.loads((config.BENCHMARK_DIR / "questions.json").read_text(encoding="utf-8"))
                 if q["split"] == "dev" and q["answerable"]]
    ids = [q["id"] for q in questions]
    embedder, chat = OpenAIEmbedder(), Chat()
    res = Resources(PgVectorStore(os.environ["DATABASE_URL"], embedder.dimensions, embedder.model_name), embedder)
    rewriter = Pipeline(PipelineConfig("rw", "hybrid", "B", rewrite=True), res, chat)

    vectors = {q["id"]: embedder.embed_query(q["question"]) for q in questions}
    rewrites = {}
    for q in questions:
        text, log = rewriter.rewrite(q["question"])
        rewrites[q["id"]] = {"accepted": text, **log}

    dense, lex, lex_rw = {}, {}, {}
    for index in ("A", "B"):
        for q in questions:
            dense[index, q["id"]] = res.dense[index].search_vector(vectors[q["id"]], top_k=DEPTH)
            lex[index, q["id"]] = res.bm25[index].search(q["question"], top_k=DEPTH)
            rw = rewrites[q["id"]]["accepted"]
            lex_rw[index, q["id"]] = res.bm25[index].search(rw, top_k=DEPTH) if rw else None

    def rankings(method: str, index: str, mode: str) -> dict[str, list[dict]]:
        out = {}
        for i in ids:
            if method == "dense":
                out[i] = dense[index, i][:RANK_CUT]
                continue
            lists = [dense[index, i], lex[index, i]]
            if mode == "c1" and lex_rw[index, i]:
                lists.append(lex_rw[index, i])
            if mode == "twice":
                lists.append(lex[index, i])
            out[i] = rrf(lists, k=RRF_K, top_k=RANK_CUT)
        return out

    rows, per_question = [], {}

    def evaluate(name: str, ranked: dict[str, list[dict]], *, expand: bool, budget: int, seeds: int, ref: str, part: int) -> None:
        method, index = name.split(" ")[:2]
        builder = ContextBuilder(PipelineConfig("v", method, index, expand=expand, budget=budget), res)
        ranks = [first_hit_rank(ranked[q["id"]], q) for q in questions]
        ctx = {q["id"]: context_has_evidence(builder.build(ranked[q["id"]][:seeds])["passages"], q) for q in questions}
        rows.append({"config": name, "part": part, "reference": ref, "budget_chars": budget, "seeds": seeds,
                     **ranking_metrics(ranks), "context_evidence": sum(ctx.values())})
        per_question[name] = {"first_hit_rank": dict(zip(ids, ranks)), "context_evidence": ctx}

    for method, index in BASES:
        plain = f"{method} {index}"
        base = rankings(method, index, "plain")
        evaluate(plain, base, expand=False, budget=2400, seeds=TOP_K, ref=plain, part=1)
        evaluate(plain + " + C2", base, expand=True, budget=2400, seeds=TOP_K, ref=plain, part=1)
        if method == "hybrid":
            c1 = rankings(method, index, "c1")
            evaluate(plain + " + C1", c1, expand=False, budget=2400, seeds=TOP_K, ref=plain, part=1)
            evaluate(plain + " + C1 + C2", c1, expand=True, budget=2400, seeds=TOP_K, ref=plain, part=1)
            evaluate(plain + " + BM25 twice (C1 control)", rankings(method, index, "twice"), expand=False,
                     budget=2400, seeds=TOP_K, ref=plain, part=2)
        for b in (3200, 4000):
            evaluate(plain + f" + C2 @{b}", base, expand=True, budget=b, seeds=TOP_K, ref=plain, part=2)
        evaluate(plain + " top-5 seeds @4000 (C2 control)", base, expand=False, budget=4000, seeds=5, ref=plain, part=2)

    def diff(name: str, ref: str, field: str) -> dict:
        a, b = per_question[ref][field], per_question[name][field]
        ok = (lambda v: v) if field == "context_evidence" else (lambda v: v is not None and v <= 3)
        return {"gained": [i for i in ids if ok(b[i]) and not ok(a[i])], "lost": [i for i in ids if ok(a[i]) and not ok(b[i])]}

    comparisons = {r["config"]: {"vs": r["reference"], "hit_at_3": diff(r["config"], r["reference"], "first_hit_rank"),
                                 "context_evidence": diff(r["config"], r["reference"], "context_evidence")}
                   for r in rows if r["config"] != r["reference"]}
    result = {"split": "dev", "answerable": len(questions), "query": "original question", "rrf_k": RRF_K, "depth": DEPTH,
              "rewrites": rewrites, "rows": rows, "vs_reference": comparisons, "per_question": per_question,
              "llm_tokens": {"prompt": chat.prompt_tokens, "completion": chat.completion_tokens},
              "note": "exploratory, dev only; not used to select the configuration"}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"dev, n = {len(questions)} answerable, query = original question; rewrites accepted "
          f"{sum(bool(v['accepted']) for v in rewrites.values())}/{len(rewrites)}")
    print(f"{'config':44s} {'Hit@1':>5s} {'Hit@3':>5s} {'Hit@10':>6s} {'MRR':>6s} {'ctxEv':>5s}  vs reference: context gained/lost | Hit@3 gained/lost")
    for r in rows:
        c = comparisons.get(r["config"])
        extra = "" if not c else f"  +{c['context_evidence']['gained']} -{c['context_evidence']['lost']} | +{c['hit_at_3']['gained']} -{c['hit_at_3']['lost']}"
        print(f"{r['config']:44s} {r['hit_at_1']:>5d} {r['hit_at_3']:>5d} {r['hit_at_10']:>6d} {r['mrr_at_10']:>6.3f} {r['context_evidence']:>5d}{extra}")


if __name__ == "__main__":
    main()
