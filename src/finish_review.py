"""Turn the filled review labels into the metrics of BENCHMARK.md (uses starter/agent_metrics.py for the aggregation).

    python -m src.finish_review

Needs results/agent/test/review/review_labels.json fully filled (no null) and blind_key.json. Writes
review/reviews_<config>.json and review/summary_<config>.json (reused / new / combined subsets).
Nothing here judges content; it only counts the human labels.
"""
from __future__ import annotations

import json
import sys

from . import config

sys.path.insert(0, str(config.REPO_ROOT / "starter"))
from agent_metrics import aggregate  # noqa: E402

REVIEW = config.RESULTS_DIR / "agent" / "test" / "review"
CONFIGS = ["R0", "BASE"]


def main() -> None:
    labels = json.loads((REVIEW / "review_labels.json").read_text(encoding="utf-8"))
    key = json.loads((REVIEW / "blind_key.json").read_text(encoding="utf-8"))
    questions = {q["id"]: q for q in json.loads((config.BENCHMARK_DIR / "questions.json").read_text(encoding="utf-8"))}
    missing = []
    for row in labels:
        for field in ("context_grade", "answer_grade", "abstention_correct"):
            if field in row and row[field] is None:
                missing.append((row["item"], field))
        if any(v is None for v in row["citation_support"]):
            missing.append((row["item"], "citation_support"))
    if missing:
        raise SystemExit(f"{len(missing)} label(s) still null, e.g. {missing[:5]}")
    for cfg in CONFIGS:
        traces = json.loads((config.RESULTS_DIR / "agent" / "test" / cfg / "traces.json").read_text(encoding="utf-8"))
        by_q = {t["query_id"]: t for t in traces}
        mine = [r for r in labels if key[r["item"]] == cfg]
        reviews = []
        for r in mine:
            rev = {"query_id": r["query_id"], "citation_support": r["citation_support"]}
            if "answer_grade" in r:
                rev["answer_grade"] = r["answer_grade"]
            if "abstention_correct" in r:
                rev["abstention_correct"] = r["abstention_correct"]
            reviews.append(rev)
        (REVIEW / f"reviews_{cfg}.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding="utf-8")
        out = {}
        for name, keep in (("combined", lambda q: True), ("reused", lambda q: q["origin"] == "day6_test_reused"),
                           ("new", lambda q: q["origin"] != "day6_test_reused")):
            cases = [{"id": q["id"], "answerable": q["answerable"]} for q in questions.values()
                     if q["split"] == "test" and (keep(q) or not q["answerable"] and name == "new")]
            ids = {c["id"] for c in cases}
            part = aggregate(cases, [t for t in traces if t["query_id"] in ids], [r for r in reviews if r["query_id"] in ids])
            ctx = [r["context_grade"] for r in mine if "context_grade" in r and r["query_id"] in ids]
            part["context_grade"] = {str(g): ctx.count(g) for g in (0, 1, 2)} | {"N": len(ctx)}
            out[name] = part
        (REVIEW / f"summary_{cfg}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        g = out["combined"]
        print(cfg, "| grounded", g["grounded_answer"], "| citation", g["citation_validity"], "| abstention", g["abstention"],
              "| false abstention", g["false_abstention"], "| context", g["context_grade"])


if __name__ == "__main__":
    main()
