"""
Shared API-key loader for scan-trends scripts.

Resolution order for any key (first hit wins):
  1. real process environment variable (explicit export always overrides)
  2. ~/.claude/.env            (recommended canonical, Claude-wide secrets)
  3. ~/.claude/skills/.env     (alternate, skills-scoped)

The .env format is plain `KEY=VALUE` lines; blank lines and `#` comments are
ignored, surrounding quotes on the value are stripped. Values are loaded into
os.environ only if not already set, so a real env var wins. Empty values
(`KEY=`) are skipped entirely — a placeholder never shadows a real key set in
a lower-precedence file.

Keep secrets out of logs: callers must send keys in request *headers*, never in
URLs/query strings, so they can't surface in the stderr error lines scripts print.
"""
import os
import stat

_ENV_FILES = [
    os.path.expanduser("~/.claude/.env"),
    os.path.expanduser("~/.claude/skills/.env"),
]


def _parse(path):
    pairs = {}
    try:
        with open(path, "r") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k:
                    pairs[k] = v
    except OSError:
        pass
    return pairs


def perm_warnings():
    """Return a list of human-readable warnings for world/group-readable .env files."""
    warns = []
    for path in _ENV_FILES:
        if not os.path.exists(path):
            continue
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode & 0o077:
            warns.append(
                f"{path} is mode {oct(mode)} — secrets readable by others; "
                f"run: chmod 600 {path}"
            )
    return warns


def load():
    """Populate os.environ from the .env files (without overriding real env vars).
    Returns the dict of keys that came from a file (for diagnostics)."""
    from_file = {}
    for path in _ENV_FILES:
        for k, v in _parse(path).items():
            if v and k not in os.environ:   # skip empty placeholders
                os.environ[k] = v
                from_file[k] = path
    return from_file


def get(name):
    """Convenience: ensure .env is loaded, then return the value (or None)."""
    load()
    return os.environ.get(name)
