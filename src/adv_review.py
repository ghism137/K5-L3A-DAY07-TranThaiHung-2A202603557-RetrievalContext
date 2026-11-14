"""Advanced challenge: review sheet and final tally for the test split.

    python -m src.adv_review

Reads results/advanced/test/<config>/traces.json and the hand labels in results/advanced/test/review/labels.json, writes
review/review_sheet.md (question, reference answer, gold evidence with the original page image path, system answer, what each
citation points to, the first-pass automatic grade, the label and its reason) and review/final_summary.json (n/N overall and per
group, errors, tokens, time). The labels are the grade of record; the automatic grade is only a first pass.

Pass rule (ADVANCED.md): answerable = correct and complete (units, conditions, calculation), citation identifies the page and region,
the cited evidence supports the whole answer; partial, wrong citation or refusal = fail. Unanswerable = refuses or states clearly that
the evidence is missing, adds no unsupported claim. System error / timeout / no result = fail and stays in the denominator.
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict

from . import config

CONFIG = "VISUAL"
REVIEW = config.RESULTS_DIR / "advanced" / "test" / "review"
BENCH = config.BENCHMARK_DIR / "advanced"


def main() -> None:
    questions = {q["id"]: q for q in json.loads((BENCH / "questions.json").read_text(encoding="utf-8")) if q["split"] == "test"}
    traces = {t["query_id"]: t for t in json.loads((config.RESULTS_DIR / "advanced" / "test" / CONFIG / "traces.json").read_text(encoding="utf-8"))}
    chunks = {c["id"]: c for c in json.loads((config.DATA_DIR / "advanced" / "index" / "chunks.json").read_text(encoding="utf-8"))}
    labels = {r["id"]: r for r in json.loads((REVIEW / "labels.json").read_text(encoding="utf-8"))}
    missing = [q for q in questions if q not in labels or labels[q]["label"] not in ("pass", "fail")]
    if missing:
        raise SystemExit(f"labels missing for {missing}")

    lines = [f"# Bảng chấm tay — thử thách nâng cao, test ({CONFIG})", "",
             "Mỗi câu: câu hỏi, đáp án chuẩn, evidence gold (kèm ảnh trang gốc), câu trả lời của hệ thống, nơi các citation trỏ tới, "
             "chấm tự động lượt đầu và **nhãn** kèm lý do. Ảnh trang gốc nằm ở `data/advanced/pages/pNNN.png` "
             "(dựng lại bằng `python -m src.adv_render`). Nhãn là điểm của câu; chấm tự động chỉ là lượt đầu.", ""]
    tally = defaultdict(lambda: [0, 0])
    for qid in sorted(questions):
        q, t, lab = questions[qid], traces[qid], labels[qid]
        tally[q["group"]][1] += 1
        tally[q["group"]][0] += lab["label"] == "pass"
        lines += ["---", "", f"## {qid} — {q['group']} — nhãn: **{lab['label'].upper()}**"
                  + (" (khác chấm tự động)" if lab["label"] != ("pass" if t["grade"]["pass_auto"] else "fail") else ""), "",
                  f"**Câu hỏi:** {q['question']}", ""]
        if q["answerable"]:
            lines += [f"**Đáp án chuẩn:** {q['expected_answer']}" + (f" (dung sai {q['tolerance']})" if q.get("tolerance") else ""), ""]
            for g in q["gold"]:
                lines.append(f"- Evidence gold: trang {g['page']} — {g['locator']} → `{g['evidence']}` "
                             f"(ảnh gốc `data/advanced/pages/p{g['page']:03d}.png`)")
            lines.append("")
        else:
            lines += [f"**Hành vi mong đợi:** từ chối. Lý do: {q['absence_reason']}", ""]
            note = q["absence_check"].get("visual_note")
            if note:
                lines += [f"Kiểm tra bằng ảnh: {note}", ""]
        lines += [f"**Hệ thống ({t['status']}, {t['grade']['n_searches']} lượt tìm, {t['elapsed_s']} s):** {t['answer']}", ""]
        if t["status"] != "answered":
            ev = t["events"][-1]
            lines += [f"Lý do hệ thống nêu: {ev.get('reason', ev.get('event'))}", ""]
        for cid in t["citations"]:
            ch = chunks.get(cid)
            if ch:
                meta = ch["metadata"]
                what = (meta.get("label") or meta.get("title") or meta.get("kind")) if meta["kind"] == "visual" else "văn bản"
                lines.append(f"- Citation `{cid}` → trang {ch['page']}, {what}")
        lines += ["", f"Chấm tự động lượt đầu: {'đạt' if t['grade']['pass_auto'] else 'không đạt'} ({t['grade']['why']}). "
                      f"**Lý do nhãn:** {lab['reason']}", ""]
    (REVIEW / "review_sheet.md").write_text("\n".join(lines), encoding="utf-8")

    n_pass = sum(v[0] for v in tally.values())
    n_total = sum(v[1] for v in tally.values())
    ok = [t for t in traces.values() if t["status"] != "error"]
    auto = sum(t["grade"]["pass_auto"] for t in traces.values())
    summary = {"config": CONFIG, "split": "test", "passed": n_pass, "total": n_total, "rate_percent": round(100 * n_pass / n_total, 2),
               "threshold": "27/30 (90%), not rounded", "meets_threshold": n_pass * 10 >= n_total * 9,
               "by_group": {g: f"{a}/{b}" for g, (a, b) in sorted(tally.items())},
               "failed": [q for q in sorted(questions) if labels[q]["label"] == "fail"],
               "system_errors": [q for q, t in traces.items() if t["status"] == "error"],
               "first_pass_auto": f"{auto}/{n_total}",
               "labels_changed_from_auto": [q for q in sorted(questions)
                                            if labels[q]["label"] != ("pass" if traces[q]["grade"]["pass_auto"] else "fail")],
               "median_seconds": round(statistics.median(t["elapsed_s"] for t in ok), 1),
               "tokens": {"agent_input": sum(t["usage"]["input_tokens"] for t in traces.values()),
                          "agent_output": sum(t["usage"]["output_tokens"] for t in traces.values()),
                          "agent_reasoning": sum(t["usage"]["reasoning_tokens"] for t in traces.values()),
                          "embedding": sum(t["usage"]["embedding_tokens"] for t in traces.values())},
               "note": "labels are the grade of record; gpt-6.1-terra prices are unknown, so cost is reported in tokens"}
    (REVIEW / "final_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
