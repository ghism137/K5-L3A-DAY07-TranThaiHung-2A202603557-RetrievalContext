"""Three retrieval methods over the Day 6 chunks: dense (pgvector), BM25 (lexical), hybrid RRF.

All return the same result shape (id, text, source_id, source, page, metadata, score, rank, method)
so they can be compared, fused, and passed to an agent unchanged. No benchmark gold is used here.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from typing import Any

from .embeddings import Embedder
from .store import PgVectorStore

_TOKEN = re.compile(r"\w+")


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens. English corpus: no stemming, no stop-word list (BM25's IDF
    already down-weights frequent words); numbers like '28.2' become '28' and '2'."""
    return _TOKEN.findall(unicodedata.normalize("NFKC", text).casefold())


def _result(chunk: dict[str, Any], score: float, rank: int, method: str) -> dict[str, Any]:
    return {"id": chunk["id"], "text": chunk["text"], "source_id": chunk["source_id"], "source": chunk["source"],
            "page": chunk["page"], "metadata": chunk["metadata"], "score": float(score), "rank": rank, "method": method}


def _passes(chunk: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    return all(chunk["metadata"].get(k) == v for k, v in (filters or {}).items())


class BM25Retriever:
    """Okapi BM25 (k1=1.5, b=0.75) over an exported chunk list. Statistics (IDF, average length)
    are computed once over the whole index; a metadata filter only restricts which chunks may be returned."""

    method = "bm25"

    def __init__(self, chunks: list[dict[str, Any]], k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks, self.k1, self.b = chunks, k1, b
        self.tf = [Counter(tokenize(c["text"])) for c in chunks]
        self.len = [sum(t.values()) for t in self.tf]
        self.avg_len = sum(self.len) / len(chunks)
        df = Counter(term for t in self.tf for term in t)
        n = len(chunks)
        self.idf = {term: math.log(1 + (n - d + 0.5) / (d + 0.5)) for term, d in df.items()}

    def search(self, query: str, *, top_k: int, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        terms = [t for t in set(tokenize(query)) if t in self.idf]
        scored = []
        for chunk, tf, length in zip(self.chunks, self.tf, self.len):
            if not _passes(chunk, filters):
                continue
            score = sum(self.idf[t] * tf[t] * (self.k1 + 1) /
                        (tf[t] + self.k1 * (1 - self.b + self.b * length / self.avg_len))
                        for t in terms if t in tf)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda x: (-x[0], x[1]["id"]))
        return [_result(c, s, i, self.method) for i, (s, c) in enumerate(scored[:top_k], 1)]


class DenseRetriever:
    """Cosine nearest neighbours in the Day 6 pgvector index; the query is embedded with the
    same model as the documents. `search_vector` lets callers embed once and reuse the vector."""

    method = "dense"

    def __init__(self, store: PgVectorStore, embedder: Embedder, strategy: str) -> None:
        self.store, self.embedder, self.strategy = store, embedder, strategy

    def search_vector(self, vector: list[float], *, top_k: int,
                      filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        rows = self.store.search(self.strategy, vector, top_k, filters)
        return [_result({"id": r["chunk_id"], "text": r["text"], "source_id": r["document_id"],
                         "source": r["source"], "page": r["page"], "metadata": r["metadata"]},
                        r["score"], i, self.method) for i, r in enumerate(rows, 1)]

    def search(self, query: str, *, top_k: int, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.search_vector(self.embedder.embed_query(query), top_k=top_k, filters=filters)


def rrf(rank_lists: list[list[dict[str, Any]]], *, k: int = 60, top_k: int, method: str = "hybrid_rrf") -> list[dict[str, Any]]:
    """Reciprocal Rank Fusion: score(chunk) = sum over lists of 1 / (k + rank in that list).
    Only ranks are used, so dense (cosine) and BM25 scores need no common scale."""
    fused: dict[str, float] = {}
    first: dict[str, dict[str, Any]] = {}
    for results in rank_lists:
        for r in results:
            fused[r["id"]] = fused.get(r["id"], 0.0) + 1.0 / (k + r["rank"])
            first.setdefault(r["id"], r)
    ordered = sorted(fused, key=lambda i: (-fused[i], i))[:top_k]
    return [_result(first[i], fused[i], rank, method) for rank, i in enumerate(ordered, 1)]
