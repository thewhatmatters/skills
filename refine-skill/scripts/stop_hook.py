#!/usr/bin/env python3
"""Stop-hook handler for refine-skill — the opt-in reflection offer (spec A7/A8).

Registered as a Cursor `stop` hook (also understands legacy Stop stdin).
When a session used a skill from the user's own collection, it surfaces a
ONE-LINE, non-blocking suggestion to run `/refine-skill <skill>`.

Design choices:
- Offers, never forces: exit 0 + systemMessage (not decision:block / exit 2).
- Once per session: a marker file under the temp dir suppresses repeats so the
  notice is not shown on every turn.
- Scoped: only suggests skills that exist as directories under ~/.cursor/skills
  (the user's own), excluding refine-skill itself; stays silent if refine-skill
  was already used this session.
- Fails silent: any error → exit 0 with no output (never break the session).
"""
import json
import os
import re
import sys
import tempfile

SKILLS_DIR = os.path.expanduser("~/.cursor/skills")
MARKER_DIR = os.path.join(tempfile.gettempdir(), "refine-skill-hook")
_SKILL_MD_RE = re.compile(
    r"(?:^|/)(?:\.cursor/skills|skills)/([a-z][a-z0-9-]*)/SKILL\.md$"
)


def _own_skills():
    try:
        return {n for n in os.listdir(SKILLS_DIR)
                if os.path.isfile(os.path.join(SKILLS_DIR, n, "SKILL.md"))}
    except OSError:
        return set()


def _skills_used(transcript_path):
    """Ordered list of Skill invocations (input.skill) in the transcript."""
    used = []
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = entry.get("message")
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content")
                if not isinstance(content, list):
                    continue
                for blk in content:
                    if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                        continue
                    name = blk.get("name")
                    inp = blk.get("input") or {}
                    if name == "Skill":
                        sk = inp.get("skill")
                        if sk:
                            used.append(sk)
                    elif name == "Read":
                        p = (inp.get("path") or "").replace("\\", "/")
                        m = _SKILL_MD_RE.search(p)
                        if m:
                            used.append(m.group(1))
    except OSError:
        pass
    return used


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    # Loop guard (defensive; we never block, but honor the flag anyway).
    if data.get("stop_hook_active"):
        sys.exit(0)

    session_id = data.get("session_id") or "unknown"
    transcript = data.get("transcript_path")
    if not transcript or not os.path.isfile(transcript):
        sys.exit(0)

    # Once per session: bail fast if we've already offered.
    marker = os.path.join(MARKER_DIR, f"{session_id}.seen")
    if os.path.exists(marker):
        sys.exit(0)

    used = _skills_used(transcript)
    if "refine-skill" in used:
        sys.exit(0)  # already reflecting; don't nag

    own = _own_skills()
    candidates = [s for s in used if s in own and s != "refine-skill"]
    if not candidates:
        sys.exit(0)

    target = candidates[-1]  # most recently used own-skill

    # Mark first so a failure to write doesn't cause repeat nags on retry.
    try:
        os.makedirs(MARKER_DIR, exist_ok=True)
        open(marker, "w").close()
    except OSError:
        pass

    extra = ""
    others = [s for s in dict.fromkeys(candidates) if s != target]
    if others:
        extra = f" (also used: {', '.join(others)})"
    msg = (f"This session used /{target}{extra} — run `/refine-skill {target}` "
           f"to turn this run into a proposed skill improvement.")
    print(json.dumps({"systemMessage": msg}))
    sys.exit(0)


if __name__ == "__main__":
    main()
