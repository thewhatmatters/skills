#!/usr/bin/env python3
"""Readiness check for audit-ui (spec A6) — one check per audit dimension dependency.

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down (with a gate id).

Checks → dimensions:
    playwright — a11y + visual. gated PLAYWRIGHT_MISSING / BROWSERS_MISSING
                 (fix: pip install playwright && python3 -m playwright install chromium)
    axe        — a11y. ready if cached; degraded AXE_FETCH_PENDING if a one-time
                 CDN fetch will be needed (axe_scan.py does it); gated
                 AXE_UNAVAILABLE only matters under --no-network
    server     — all live dimensions. Probes --url (default http://localhost:3000);
                 gated SERVER_UNREACHABLE — the FIX IS THE USER'S (start the dev
                 server); never started here
    lighthouse — vitals. degraded LIGHTHOUSE_UNAVAILABLE when no lighthouse/npx
    design_md  — tokens. degraded NO_DESIGN_MD → no-spec mode (internal
                 consistency only; the design-md skill can produce a spec)

`overall` is the worst state, BUT a gated/degraded check only disables its own
dimension — SKILL.md treats anything except `down` as runnable-in-part.
"""
import argparse
import json
import shutil
import sys
import urllib.request
from pathlib import Path

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}
SKILL_DIR = Path(__file__).resolve().parent.parent


def check_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        return ("gated", "PLAYWRIGHT_MISSING",
                "pip install playwright && python3 -m playwright install chromium")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            if not Path(p.chromium.executable_path).exists():
                return ("gated", "BROWSERS_MISSING",
                        "python3 -m playwright install chromium")
    except Exception as e:  # noqa: BLE001 — any probe failure = browsers unknown
        return ("gated", "BROWSERS_MISSING", f"chromium probe failed: {e}")
    return ("ready", None, "playwright + chromium present")


def check_axe(no_network):
    cached = SKILL_DIR / ".cache" / "axe.min.js"
    if cached.is_file() and cached.stat().st_size > 100_000:
        return ("ready", None, f"axe-core cached ({cached.name})")
    if no_network:
        return ("gated", "AXE_UNAVAILABLE", "no cached axe.min.js and --no-network set")
    return ("degraded", "AXE_FETCH_PENDING",
            "axe-core will be fetched once from CDN and cached")


def check_server(url):
    try:
        req = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "audit-ui-preflight"})
        with urllib.request.urlopen(req, timeout=5) as r:
            return ("ready", None, f"{url} reachable (http {r.status})")
    except OSError as e:
        return ("gated", "SERVER_UNREACHABLE",
                f"{url} not reachable ({e}) — start the dev server or pass --url")


def check_lighthouse():
    import os
    if os.environ.get("LIGHTHOUSE_BIN") or shutil.which("lighthouse"):
        return ("ready", None, "lighthouse binary available")
    if shutil.which("npx"):
        return ("ready", None, "lighthouse via npx (on-demand)")
    return ("degraded", "LIGHTHOUSE_UNAVAILABLE",
            "no lighthouse/npx — vitals dimension unavailable")


def check_design_md(project):
    root = Path(project).expanduser()
    for cand in ("DESIGN.md", "design.md"):
        if (root / cand).is_file():
            return ("ready", None, f"{cand} found — tokens audits against it")
    return ("degraded", "NO_DESIGN_MD",
            "no DESIGN.md — tokens runs in no-spec (consistency) mode")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:3000",
                    help="dev-server URL to probe (default: http://localhost:3000)")
    ap.add_argument("--project", default=".", help="project root for the tokens check")
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    checks = {
        "playwright": check_playwright(),
        "axe":        check_axe(args.no_network),
        "server":     check_server(args.url),
        "lighthouse": check_lighthouse(),
        "design_md":  check_design_md(args.project),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("audit-ui readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<10} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall} (gated/degraded checks disable only their own dimension)",
          file=sys.stderr)

    payload = {
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": f"{overall}: " + ", ".join(
            f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
