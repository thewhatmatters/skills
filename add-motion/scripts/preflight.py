#!/usr/bin/env python3
"""Readiness check for add-motion (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down (with a gate id).

Checks:
    project   — the --project path resolves to a real directory
                (down + PROJECT_NOT_FOUND otherwise; nothing to animate).
    package   — package.json found at/above the project root. Absent is NOT
                fatal: a plain HTML/CSS project still gets the CSS tier
                (degraded + NO_PACKAGE_JSON).

add-motion has no network, key, or binary dependencies — implementation is
file edits in the user's project — so preflight is deliberately small.
"""
import argparse
import json
import sys
from pathlib import Path

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def find_package_json(start):
    cur = Path(start).expanduser().resolve()
    for p in [cur, *cur.parents]:
        if (p / "package.json").is_file():
            return p / "package.json"
    return None


def check_project(path):
    p = Path(path).expanduser()
    if not p.is_dir():
        return ("down", "PROJECT_NOT_FOUND", f"{p} is not a directory")
    return ("ready", None, str(p.resolve()))


def check_package(path):
    if not Path(path).expanduser().is_dir():
        return ("down", "PROJECT_NOT_FOUND", "no project dir to scan")
    pj = find_package_json(path)
    if pj is None:
        return ("degraded", "NO_PACKAGE_JSON",
                "no package.json up-tree — CSS tier only")
    return ("ready", None, str(pj))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".", help="project root (default: cwd)")
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    checks = {
        "project": check_project(args.project),
        "package": check_package(args.project),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("add-motion readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<8} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)

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
