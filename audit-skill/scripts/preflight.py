#!/usr/bin/env python3
"""Readiness check for audit-skill's `--triggers` mode (spec A6).

The structural audit needs nothing (it reads the spec + skill files with
built-in tools). Only the OPT-IN triggering bake-off has a dependency: the
`claude` CLI, which `trigger_eval.py` shells out to. This preflight verifies
that and surfaces the cost intent — it does not run anything expensive.

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse
import json
import shutil
import sys

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_claude_cli():
    if shutil.which("claude"):
        return ("ready", None, "`claude` CLI on PATH (triggering bake-off available)")
    # A recoverable setup gap, not a transient error → a gate, never a silent
    # degrade. The structural audit still works without it.
    return ("gated", "CLAUDE_CLI_MISSING",
            "`claude` CLI not found — structural audit still works; "
            "triggering bake-off unavailable until installed")


def check_cost_notice():
    # Not a failure — an informational gate so the run is intentional. The
    # bake-off fires one `claude -p` per query (real tokens/time); only run it
    # when a description actually changed.
    return ("ready", None,
            "note: --triggers fires 1 `claude -p` per query (cost/time) — "
            "run it on description changes, not on a schedule")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.parse_args()
    checks = {"claude_cli": check_claude_cli(), "cost": check_cost_notice()}

    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("audit-skill --triggers readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<11} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)

    payload = {
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": ", ".join(f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    # `gated` does not stop the structural audit; only `down` would.
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
