#!/usr/bin/env python3
"""Readiness check for remotion (spec A6).

A local skill — no network, no secrets. What can fail: python3 too old, Node not
on PATH (needed to run Studio/render, but you can still author code), and the
target not being a usable project dir. Verified for real, not guessed.

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_python():
    v = sys.version_info
    if v < (3, 8):
        return ("degraded", None, f"python {v.major}.{v.minor} (3.8+ recommended)")
    return ("ready", None, f"python {v.major}.{v.minor}")


def check_node():
    """Node powers Studio + render. Absent → gated (recoverable), not down:
    you can still author Remotion components without it."""
    if shutil.which("node"):
        return ("ready", None, "node on PATH")
    return ("gated", "NODE_MISSING",
            "node not on PATH — author-only; install Node 18+ to preview/render")


def check_project(start):
    cur = Path(start).expanduser().resolve()
    for p in [cur, *cur.parents]:
        if (p / "package.json").is_file():
            return ("ready", None, f"package.json at {p}")
        if (p / ".git").exists():
            return ("degraded", "NO_PACKAGE_JSON",
                    f"git repo at {p} but no package.json — greenfield/scaffold path")
    # An empty/new dir is a valid scaffold target, not a failure — and not a
    # recoverable gap to gate on, so no gate id (degraded is purely informational).
    return ("degraded", None,
            f"no package.json or .git up from {cur} — scaffold path (create-video)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    # --agent is a no-op here (preflight is non-interactive by nature); accepted
    # so the harness can pass SKILL.md's standard flag through without an error.
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    checks = {
        "python": check_python(),
        "node": check_node(),
        "project": check_project(args.project),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("remotion readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<7} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)

    payload = {
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": ", ".join(f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    # Only `down` halts; a gate (NODE_MISSING) never blocks (spec A7).
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
