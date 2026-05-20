#!/usr/bin/env python3
"""Readiness check for prd-generator (spec A6).

One concern: confirm we can write the PRD where the user asked. prd-generator
has no external services, no auth, and no API keys — its only environmental
need is a writable output directory. Everything else (the discussion source,
the synthesis quality) is runtime / model-side and not knowable at preflight.

USAGE
    python3 scripts/preflight.py [--out=PATH] [--agent]

    --out=PATH  output directory the PRD will be written to (default: cwd)
    --agent     non-interactive; report only, never prompt

I/O CONTRACT
    stdout : a single JSON object — {overall, checks{...}, summary}
    stderr : a human readiness board
    exit   : 0 if overall ∈ {ready, degraded, gated};
             1 if overall == down (a hard blocker)

PER-CHECK STATUS  ∈ {ready, degraded, gated, down}  (+ a gate id when not ready)
    target   output dir writable / safe              down → TARGET_UNWRITABLE
    html     python3 + scripts/report.py present     degraded → HTML_UNAVAILABLE
                                                     (informational: markdown
                                                     path still works fully)
"""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPORT_SCRIPT = SCRIPT_DIR / "report.py"

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
# overall = the worst single check (down > gated > degraded > ready)
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def log(msg):
    print(msg, file=sys.stderr)


def check_target(out):
    """Can we create the PRD under <out>?

    Walks up to the nearest existing parent and checks W_OK. Matches the
    skill-generator preflight idiom — no clobber-protection for a specific
    filename here; that's for the runtime no-clobber step (spec A11).
    """
    probe = Path(out).expanduser()
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    if probe.is_dir() and os.access(probe, os.W_OK):
        return ("ready", None, f"{out} writable")
    return ("down", "TARGET_UNWRITABLE", f"cannot write under {probe}")


def check_html():
    """Is the HTML render path available? Informational, not blocking.

    Markdown always works (model-driven). HTML needs python3 (which we are,
    transitively — we're running) and report.py. If report.py is missing
    we surface degraded, with a hint that --no-html avoids the notice.
    """
    if REPORT_SCRIPT.is_file():
        return ("ready", None, "report.py present (HTML render available)")
    return ("degraded", "HTML_UNAVAILABLE",
            f"missing {REPORT_SCRIPT.name} — markdown still works; "
            "pass --no-html to silence")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--out", default=str(Path.cwd()))
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    checks = {
        "target": check_target(args.out),
        "html": check_html(),
    }

    overall = "ready"
    for status, _gate, _detail in checks.values():
        if RANK[status] > RANK[overall]:
            overall = status

    log("prd-generator readiness")
    for name, (status, gate, detail) in checks.items():
        g = f"  [{gate}]" if gate else ""
        log(f"  {MARK[status]} {name:<6} {detail}{g}")
    log(f"  → overall: {overall}")
    if overall == "down":
        log("  (a hard blocker is present — resolve the ⛔ item above)")

    payload = {
        "overall": overall,
        "checks": {
            n: {"status": s, "gate": g, "detail": d}
            for n, (s, g, d) in checks.items()
        },
        "summary": f"{overall}: " + ", ".join(
            f"{n}={s}" for n, (s, _g, _d) in checks.items()
        ),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
