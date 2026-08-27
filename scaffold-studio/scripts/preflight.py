#!/usr/bin/env python3
"""Readiness check for scaffold-studio (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).

USAGE
    python3 scripts/preflight.py [--project=PATH] [--agent]
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}

HOME = Path(os.path.expanduser("~"))
DEFAULT_PLUGIN_PARENT = HOME / ".cursor" / "plugins" / "local"


def log(msg):
    print(msg, file=sys.stderr)


def check_git():
    path = shutil.which("git")
    if path:
        return ("ready", None, path)
    return ("gated", "GIT_MISSING", "git not on PATH — needed to clone Motion plugin")


def check_npm():
    path = shutil.which("npm")
    if path:
        return ("ready", None, path)
    return (
        "gated",
        "NPM_MISSING",
        "npm not on PATH — needed for CSS Studio (skip that layer if unused)",
    )


def check_plugin_dir():
    override = os.environ.get("MOTION_PLUGIN_DIR")
    parent = Path(override).expanduser().parent if override else DEFAULT_PLUGIN_PARENT
    try:
        parent.mkdir(parents=True, exist_ok=True)
        probe = parent / ".scaffold-studio-write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return ("ready", None, str(parent))
    except OSError as e:
        return (
            "gated",
            "PLUGIN_DIR_UNWRITABLE",
            f"cannot write {parent} ({e.__class__.__name__})",
        )


def check_project(project: Path):
    if not project.exists():
        return ("gated", "PROJECT_MISSING", f"missing {project}")
    pkg = project / "package.json"
    if pkg.is_file():
        return ("ready", None, f"package.json in {project}")
    return (
        "degraded",
        None,
        f"no package.json in {project} — CSS Studio needs an ESM or script-tag entry",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.add_argument("--project", default=".")
    args = ap.parse_args()
    project = Path(args.project).expanduser().resolve()
    checks = {
        "git": check_git(),
        "npm": check_npm(),
        "plugin": check_plugin_dir(),
        "project": check_project(project),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s
    log("scaffold-studio readiness")
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        log(f"  {MARK[s]} {n:<8} {d}{suffix}")
    log(f"  → overall: {overall}")
    payload = {
        "overall": overall,
        "checks": {
            n: {"status": s, "gate": g, "detail": d} for n, (s, g, d) in checks.items()
        },
        "summary": f"{overall}: " + ", ".join(f"{n}={s}" for n, (s, _, _) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
