"""Read and normalize source data."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from .models import DocumentPage

# Soft hyphen and zero-width characters carry no meaning in extracted text.
_INVISIBLE = dict.fromkeys(map(ord, "­​‌‍﻿"))
_SPACES = re.compile(r"[ \t\f\v]+")
_BLANK_RUNS = re.compile(r"\n{3,}")
_PAGE_NUMBER = re.compile(r"\d{1,3}")
_CHAPTER_TITLE = re.compile(r"Chapter (\d+)\.\s*(.+)")
_BACK_MATTER_TITLES = {"Notes", "References"}


@dataclass
class OutlineEntry:
    depth: int
    title: str
    page: int | None  # physical page, 1-based


def normalize_text(text: str) -> str:
    """NFKC, drop invisible characters, collapse spaces; keep line breaks.

    Line breaks are kept on purpose: paragraph chunking needs the page structure.
    NFKC turns no-break spaces and ligatures into plain characters; en dashes stay.
    """
    text = unicodedata.normalize("NFKC", text).translate(_INVISIBLE)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_SPACES.sub(" ", line).strip() for line in text.split("\n")]
    return _BLANK_RUNS.sub("\n\n", "\n".join(lines)).strip()


def strip_running_header(
    text: str, banner: re.Pattern[str] | None
) -> tuple[str, int | None, bool]:
    """Remove the two-line running header; return (text, printed_page, stripped).

    Odd and even pages put the printed page number and the banner on either line,
    so both orders are accepted. If the pattern is not found the text is untouched.
    """
    if banner is None:
        return text, None, False
    lines = text.split("\n")
    if len(lines) < 2:
        return text, None, False
    first, second = lines[0].strip(), lines[1].strip()
    for number, label in ((first, second), (second, first)):
        if _PAGE_NUMBER.fullmatch(number) and banner.fullmatch(label):
            return "\n".join(lines[2:]).strip(), int(number), True
    return text, None, False


def load_pdf(
    path: Path,
    document_id: str,
    source: str,
    header_banner: re.Pattern[str] | None = None,
) -> list[DocumentPage]:
    """Extract every physical page; page numbers are 1-based PDF pages.

    Failures are recorded in metadata["extract_error"], never swallowed silently.
    Empty pages are flagged with metadata["is_empty"] (OCR would be a separate step).
    """
    reader = PdfReader(str(path))
    pages: list[DocumentPage] = []
    for number, pdf_page in enumerate(reader.pages, start=1):
        error = None
        try:
            raw = pdf_page.extract_text() or ""
        except Exception as exc:  # recorded and reported by the caller
            raw, error = "", f"{type(exc).__name__}: {exc}"
        text = normalize_text(raw)
        text, printed_page, stripped = strip_running_header(text, header_banner)
        pages.append(
            DocumentPage(
                document_id=document_id,
                source=source,
                page=number,
                text=text,
                metadata={
                    "printed_page": printed_page,
                    "header_stripped": stripped,
                    "is_empty": not text.strip(),
                    "extract_error": error,
                },
            )
        )
    return pages


def read_outline(path: Path) -> list[OutlineEntry]:
    """Flatten the PDF bookmarks; depth 0 = chapters/parts, 1 = sections."""
    reader = PdfReader(str(path))
    entries: list[OutlineEntry] = []

    def walk(items: list, depth: int) -> None:
        for item in items:
            if isinstance(item, list):
                walk(item, depth + 1)
                continue
            try:
                page = reader.get_destination_page_number(item) + 1
            except Exception:
                page = None
            entries.append(OutlineEntry(depth, normalize_text(item.title or ""), page))

    walk(reader.outline, 0)
    return entries


def apply_report_structure(
    pages: list[DocumentPage], outline: list[OutlineEntry], min_content_chars: int
) -> tuple[int, int]:
    """Attach chapter/section and mark each page's status (specific to this report).

    Status values: content, excluded_blank, excluded_back_matter, excluded_short,
    out_of_scope. Returns the (first, last) physical page of the scope.
    Section is the latest outline section that starts on or before the page, so a
    page where a section starts mid-page carries the new section label.
    """
    top = [e for e in outline if e.depth == 0 and e.page]
    chapters = [(e.page, int(m.group(1)), m.group(2).strip())
                for e in top if (m := _CHAPTER_TITLE.fullmatch(e.title))]
    chapters.sort()
    first = chapters[0][0]
    last = min(e.page for e in top if e.page > chapters[-1][0]) - 1  # next Part starts
    # Only children of a chapter entry: other top-level entries (e.g. lists of figures
    # and tables) also have depth-1 children, which are not document sections.
    sections, in_chapter = [], False
    for entry in outline:
        if entry.depth == 0:
            in_chapter = bool(_CHAPTER_TITLE.fullmatch(entry.title))
        elif entry.depth == 1 and in_chapter and entry.page and entry.title not in _BACK_MATTER_TITLES:
            sections.append((entry.page, entry.title))
    sections.sort(key=lambda s: s[0])  # stable: same-page sections keep outline order

    in_back_matter, current = False, None
    for page in pages:
        md = page.metadata
        if not first <= page.page <= last:
            md["status"] = "out_of_scope"
            continue
        start, number, title = max(c for c in chapters if c[0] <= page.page)
        if current != number:
            current, in_back_matter = number, False
        md.update(
            chapter=number,
            chapter_title=title,
            section=[s for s in sections if start <= s[0] <= page.page][-1][1],
        )
        if md["is_empty"]:
            md["status"] = "excluded_blank"
            continue
        if in_back_matter:
            md["status"] = "excluded_back_matter"
            continue
        lines = page.text.split("\n")
        cut = next((i for i, line in enumerate(lines) if line == "Notes"), None)
        if cut is not None:  # "Notes" heading starts the back matter of this chapter
            in_back_matter = True
            body = "\n".join(lines[:cut]).strip()
            md["trimmed_back_matter_chars"] = len(page.text) - len(body)
            page.text = body
        if len(page.text) >= min_content_chars:
            md["status"] = "content"
        else:
            md["status"] = "excluded_back_matter" if cut is not None else "excluded_short"
    return first, last


def content_pages(pages: list[DocumentPage]) -> list[DocumentPage]:
    return [p for p in pages if p.metadata.get("status") == "content"]
