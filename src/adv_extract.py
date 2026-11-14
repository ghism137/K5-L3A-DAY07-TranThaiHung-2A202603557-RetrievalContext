"""Advanced challenge, step 2: a vision model reads every page and lists its non-decorative visual elements.

    python -m src.adv_extract [--pages 1-280] [--workers 6]

For each page the model gets the page image and the PDF text layer (which may be incomplete or misordered) and returns
JSON: page_type and a list of elements (chart / table / diagram / infographic / map / photo) with title, axes, legend,
printed data values, a table transcription and a short factual description. The model is told never to invent values;
values read off an axis must be flagged as estimates. Output is NOT trusted by itself: the report states the
verification against the original page images.

Resumable: pages with a valid data/advanced/extraction/pNNN.json are skipped. Failures are recorded, never hidden.
"""
from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError
from pypdf import PdfReader

from . import config
from .adv_render import ADV_DIR, page_image_path

logging.getLogger("pypdf").setLevel(logging.ERROR)
OUT_DIR = ADV_DIR / "extraction"
PROMPT_VERSION = "v1"
MAX_TEXT_CHARS = 6000

SYSTEM = """You digitize one page of the World Bank report "International Debt Report 2026" for a search index.
You get the page image and the text layer extracted from the PDF (it can be incomplete or in the wrong order).
List every NON-DECORATIVE visual element on the page: charts, tables, diagrams or schematics, infographics, maps, photos.
Ignore running headers and footers, page numbers, decorative backgrounds and plain body text.
Return ONLY a JSON object:
{
 "page_type": "text|chart|table|diagram|mixed|profile|divider|cover|blank",
 "elements": [
  {
   "kind": "chart|table|diagram|infographic|map|photo",
   "label": "printed label such as 'Figure 1.6', 'Table 1.1', 'Figure B1.4.1', or '' if none",
   "title": "title exactly as printed",
   "chart_type": "line|bar|stacked bar|box plot|scatter|area|treemap|other|'' (charts and infographics only)",
   "axes": {"x": "name and unit", "y": "name and unit"},
   "legend": ["series name (colour)"],
   "data": [{"label": "...", "series": "...", "value": "number or text as printed", "unit": "...", "estimate": false}],
   "table": "full markdown transcription with header row and units (tables only, else '')",
   "description": "2-4 factual sentences: what it shows, time span, main pattern, highest and lowest items",
   "notes": "source or note line as printed, else ''"
  }
 ]
}
Rules: (1) Use only what is visible on the page or in its text layer; never invent or recall outside values.
(2) Put in "data" every value that is PRINTED on the graphic or present in the text layer for it. A value you can only read
off an axis must have "estimate": true and be rounded honestly; if you cannot read it, omit it.
(3) For a diagram or infographic, describe every box, node, label and arrow in "description" in reading order.
(4) For a table, transcribe all rows and columns you can read; mark unreadable cells with '?'.
(5) If the page has no non-decorative visual element, return "elements": [].
(6) Output JSON only, no commentary."""


def parse_range(spec: str, last: int) -> list[int]:
    pages: list[int] = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        pages += list(range(int(a), int(b or a) + 1))
    return [p for p in pages if 1 <= p <= last]


def _call(client: OpenAI, model: str, page: int, text: str) -> tuple[dict, dict]:
    image = base64.b64encode(page_image_path(page).read_bytes()).decode()
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": [
                    {"type": "text", "text": f"Page {page} of the PDF.\n\nText layer (may be wrong):\n{text[:MAX_TEXT_CHARS] or '(empty)'}"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image}}]}]
    last_error = None
    for attempt in range(1, 6):
        try:
            response = client.chat.completions.create(model=model, messages=messages, max_completion_tokens=12000,
                                                      response_format={"type": "json_object"})
        except (RateLimitError, APIConnectionError) as exc:
            last_error = exc
        except APIStatusError as exc:
            if exc.status_code < 500:
                raise
            last_error = exc
        else:
            usage = response.usage
            details = getattr(usage, "completion_tokens_details", None)
            return json.loads(response.choices[0].message.content), {
                "prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens,
                "reasoning_tokens": getattr(details, "reasoning_tokens", None)}
        time.sleep(2 ** attempt)
    raise RuntimeError(f"gave up after retries: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", default="1-280")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--model", default=None, help="default: VISION_MODEL or AGENT_MODEL from .env")
    args = parser.parse_args()
    load_dotenv(config.ENV_PATH)
    model = args.model or os.environ.get("VISION_MODEL") or os.environ["AGENT_MODEL"]
    reader = PdfReader(str(config.PDF_PATH))
    pages = parse_range(args.pages, len(reader.pages))
    texts = {p: (reader.pages[p - 1].extract_text() or "") for p in pages}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    client = OpenAI(max_retries=0)
    todo = [p for p in pages if not (OUT_DIR / f"p{p:03d}.json").exists()]
    print(f"model {model}: {len(pages)} page(s) requested, {len(todo)} to do, {args.workers} workers")
    lock, tally = threading.Lock(), {"prompt": 0, "completion": 0, "ok": 0, "failed": []}

    def work(page: int) -> None:
        started = time.perf_counter()
        try:
            data, usage = _call(client, model, page, texts[page])
            if not isinstance(data.get("elements"), list):
                raise ValueError("response has no 'elements' list")
            record = {"page": page, "model": model, "prompt_version": PROMPT_VERSION, "status": "ok",
                      "seconds": round(time.perf_counter() - started, 1), "usage": usage, **data}
        except Exception as exc:  # recorded as a failed page, reported at the end
            record = {"page": page, "model": model, "prompt_version": PROMPT_VERSION, "status": "failed",
                      "error": f"{type(exc).__name__}: {str(exc)[:300]}"}
        (OUT_DIR / f"p{page:03d}.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
        with lock:
            if record["status"] == "ok":
                tally["ok"] += 1
                tally["prompt"] += record["usage"]["prompt_tokens"]
                tally["completion"] += record["usage"]["completion_tokens"]
            else:
                tally["failed"].append(page)
            done = tally["ok"] + len(tally["failed"])
            if done % 20 == 0:
                print(f"  {done}/{len(todo)} done (failed so far: {len(tally['failed'])})", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(work, p) for p in todo]):
            future.result()
    print(json.dumps({"ok": tally["ok"], "failed_pages": sorted(tally["failed"]), "prompt_tokens": tally["prompt"],
                      "completion_tokens": tally["completion"]}))


if __name__ == "__main__":
    main()
