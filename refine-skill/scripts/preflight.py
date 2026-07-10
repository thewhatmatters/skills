#!/usr/bin/env python3
"""Readiness check for refine-skill (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).

Checks: python present; a session transcript is locatable (explicit --transcript
or the newest .jsonl for this project); audit-skill present (needed for the
spec-compliance validation step — degrades, never blocks).
"""
import argparse
import json
import os
import sys

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}

SKILLS_DIR = os.path.expanduser("~/.claude/skills")
PROJECTS_DIR = os.path.expanduser("~/.claude/projects")


def _encode(path):
    return os.path.join(PROJECTS_DIR, path.replace("/", "-").replace(".", "-"))


def project_transcript_dir(cwd=None):
    """Transcript dir for the session's project (cwd encoded with '/' and '.'
    as '-'). Walk cwd then ancestors so it resolves from a subdirectory too."""
    cwd = cwd or os.getcwd()
    while True:
        d = _encode(cwd)
        if os.path.isdir(d) and any(f.endswith(".jsonl") for f in os.listdir(d)):
            return d
        parent = os.path.dirname(cwd)
        if parent == cwd:
            return _encode(cwd or os.getcwd())
        cwd = parent


def check_python():
    return ("ready", None, f"python {sys.version_info.major}.{sys.version_info.minor}")


def check_transcript(explicit):
    if explicit:
        if os.path.isfile(explicit):
            return ("ready", None, f"transcript: {os.path.basename(explicit)}")
        return ("down", "TRANSCRIPT_MISSING", f"--transcript not found: {explicit}")
    d = project_transcript_dir()
    try:
        jsonls = [f for f in os.listdir(d) if f.endswith(".jsonl")]
    except OSError:
        jsonls = []
    if jsonls:
        return ("ready", None, f"{len(jsonls)} transcript(s) in {os.path.basename(d)}")
    return ("down", "TRANSCRIPT_MISSING",
            "no session transcript for this project (pass --transcript=PATH)")


def check_audit_skill():
    if os.path.isdir(os.path.join(SKILLS_DIR, "audit-skill")):
        return ("ready", None, "audit-skill present")
    return ("degraded", "AUDIT_SKILL_ABSENT",
            "audit-skill missing — spec-compliance validation step skipped")


def check_hook():
    """Is the opt-in Stop hook wired in user settings? Informational only —
    the manual command works without it (so this never blocks)."""
    settings = os.path.expanduser("~/.claude/settings.json")
    try:
        with open(settings, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError, ValueError):
        data = {}
    stop = (data.get("hooks") or {}).get("Stop") or []
    text = json.dumps(stop)
    if "stop_hook.py" in text:
        return ("ready", None, "Stop hook wired")
    return ("degraded", "HOOK_NOT_INSTALLED",
            "Stop hook not wired — run scripts/install_hook.py (manual /refine-skill still works)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    checks = {
        "python": check_python(),
        "transcript": check_transcript(args.transcript),
        "audit_skill": check_audit_skill(),
        "hook": check_hook(),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("refine-skill readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<11} {d}{suffix}", file=sys.stderr)
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
