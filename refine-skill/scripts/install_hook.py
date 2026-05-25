#!/usr/bin/env python3
"""Wire (or remove) the refine-skill Stop hook in ~/.claude/settings.json.

Portable + idempotent: the hook command is computed from THIS file's location
(`stop_hook.py` next to it), so a fresh clone on any machine/user wires the
correct absolute path — no hardcoded home dir. Safe to re-run; preserves all
other settings; backs up before writing.

I/O: [--remove] [--settings PATH] · stdout JSON {action, settings_path,
     hook_command, backup} · stderr human status · exit 0 ok, 1 only if the
     existing settings.json is unparseable (never clobbered).

Run on a new machine:  python3 refine-skill/scripts/install_hook.py
Remove the hook:       python3 refine-skill/scripts/install_hook.py --remove
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.realpath(__file__))
HOOK_SCRIPT = os.path.join(HERE, "stop_hook.py")
HOOK_COMMAND = f"python3 {HOOK_SCRIPT}"
DEFAULT_SETTINGS = os.path.expanduser("~/.claude/settings.json")
MARKER = "stop_hook.py"  # how we recognise our own Stop entries


def _commands_in(entry):
    """All command strings in a Stop entry (handles grouped + flat shapes)."""
    if not isinstance(entry, dict):
        return []
    if isinstance(entry.get("hooks"), list):
        return [h.get("command", "") for h in entry["hooks"] if isinstance(h, dict)]
    if "command" in entry:
        return [entry.get("command", "")]
    return []


def _is_ours(entry):
    return any(MARKER in c for c in _commands_in(entry))


def load_settings(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return {}, True  # (settings, fresh)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), False
    except (json.JSONDecodeError, ValueError) as e:
        print(f"  ⛔ {path} is not valid JSON ({e}); refusing to modify it.",
              file=sys.stderr)
        sys.exit(1)


def write_settings(path, settings):
    backup = None
    if os.path.exists(path) and os.path.getsize(path) > 0:
        backup = f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(path, backup)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)
        fh.write("\n")
    return backup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--remove", action="store_true", help="remove the hook")
    ap.add_argument("--settings", default=DEFAULT_SETTINGS)
    args = ap.parse_args()
    path = os.path.expanduser(args.settings)

    settings, _fresh = load_settings(path)
    hooks = settings.setdefault("hooks", {}) if isinstance(settings, dict) else {}
    stop = hooks.get("Stop")
    if not isinstance(stop, list):
        stop = [] if stop is None else [stop]

    ours = [e for e in stop if _is_ours(e)]
    action, backup = "none", None

    if args.remove:
        if ours:
            stop = [e for e in stop if not _is_ours(e)]
            action = "removed"
        else:
            action = "absent"
    else:
        current = ours[0] if ours else None
        already_correct = current and _commands_in(current) == [HOOK_COMMAND]
        if already_correct:
            action = "already-installed"
        else:
            stop = [e for e in stop if not _is_ours(e)]  # drop stale/mismatched
            stop.append({"hooks": [{"type": "command", "command": HOOK_COMMAND}]})
            action = "updated" if ours else "installed"

    # Persist only if something changed; tidy empty structures.
    if action in ("installed", "updated", "removed"):
        if stop:
            hooks["Stop"] = stop
        else:
            hooks.pop("Stop", None)
        if not hooks:
            settings.pop("hooks", None)
        backup = write_settings(path, settings)

    sym = {"installed": "✅ installed", "updated": "✅ updated (fixed path)",
           "already-installed": "✅ already installed (no change)",
           "removed": "✅ removed", "absent": "· not present (nothing to remove)",
           "none": "· no change"}[action]
    print(f"refine-skill Stop hook → {path}", file=sys.stderr)
    print(f"  {sym}", file=sys.stderr)
    print(f"  command: {HOOK_COMMAND}", file=sys.stderr)
    if not os.path.isfile(HOOK_SCRIPT):
        print(f"  ⚠  handler not found at {HOOK_SCRIPT}", file=sys.stderr)
    if backup:
        print(f"  backup: {backup}", file=sys.stderr)

    print(json.dumps({"action": action, "settings_path": path,
                      "hook_command": HOOK_COMMAND, "backup": backup}, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
