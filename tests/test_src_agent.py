"""Offline tests for the Day 7 student code: context building, fusion and the agent loop with a scripted model.

The scripted model is only used to test control flow (citation validation, abstention, search limit); it is never
used to report benchmark quality.  Run (no pytest needed):  PYTHONUTF8=1 python tests/test_src_agent.py
"""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent import (CONFIGS, ContextBuilder, PipelineConfig, Resources, merge_run, new_facts, overlap,  # noqa: E402
                       render, run_agent, seq_of, system_prompt)
from src.retrieval import BM25Retriever, rrf  # noqa: E402


def chunk(page, seq, text, prefix="fixed"):
    return {"id": f"{prefix}:idr:p{page:04d}:{seq:03d}", "text": text, "source_id": "idr", "source": "x.pdf",
            "page": page, "metadata": {"chapter": 1}}


def fake_resources(chunks, index="A"):
    res = object.__new__(Resources)
    res.chunks = {index: chunks}
    res.by_key = {index: {(c["page"], seq_of(c["id"])): c for c in chunks}}
    return res


def seed(c, rank):
    return {**c, "score": 1.0, "rank": rank, "method": "x"}


def test_overlap_and_merge_remove_duplicated_tail():
    a = "A" * 700 + "0123456789" * 10
    b = "0123456789" * 10 + "B" * 700
    assert overlap(a, b) == 100
    assert merge_run([{"text": a}, {"text": b}]) == "A" * 700 + "0123456789" * 10 + "B" * 700


def test_baseline_context_keeps_whole_chunks_and_respects_budget():
    chunks = [chunk(5, i, "x" * 800) for i in range(4)]
    builder = ContextBuilder(CONFIGS["R0"], fake_resources(chunks))
    ctx = builder.build([seed(c, i + 1) for i, c in enumerate(chunks[:3])])
    assert ctx["body_chars"] == 2400 and len(ctx["ids"]) == 3
    ctx = builder.build([seed(c, i + 1) for i, c in enumerate(chunks)])  # a 4th chunk does not fit
    assert len(ctx["ids"]) == 3


def test_expand_merges_overlap_and_adds_neighbour_within_budget():
    tail = "0123456789" * 10
    c0 = chunk(7, 0, "P" * 700 + tail)
    c1 = chunk(7, 1, tail + "Q" * 700)
    c2 = chunk(7, 2, "R" * 800)
    res = fake_resources([c0, c1, c2])
    builder = ContextBuilder(PipelineConfig("t", "dense", "A", expand=True), res)
    ctx = builder.build([seed(c1, 1)])
    # seed c1 + previous neighbour c0 (100-char overlap removed) + next neighbour c2 (no overlap: joined by one space)
    assert ctx["ids"] == [c0["id"], c1["id"], c2["id"]]
    assert len(ctx["passages"]) == 1
    assert ctx["body_chars"] == (700 + 100 + 700) + 1 + 800 <= 2400


def test_rewrite_guard_flags_added_numbers_and_acronyms_only():
    q = "external debt of low- and middle-income countries at the end of 2025"
    assert new_facts(q, "external debt low-income and middle-income countries end of 2025") == []
    assert new_facts(q, "external debt ... end of 2026") == ["2026"]
    assert new_facts("What is a TRS?", "total return swap TRS IMF") == ["IMF"]


def test_passage_header_exposes_bracketed_ids_for_copying():
    text = render([{"ids": ["a:1", "a:2"], "page": 9, "text": "body"}])
    assert text.startswith("[a:1] [a:2] (page 9)\nbody")


def test_rrf_prefers_chunks_ranked_high_in_both_lists():
    mk = lambda ids: [{"id": i, "rank": r, "text": "", "source_id": "s", "source": "s", "page": 1, "metadata": {}, "score": 0}
                      for r, i in enumerate(ids, 1)]
    fused = rrf([mk(["a", "b", "c"]), mk(["d", "b", "e"])], k=60, top_k=3)
    assert fused[0]["id"] == "b"  # 1/62 + 1/62 beats 1/61 + absent
    assert abs(fused[0]["score"] - 2 / 62) < 1e-12


def test_bm25_filter_restricts_results_only():
    chunks = [chunk(1, 0, "domestic debt share"), {**chunk(2, 0, "domestic debt share"), "metadata": {"chapter": 3}}]
    bm = BM25Retriever(chunks)
    assert [r["page"] for r in bm.search("domestic debt", top_k=5, filters={"chapter": 3})] == [2]


# ---- agent loop with a scripted model (control flow only)
class Scripted:
    def __init__(self, calls):
        self.calls = list(calls)

    def create(self, messages, tools=None):
        name, args = self.calls.pop(0)
        import json
        call = SimpleNamespace(id=f"c{len(messages)}", function=SimpleNamespace(name=name, arguments=json.dumps(args)))
        return SimpleNamespace(content=None, tool_calls=[call])


class FakePipeline:
    def __init__(self, seeds):
        self.seeds = seeds
        self.cfg = SimpleNamespace(index="A")

    def search(self, query, filters):
        return self.seeds, {"rewritten_query": None, "retrieval_ms": 0.0}


def run(calls, chunks):
    res = fake_resources(chunks)
    return run_agent("q?", None, FakePipeline([seed(c, i + 1) for i, c in enumerate(chunks)]),
                     ContextBuilder(CONFIGS["R0"], res), Scripted(calls), max_searches=3)


def test_agent_accepts_only_citations_present_in_context_and_answer():
    c = chunk(1, 0, "fact")
    ok = run([("search_documents", {"query": "x"}), ("answer", {"answer": f"yes [{c['id']}]", "citations": [c["id"]]})], [c])
    assert ok["status"] == "answered" and ok["citations"] == [c["id"]]
    bad = run([("search_documents", {"query": "x"}), ("answer", {"answer": "yes", "citations": [c["id"]]})], [c])
    assert bad["status"] == "abstain" and bad["events"][-1]["event"] == "invalid_or_missing_citations"
    unknown = run([("search_documents", {"query": "x"}), ("answer", {"answer": "yes [zzz]", "citations": ["zzz"]})], [c])
    assert unknown["status"] == "abstain"


def test_malformed_model_output_is_an_abstention_not_a_provider_error():
    c = chunk(1, 0, "fact")
    r = run([("search_documents", {"query": "x"}), ("answer", {"answer": "yes", "citations": c["id"]})], [c])
    assert r["status"] == "abstain" and r["events"][-1]["event"] == "malformed_answer"
    assert run([("search_documents", {"query": ""})], [c])["events"][-1]["event"] == "malformed_search_query"


def test_prompt_example_id_matches_index_prefix():
    assert "[fixed:idr-2026:p0031:003]" in system_prompt("A") and "para:" not in system_prompt("A")
    assert "[para:idr-2026:p0031:003]" in system_prompt("B") and "fixed:" not in system_prompt("B")


def test_agent_abstains_without_search_and_after_search_limit_and_on_request():
    c = chunk(1, 0, "fact")
    assert run([("answer", {"answer": f"[{c['id']}]", "citations": [c["id"]]})], [c])["status"] == "abstain"
    assert run([("search_documents", {"query": "x"}), ("abstain", {"reason": "no evidence"})], [c])["events"][-1]["event"] == "model_abstain"
    four = [("search_documents", {"query": f"x{i}"}) for i in range(4)]
    assert run(four, [c])["events"][-1]["event"] == "search_limit"


if __name__ == "__main__":
    import traceback
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except Exception:
                failed += 1
                print("FAIL", name)
                traceback.print_exc()
    raise SystemExit(1 if failed else 0)
