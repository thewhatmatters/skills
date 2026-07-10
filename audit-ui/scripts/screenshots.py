#!/usr/bin/env python3
"""Capture full-page screenshots of URLs at responsive breakpoints (spec A4).

One concern: viewport-sized captures for the visual dimension. Reviewing the
images (overflow, wrapping, breakage) is the model's job
(references/visual-review.md), not this script's.

I/O:
    stdin  : —
    stdout : JSON [{url, width, path, ok, error?}]
    stderr : progress diagnostics + markers (PLAYWRIGHT_MISSING, NAV_TIMEOUT)
    exit   : 0 = ran (some captures may have failed individually);
             2 = could not run at all (no playwright / unwritable out dir)

Timeouts: 20s navigation per page — never hangs. Writes ONLY under --out.
"""
import argparse
import json
import re
import sys
from pathlib import Path

NAV_TIMEOUT_MS = 20_000
DEFAULT_BREAKPOINTS = "375,768,1280,1920"


def slugify(url):
    s = re.sub(r"^[a-z]+://", "", url).strip("/")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "page"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", required=True,
                    help="URL to capture (repeatable; comma-separated accepted)")
    ap.add_argument("--breakpoints", default=DEFAULT_BREAKPOINTS,
                    help=f"viewport widths (default {DEFAULT_BREAKPOINTS})")
    ap.add_argument("--out", required=True, help="directory for the PNGs")
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    urls = [u for arg in args.url for u in arg.split(",") if u]
    try:
        widths = [int(w) for w in args.breakpoints.split(",") if w.strip()]
    except ValueError:
        print(f"BAD_BREAKPOINTS: {args.breakpoints!r} — expected comma-separated ints",
              file=sys.stderr)
        print("[]")
        sys.exit(2)

    out_dir = Path(args.out).expanduser()
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"OUT_UNWRITABLE: {e}", file=sys.stderr)
        print("[]")
        sys.exit(2)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("PLAYWRIGHT_MISSING: pip install playwright && "
              "python3 -m playwright install chromium", file=sys.stderr)
        print("[]")
        sys.exit(2)

    shots = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for url in urls:
                slug = slugify(url)
                for width in widths:
                    page = browser.new_page(viewport={"width": width, "height": 900})
                    path = out_dir / f"{slug}-{width}.png"
                    try:
                        page.goto(url, timeout=NAV_TIMEOUT_MS, wait_until="load")
                        page.wait_for_timeout(500)
                        page.screenshot(path=str(path), full_page=True)
                        shots.append({"url": url, "width": width,
                                      "path": str(path), "ok": True})
                        print(f"captured {path}", file=sys.stderr)
                    except Exception as e:  # noqa: BLE001 — per-capture failure
                        print(f"NAV_TIMEOUT {url}@{width}: {e}", file=sys.stderr)
                        shots.append({"url": url, "width": width, "path": None,
                                      "ok": False, "error": str(e)})
                    finally:
                        page.close()
            browser.close()
    except Exception as e:  # noqa: BLE001
        print(f"BROWSER_FAILED: {e}", file=sys.stderr)
        print(json.dumps(shots or []))
        sys.exit(2)

    print(json.dumps(shots, indent=2))


if __name__ == "__main__":
    main()
