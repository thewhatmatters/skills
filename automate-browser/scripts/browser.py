#!/usr/bin/env python3
"""Persistent-profile Chromium automation via Playwright (sync API).

Both a **library** (import the helpers in an inline Python script for a
multi-step flow) and a **thin CLI** (one-shot navigate + extract + optional
screenshot). See references/browser-api.md for the full API.

PERSISTENCE MODEL (read this — it differs from the original Amp skill)
    Sessions/cookies/localStorage persist across runs via a persistent
    Chromium user-data-dir at  <skill>/.cache/profile  (gitignored).
    A *live page* does NOT persist between separate processes — there is no
    long-running server here (deliberate: simpler + robust). So each inline
    script opens the context, does its work, closes. Once you've logged in,
    later runs are already authenticated, so re-`goto` is cheap. For a
    multi-step interaction on one live page, do it all inside ONE script.

LIBRARY
    from scripts.browser import launch, wait_for_load, interactive_outline, \\
        outline, visible_text, aria_snapshot

    with launch(headless=False) as (ctx, page):   # ctx = BrowserContext
        page.goto("https://example.com")
        wait_for_load(page)
        print(interactive_outline(page))
        # standard Playwright locators for interaction:
        page.get_by_role("link", name="Sign in").click()

THIN CLI (one self-contained process)
    python3 scripts/browser.py goto <url> \\
        [--mode interactive|text|outline|aria|none] [--selector CSS] \\
        [--limit N] [--screenshot PATH] [--headless] [--timeout MS]

I/O CONTRACT (CLI)
    stdout : a single JSON object — {url, title, mode, extract?, screenshot?}
    stderr : human diagnostics (mode, timing, any wait fallback)
    exit   : 0 on success; 1 on a missing dependency, navigation failure, or
             a write failure. Never hangs (every wait is bounded by timeout).

NATIVE FALLBACK
    If `playwright` is not installed, the CLI exits 1 with the install hint;
    the skill's SKILL.md Step 1 routes to NATIVE read-only (WebFetch) in that
    case. This script is the SCRIPTS-mode worker only.
"""

import argparse
import contextlib
import json
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
PROFILE_DIR = SKILL_ROOT / ".cache" / "profile"
DEFAULT_TIMEOUT = 20000  # ms; bounds every wait so the script never hangs


def log(msg):
    print(msg, file=sys.stderr)


# --- JS extractors (run in the page via page.evaluate) ----------------------

_JS_INTERACTIVE = r"""
(arg) => {
  const root = (arg && arg.root) || document.body;
  const LAND = new Set(['HEADER','NAV','MAIN','FOOTER','FORM','ASIDE','SECTION']);
  const IROLES = new Set(['button','link','checkbox','radio','tab','menuitem',
                          'textbox','combobox','switch','option']);
  const interactive = (el) => {
    if (['A','BUTTON','INPUT','SELECT','TEXTAREA'].includes(el.tagName)) return true;
    const r = el.getAttribute('role');
    if (r && IROLES.has(r)) return true;
    if (el.isContentEditable) return true;
    const ti = el.getAttribute('tabindex');
    return ti !== null && parseInt(ti, 10) >= 0;
  };
  const visible = (el) => {
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden' ||
        parseFloat(s.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const label = (el) => {
    const t = el.tagName.toLowerCase();
    if (LAND.has(el.tagName)) {
      const role = el.getAttribute('role');
      return t + (role ? ` [role=${role}]` : '');
    }
    const txt = (el.innerText || el.value || el.getAttribute('aria-label') ||
                 el.getAttribute('placeholder') || '')
      .trim().replace(/\s+/g, ' ').slice(0, 80);
    let s = t;
    if (el.tagName === 'INPUT') s += ` [type=${el.type || 'text'}]`;
    if (txt) s += ` "${txt}"`;
    const href = el.getAttribute && el.getAttribute('href');
    if (href) s += ` [href=${href}]`;
    return s;
  };
  const lines = [];
  const walk = (el, depth) => {
    let nd = depth;
    if ((LAND.has(el.tagName) || interactive(el)) && visible(el)) {
      lines.push('  '.repeat(depth) + label(el));
      nd = depth + 1;
    }
    for (const c of el.children) walk(c, nd);
  };
  walk(root, 0);
  return lines.join('\n');
}
"""

_JS_OUTLINE = r"""
(arg) => {
  const root = (arg && arg.root) || document.body;
  const maxDepth = (arg && arg.maxDepth != null) ? arg.maxDepth : 6;
  const sig = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (el.className && typeof el.className === 'string') {
      const cls = el.className.trim().split(/\s+/).slice(0, 2).filter(Boolean);
      if (cls.length) s += '.' + cls.join('.');
    }
    return s;
  };
  const lines = [sig(root)];
  const walk = (el, depth) => {
    if (depth > maxDepth) return;
    const kids = Array.from(el.children);
    let i = 0;
    while (i < kids.length) {
      let j = i;
      const s = sig(kids[i]);
      while (j + 1 < kids.length && sig(kids[j + 1]) === s) j++;
      const n = j - i + 1;
      lines.push('  '.repeat(depth) + s + (n > 1 ? ` (×${n})` : ''));
      if (n === 1) walk(kids[i], depth + 1);
      i = j + 1;
    }
  };
  walk(root, 1);
  return lines.join('\n');
}
"""


def _require_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415
        return sync_playwright
    except ImportError as e:
        raise SystemExit(
            "FATAL: `playwright` not installed. Fix: pip install playwright "
            "&& python3 -m playwright install chromium. (Until then, use "
            "NATIVE read-only via Claude's built-in WebFetch.)"
        ) from e


@contextlib.contextmanager
def launch(headless=False, viewport=(1280, 800)):
    """Yield (BrowserContext, Page) on a persistent profile. Closes on exit.

    Cookies/sessions persist via PROFILE_DIR across runs; the live page does
    not persist between processes (no server). Headed by default so you can
    watch; pass headless=True on a no-display server.
    """
    sync_playwright = _require_playwright()
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": viewport[0], "height": viewport[1]},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            yield ctx, page
        finally:
            with contextlib.suppress(Exception):
                ctx.close()


def wait_for_load(page, timeout=DEFAULT_TIMEOUT):
    """Best-effort settle: try networkidle, fall back to load. Never raises
    past the timeout — a slow page should not hang the run (spec A4)."""
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:  # noqa: BLE001
        with contextlib.suppress(Exception):
            page.wait_for_load_state("load", timeout=timeout)


def visible_text(page, selector=None, limit=None):
    """Rendered visible text (Playwright inner_text already excludes hidden)."""
    try:
        txt = page.inner_text(selector) if selector else page.inner_text("body")
    except Exception:  # noqa: BLE001
        txt = ""
    return txt[:limit] if limit else txt


def _scoped_eval(page, js, selector, **opts):
    """Run an extractor JS over an optional CSS-scoped root.

    The resolved root element (or None → the JS defaults to document.body) is
    passed inside the arg object, so one JS function works both scoped and
    unscoped. If a selector is given but matches nothing, return an honest
    marker rather than silently falling back to the whole page (spec A12).
    """
    root = None
    if selector:
        root = page.query_selector(selector)
        if root is None:
            return f"(selector not found: {selector})"
    return page.evaluate(js, {"root": root, **opts})


def interactive_outline(page, selector=None):
    """Token-efficient tree of interactive elements + landmarks. Scoped to
    `selector` when given, else the whole document."""
    return _scoped_eval(page, _JS_INTERACTIVE, selector)


def outline(page, max_depth=6, selector=None):
    """DOM structure outline with repeated-sibling collapse (×N). Scoped to
    `selector` when given, else the whole document."""
    return _scoped_eval(page, _JS_OUTLINE, selector, maxDepth=max_depth)


def aria_snapshot(page, selector="body"):
    """Playwright's accessibility-tree YAML for the subtree. Read-only — for
    interaction use standard locators (get_by_role / get_by_text / CSS)."""
    try:
        return page.locator(selector).aria_snapshot()
    except Exception as e:  # noqa: BLE001
        return f"(aria_snapshot unavailable: {e.__class__.__name__})"


def _extract(page, mode, selector, limit):
    if mode == "interactive":
        return interactive_outline(page, selector)
    if mode == "text":
        return visible_text(page, selector, limit)
    if mode == "outline":
        return outline(page, selector=selector)
    if mode == "aria":
        return aria_snapshot(page, selector or "body")
    return None


def main():
    ap = argparse.ArgumentParser(add_help=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("goto", help="navigate + optionally extract/screenshot")
    g.add_argument("url")
    g.add_argument("--mode", choices=("interactive", "text", "outline", "aria", "none"),
                   default="interactive")
    g.add_argument("--selector", default=None)
    g.add_argument("--limit", type=int, default=None)
    g.add_argument("--screenshot", default=None, help="path to write a PNG")
    g.add_argument("--headless", action="store_true")
    g.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = ap.parse_args()

    start = time.monotonic()
    out = {"url": args.url, "title": None, "mode": args.mode}
    try:
        with launch(headless=args.headless) as (_ctx, page):
            resp = page.goto(args.url, timeout=args.timeout)
            wait_for_load(page, timeout=args.timeout)
            out["title"] = page.title()
            out["url"] = page.url
            out["http_status"] = resp.status if resp else None
            if args.mode != "none":
                out["extract"] = _extract(page, args.mode, args.selector, args.limit)
            if args.screenshot:
                target = Path(args.screenshot).expanduser()
                target.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(target), full_page=True)
                out["screenshot"] = str(target)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 - any nav/render failure → exit 1
        log(f"FATAL: {e.__class__.__name__}: {e}")
        sys.exit(1)

    log(f"goto ok mode={args.mode} elapsed={time.monotonic() - start:.1f}s")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
