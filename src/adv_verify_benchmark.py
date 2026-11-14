"""Verify the advanced benchmark against the original PDF and (with --freeze) freeze it by sha256.

    python -m src.adv_verify_benchmark [--freeze]

Checks: split sizes and group minimums from ADVANCED.md; ids unique; dev and test use disjoint pages and no question text is
shared; every gold page exists; text-layer checks (required ones must pass; the others are reported as 'visual only');
absence regexes match 0 of the 280 pages; no gold, answer or evidence field is meant for the pipeline (the runner only reads
id, question, split).
"""
from __future__ import annotations

import argparse
import datetime
import json
import logging
import re
import sys

from pypdf import PdfReader

from . import config
from .textutil import sha256_lf

logging.getLogger("pypdf").setLevel(logging.ERROR)
BENCH = config.BENCHMARK_DIR / "advanced"
MINIMUM = {"test": {"table": 6, "diagram": 5, "chart": 5, "multihop": 4, "text": 4, "abstain": 6},
           "dev": {"abstain": 3}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    questions = json.loads((BENCH / "questions.json").read_text(encoding="utf-8"))
    reader = PdfReader(str(config.PDF_PATH))
    text = {i: re.sub(r"\s+", " ", (p.extract_text() or "")) for i, p in enumerate(reader.pages, 1)}
    problems, notes = [], []

    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids")
    if len({q["question"] for q in questions}) != len(questions):
        problems.append("a question text is repeated")
    for split, need in MINIMUM.items():
        rows = [q for q in questions if q["split"] == split]
        answerable = [q for q in rows if q["answerable"]]
        if split == "test" and (len(rows) < 30 or len(answerable) < 24):
            problems.append(f"test needs >= 30 questions and >= 24 answerable, has {len(rows)} / {len(answerable)}")
        if split == "dev" and (len(answerable) < 15):
            problems.append(f"dev needs >= 15 answerable, has {len(answerable)}")
        for group, minimum in need.items():
            have = sum(q["group"] == group for q in rows)
            if have < minimum:
                problems.append(f"{split}: group {group} has {have} < {minimum}")
    pages = {s: {g["page"] for q in questions if q["split"] == s and q["answerable"] for g in q["gold"]} for s in ("dev", "test")}
    shared = sorted(pages["dev"] & pages["test"])
    if shared:
        problems.append(f"dev and test share gold pages {shared}")

    visual_only = []
    for q in questions:
        if q["answerable"]:
            for gold in q["gold"]:
                if not 1 <= gold["page"] <= len(reader.pages):
                    problems.append(f"{q['id']}: page {gold['page']} out of range")
            for chk in q["checks"]:
                missing = [t for t in chk["contains"] if re.sub(r"\s+", " ", t) not in text[chk["page"]]]
                if missing and chk["required"]:
                    problems.append(f"{q['id']}: required text {missing} not on page {chk['page']}")
                elif missing:
                    visual_only.append((q["id"], chk["page"], missing))
        else:
            for rx in q["absence_check"]["regexes_over_all_pages"]:
                found = [p for p, t in text.items() if re.search(rx, t, flags=re.I)]
                if found:
                    problems.append(f"{q['id']}: absence regex {rx!r} matches pages {found}")
            if not q["absence_check"]["regexes_over_all_pages"] and not q["absence_check"]["visual_note"]:
                problems.append(f"{q['id']}: no absence check")

    for split in ("dev", "test"):
        rows = [q for q in questions if q["split"] == split]
        notes.append(f"{split}: {len(rows)} questions, {sum(q['answerable'] for q in rows)} answerable, "
                     + ", ".join(f"{g} {sum(q['group'] == g for q in rows)}" for g in ("table", "diagram", "chart", "multihop", "text", "abstain")))
    notes.append(f"gold pages dev {sorted(pages['dev'])}")
    notes.append(f"gold pages test {sorted(pages['test'])}")
    notes.append(f"{sum(len(q.get('checks', [])) for q in questions)} text checks; not found in the text layer (evidence is visual only): {visual_only or 'none'}")
    print("\n".join(notes))
    if problems:
        print("\nPROBLEMS:\n- " + "\n- ".join(problems))
        sys.exit(1)
    print("\nOK: all checks passed")
    if args.freeze:
        tz = datetime.timezone(datetime.timedelta(hours=7))
        record = {"file": "benchmark/advanced/questions.json", "sha256": sha256_lf(BENCH / "questions.json"),
                  "frozen_at": datetime.datetime.now(tz).isoformat(timespec="seconds"),
                  "note": "Frozen before any advanced pipeline run on dev or test; the runner refuses to run if the hash differs."}
        (BENCH / "FROZEN.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print("frozen:", record["sha256"])


if __name__ == "__main__":
    main()
