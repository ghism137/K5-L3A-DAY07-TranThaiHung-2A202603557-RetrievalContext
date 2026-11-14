"""Check the Day 7 environment end to end. Never prints the API key.

    python -m src.check_setup            # database checks, then a live embedding + search if a key is set
"""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from . import config
from .store import PgVectorStore

EXPECTED_CHUNKS = {"A": 376, "B": 429}  # Day 6 index sizes (results/chunk_stats.json in Day 6)


def line(ok: bool | None, msg: str) -> None:
    print(("PASS " if ok else "SKIP " if ok is None else "FAIL ") + msg)


def main() -> int:
    if not config.ENV_PATH.exists():
        line(False, f"{config.ENV_PATH.name} not found: copy .env.example to .env")
        return 1
    load_dotenv(config.ENV_PATH)
    failed = False
    url, model = os.environ.get("DATABASE_URL", ""), os.environ.get("EMBEDDING_MODEL", "")
    line(bool(url), "DATABASE_URL is set")
    line(model == "text-embedding-3-small", f"EMBEDDING_MODEL = {model!r} (must match the Day 6 index)")
    store = PgVectorStore(url, 1536, model)
    try:
        v = store.versions()
        line(True, f"database reachable: PostgreSQL {v['postgresql'].split()[0]}, pgvector {v['pgvector']}")
        for s, expected in EXPECTED_CHUNKS.items():
            rows, distinct = store.count(s)
            ok = rows == distinct == expected
            failed |= not ok
            line(ok, f"index {s}: {rows} rows, {distinct} distinct ids (expected {expected})")
    except Exception as exc:  # report the connection problem, do not hide it
        line(False, f"database: {type(exc).__name__}: {exc}")
        return 1

    key = os.environ.get("OPENAI_API_KEY")
    line(bool(key), "OPENAI_API_KEY is set" if key else "OPENAI_API_KEY is empty")
    if not key:
        return 1
    from .embeddings import OpenAIEmbedder
    try:
        emb = OpenAIEmbedder()
        hits = store.search("A", emb.embed_query("What was the record level of LMIC external debt in 2025?"), 3)
        line(bool(hits), f"live query: top-1 {hits[0]['chunk_id']} p{hits[0]['page']} score {hits[0]['score']:.3f}"
                         f" ({emb.total_tokens} tokens, ~${emb.estimated_cost_usd:.7f})")
        failed |= not hits
    except Exception as exc:
        line(False, f"embedding/search: {type(exc).__name__}: {exc}")
        return 1
    if os.environ.get("AGENT_MODEL"):
        line(True, f"AGENT_MODEL = {os.environ['AGENT_MODEL']} (not called here)")
    else:
        line(None, "AGENT_MODEL is empty: set it before running the agent")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
