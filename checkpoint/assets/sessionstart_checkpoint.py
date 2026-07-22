#!/usr/bin/env python3
"""SessionStart hook: resurface the project's checkpoint memory entry.

When a session starts/resumes/clears/compacts, this reads the project's
checkpoint from `~/.claude/projects/<munged-cwd>/memory/checkpoint.md` and
returns it as `additionalContext`, so the new session resumes sharp instead
of cold. Memory's native loading is the MEMORY.md index line only — this hook
is what guarantees the FULL checkpoint crosses the refresh boundary.

Falls back to a legacy `<cwd>/HANDOFF.md` if no memory checkpoint exists yet
(migration grace; the checkpoint skill deletes HANDOFF.md on its next run).

Input (stdin JSON): session_id, source ("startup"|"resume"|"clear"|"compact"),
cwd, model. Output (stdout JSON): hookSpecificOutput.additionalContext. MUST
exit 0. If a Claude Code version ignores additionalContext, the entry is
still on disk and indexed in MEMORY.md — this never blocks.
"""
import json
import os
import re
import sys

MAX_CHARS = 8000   # cap so a huge checkpoint can't itself bloat the new context


def memory_checkpoint_path(cwd):
    munged = re.sub(r"[^A-Za-z0-9-]", "-", cwd)
    return os.path.join(os.path.expanduser("~/.claude/projects"),
                        munged, "memory", "checkpoint.md")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    cwd = data.get("cwd") or os.getcwd()

    src = memory_checkpoint_path(cwd)
    label = "checkpoint memory entry"
    if not os.path.isfile(src):
        src = os.path.join(cwd, "HANDOFF.md")   # legacy fallback
        label = "legacy HANDOFF.md (will migrate on next /checkpoint)"
    try:
        with open(src) as f:
            body = f.read()
    except OSError:
        return                       # no checkpoint → nothing to surface

    if len(body) > MAX_CHARS:
        body = body[:MAX_CHARS] + f"\n\n…(truncated — open {src} for the rest)"

    context = (f"Resuming work. The previous session left this {label} — use it "
               "to continue without re-deriving context:\n\n" + body)
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                  "additionalContext": context}}
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)
