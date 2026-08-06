#!/usr/bin/env python3
"""Readiness check for wire-sagan (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse
import json
import os
import sys

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "assets", "template")
REQUIRED = ["sagan.yaml", "MEMORY.md", "gitignore-fragment",
            os.path.join("roles", "frontend.md"),
            os.path.join("roles", "critic.md"),
            os.path.join("roles", "verify.md"),
            os.path.join("tickets", "T-000-example.md")]


def check_template():
    missing = [p for p in REQUIRED
               if not os.path.isfile(os.path.join(TEMPLATE_DIR, p))]
    if missing:
        return ("down", "TEMPLATE_MISSING",
                f"template files missing: {', '.join(missing)} — run: git -C ~/.claude pull")
    return ("ready", None, f"template present ({len(REQUIRED)} files)")


def check_git():
    from shutil import which
    if which("git"):
        return ("ready", None, "git on PATH")
    return ("degraded", None,
            "git not found — SHA-bound evidence and repo probes unavailable")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.parse_args()
    checks = {"template": check_template(), "git": check_git()}
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s
    print("wire-sagan readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<8} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)
    payload = {
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": "; ".join(f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
