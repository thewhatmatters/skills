#!/usr/bin/env python3
"""PreCompact hook: snapshot HANDOFF.md before the context is compacted.

Claude Code fires this before auto (~threshold) or manual `/compact`. A hook
runs a shell command, not the model, so it cannot *generate* a summary — it
preserves what `/handoff` already wrote: it copies the current HANDOFF.md to a
timestamped archive so the working state survives the compaction boundary.

Input (stdin JSON): session_id, transcript_path, cwd, hook_event_name, matcher
("auto" | "manual"). Output: none required. MUST exit 0 — never block compaction.
"""
import datetime
import json
import os
import shutil
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    cwd = data.get("cwd") or os.getcwd()
    matcher = data.get("matcher") or "auto"

    src = os.path.join(cwd, "HANDOFF.md")
    if not os.path.isfile(src):
        # Nothing written yet — remind on stderr (shown in hook output), don't fail.
        print("PreCompact: no HANDOFF.md to snapshot — consider running /handoff "
              "before heavy compaction.", file=sys.stderr)
        return

    archive = os.path.join(cwd, ".claude", "handoff-archive")
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(archive, f"HANDOFF-{ts}-{matcher}.md")
    try:
        os.makedirs(archive, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"PreCompact: snapshotted HANDOFF.md → {dst}", file=sys.stderr)
    except OSError as e:
        print(f"PreCompact: snapshot skipped ({e})", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)          # never block compaction
