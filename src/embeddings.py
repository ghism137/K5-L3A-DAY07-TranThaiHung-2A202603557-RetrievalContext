"""OpenAI embedding adapter. Any failure raises; there is no fallback to mock vectors."""
from __future__ import annotations

import os
import time
from typing import Protocol

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from . import config

KNOWN_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}
# Assumed list price in USD per 1M input tokens. Verify on OpenAI's pricing page
# before quoting it in the report; token counts below are measured, the price is not.
ASSUMED_USD_PER_MILLION = {"text-embedding-3-small": 0.02, "text-embedding-3-large": 0.13}


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class OpenAIEmbedder:
    """Documents and queries use the same model and no prefix (OpenAI embeddings are symmetric)."""

    BATCH_SIZE = 64
    MAX_ATTEMPTS = 5

    def __init__(self, model_name: str | None = None) -> None:
        load_dotenv(config.ENV_PATH)
        self.model_name = model_name or os.environ.get("EMBEDDING_MODEL", "")
        if self.model_name not in KNOWN_DIMENSIONS:
            raise ValueError(f"EMBEDDING_MODEL={self.model_name!r} is not one of {sorted(KNOWN_DIMENSIONS)}")
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set in .env (copy .env.example)")
        self.dimensions = KNOWN_DIMENSIONS[self.model_name]
        self._client = OpenAI(max_retries=0)  # retries are handled (and counted) here
        self.total_tokens = 0
        self.requests = 0
        self.seconds = 0.0

    @property
    def estimated_cost_usd(self) -> float:
        return self.total_tokens / 1_000_000 * ASSUMED_USD_PER_MILLION[self.model_name]

    def _embed(self, texts: list[str]) -> list[list[float]]:
        if any(not t.strip() for t in texts):
            raise ValueError("cannot embed an empty text")
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            started = time.perf_counter()
            try:
                response = self._client.embeddings.create(model=self.model_name, input=texts)
            except (RateLimitError, APIConnectionError) as exc:
                error = exc
            except APIStatusError as exc:
                if exc.status_code < 500:
                    raise  # auth, bad request, quota: do not retry or hide
                error = exc
            else:
                self.seconds += time.perf_counter() - started
                self.requests += 1
                self.total_tokens += response.usage.total_tokens
                data = sorted(response.data, key=lambda d: d.index)
                vectors = [d.embedding for d in data]
                if len(vectors) != len(texts) or any(len(v) != self.dimensions for v in vectors):
                    raise RuntimeError("embedding response has unexpected count or dimensions")
                return vectors
            if attempt == self.MAX_ATTEMPTS:
                raise RuntimeError(f"OpenAI embeddings failed after {attempt} attempts: {error}") from error
            time.sleep(2 ** attempt)
        raise AssertionError("unreachable")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.BATCH_SIZE):
            vectors.extend(self._embed(texts[start:start + self.BATCH_SIZE]))
        return vectors

    def embed_query(self, question: str) -> list[float]:
        return self._embed([question])[0]
