"""PostgreSQL + pgvector store. Search is exact cosine (no ANN index; ~400 rows per strategy)."""
from __future__ import annotations

import hashlib
from typing import Any

import psycopg

from .models import Chunk

# Only these metadata columns may be used as filters; names are never taken from user input.
FILTERABLE: dict[str, type] = {"chapter": int, "section": str, "chapter_title": str}


def content_hash(model_name: str, text: str) -> str:
    """Identity of a stored vector: same model and same text => same vector."""
    return hashlib.sha256(f"{model_name}\n{text}".encode("utf-8")).hexdigest()


def _literal(vector: list[float]) -> str:
    return "[" + ",".join(repr(float(x)) for x in vector) + "]"


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int, model_name: str) -> None:
        if not database_url:
            raise ValueError("DATABASE_URL is empty")
        if not isinstance(dimensions, int) or dimensions <= 0:
            raise ValueError("dimensions must be a positive integer")
        self.database_url = database_url
        self.dimensions = dimensions
        self.model_name = model_name

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url, connect_timeout=5)

    def create_schema(self) -> None:
        """Create the table if needed and refuse to continue if its vector size differs."""
        with self._connect() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS chunks (
                    strategy      text    NOT NULL,
                    chunk_id      text    NOT NULL,
                    document_id   text    NOT NULL,
                    source        text    NOT NULL,
                    page          integer NOT NULL,
                    printed_page  integer,
                    chapter       integer NOT NULL,
                    chapter_title text    NOT NULL,
                    section       text    NOT NULL,
                    chunk_index   integer NOT NULL,
                    char_count    integer NOT NULL,
                    text          text    NOT NULL,
                    model         text    NOT NULL,
                    content_hash  text    NOT NULL,
                    embedding     vector({self.dimensions}) NOT NULL,
                    ingested_at   timestamptz NOT NULL DEFAULT now(),
                    PRIMARY KEY (strategy, chunk_id)
                )""")
            conn.execute("CREATE INDEX IF NOT EXISTS chunks_filter_idx ON chunks (strategy, chapter)")
            size = conn.execute(
                "SELECT atttypmod FROM pg_attribute WHERE attrelid = 'chunks'::regclass AND attname = 'embedding'"
            ).fetchone()[0]
        if size != self.dimensions:
            raise RuntimeError(f"table chunks stores {size}-dim vectors but the embedder produces {self.dimensions}")

    def versions(self) -> dict[str, str]:
        with self._connect() as conn:
            pg = conn.execute("SELECT current_setting('server_version')").fetchone()[0]
            vec = conn.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'").fetchone()[0]
        return {"postgresql": pg, "pgvector": vec}

    def existing_hashes(self, strategy: str, document_id: str) -> dict[str, str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT chunk_id, content_hash FROM chunks WHERE strategy = %s AND document_id = %s",
                (strategy, document_id)).fetchall()
        return dict(rows)

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Insert or update by (strategy, chunk_id); never creates duplicates."""
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        if any(len(v) != self.dimensions for v in vectors):
            raise ValueError(f"every vector must have {self.dimensions} dimensions")
        rows = [(strategy, c.chunk_id, c.document_id, c.source, c.page, c.metadata["printed_page"],
                 c.metadata["chapter"], c.metadata["chapter_title"], c.metadata["section"],
                 c.metadata["chunk_index"], c.metadata["char_count"], c.text, self.model_name,
                 content_hash(self.model_name, c.text), _literal(v))
                for c, v in zip(chunks, vectors)]
        with self._connect() as conn:
            conn.cursor().executemany("""
                INSERT INTO chunks (strategy, chunk_id, document_id, source, page, printed_page, chapter,
                                    chapter_title, section, chunk_index, char_count, text, model,
                                    content_hash, embedding)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)
                ON CONFLICT (strategy, chunk_id) DO UPDATE SET
                    source = EXCLUDED.source, page = EXCLUDED.page, printed_page = EXCLUDED.printed_page,
                    chapter = EXCLUDED.chapter, chapter_title = EXCLUDED.chapter_title,
                    section = EXCLUDED.section, chunk_index = EXCLUDED.chunk_index,
                    char_count = EXCLUDED.char_count, text = EXCLUDED.text, model = EXCLUDED.model,
                    content_hash = EXCLUDED.content_hash, embedding = EXCLUDED.embedding,
                    ingested_at = now()""", rows)

    def delete_obsolete(self, strategy: str, document_id: str, keep_ids: list[str]) -> int:
        """Remove chunks of this document that are no longer produced (source text changed)."""
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM chunks WHERE strategy = %s AND document_id = %s AND chunk_id <> ALL(%s)",
                (strategy, document_id, keep_ids))
            return cur.rowcount

    def count(self, strategy: str) -> tuple[int, int]:
        """(rows, distinct chunk ids): equal numbers prove there are no duplicates."""
        with self._connect() as conn:
            return conn.execute(
                "SELECT count(*), count(DISTINCT chunk_id) FROM chunks WHERE strategy = %s",
                (strategy,)).fetchone()

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Filter in SQL on allowed metadata, rank by cosine distance; score = 1 - distance."""
        if len(query_vector) != self.dimensions:
            raise ValueError("query vector has the wrong number of dimensions")
        where, params = ["strategy = %s"], [strategy]
        for key, value in (filters or {}).items():
            if key not in FILTERABLE:
                raise ValueError(f"cannot filter on {key!r}; allowed: {sorted(FILTERABLE)}")
            where.append(f"{key} = %s")
            params.append(FILTERABLE[key](value))
        sql = f"""
            SELECT chunk_id, document_id, source, page, printed_page, chapter, chapter_title, section,
                   chunk_index, char_count, text, embedding <=> %s::vector AS distance
            FROM chunks WHERE {' AND '.join(where)}
            ORDER BY distance, chunk_id LIMIT %s"""
        with self._connect() as conn:
            rows = conn.execute(sql, [_literal(query_vector), *params, top_k]).fetchall()
        return [{
            "chunk_id": r[0], "document_id": r[1], "source": r[2], "page": r[3], "text": r[10],
            "score": 1.0 - float(r[11]), "distance": float(r[11]),
            "metadata": {"printed_page": r[4], "chapter": r[5], "chapter_title": r[6],
                         "section": r[7], "chunk_index": r[8], "char_count": r[9]},
        } for r in rows]
