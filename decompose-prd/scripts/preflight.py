#!/usr/bin/env python3
"""Readiness check for decompose-prd (spec A6).

A local transform — no network, no secrets. The only things that can fail are
(a) the PRD input not being readable and (b) the output target dir not being
writable. Verified for real, not guessed from extensions.

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


def check_input(path):
    if not path:
        return ("ready", None, "PRD will be read from the request/stdin")
    p = Path(path).expanduser()
    if not p.exists():
        return ("down", "INPUT_MISSING", f"no such PRD file: {p}")
    if not os.access(p, os.R_OK):
        return ("down", "INPUT_UNREADABLE", f"not readable: {p}")
    return ("ready", None, f"PRD readable: {p.name}")


def check_output(path):
    parent = (Path(path).expanduser().parent if path else Path(".")) or Path(".")
    if not parent.exists():
        return ("down", "OUT_DIR_MISSING", f"no such directory: {parent}")
    if not os.access(parent, os.W_OK):
        return ("down", "OUT_UNWRITABLE", f"not writable: {parent}")
    return ("ready", None, f"output dir writable: {parent}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.add_argument("--in", dest="inp")
    ap.add_argument("--out")
    args = ap.parse_args()

    checks = {
        "python": check_python(),
        "input": check_input(args.inp),
        "output": check_output(args.out),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("decompose-prd readiness", file=sys.stderr)
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
