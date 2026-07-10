#!/usr/bin/env python3
"""Readiness check for draw-diagram (spec A6).

This skill's core (a fenced ```mermaid block) has NO dependencies, so it can
never be fully "down" as long as the output target is writable. The optional
capabilities — mmdc/Node for local SVG/PNG, and Kroki for network rendering —
are probed for real and reported as `degraded` when absent (not `down`),
because the renderer falls back to the fenced block (spec A3/A7d).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse
import json
import os
import shutil
import sys
import urllib.request

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_output(path):
    if not path:
        return ("ready", None, "writing to stdout (no --out)")
    parent = os.path.dirname(os.path.abspath(os.path.expanduser(path))) or "."
    if not os.path.isdir(parent):
        return ("down", "OUT_DIR_MISSING", f"no such directory: {parent}")
    if not os.access(parent, os.W_OK):
        return ("down", "OUT_UNWRITABLE", f"not writable: {parent}")
    return ("ready", None, f"output dir writable: {parent}")


def check_render():
    """Local raster capability: a global mmdc, or npx (which can fetch it)."""
    if os.environ.get("MMDC_BIN"):
        return ("ready", None, f"MMDC_BIN override set: {os.environ['MMDC_BIN']}")
    if shutil.which("mmdc"):
        return ("ready", None, "mmdc on PATH (local SVG/PNG available)")
    if shutil.which("npx"):
        return ("ready", None, "npx present (mmdc via npx; first run downloads it)")
    return ("degraded", None, "no mmdc/npx — SVG/PNG falls back to Kroki or the "
            "fenced ```mermaid block")


def check_network(no_network):
    """Kroki reachability — only matters as the no-Node raster fallback."""
    if no_network:
        return ("degraded", None, "network disabled (--no-network); Kroki off")
    try:
        urllib.request.urlopen("https://kroki.io/health", timeout=6)
        return ("ready", None, "Kroki reachable (network render available)")
    except Exception:
        return ("degraded", None, "Kroki unreachable — fenced block / local mmdc only")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--no-network", action="store_true")
    args = ap.parse_args()

    checks = {
        "output": check_output(args.out),
        "render": check_render(),
        "network": check_network(args.no_network),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("draw-diagram readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<8} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)

    payload = {
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": ", ".join(f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
