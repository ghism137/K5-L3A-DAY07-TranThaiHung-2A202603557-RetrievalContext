"""Fixed-size and structure-aware chunking. Chunks never cross a page boundary,
so every chunk keeps an exact `page` (a paragraph that continues on the next page
is therefore split at the page break; this is a known limitation).
"""
from __future__ import annotations

import re

from .models import Chunk, DocumentPage

# The PDF hard-wraps lines at ~70-89 characters (62% of body lines, measured on the
# 103 content pages). A line shorter than this that ends a sentence closes a paragraph.
FULL_LINE = 68
_TERMINAL = (".", "?", "!", ":", ")", "”", "’", '"')
_SENTENCE_SPLIT = re.compile(r"(?<=[.?!])\s+(?=[A-Z“\"(•$0-9])")
_KEEP_SPACE_BEFORE = {"and", "or"}  # "low- and middle-income": keep the space


def flow(lines: list[str]) -> str:
    """Join hard-wrapped lines into running text.

    A line ending with a hyphen is joined without a space ("long-" + "term"), except
    before "and"/"or" (suspended hyphen: "low- and middle-income").
    """
    out = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if not out:
            out = line
        elif out.endswith("-") and line[:1].islower() and line.split()[0] not in _KEEP_SPACE_BEFORE:
            out += line
        else:
            out += " " + line
    return out


def _meta(page: DocumentPage, index: int, text: str) -> dict:
    md = page.metadata
    return {
        "chapter": md["chapter"],
        "chapter_title": md["chapter_title"],
        "section": md["section"],
        "printed_page": md["printed_page"],
        "chunk_index": index,
        "char_count": len(text),
    }


def _make(kind: str, page: DocumentPage, index: int, text: str) -> Chunk:
    return Chunk(
        chunk_id=f"{kind}:{page.document_id}:p{page.page:04d}:{index:03d}",
        document_id=page.document_id,
        source=page.source,
        page=page.page,
        text=text,
        metadata=_meta(page, index, text),
    )


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    """Overlapping character windows over the flowed page text (no structure used)."""
    if not 0 <= overlap < size:
        raise ValueError("overlap must satisfy 0 <= overlap < size")
    text = flow(page.text.split("\n"))
    chunks: list[Chunk] = []
    start = 0
    while start < len(text):
        piece = text[start:start + size].strip()
        if piece:
            chunks.append(_make("fixed", page, len(chunks), piece))
        if start + size >= len(text):
            break
        start += size - overlap
    return chunks


def _paragraph_blocks(lines: list[str]) -> list[str]:
    """Split page lines into paragraph-like blocks.

    A block closes after a short line that ends with sentence punctuation, or before a
    bullet. Headings and chart labels have no closing punctuation, so they stay attached
    to the text that follows them.
    """
    blocks: list[list[str]] = []
    current: list[str] = []
    for i, line in enumerate(lines):
        current.append(line)
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        closes = len(line) < FULL_LINE and line.endswith(_TERMINAL)
        if nxt is None or closes or nxt.startswith("•"):
            blocks.append(current)
            current = []
    return [t for t in (_block_text(b) for b in blocks) if t]


def _block_text(lines: list[str]) -> str:
    """Flow a block; leading short lines without closing punctuation are headings and
    stay on their own line instead of being glued to the first sentence."""
    heading = 0
    while heading < len(lines) - 1 and len(lines[heading]) < FULL_LINE \
            and not lines[heading].endswith(_TERMINAL):
        heading += 1
    if heading == 0:
        return flow(lines)
    return flow(lines[:heading]) + "\n" + flow(lines[heading:])


def _split_oversize(text: str, max_size: int) -> list[str]:
    """Split a block longer than max_size at sentence ends; hard-split at spaces last."""
    if len(text) <= max_size:
        return [text]
    parts: list[str] = []
    current = ""
    for sentence in _SENTENCE_SPLIT.split(text):
        while len(sentence) > max_size:  # one sentence longer than the limit
            cut = sentence.rfind(" ", 0, max_size)
            cut = cut if cut > 0 else max_size
            if current:
                parts.append(current)
                current = ""
            parts.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if current and len(current) + 1 + len(sentence) > max_size:
            parts.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        parts.append(current)
    return parts


def by_paragraph(page: DocumentPage, max_size: int) -> list[Chunk]:
    """Pack whole paragraphs (blank-line separated) into chunks of at most max_size."""
    chunks: list[Chunk] = []
    current = ""
    for block in _paragraph_blocks(page.text.split("\n")):
        for part in _split_oversize(block, max_size):
            if current and len(current) + 2 + len(part) > max_size:
                chunks.append(_make("para", page, len(chunks), current))
                current = ""
            current = f"{current}\n\n{part}" if current else part
    if current:
        chunks.append(_make("para", page, len(chunks), current))
    return chunks
