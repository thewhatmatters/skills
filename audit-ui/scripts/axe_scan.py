#!/usr/bin/env python3
"""Run axe-core against one or more URLs via Playwright (spec A4).

One concern: load each URL in headless Chromium, inject axe-core, run it, and
emit the violations as JSON. Interpretation/severity mapping is the model's job
(references/a11y-audit.md), not this script's.

axe-core source resolution is layered (spec A11):
    $AXE_JS (explicit path) -> <skill>/.cache/axe.min.js (cached copy)
    -> one-time CDN download into the cache (skipped with --no-network)
    -> error AXE_UNAVAILABLE (stderr marker; exit 2)

I/O:
    stdin  : —
    stdout : JSON [{url, ok, error?, violations:[{id, impact, help, helpUrl,
             tags, nodes:[{target, html}]}], counts:{critical,serious,
             moderate,minor}}]
    stderr : progress diagnostics + error markers (PLAYWRIGHT_MISSING,
             AXE_UNAVAILABLE, NAV_TIMEOUT <url>)
    exit   : 0 = ran (even with violations or some per-URL failures);
             2 = could not run at all (no playwright / no axe source)

Timeouts: 20s navigation, 30s axe.run — never hangs.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / ".cache"
AXE_CDN = "https://cdn.jsdelivr.net/npm/axe-core@4/axe.min.js"
NAV_TIMEOUT_MS = 20_000
AXE_TIMEOUT_MS = 30_000
SNIPPET_MAX = 200
NODES_MAX = 10


def resolve_axe_js(no_network):
    """Return axe-core source text via the layered ladder, or None."""
    import os
    explicit = os.environ.get("AXE_JS")
    if explicit and Path(explicit).is_file():
        print(f"axe source: $AXE_JS ({explicit})", file=sys.stderr)
        return Path(explicit).read_text("utf-8")
    cached = CACHE / "axe.min.js"
    if cached.is_file() and cached.stat().st_size > 100_000:
        print(f"axe source: cache ({cached})", file=sys.stderr)
        return cached.read_text("utf-8")
    if no_network:
        print("AXE_UNAVAILABLE: no cache and --no-network set", file=sys.stderr)
        return None
    print(f"axe source: fetching {AXE_CDN} (one-time, cached)", file=sys.stderr)
    text = _fetch(AXE_CDN)
    if text and len(text) > 100_000:
        CACHE.mkdir(exist_ok=True)
        cached.write_text(text, "utf-8")
        return text
    print("AXE_UNAVAILABLE: CDN fetch failed on every transport", file=sys.stderr)
    return None


def _fetch(url):
    """Fetch ladder: requests (bundles CA certs) -> urllib -> curl.

    macOS python.org installs often lack a CA bundle for stdlib SSL; requests
    ships certifi and curl uses the system store, so one of the three works
    on any normal machine.
    """
    try:
        import requests
        return requests.get(url, timeout=20).text
    except Exception as e:  # noqa: BLE001 — fall through the ladder
        print(f"  requests transport failed: {e}", file=sys.stderr)
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.read().decode("utf-8")
    except OSError as e:
        print(f"  urllib transport failed: {e}", file=sys.stderr)
    try:
        import subprocess
        proc = subprocess.run(["curl", "-sL", "--max-time", "20", url],
                              capture_output=True, text=True, timeout=25)
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout
        print(f"  curl transport failed (rc={proc.returncode})", file=sys.stderr)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"  curl transport failed: {e}", file=sys.stderr)
    return None


def scan(page, url, axe_js):
    try:
        page.goto(url, timeout=NAV_TIMEOUT_MS, wait_until="load")
        page.wait_for_timeout(500)  # let late client renders settle
    except Exception as e:  # noqa: BLE001 — per-URL failure must not kill the run
        print(f"NAV_TIMEOUT {url}: {e}", file=sys.stderr)
        return {"url": url, "ok": False, "error": f"navigation failed: {e}",
                "violations": [], "counts": {}}
    try:
        page.add_script_tag(content=axe_js)
        result = page.evaluate(
            """async () => await axe.run(document, {
                 runOnly: { type: 'tag',
                            values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa'] }
               })""",
        )
    except Exception as e:  # noqa: BLE001
        print(f"AXE_RUN_FAILED {url}: {e}", file=sys.stderr)
        return {"url": url, "ok": False, "error": f"axe.run failed: {e}",
                "violations": [], "counts": {}}

    violations = []
    counts = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    for v in result.get("violations", []):
        impact = v.get("impact") or "minor"
        counts[impact] = counts.get(impact, 0) + 1
        violations.append({
            "id": v.get("id"),
            "impact": impact,
            "help": v.get("help"),
            "helpUrl": v.get("helpUrl"),
            "tags": [t for t in v.get("tags", []) if t.startswith("wcag")],
            "nodes": [{"target": ", ".join(n.get("target", [])),
                       "html": (n.get("html") or "")[:SNIPPET_MAX]}
                      for n in v.get("nodes", [])[:NODES_MAX]],
        })
    print(f"scanned {url}: {sum(counts.values())} violations {counts}", file=sys.stderr)
    return {"url": url, "ok": True, "violations": violations, "counts": counts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", required=True,
                    help="URL to scan (repeatable; comma-separated also accepted)")
    ap.add_argument("--no-network", action="store_true",
                    help="forbid the one-time axe CDN fetch")
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    urls = [u for arg in args.url for u in arg.split(",") if u]

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("PLAYWRIGHT_MISSING: pip install playwright && "
              "python3 -m playwright install chromium", file=sys.stderr)
        print("[]")
        sys.exit(2)

    axe_js = resolve_axe_js(args.no_network)
    if axe_js is None:
        print("[]")
        sys.exit(2)

    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(AXE_TIMEOUT_MS)
            for url in urls:
                results.append(scan(page, url, axe_js))
            browser.close()
    except Exception as e:  # noqa: BLE001 — browser-level failure
        print(f"BROWSER_FAILED: {e}", file=sys.stderr)
        print(json.dumps(results or []))
        sys.exit(2)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
