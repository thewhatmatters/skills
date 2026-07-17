#!/usr/bin/env python3
"""Readiness check for extract-docs (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
Checks: target site reachable (--url), destination writable (--out).
"""
import argparse
import json
import os
import sys
from _net import get

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}
def check_site(url):
    if not url:
        return ("degraded", None, "no --url given; site check skipped")
    st, _ = get(url, timeout=10, method="HEAD")
    if st == 200:
        return ("ready", None, f"{url} reachable (HTTP {st})")
    if st in (405, 403):  # HEAD blocked; site is up
        return ("ready", None, f"{url} up (HEAD blocked, HTTP {st})")
    if st:
        return ("down", "SITE_UNREACHABLE", f"{url} → HTTP {st}")
    return ("down", "SITE_UNREACHABLE", f"{url} → network/SSL failure")


def check_dest(out):
    if not out:
        return ("ready", None, "destination resolved later (Step 3)")
    probe = out if os.path.isdir(out) else os.path.dirname(out.rstrip("/")) or "."
    while probe and not os.path.isdir(probe):
        probe = os.path.dirname(probe)
    if probe and os.access(probe, os.W_OK):
        return ("ready", None, f"{out} writable (via {probe})")
    return ("down", "DEST_UNWRITABLE", f"{out} not writable")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url")
    ap.add_argument("--out")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    checks = {"site": check_site(args.url), "dest": check_dest(args.out)}
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("extract-docs readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<5} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)

    print(json.dumps({
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
    }, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
