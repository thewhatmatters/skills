#!/usr/bin/env python3
"""Wire (or remove) the refine-skill stop hook in ~/.cursor/hooks.json.

Portable + idempotent: the hook command is computed from THIS file's location.
Safe to re-run; preserves all other hooks; backs up before writing.

I/O: [--remove] [--settings PATH] · stdout JSON {action, settings_path,
     hook_command, backup} · stderr human status · exit 0 ok, 1 only if the
     existing hooks.json is unparseable (never clobbered).
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
DEFAULT_SETTINGS = os.path.expanduser("~/.cursor/hooks.json")
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
    if not isinstance(settings, dict):
        settings = {}
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        hooks = {}
        settings["hooks"] = hooks
    stop = hooks.get("stop")
    if not isinstance(stop, list):
        stop = [] if stop is None else [stop]

    ours = [e for e in stop if _is_ours(e)]
    action, backup = "none", None
    entry = {"command": HOOK_COMMAND, "timeout": 15}

    if args.remove:
        if ours:
            stop = [e for e in stop if not _is_ours(e)]
            action = "removed"
        else:
            action = "absent"
    else:
        current = ours[0] if ours else None
        already_correct = (
            isinstance(current, dict)
            and current.get("command") == HOOK_COMMAND
        )
        if already_correct:
            action = "already-installed"
        else:
            stop = [e for e in stop if not _is_ours(e)]
            stop.append(entry)
            action = "updated" if ours else "installed"

    if action in ("installed", "updated", "removed"):
        if stop:
            hooks["stop"] = stop
        else:
            hooks.pop("stop", None)
        if not hooks:
            settings.pop("hooks", None)
        backup = write_settings(path, settings)

    sym = {"installed": "✅ installed", "updated": "✅ updated (fixed path)",
           "already-installed": "✅ already installed (no change)",
           "removed": "✅ removed", "absent": "· not present (nothing to remove)",
           "none": "· no change"}[action]
    print(f"refine-skill stop hook → {path}", file=sys.stderr)
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
