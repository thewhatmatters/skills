#!/usr/bin/env python3
"""SessionStart hook: resurface HANDOFF.md into a fresh session.

When a session starts/resumes/clears/compacts, this reads the project's
HANDOFF.md and returns it as `additionalContext`, so the new session resumes
sharp instead of cold. This is how state crosses the refresh boundary the user
can't automate away.

Input (stdin JSON): session_id, source ("startup"|"resume"|"clear"|"compact"),
cwd, model. Output (stdout JSON): hookSpecificOutput.additionalContext. MUST
exit 0. If a Claude Code version ignores additionalContext, the on-disk
HANDOFF.md (and a CLAUDE.md `@import`) remain the reload path — this never blocks.
"""
import json
import os
import sys

MAX_CHARS = 8000   # cap so a huge handoff can't itself bloat the new context


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    cwd = data.get("cwd") or os.getcwd()
    src = os.path.join(cwd, "HANDOFF.md")
    try:
        with open(src) as f:
            body = f.read()
    except OSError:
        return                       # no handoff → nothing to surface

    if len(body) > MAX_CHARS:
        body = body[:MAX_CHARS] + "\n\n…(truncated — open HANDOFF.md for the rest)"

    context = ("Resuming work. The previous session left this HANDOFF.md — use it "
               "to continue without re-deriving context:\n\n" + body)
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                  "additionalContext": context}}
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)
