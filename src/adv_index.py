"""Advanced challenge, step 3: one index over ALL 280 pages = text chunks + one chunk per visual element.

    python -m src.adv_index            # build chunks, embed, save, print statistics

Text chunks: the Day 6/7 paragraph packing (<= 800 characters) over the PDF text layer of every page.
Visual chunks: one per element found by src.adv_extract (chart, table, diagram, infographic, map, photo); the chunk text is
built from the model's title, axes, legend, printed data values, table transcription and description, prefixed with the page
context (country or region name on profile pages). Each chunk keeps the page number and, for visual chunks, the page image path
so the figure can be re-checked against the original. Pages with no text layer and no element are listed as not processed.

Storage: data/advanced/index/chunks.json (committed) and embeddings.npy (ignored by git, rebuilt by this script).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

import numpy as np

from . import config
from .adv_render import ADV_DIR, page_image_path
from .chunking import by_paragraph
from .ingestion import load_pdf
from .retrieval import BM25Retriever, _result, rrf

logging.getLogger("pypdf").setLevel(logging.ERROR)
INDEX_DIR = ADV_DIR / "index"
CHUNKS_PATH = INDEX_DIR / "chunks.json"
EMB_PATH = INDEX_DIR / "embeddings.npy"
EXTRACT_DIR = ADV_DIR / "extraction"
MAX_VISUAL_CHARS = 6000

_TITLE = re.compile(r"([A-Z][A-Z ,’'.\-&()]{2,70}?)\s+(?:Latin America|Sub-Saharan|Europe &|Europe and|East Asia|South Asia|"
                    r"Middle East|\d+ countries|Population|Low-|Lower-|Upper-|High-)")


def page_context(text: str, page_type: str) -> str:
    """Country/region name on profile pages, taken from the text layer (e.g. 'AZERBAIJAN')."""
    if page_type not in ("profile", "chart", "mixed"):
        return ""
    head = re.sub(r"\s+", " ", text)[:400]
    m = _TITLE.search(head)
    name = m.group(1).strip() if m else ""
    return name if 2 < len(name) <= 70 and name.upper() == name else ""


def element_text(e: dict[str, Any], page: int, ctx: str) -> str:
    parts = [f"{e.get('kind', 'visual').upper()} on page {page}" + (f" ({ctx})" if ctx else "")]
    head = " - ".join(x for x in (e.get("label"), e.get("title")) if x)
    if head:
        parts.append(head)
    if e.get("chart_type"):
        parts.append(f"Type: {e['chart_type']}.")
    axes = e.get("axes") or {}
    if isinstance(axes, dict) and any(axes.values()):
        parts.append("Axes: " + "; ".join(f"{k}: {v}" for k, v in axes.items() if v) + ".")
    if e.get("legend"):
        parts.append("Legend: " + "; ".join(map(str, e["legend"])) + ".")
    data = e.get("data") or []
    if data:
        rows = []
        for d in data:
            if isinstance(d, dict):
                est = " (estimate)" if d.get("estimate") else ""
                rows.append(f"{d.get('series') or ''} {d.get('label') or ''} = {d.get('value')} {d.get('unit') or ''}{est}".strip())
        parts.append("Values: " + "; ".join(rows) + ".")
    if e.get("table"):
        parts.append("Table:\n" + e["table"])
    if e.get("description"):
        parts.append(e["description"])
    if e.get("notes"):
        parts.append("Note: " + e["notes"])
    return "\n".join(parts)[:MAX_VISUAL_CHARS]


def build_chunks() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source = str(config.PDF_PATH.relative_to(config.REPO_ROOT)).replace("\\", "/")
    pages = load_pdf(config.PDF_PATH, config.DOCUMENT_ID, source, header_banner=config.HEADER_BANNER)
    chunks, stats = [], {"text_chunks": 0, "visual_chunks": 0, "pages": len(pages), "pages_without_content": [],
                         "extraction_failed": [], "elements_by_kind": {}}
    for page in pages:
        # the Day 6 chunker reads report-structure metadata that only exists for chapters 1-3; the whole document has none
        for key in ("chapter", "chapter_title", "section"):
            page.metadata.setdefault(key, None)
        record_path = EXTRACT_DIR / f"p{page.page:03d}.json"
        record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else None
        if record is None or record["status"] != "ok":
            stats["extraction_failed"].append(page.page)
        page_type = (record or {}).get("page_type", "")
        ctx = page_context(page.text, page_type)
        for c in by_paragraph(page, config.CHUNK_MAX_CHARS) if page.text.strip() else []:
            chunks.append({"id": c.chunk_id, "text": (f"[{ctx}] " if ctx else "") + c.text, "source_id": c.document_id,
                           "source": c.source, "page": c.page,
                           "metadata": {"kind": "text", "page_type": page_type, "page_image": f"data/advanced/pages/p{c.page:03d}.png"}})
            stats["text_chunks"] += 1
        n_visual = 0
        for k, e in enumerate((record or {}).get("elements", []), 1):
            kind = str(e.get("kind", "visual"))
            if kind in ("photo", "decorative") and not e.get("description"):
                continue
            n_visual += 1
            stats["elements_by_kind"][kind] = stats["elements_by_kind"].get(kind, 0) + 1
            chunks.append({"id": f"vis:{config.DOCUMENT_ID}:p{page.page:04d}:e{k:02d}", "text": element_text(e, page.page, ctx),
                           "source_id": config.DOCUMENT_ID, "source": source, "page": page.page,
                           "metadata": {"kind": "visual", "element_kind": kind, "label": e.get("label", ""),
                                        "title": e.get("title", ""), "page_type": page_type,
                                        "page_image": f"data/advanced/pages/p{page.page:03d}.png"}})
            stats["visual_chunks"] += 1
        if not page.text.strip() and n_visual == 0:
            stats["pages_without_content"].append(page.page)
    ids = [c["id"] for c in chunks]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate chunk ids")
    return chunks, stats


class AdvIndex:
    """Dense (numpy cosine), BM25 and hybrid RRF over the advanced chunks; `kinds` restricts to text and/or visual chunks."""

    def __init__(self, embedder, chunks: list[dict[str, Any]] | None = None, embeddings: np.ndarray | None = None) -> None:
        self.embedder = embedder
        self.chunks = chunks if chunks is not None else json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
        self.emb = embeddings if embeddings is not None else np.load(EMB_PATH)
        if len(self.chunks) != len(self.emb):
            raise RuntimeError("chunks and embeddings out of sync; rebuild with python -m src.adv_index")
        self.emb = self.emb / np.maximum(np.linalg.norm(self.emb, axis=1, keepdims=True), 1e-9)
        self._bm25: dict[tuple[str, ...], tuple[BM25Retriever, list[int]]] = {}

    def _subset(self, kinds: tuple[str, ...]) -> list[int]:
        return [i for i, c in enumerate(self.chunks) if c["metadata"]["kind"] in kinds]

    def _bm(self, kinds: tuple[str, ...]):
        if kinds not in self._bm25:
            idx = self._subset(kinds)
            self._bm25[kinds] = (BM25Retriever([self.chunks[i] for i in idx]), idx)
        return self._bm25[kinds]

    def dense(self, vector: list[float], kinds: tuple[str, ...], top_k: int) -> list[dict[str, Any]]:
        idx = np.array(self._subset(kinds))
        v = np.asarray(vector, dtype=np.float32)
        v = v / max(float(np.linalg.norm(v)), 1e-9)
        scores = self.emb[idx] @ v
        order = np.argsort(-scores)[:top_k]
        return [_result(self.chunks[idx[j]], float(scores[j]), r, "dense") for r, j in enumerate(order, 1)]

    def search(self, query: str, *, kinds: tuple[str, ...] = ("text", "visual"), top_k: int = 6, depth: int = 30,
               rrf_k: int = 60) -> list[dict[str, Any]]:
        dense = self.dense(self.embedder.embed_query(query), kinds, depth)
        bm, _ = self._bm(kinds)
        lexical = bm.search(query, top_k=depth)
        return rrf([dense, lexical], k=rrf_k, top_k=top_k)


def main() -> None:
    from .embeddings import OpenAIEmbedder
    chunks, stats = build_chunks()
    embedder = OpenAIEmbedder()
    vectors = embedder.embed_documents([c["text"] for c in chunks])
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_PATH.write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    np.save(EMB_PATH, np.asarray(vectors, dtype=np.float32))
    stats |= {"embedding_model": embedder.model_name, "dimensions": embedder.dimensions,
              "embedding_tokens": embedder.total_tokens, "embedding_cost_usd_assumed": round(embedder.estimated_cost_usd, 6)}
    (INDEX_DIR / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
