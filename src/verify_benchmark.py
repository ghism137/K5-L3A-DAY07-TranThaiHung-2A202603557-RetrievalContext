"""Verify benchmark/questions.json (Day 7 schema) against the PDF and the exported chunks.

    python -m src.verify_benchmark             # check only -> results/benchmark_verification.txt
    python -m src.verify_benchmark --freeze    # check, then record a sha256 in benchmark/FROZEN.json

Answerable questions: evidence and key facts occur on the gold page; the filter does not exclude
the gold page; every key fact lies inside ONE chunk of index A and of index B (otherwise the
chunking, not retrieval, would decide the outcome); other pages containing all key facts are listed.
Unanswerable questions: each absence_check term matches no page of the whole 280-page PDF.
Nothing here looks at retrieval results.
"""
from __future__ import annotations

import json
import logging
import re
import sys
from collections import Counter
from datetime import datetime

from . import config
from .ingestion import apply_report_structure, content_pages, load_pdf, read_outline
from .textutil import canon, sha256_lf

logging.getLogger("pypdf").setLevel(logging.ERROR)

QUESTIONS = config.BENCHMARK_DIR / "questions.json"
FROZEN = config.BENCHMARK_DIR / "FROZEN.json"
DAY6_QUESTIONS = config.BENCHMARK_DIR / "day6_questions.json"
DAY6_FROZEN = config.BENCHMARK_DIR / "day6_FROZEN.json"
REPORT = config.RESULTS_DIR / "benchmark_verification.txt"
INDEX_DIR = config.DATA_DIR / "index"
COMMON = {"id", "split", "origin", "type", "question", "answerable", "expected_behavior", "filter"}
ANSWERABLE = {"expected_answer", "gold", "key_facts", "chapter_of_gold"}
UNANSWERABLE = {"absence_reason", "absence_check"}


def main() -> int:
    freeze = "--freeze" in sys.argv
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    out: list[str] = []
    problems: list[str] = []

    def fail(qid: str, msg: str) -> None:
        problems.append(f"{qid}: {msg}")

    # Provenance: the Day 6 file we converted from must be the one frozen in Day 6.
    day6_ok = sha256_lf(DAY6_QUESTIONS) == json.loads(DAY6_FROZEN.read_text(encoding="utf-8"))["sha256"]
    out.append(("PASS " if day6_ok else "FAIL ") + "benchmark/day6_questions.json matches its Day 6 frozen hash")
    if not day6_ok:
        problems.append("day6_questions.json changed since Day 6")

    pages = load_pdf(config.PDF_PATH, config.DOCUMENT_ID, "x", header_banner=config.HEADER_BANNER)
    full = {p.page: canon(p.text) for p in pages}  # every physical page, before scope trimming
    apply_report_structure(pages, read_outline(config.PDF_PATH), config.MIN_CONTENT_CHARS)
    by_page = {p.page: p for p in content_pages(pages)}
    text = {n: canon(p.text) for n, p in by_page.items()}
    chunks = {s: json.loads((INDEX_DIR / f"chunks_{s}.json").read_text(encoding="utf-8")) for s in ("A", "B")}
    chunk_text = {s: [canon(c["text"]) for c in rows] for s, rows in chunks.items()}

    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        fail("-", "duplicate ids")
    if len({q["question"] for q in questions}) != len(questions):
        fail("-", "duplicate question text")

    for q in questions:
        qid = q["id"]
        need = COMMON | (ANSWERABLE if q.get("answerable") else UNANSWERABLE)
        if need - q.keys():
            fail(qid, f"missing fields {sorted(need - q.keys())}")
            continue
        if q["split"] not in ("dev", "test"):
            fail(qid, f"split must be dev or test, got {q['split']!r}")
        if not q["answerable"]:
            hits = {t: [n for n, x in full.items() if re.search(t, x, re.I)] for t in q["absence_check"]["terms"]}
            bad = {t: p for t, p in hits.items() if p}
            if bad:
                fail(qid, f"absence terms found in the PDF: {bad}")
            out.append(f"{'BAD' if bad else 'OK '} {qid} [{q['split']:4s}] UNANSWERABLE terms with 0 PDF pages: "
                       f"{[t for t, p in hits.items() if not p]}")
            continue
        gold_pages = {g["page"] for g in q["gold"]}
        probs = []
        for g in q["gold"]:
            if g["page"] not in by_page:
                probs.append(f"gold page {g['page']} is not a content page")
            elif canon(g["evidence"]) not in text[g["page"]]:
                probs.append(f"evidence NOT found on p{g['page']}")
        page = q["gold"][0]["page"]
        if page in by_page:
            missing = [k for k in q["key_facts"] if canon(k) not in text[page]]
            if missing:
                probs.append(f"key facts not on p{page}: {missing}")
            chapter = by_page[page].metadata["chapter"]
            if q["chapter_of_gold"] != chapter:
                probs.append(f"chapter_of_gold={q['chapter_of_gold']} but p{page} is chapter {chapter}")
            if q["filter"] and q["filter"].get("chapter") not in (None, chapter):
                probs.append(f"filter {q['filter']} excludes gold page p{page}")
        facts = [canon(k) for k in q["key_facts"]]
        for s in ("A", "B"):
            # a chunk on a gold page that holds every key fact
            ok = any(all(f in ct for f in facts) for c, ct in zip(chunks[s], chunk_text[s]) if c["page"] in gold_pages)
            if not ok:
                probs.append(f"no single chunk of index {s} holds every key fact (chunking failure by construction)")
        others = [n for n, t in text.items() if n not in gold_pages and all(f in t for f in facts)]
        for p in probs:
            fail(qid, p)
        if others:
            problems.append(f"{qid}: key facts also on {others}: decide whether to add as a second gold")
        out.append(f"{'BAD' if probs else 'OK '} {qid} [{q['split']:4s}] {q['origin']:17s} p{page} ch{q['chapter_of_gold']} "
                   f"filter={q['filter']} | other pages with all key facts: {others or '-'}")

    ans = [q for q in questions if q.get("answerable")]
    una = [q for q in questions if not q.get("answerable")]
    n = lambda qs, split: sum(q["split"] == split for q in qs)  # noqa: E731
    new_test = [q for q in ans if q["split"] == "test" and q["origin"] != "day6_test_reused"]
    gold_pages_by_split = {s: Counter(g["page"] for q in ans if q["split"] == s for g in q["gold"][:1]) for s in ("dev", "test")}
    shared = sorted(set(gold_pages_by_split["dev"]) & set(gold_pages_by_split["test"]))
    dup_pages = sorted(p for c in gold_pages_by_split.values() for p, k in c.items() if k > 1)
    checks = [
        (n(ans, "dev") >= 15, f"dev answerable = {n(ans, 'dev')} (need >= 15)"),
        (n(una, "dev") >= 2, f"dev unanswerable = {n(una, 'dev')} (need >= 2)"),
        (n(ans, "test") >= 5, f"test answerable = {n(ans, 'test')} (need >= 5)"),
        (n(una, "test") >= 2, f"test unanswerable = {n(una, 'test')} (need >= 2)"),
        (len(new_test) >= 5, f"test answerable never seen in Day 6 = {len(new_test)} (need >= 5 for a standalone new test)"),
        (not shared, f"gold pages shared by dev and test: {shared or 'none'}"),
    ]
    out += ["", f"counts: {dict(Counter((q['split'], 'answerable' if q['answerable'] else 'unanswerable') for q in questions))}",
            f"origins: {dict(Counter(q['origin'] for q in questions))}",
            f"filter questions: {dict(Counter(q['split'] for q in ans if q['filter']))}",
            f"gold pages used by more than one question in the same split (informational): {dup_pages or 'none'}"]
    for ok, msg in checks:
        out.append(("PASS " if ok else "FAIL ") + msg)
        if not ok:
            problems.append(msg)
    out += ["", "PROBLEMS:" if problems else "No problems found."] + [f"  - {p}" for p in problems]

    config.RESULTS_DIR.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))

    hard = [p for p in problems if "also on" not in p]
    if freeze:
        if hard:
            print("\nNot frozen: fix the problems above first.")
            return 1
        digest = sha256_lf(QUESTIONS)
        FROZEN.write_text(json.dumps({
            "file": "benchmark/questions.json", "sha256": digest,
            "frozen_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "counts": dict(Counter(f"{q['split']}_{'answerable' if q['answerable'] else 'unanswerable'}" for q in questions)),
            "note": "Recorded before any Day 7 retrieval or agent run. Any later change to the file changes the hash.",
        }, indent=2), encoding="utf-8")
        print(f"\nFrozen: sha256 {digest[:16]}... -> benchmark/FROZEN.json")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
