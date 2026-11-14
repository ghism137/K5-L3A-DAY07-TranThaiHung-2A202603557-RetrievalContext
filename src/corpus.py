"""Shared helpers: load the content pages and build the chunk sets used by A, B and C."""
from __future__ import annotations

import logging

from . import config
from .chunking import by_paragraph, fixed_size
from .ingestion import apply_report_structure, content_pages, load_pdf, read_outline
from .models import Chunk, DocumentPage

logging.getLogger("pypdf").setLevel(logging.ERROR)  # fontTools warning verified harmless


def load_content_pages() -> list[DocumentPage]:
    pages = load_pdf(config.PDF_PATH, config.DOCUMENT_ID,
                     str(config.PDF_PATH.relative_to(config.REPO_ROOT)).replace("\\", "/"),
                     header_banner=config.HEADER_BANNER)
    apply_report_structure(pages, read_outline(config.PDF_PATH), config.MIN_CONTENT_CHARS)
    return content_pages(pages)


def build_chunks(strategy: str, pages: list[DocumentPage]) -> list[Chunk]:
    """Strategy A = fixed windows. B and C share the same paragraph chunks (C only adds a filter)."""
    if strategy == "A":
        chunks = [c for p in pages for c in fixed_size(p, config.CHUNK_MAX_CHARS, config.FIXED_OVERLAP)]
    elif strategy in ("B", "C"):
        chunks = [c for p in pages for c in by_paragraph(p, config.CHUNK_MAX_CHARS)]
    else:
        raise ValueError(f"unknown strategy {strategy!r}")
    ids = [c.chunk_id for c in chunks]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate chunk ids")
    return chunks
