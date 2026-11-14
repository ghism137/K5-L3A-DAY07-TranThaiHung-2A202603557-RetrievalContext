"""Day 7 paths and settings. Corpus scope and chunking limits are carried over unchanged
from Day 6 so the Day 6 vector store can be reused as-is."""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
BENCHMARK_DIR = REPO_ROOT / "benchmark"
RESULTS_DIR = REPO_ROOT / "results"
ENV_PATH = REPO_ROOT / ".env"

# --- the one source document (same as Day 6) ----------------------------------
DOCUMENT_ID = "idr-2026"
TITLE = "International Debt Report 2026"
PDF_PATH = DATA_DIR / "international-debt-report-2026.pdf"
ORIGIN_URL = "https://hdl.handle.net/10986/45762"
DOI = "https://doi.org/10.1596/978-1-4648-2355-8"
LICENSE = "CC BY 3.0 IGO (printed on the PDF, physical p6); attribution required"
PDF_SHA256 = "c25b3b8918788b89a148f7b8874b232b8a4d0dc64e8d7220699fc8a47c89e36e"

# --- scope: chapters 1-3 (physical pages 27-134), 103 content pages -------------
MIN_CONTENT_CHARS = 200

# --- Day 6 chunking, unchanged (index "A" = fixed 800/100, "B" = paragraph packing 800)
CHUNK_MAX_CHARS = 800
FIXED_OVERLAP = 100
TOP_K = 3

# Running header = bare page number + (report banner | chapter title), in either order.
HEADER_BANNER = re.compile(r"(?i)INTERNATIONAL DEBT REPORT 2026|\d\.\s+\S.{2,100}")
