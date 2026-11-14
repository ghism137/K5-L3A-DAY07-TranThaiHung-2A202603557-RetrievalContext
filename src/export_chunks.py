"""Export the chunks stored in the Day 6 vector store to the Day 7 JSON contract (data/README.md).

Reads the database only (no API key needed). The export is what lexical retrievers index, so
it comes from the same rows the dense retriever searches; nothing is re-chunked here.

    python -m src.export_chunks            # writes data/index/chunks_A.json and chunks_B.json
"""
from __future__ import annotations

import json
import os

import psycopg
from dotenv import load_dotenv

from . import config

OUT_DIR = config.DATA_DIR / "index"


def export(conn: psycopg.Connection, strategy: str) -> list[dict]:
    rows = conn.execute(
        """SELECT chunk_id, document_id, source, page, printed_page, chapter, chapter_title,
                  section, chunk_index, char_count, text
           FROM chunks WHERE strategy = %s ORDER BY page, chunk_index""", (strategy,)).fetchall()
    return [{
        "id": r[0], "text": r[10], "source_id": r[1], "source": r[2], "page": r[3],
        "metadata": {"printed_page": r[4], "chapter": r[5], "chapter_title": r[6],
                     "section": r[7], "chunk_index": r[8], "char_count": r[9], "strategy": strategy},
    } for r in rows]


def main() -> None:
    load_dotenv(config.ENV_PATH)
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is not set (copy .env.example to .env)")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(url, connect_timeout=5) as conn:
        for strategy in ("A", "B"):
            chunks = export(conn, strategy)
            ids = [c["id"] for c in chunks]
            if not chunks or len(ids) != len(set(ids)):
                raise RuntimeError(f"strategy {strategy}: empty export or duplicate ids")
            path = OUT_DIR / f"chunks_{strategy}.json"
            path.write_text(json.dumps(chunks, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"{strategy}: {len(chunks)} chunks -> {path.relative_to(config.REPO_ROOT)}")


if __name__ == "__main__":
    main()
