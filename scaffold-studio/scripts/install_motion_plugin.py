#!/usr/bin/env python3
"""Install or refresh the Motion Cursor plugin into the local plugins dir.

Idempotent: if plugin.json already names "motion", skip unless --force.
Never deletes sibling plugins. Never writes ~/.cursor/mcp.json.

I/O: stdout JSON {status, dest, skipped, name} · stderr diagnostics.
Exit 0 on success/skip; 1 on failure.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "https://github.com/motiondivision/cursor-plugin"
HOME = Path(os.path.expanduser("~"))


def log(msg):
    print(msg, file=sys.stderr)


def dest_dir() -> Path:
    override = os.environ.get("MOTION_PLUGIN_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return HOME / ".cursor" / "plugins" / "local" / "motion"


def plugin_name(dest: Path):
    meta = dest / ".cursor-plugin" / "plugin.json"
    if not meta.is_file():
        return None
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    name = data.get("name")
    return name if isinstance(name, str) else None


def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def install(dest: Path, force: bool) -> dict:
    existing = plugin_name(dest)
    if existing == "motion" and not force:
        return {"status": "skipped", "dest": str(dest), "skipped": True, "name": existing}

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="motion-cursor-plugin-"))
    try:
        run(["git", "clone", "--depth", "1", REPO, str(tmp)])
        src = tmp / "plugins" / "motion"
        if not src.is_dir():
            raise FileNotFoundError(f"clone missing {src}")
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    name = plugin_name(dest)
    if name != "motion":
        raise RuntimeError(f"plugin.json name is {name!r}, expected 'motion'")
    return {"status": "installed", "dest": str(dest), "skipped": False, "name": name}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()
    dest = dest_dir()
    try:
        result = install(dest, force=args.force)
    except Exception as e:
        log(f"install_motion_plugin failed: {e}")
        print(json.dumps({"status": "error", "error": str(e), "dest": str(dest)}))
        sys.exit(1)
    log(f"  {result['status']} → {result['dest']}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
