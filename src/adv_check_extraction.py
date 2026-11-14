"""Check the vision extraction against values read directly from the original page images.

    python -m src.adv_check_extraction

For each listed page, EXPECTED holds values the author-assistant read from the page image (not from the extraction). The check
asks whether each value appears in the text of the visual chunks of that page (src.adv_index). It reports found / missing per page
and overall. It measures recall of printed values on pages we could verify; it is not a full audit of the 280 pages, and the pages
are the ones used by the benchmark plus a few outside it (marked 'outside benchmark').
"""
from __future__ import annotations

import json
import re

from . import config
from .adv_index import CHUNKS_PATH

# page: (note, [values read from the image])
EXPECTED: dict[int, tuple[str, list[str]]] = {
    28: ("Table 1.1 (benchmark dev)", ["5,915.7", "9,445.0", "7,020.9", "4,396.6", "1,236.5", "498.7", "278.0", "386.4", "214.6", "2,364.4", "1,993.3", "499.6", "366.6"]),
    63: ("Table 1.2 (benchmark test)", ["85.9", "14.8", "13.3", "44.4", "66.3", "15.2", "13.5", "66.9", "12.7", "9.8"]),
    37: ("Figure B1.3.1 (benchmark dev)", ["23", "30", "19", "47"]),
    88: ("Figure 2.10 (benchmark dev)", ["-22", "15", "-7", "6"]),
    110: ("Figure 3.1 (benchmark test)", ["Accessibility", "Coverage", "Sub-Saharan Africa", "Other regions"]),
    111: ("Figure 3.2 (benchmark test)", ["March", "April", "June", "Late reporters"]),
    113: ("Figure 3.3 (benchmark test)", ["3,762", "3,655", "4,692", "4,875", "2,904", "3,437", "62.9", "61.8", "63.4"]),
    132: ("Figure 3B.1 (benchmark test)", ["Tier 1", "Tier 2", "Tier 3", "DRS", "IDS", "IDR", "Actionable knowledge", "Gaps and findings strengthen reporting"]),
    136: ("reading guide with Belize sample (benchmark test)", ["1,609", "1,283", "24 yrs", "3.6%", "17 yrs", "2.0%"]),
    150: ("Azerbaijan profile (benchmark dev)", ["12,327", "11,041", "1,064", "5,111", "797", "5,133", "1,925", "880", "2,306", "381", "282", "135", "13,179"]),
    202: ("Kenya profile (benchmark dev)", ["46,313", "43,845", "26,297", "7,834", "9,714", "13,054", "4,413", "8,829", "4,923", "1,164", "1,747", "19,788"]),
    200: ("Jordan profile (benchmark test)", ["50,519", "25,598"]),
    230: ("Peru profile (benchmark test)", ["94,270", "67,830"]),
    262: ("Zambia profile (benchmark test)", ["28,633", "12,311"]),
    175: ("Dominican Republic profile (benchmark test)", ["56,284", "26,727"]),
    137: ("all LMIC aggregate (benchmark test)", ["9,445", "5,916"]),
    138: ("East Asia and Pacific aggregate (benchmark test)", ["3,313", "2,004"]),
    142: ("South Asia aggregate (benchmark test)", ["955", "569"]),
    143: ("Sub-Saharan Africa aggregate (benchmark test)", ["1,020", "556"]),
}


def norm(s: str) -> str:
    """Whitespace-insensitive, including a space before '%' (the model writes '3.6 %' for the printed '3.6%')."""
    s = re.sub(r"\s+", " ", s.replace("−", "-").replace("–", "-"))
    return re.sub(r"\s+%", "%", s)


def main() -> None:
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    total = found = 0
    rows = []
    for page, (note, values) in sorted(EXPECTED.items()):
        text = norm(" ".join(c["text"] for c in chunks if c["page"] == page and c["metadata"]["kind"] == "visual"))
        has_visual = bool(text)
        miss = [v for v in values if norm(v) not in text]
        total += len(values)
        found += len(values) - len(miss)
        rows.append((page, note, has_visual, len(values) - len(miss), len(values), miss))
    print(f"{'page':>4s}  {'found':>7s}  note / missing")
    for page, note, has_visual, f, n, miss in rows:
        flag = "" if has_visual else "  [NO VISUAL CHUNK]"
        print(f"{page:>4d}  {f:>3d}/{n:<3d}  {note}{flag}" + (f"  MISSING: {miss}" if miss else ""))
    print(f"\nvalues read from the original found in the visual chunks: {found}/{total} ({100 * found / total:.1f}%)")


if __name__ == "__main__":
    main()
