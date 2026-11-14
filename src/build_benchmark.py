"""Build benchmark/questions.json (Day 7 schema) from the frozen Day 6 benchmark plus new questions.

    python -m src.build_benchmark

Sources, all decided before any Day 7 retrieval run:
  * Day 6 dev (15)                      -> dev,  origin "day6_dev"
  * Day 6 test (5), reused               -> test, origin "day6_test_reused"  (results were seen in Day 6)
  * Day 6 spare s01-s04 (never searched) -> test, origin "day6_spare_new"
  * n01, n02: new answerable questions   -> test, origin "day7_new"
  * u01, u02 (dev), u03, u04 (test): unanswerable questions written for Day 7, origin "day7_new"
The Day 6 file is read verbatim from benchmark/day6_questions.json (hash checked in verify_benchmark).
"""
from __future__ import annotations

import json

from . import config

DAY6 = config.BENCHMARK_DIR / "day6_questions.json"
OUT = config.BENCHMARK_DIR / "questions.json"
SOURCE_ID = config.DOCUMENT_ID

# --- new answerable questions (evidence copied from the PDF text of the gold page) -------------
NEW_ANSWERABLE = [
    {
        "id": "n01", "split": "test", "origin": "day7_new", "type": "dien_dat_lai", "chapter_of_gold": 1,
        "question": "Within Sub-Saharan Africa, which country was the largest international bond issuer in 2025, and how much did it raise?",
        "expected_answer": "Kenya, which raised $3.5 billion in 2025.",
        "gold": [{"source_id": SOURCE_ID, "page": 64,
                  "evidence": "Kenya, the largest issuer in the region, raised $3.5 billion in 2025."}],
        "key_facts": ["Kenya, the largest issuer in the region", "$3.5 billion in 2025"], "filter": None,
    },
    {
        "id": "n02", "split": "test", "origin": "day7_new", "type": "dien_dat_lai", "chapter_of_gold": 2,
        "question": "For which food groups do countries with heavier debt burdens relative to exports import from a wider variety of suppliers?",
        "expected_answer": "Oils and fats, and legumes, nuts, and seeds.",
        "gold": [{"source_id": SOURCE_ID, "page": 100,
                  "evidence": "By contrast, higher debt burdens are associated with greater import source diversity for oils and fats, and for legumes, nuts, and seeds."}],
        "key_facts": ["greater import source diversity for oils and fats", "legumes, nuts, and seeds"], "filter": None,
    },
]

# --- unanswerable questions: near the report's topics, absent from the whole PDF ----------------
# absence_check.terms are regular expressions that must match NO page of the full 280-page PDF;
# verify_benchmark re-runs them. "manual" records what was read by hand beyond keyword search.
UNANSWERABLE = [
    {
        "id": "u01", "split": "dev", "type": "thieu_bang_chung",
        "question": "How much did low- and middle-income countries borrow through cryptocurrency- or stablecoin-backed loans in 2025?",
        "absence_reason": "The report covers bonds, bank loans and total return swaps, but never discusses crypto-assets or stablecoin-backed borrowing.",
        "absence_check": {"terms": ["stablecoin", "crypto", "bitcoin", "digital asset", "blockchain"], "manual": None},
    },
    {
        "id": "u02", "split": "dev", "type": "thieu_bang_chung",
        "question": "How much did low- and middle-income countries raise through Panda bond issuance in 2025?",
        "absence_reason": "The report gives bond issuance by country and region but never mentions Panda bonds. The Chinese yuan appears only as a valuation currency and as a loan-repayment currency in a Zambia restructuring (physical pages 33, 71, 74), with no bond issuance amounts.",
        "absence_check": {"terms": ["panda"], "manual": "Read the 3 pages that mention the yuan (p33, p71, p74): none gives issuance amounts."},
    },
    {
        "id": "u03", "split": "test", "type": "thieu_bang_chung",
        "question": "What does the report project the total external debt stock of low- and middle-income countries will be at the end of 2028?",
        "absence_reason": "The report analyses 2025 outcomes. Its only forward-looking statements are that IDA-eligible countries' borrowing costs are 'projected to increase' (no figure, p67) and timelines for the revised debt framework (p88-89); it gives no projected debt stock.",
        "absence_check": {"terms": ["forecast", r"debt stocks? .{0,60}\b2028\b", r"\b2028\b.{0,60}debt stocks?"],
                          "manual": "Scanned chapters 1-3 for 'projected', 'projection', 'expected to', 'outlook', 'will rise/reach': no projected debt stock value."},
    },
    {
        "id": "u04", "split": "test", "type": "thieu_bang_chung",
        "question": "By how much did changes in gold prices alter the external-debt-to-exports ratios of commodity-exporting low- and middle-income countries in 2025?",
        "absence_reason": "The report discusses commodity price shocks and debt but never mentions gold.",
        "absence_check": {"terms": [r"\bgold\b", "bullion"], "manual": None},
    },
]


def convert_day6(q: dict) -> dict:
    origin = {"dev": "day6_dev", "test": "day6_test_reused", "spare": "day6_spare_new"}[q["split"]]
    gold = [{"source_id": q["gold_source_id"], "page": q["gold_page"], "evidence": q["evidence_quote"]}]
    gold += [{"source_id": q["gold_source_id"], "page": a["page"], "evidence": a["evidence_quote"]} for a in q["alt_gold"]]
    return {"id": q["id"], "split": "test" if q["split"] == "spare" else q["split"], "origin": origin,
            "type": q["type"], "chapter_of_gold": q["chapter_of_gold"], "question": q["question"],
            "expected_answer": q["expected_answer"], "gold": gold, "key_facts": q["key_facts"], "filter": q["filter"]}


def main() -> None:
    day6 = json.loads(DAY6.read_text(encoding="utf-8"))
    answerable = [{**convert_day6(q), "answerable": True, "expected_behavior": "search_and_answer"} for q in day6]
    answerable += [{**q, "answerable": True, "expected_behavior": "search_and_answer"} for q in NEW_ANSWERABLE]
    unanswerable = [{**q, "origin": "day7_new", "answerable": False, "expected_behavior": "search_and_abstain",
                     "filter": None} for q in UNANSWERABLE]
    order = {"dev": 0, "test": 1}
    questions = sorted(answerable + unanswerable, key=lambda q: (order[q["split"]], not q["answerable"], q["id"]))
    OUT.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    by = {}
    for q in questions:
        key = (q["split"], "answerable" if q["answerable"] else "unanswerable", q["origin"])
        by[key] = by.get(key, 0) + 1
    for key, n in sorted(by.items()):
        print(key, n)
    print(f"{len(questions)} questions -> {OUT.relative_to(config.REPO_ROOT)}")


if __name__ == "__main__":
    main()
