#!/usr/bin/env python3
"""Readiness check for format-markdown (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
Checks: style spec present (down if missing — the skill is spec-bound);
markdownlint resolvable via the A11 ladder (degraded if not — judgment-only).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_spec():
    path = os.path.join(SKILL_DIR, "references", "markdown-style.md")
    if os.path.isfile(path):
        return ("ready", None, "style spec present")
    return ("down", "SPEC_MISSING", f"style spec missing: {path}")


def resolve_markdownlint():
    """A11 ladder: $MARKDOWNLINT_BIN -> PATH -> npx. Returns (argv, label) or (None, None)."""
    override = os.environ.get("MARKDOWNLINT_BIN", "").strip()
    if override and shutil.which(override):
        return ([override], f"$MARKDOWNLINT_BIN ({override})")
    if shutil.which("markdownlint"):
        return (["markdownlint"], "markdownlint on PATH")
    if shutil.which("npx"):
        return (["npx", "--yes", "markdownlint-cli"], "npx markdownlint-cli")
    return (None, None)


def check_lint():
    argv, label = resolve_markdownlint()
    if argv is None:
        return ("degraded", None,
                "markdownlint unavailable (no $MARKDOWNLINT_BIN/PATH/npx) — judgment-only")
    return ("ready", None, f"lint via {label}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.parse_args()
    checks = {"spec": check_spec(), "lint": check_lint()}
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s
    print("format-markdown readiness", file=sys.stderr)
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
