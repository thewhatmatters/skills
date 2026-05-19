#!/usr/bin/env python3
"""Readiness check run before the generator scaffolds anything (DESIGN.md §6.1).

One concern: answer "is everything in place to generate a skill right now?"
with a 4-state status, so a half-scaffolded skill never results from a missing
input. It does NOT fetch or refresh — it *assesses* what docs.py left behind
plus a quick connectivity probe. Same pattern as trendscan's preflight
(skill-architecture.md pattern A6).

USAGE
    python3 scripts/preflight.py [--out=PATH] [--agent]

    --out=PATH  destination dir for the skill to be generated
                (default: the skills dir, ~/.claude/skills)
    --agent     non-interactive; report only, never prompt

I/O CONTRACT
    stdout : a single JSON object — {overall, checks{...}, summary}
    stderr : a human readiness board
    exit   : 0 if overall ∈ {ready, degraded, gated};
             1 if overall == down (a hard blocker)

PER-CHECK STATUS  ∈ {ready, degraded, gated, down}  (+ a gate id when not ready)
    spec     skill-architecture.md present & readable      down → NO_SPEC
    docs     usable doc set available, and how fresh        gated → DOCS_STALE
                                                            down  → NO_DOCS
    target   destination dir writable / safe                down  → TARGET_UNWRITABLE
    network  code.claude.com reachable (to refresh)         degraded → OFFLINE
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import docs  # noqa: E402 - sibling module, intentional path insert

SKILL_ROOT = SCRIPT_DIR.parent
SKILLS_DIR = SKILL_ROOT.parent  # ~/.claude/skills
SPEC = SKILLS_DIR / "skill-architecture.md"
NET_PROBE_URL = "https://code.claude.com/docs/en/skills.md"
NET_TIMEOUT = 3  # seconds; keeps preflight fast

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
# overall = the worst single check (down > gated > degraded > ready)
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def log(msg):
    print(msg, file=sys.stderr)


def check_spec():
    if SPEC.is_file():
        try:
            if SPEC.read_text("utf-8").strip():
                return ("ready", None, f"{SPEC.name} readable")
        except OSError as e:
            return ("down", "NO_SPEC", f"unreadable ({e.__class__.__name__})")
    return ("down", "NO_SPEC",
            f"missing {SPEC} — generator has no spec to scaffold against")


def check_docs():
    manifest = docs.load_manifest()
    age = docs.cache_age_days(manifest)
    cache_ok = bool(docs.read_dir(docs.CACHE_DIR))
    snap_ok = bool(docs.read_dir(docs.SNAPSHOT_DIR))

    if cache_ok and age is not None and age <= docs.FRESHNESS_DAYS:
        v = (manifest or {}).get("claude_code_version")
        return ("ready", None,
                f"cache fresh ({age:.0f}d ≤ {docs.FRESHNESS_DAYS}d), CC {v}")
    if cache_ok or snap_ok:
        src = "stale cache" if cache_ok else "committed snapshot"
        agetxt = f"{age:.0f}d old" if age is not None else "no manifest"
        return ("gated", "DOCS_STALE",
                f"{src} ({agetxt}) — run: scripts/docs.py --refresh")
    return ("down", "NO_DOCS",
            "no cache and no snapshot — run scripts/docs.py once online")


def check_target(out):
    # The parent dir new skill folders are created under. Clobber-protection
    # for a specific skill name happens in the generator step, not here —
    # preflight only answers "can new skills be written into this location?".
    import os
    probe = Path(out).expanduser()
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    if probe.is_dir() and os.access(probe, os.W_OK):
        return ("ready", None, f"{out} writable")
    return ("down", "TARGET_UNWRITABLE", f"cannot write under {probe}")


def check_network():
    # GET (not HEAD — some servers 405 HEAD) but the body is never read; reuse
    # docs.py's certifi-backed SSL context so a trust failure isn't misread
    # as "offline".
    try:
        req = urllib.request.Request(
            NET_PROBE_URL,
            headers={"User-Agent": "skill-generator-preflight/1.0"},
        )
        with urllib.request.urlopen(
            req, timeout=NET_TIMEOUT, context=docs.ssl_context()
        ) as r:
            if r.status < 400:
                return ("ready", None, "code.claude.com reachable")
            return ("degraded", "OFFLINE", f"probe http {r.status}")
    except Exception as e:  # noqa: BLE001 - any failure = treat as offline
        return ("degraded", "OFFLINE",
                f"unreachable ({e.__class__.__name__}); cache/snapshot used")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--out", default=str(SKILLS_DIR))
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    checks = {
        "spec": check_spec(),
        "docs": check_docs(),
        "target": check_target(args.out),
        "network": check_network(),
    }

    overall = "ready"
    for status, _gate, _detail in checks.values():
        if RANK[status] > RANK[overall]:
            overall = status

    log("skill-generator readiness")
    for name, (status, gate, detail) in checks.items():
        g = f"  [{gate}]" if gate else ""
        log(f"  {MARK[status]} {name:<8} {detail}{g}")
    log(f"  → overall: {overall}")
    if overall == "down":
        log("  (a hard blocker is present — resolve the ⛔ item above)")
    elif overall in ("gated", "degraded"):
        log("  (can proceed on a degraded path; refresh when able)")

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
