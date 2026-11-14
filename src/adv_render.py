"""Advanced challenge, step 1: render every PDF page to a PNG (kept locally, not committed).

    python -m src.adv_render [--scale 2.0]

Output: data/advanced/pages/pNNN.png (NNN = physical PDF page, 1-based). These images are the "original" that
extraction output and answers are checked against, and what the multimodal agent looks at.
"""
from __future__ import annotations

import argparse

import pypdfium2 as pdfium

from . import config

ADV_DIR = config.DATA_DIR / "advanced"
PAGES_DIR = ADV_DIR / "pages"


def page_image_path(page: int):
    return PAGES_DIR / f"p{page:03d}.png"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=float, default=2.0, help="1.0 = 72 dpi")
    args = parser.parse_args()
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(config.PDF_PATH))
    done = 0
    for number in range(1, len(pdf) + 1):
        target = page_image_path(number)
        if target.exists():
            continue
        pdf[number - 1].render(scale=args.scale).to_pil().convert("RGB").save(target, optimize=True)
        done += 1
    print(f"{len(pdf)} pages; rendered {done} new image(s) at scale {args.scale} -> {PAGES_DIR}")


if __name__ == "__main__":
    main()
