#!/usr/bin/env python3
"""Readiness check for build-ui (spec A6).

A local skill — no network, no secrets. The only things that can fail are
(a) python3 too old and (b) the project root not actually being a project (no
package.json + no .git anywhere up the tree). Verified for real, not guessed.

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse
import json
import os
import sys
from pathlib import Path

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_python():
    v = sys.version_info
    if v < (3, 8):
        return ("degraded", None, f"python {v.major}.{v.minor} (3.8+ recommended)")
    return ("ready", None, f"python {v.major}.{v.minor}")


def check_project(start):
    cur = Path(start).expanduser().resolve()
    for p in [cur, *cur.parents]:
        if (p / "package.json").is_file():
            return ("ready", None, f"package.json at {p}")
        if (p / ".git").exists():
            return ("degraded", "NO_PACKAGE_JSON",
                    f"git repo at {p} but no package.json — limited probe")
    return ("down", "PROJECT_NOT_FOUND",
            f"no package.json or .git anywhere up from {cur}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.add_argument("--project", default=".")
    args = ap.parse_args()

    checks = {"python": check_python(), "project": check_project(args.project)}
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("build-ui readiness", file=sys.stderr)
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
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
