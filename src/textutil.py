"""Small text helpers shared by benchmark verification and evaluation."""
import hashlib
import re
from pathlib import Path


def canon(text: str) -> str:
    """Whitespace-insensitive form: PDF line breaks must not decide a match."""
    return re.sub(r"-\s+", "-", re.sub(r"\s+", " ", text)).strip()


def sha256_lf(path: Path) -> str:
    """SHA-256 of a text file with CRLF read as LF, so git's line-ending conversion on
    Windows cannot change the hash of an otherwise identical file."""
    crlf, lf = b"\r\n", b"\n"
    return hashlib.sha256(Path(path).read_bytes().replace(crlf, lf)).hexdigest()
