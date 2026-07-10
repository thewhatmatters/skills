#!/usr/bin/env python3
"""Readiness check for polish-copy (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down (with a gate id).

Checks:
    project      — the --project path is a real directory
                   (down + PROJECT_NOT_FOUND otherwise).
    voice_spec   — resolution ladder: DESIGN.md containing a "## Voice"
                   section -> standalone VOICE.md -> none.
                   ready (detail says which) | degraded NO_VOICE_SPEC
                   (floor-only + bootstrap offer — not a blocker by design:
                   the floor layer is voice-independent).
    copy_sources — at least one extractable source kind found
                   (.tsx/.jsx/.html/.vue/.svelte/.xcstrings/.strings).
                   ready | degraded NO_COPY_SOURCES (NATIVE judgment on
                   whatever the user points at).

polish-copy has no network, key, or binary dependencies.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}
SOURCE_EXTS = {".tsx", ".jsx", ".html", ".vue", ".svelte", ".xcstrings", ".strings"}
SKIP_DIRS = {"node_modules", ".next", ".git", "dist", "build", "out", ".turbo",
             "coverage", ".vercel", ".cache", "public", "Pods", "DerivedData"}
VOICE_HEADING_RE = re.compile(r"^##+\s*Voice\b", re.MULTILINE | re.IGNORECASE)


def check_project(path):
    p = Path(path).expanduser()
    if not p.is_dir():
        return ("down", "PROJECT_NOT_FOUND", f"{p} is not a directory")
    return ("ready", None, str(p.resolve()))


def check_voice_spec(path):
    root = Path(path).expanduser()
    if not root.is_dir():
        return ("down", "PROJECT_NOT_FOUND", "no project dir to scan")
    for cand in ("DESIGN.md", "design.md"):
        f = root / cand
        if f.is_file():
            try:
                if VOICE_HEADING_RE.search(f.read_text("utf-8", errors="replace")):
                    return ("ready", None, f"design_md_voice — '## Voice' in {cand}")
            except OSError:
                pass
    f = root / "VOICE.md"
    if f.is_file():
        return ("ready", None, "voice_md — standalone VOICE.md")
    return ("degraded", "NO_VOICE_SPEC",
            "no '## Voice' in DESIGN.md and no VOICE.md — floor-only; offer bootstrap")


def check_copy_sources(path):
    root = Path(path).expanduser()
    if not root.is_dir():
        return ("down", "PROJECT_NOT_FOUND", "no project dir to scan")
    found = set()
    n = 0
    # os.walk with pruning: never descend into SKIP_DIRS, so the entry
    # budget is spent on real candidates, not node_modules contents.
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            n += 1
            if n > 5000:
                break
            if Path(name).suffix in SOURCE_EXTS:
                found.add(Path(name).suffix)
                if len(found) >= 3:
                    break
        if n > 5000 or len(found) >= 3:
            break
    if found:
        return ("ready", None, f"sources: {', '.join(sorted(found))}")
    return ("degraded", "NO_COPY_SOURCES",
            "no extractable source kinds found — point --path at the copy")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".", help="project root (default: cwd)")
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    checks = {
        "project":      check_project(args.project),
        "voice_spec":   check_voice_spec(args.project),
        "copy_sources": check_copy_sources(args.project),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("polish-copy readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<12} {d}{suffix}", file=sys.stderr)
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
