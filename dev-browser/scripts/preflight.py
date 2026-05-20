#!/usr/bin/env python3
"""Readiness check for dev-browser (spec A6).

One concern: confirm the browser-automation path is ready. Three checks:
the `playwright` Python package is importable, its Chromium browser is
installed, and the workspace (persistent profile + screenshot out dir) is
writable. Per the skill's dual-mode design (spec A3), a missing package or
browser does NOT hard-block — it gates with a one-line install fix, and the
skill can still do read-only work via Claude's built-in WebFetch (NATIVE).

USAGE
    python3 scripts/preflight.py [--out=PATH] [--agent]

    --out=PATH  directory screenshots/artifacts get written to (default: cwd)
    --agent     non-interactive; report only, never prompt

I/O CONTRACT
    stdout : a single JSON object — {overall, checks{...}, summary}
    stderr : a human readiness board
    exit   : 0 if overall ∈ {ready, degraded, gated};
             1 if overall == down (a hard blocker)

PER-CHECK STATUS  ∈ {ready, degraded, gated, down}  (+ a gate id when not ready)
    playwright  `import playwright` works        gated → PLAYWRIGHT_MISSING
                                                 (fix: pip install playwright;
                                                 NATIVE read-only still works)
    browsers    Chromium present in the          gated → BROWSERS_MISSING
                ms-playwright cache              (fix: python3 -m playwright
                                                 install chromium)
    workspace   profile dir + --out writable      down  → WORKSPACE_UNWRITABLE
"""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
PROFILE_DIR = SKILL_ROOT / ".cache" / "profile"

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def log(msg):
    print(msg, file=sys.stderr)


def _browser_cache_dir():
    """Resolve the ms-playwright browser cache, layered (spec A11):
    explicit env override → per-OS default."""
    env = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if env and env not in ("0",):
        return Path(env).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "ms-playwright"
    if sys.platform.startswith("win"):
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ms-playwright"
    return Path.home() / ".cache" / "ms-playwright"


def check_playwright():
    try:
        import playwright  # noqa: F401, PLC0415
    except ImportError:
        return ("gated", "PLAYWRIGHT_MISSING",
                "pip install playwright — until then, NATIVE read-only "
                "(WebFetch) is the fallback")
    try:
        import importlib.metadata as _md  # noqa: PLC0415
        ver = _md.version("playwright")
    except Exception:  # noqa: BLE001
        ver = getattr(playwright, "__version__", "?")
    return ("ready", None, f"playwright {ver} importable")


def check_browsers():
    cache = _browser_cache_dir()
    if not cache.is_dir():
        return ("gated", "BROWSERS_MISSING",
                f"no browser cache at {cache} — run: "
                "python3 -m playwright install chromium")
    chromium = sorted(cache.glob("chromium-*")) + \
        sorted(cache.glob("chromium_headless_shell-*"))
    if chromium:
        names = ", ".join(p.name for p in chromium[:3])
        return ("ready", None,
                f"chromium present in cache ({names}); the first launch is "
                "the real check (a version-mismatched cache fails there, "
                "fixed by: python3 -m playwright install chromium)")
    return ("gated", "BROWSERS_MISSING",
            f"cache {cache} has no chromium — run: "
            "python3 -m playwright install chromium")


def check_workspace(out):
    """Both the persistent-profile parent and the --out dir must be writable."""
    for label, target in (("profile", PROFILE_DIR), ("out", Path(out).expanduser())):
        probe = target
        while not probe.exists() and probe != probe.parent:
            probe = probe.parent
        if not (probe.is_dir() and os.access(probe, os.W_OK)):
            return ("down", "WORKSPACE_UNWRITABLE",
                    f"cannot write {label} under {probe}")
    return ("ready", None, f"profile + {out} writable")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--out", default=str(Path.cwd()))
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    checks = {
        "playwright": check_playwright(),
        "browsers": check_browsers(),
        "workspace": check_workspace(args.out),
    }

    overall = "ready"
    for status, _gate, _detail in checks.values():
        if RANK[status] > RANK[overall]:
            overall = status

    log("dev-browser readiness")
    for name, (status, gate, detail) in checks.items():
        g = f"  [{gate}]" if gate else ""
        log(f"  {MARK[status]} {name:<10} {detail}{g}")
    log(f"  → overall: {overall}")
    if overall == "down":
        log("  (hard blocker — resolve the ⛔ item above)")
    elif overall in ("gated", "degraded"):
        log("  (can proceed; SCRIPTS gates have a one-line install fix, "
            "or fall back to NATIVE read-only — SKILL.md Step 1)")

    payload = {
        "overall": overall,
        "checks": {
            n: {"status": s, "gate": g, "detail": d}
            for n, (s, g, d) in checks.items()
        },
        "summary": f"{overall}: " + ", ".join(
            f"{n}={s}" for n, (s, _g, _d) in checks.items()
        ),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
