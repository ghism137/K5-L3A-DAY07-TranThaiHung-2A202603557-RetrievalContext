"""Build the blinded manual-review sheet for the test split.

    python -m src.make_review_sheet

Reads results/agent/test/{R0,BASE}/traces.json and writes, under results/agent/test/review/:
  review_sheet.md   what the reviewer reads: question, expected answer + gold evidence, then "System 1" and "System 2"
                    (order shuffled per question with a fixed seed; the id prefixes 'fixed:'/'para:' that would reveal
                    the index are masked as 'c:')
  review_labels.json  template to fill (null = not yet labelled)
  blind_key.json      item -> configuration; open it only after labelling
Gold is shown to the reviewer (that is the point of the audit); it never entered the agent.
"""
from __future__ import annotations

import json
import random
import re

from . import config

CONFIGS = ["R0", "BASE"]
SEED = 20261114
MASK = re.compile(r"\b(?:fixed|para):idr-2026:")
OUT = config.RESULTS_DIR / "agent" / "test" / "review"


def mask(text: str) -> str:
    return MASK.sub("c:", text)


def passage_text_for(trace: dict, chunk_id: str) -> str | None:
    searches = [e for e in trace["events"] if e["event"] == "search"]
    for p in (searches[-1]["passages"] if searches else []):
        if chunk_id in p["ids"]:
            return p["text"]
    return None


def main() -> None:
    questions = {q["id"]: q for q in json.loads((config.BENCHMARK_DIR / "questions.json").read_text(encoding="utf-8"))}
    traces = {c: {t["query_id"]: t for t in json.loads((config.RESULTS_DIR / "agent" / "test" / c / "traces.json")
                                                      .read_text(encoding="utf-8"))} for c in CONFIGS}
    rng = random.Random(SEED)
    key, labels, lines = {}, [], []
    lines += [
        "# Bảng chấm tay — test (ẩn tên hệ thống)", "",
        "Mỗi câu có hai hệ thống (1 và 2) theo thứ tự xáo trộn; tên cấu hình nằm ở `blind_key.json` (chỉ mở sau khi chấm xong). "
        "Tiền tố ID chunk được che thành `c:`. Điền nhãn vào `review_labels.json` (mục `item` trùng tiêu đề từng khối).", "",
        "## Thang chấm (BENCHMARK.md)", "",
        "- **context_grade** (câu có đáp án): 0 = context không có evidence; 1 = có nhưng thiếu điều kiện hoặc nguồn; "
        "2 = đủ evidence và nguồn. Chấm trên *context cuối* của hệ thống, kể cả khi hệ thống từ chối.",
        "- **answer_grade** (câu có đáp án): 0 = sai/thiếu evidence, hoặc từ chối; 1 = đúng một phần; 2 = đúng và đủ.",
        "- **citation_support**: một `true/false` cho từng citation: chunk được trích có *thực sự* hỗ trợ câu trả lời "
        "(ID hợp lệ chưa đủ). Hệ thống từ chối thì danh sách rỗng.",
        "- **abstention_correct** (câu thiếu evidence): `true` chỉ khi hệ thống từ chối và không thêm khẳng định vô căn cứ.", ""]
    for qid in sorted(questions, key=lambda i: (not questions[i]["answerable"], i)):
        q = questions[qid]
        if q["split"] != "test":
            continue
        order = CONFIGS[:]
        rng.shuffle(order)
        lines += ["---", "", f"## {qid} — {'có đáp án' if q['answerable'] else 'THIẾU EVIDENCE (đúng là phải từ chối)'}", "",
                  f"**Câu hỏi:** {q['question']}", ""]
        if q["answerable"]:
            lines += [f"**Đáp án mong đợi:** {q['expected_answer']}", ""]
            lines += [f"**Evidence gold:** trang {g['page']}: \"{g['evidence']}\"" for g in q["gold"]]
            lines += ["", f"**Key facts:** {q['key_facts']}", ""]
        else:
            lines += [f"**Vì sao không trả lời được:** {q['absence_reason']}", ""]
        for n, cfg in enumerate(order, 1):
            t = traces[cfg][qid]
            item = f"{qid}#{n}"
            key[item] = cfg
            searches = [e for e in t["events"] if e["event"] == "search"]
            lines += [f"### {item} — Hệ thống {n}", "",
                      f"- Trạng thái: **{t['status']}** ({t['events'][-1]['event']}); số lượt tìm: {len(searches)}",
                      "- Truy vấn: " + "; ".join(f"`{e['query']}`" for e in searches), "",
                      f"**Câu trả lời trả về:** {mask(t['answer'])}", ""]
            if t["events"][-1]["event"] == "model_abstain":
                lines += [f"*Lý do model nêu:* {mask(t['events'][-1].get('reason', ''))}", ""]
            if t["events"][-1]["event"] == "invalid_or_missing_citations":
                lines += ["<details><summary>Bản nháp model viết nhưng bị loại do citation không hợp lệ "
                          "(không tính là câu trả lời)</summary>", "",
                          mask(t["events"][-1]["model_answer"]), "",
                          f"citations khai báo: {[mask(c) for c in t['events'][-1]['model_citations']]}", "", "</details>", ""]
            for i, cid in enumerate(t["citations"], 1):
                txt = passage_text_for(t, cid) or "(không tìm thấy trong context)"
                lines += [f"**Citation {i}:** `{mask(cid)}`", "", f"> {mask(txt)}", ""]
            if searches:
                lines += ["<details><summary>Context cuối gửi cho model</summary>", "", "```", mask(searches[-1]["context"]),
                          "```", "", "</details>", ""]
            row = {"item": item, "query_id": qid, "system": n, "notes": ""}
            if q["answerable"]:
                row.update(context_grade=None, answer_grade=None, citation_support=[None] * len(t["citations"]))
            else:
                row.update(abstention_correct=None, citation_support=[None] * len(t["citations"]))
            labels.append(row)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "review_sheet.md").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "review_labels.json").write_text(json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "blind_key.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"{len(labels)} items -> {OUT}")


if __name__ == "__main__":
    main()
