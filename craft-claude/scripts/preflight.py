#!/usr/bin/env python3
"""Readiness check for craft-claude (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).

craft-claude is a local file transform — it needs only a readable canonical
spec and a target project directory. Nothing here is ever `down` unless the
spec itself is missing (that is the one true blocker).
"""
import argparse
import json
import os
import sys

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)


def check_spec():
    """The CLAUDE.md canon must be readable — without it no mode can run."""
    spec = os.path.join(SKILL_DIR, "references", "claude-md-spec.md")
    if os.path.isfile(spec) and os.access(spec, os.R_OK):
        return ("ready", None, "claude-md-spec.md readable")
    return ("down", "SPEC_MISSING", "references/claude-md-spec.md absent — cannot lint/author")


def check_target(path):
    """The target project dir must exist and be readable."""
    if os.path.isdir(path) and os.access(path, os.R_OK):
        return ("ready", None, f"target project dir readable ({path})")
    return ("down", "TARGET_MISSING", f"target dir not readable: {path}")


def check_render_html():
    """Optional: render-html for a branded audit page (degrade if absent)."""
    rh = os.path.join(os.path.dirname(SKILL_DIR), "render-html", "SKILL.md")
    if os.path.isfile(rh):
        return ("ready", None, "render-html available for branded reports")
    return ("degraded", None, "render-html not found — plain report only")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.add_argument("--path", default=os.getcwd(), help="target project root")
    args = ap.parse_args()

    checks = {
        "spec": check_spec(),
        "target": check_target(args.path),
        "render_html": check_render_html(),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("craft-claude readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<12} {d}{suffix}", file=sys.stderr)
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
