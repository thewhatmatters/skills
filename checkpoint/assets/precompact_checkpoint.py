#!/usr/bin/env python3
"""PreCompact hook: snapshot the checkpoint memory entry before compaction.

Claude Code fires this before auto (~threshold) or manual `/compact`. A hook
runs a shell command, not the model, so it cannot *generate* a summary — it
preserves what `/checkpoint` already wrote: it copies the project's
`~/.claude/projects/<munged-cwd>/memory/checkpoint.md` to a timestamped
archive under `~/.claude/.cache/checkpoint/<munged-cwd>/` so the working
state survives the compaction boundary. Archives live in .cache, never in
the memory dir itself (they must not pollute memory recall).

Input (stdin JSON): session_id, transcript_path, cwd, hook_event_name, matcher
("auto" | "manual"). Output: none required. MUST exit 0 — never block compaction.
"""
import datetime
import json
import os
import re
import shutil
import sys


def munge(cwd):
    return re.sub(r"[^A-Za-z0-9-]", "-", cwd)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    cwd = data.get("cwd") or os.getcwd()
    matcher = data.get("matcher") or "auto"

    munged = munge(cwd)
    src = os.path.join(os.path.expanduser("~/.claude/projects"),
                       munged, "memory", "checkpoint.md")
    if not os.path.isfile(src):
        # Nothing written yet — remind on stderr (shown in hook output), don't fail.
        print("PreCompact: no checkpoint to snapshot — consider running "
              "/checkpoint before heavy compaction.", file=sys.stderr)
        return

    archive = os.path.join(os.path.expanduser("~/.claude/.cache/checkpoint"), munged)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(archive, f"checkpoint-{ts}-{matcher}.md")
    try:
        os.makedirs(archive, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"PreCompact: snapshotted checkpoint → {dst}", file=sys.stderr)
    except OSError as e:
        print(f"PreCompact: snapshot skipped ({e})", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)          # never block compaction
