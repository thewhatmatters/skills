#!/usr/bin/env python3
"""Probe a project for wire-sagan installation (read-only).

I/O: stdout JSON {project, git, entry_point, sagan, gates, marker_present} ·
stderr diagnostics · exit 2 on unusable project path. Never writes.
"""
import argparse
import json
import os
import re
import subprocess
import sys

MARKER_START = "<!-- wire-sagan:start -->"


def sh(args, cwd):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                           timeout=10)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def probe_entry_point(root):
    """Return (kind, wire_target, claude_host) for the project's entry point.

    wire_target is the file the marker block goes into; claude_host is the
    CLAUDE.md that loads it (same file unless AGENTS.md is imported).
    """
    root_claude = os.path.join(root, "CLAUDE.md")
    dot_claude = os.path.join(root, ".claude", "CLAUDE.md")
    agents = os.path.join(root, "AGENTS.md")
    for path, kind in ((root_claude, "root-claude-md"),
                       (dot_claude, "dot-claude-md")):
        if os.path.isfile(path):
            body = open(path, encoding="utf-8", errors="replace").read()
            if os.path.isfile(agents) and re.search(r"^@AGENTS\.md\s*$", body,
                                                    re.MULTILINE):
                return "agents-md-imported", agents, path
            return kind, path, path
    if os.path.isfile(agents):
        return "agents-md-only", agents, agents
    return "none", None, None


def detect_gates(root):
    gates = {"test": None, "typecheck": None, "build": None}
    pkg = os.path.join(root, "package.json")
    if os.path.isfile(pkg):
        try:
            scripts = json.load(open(pkg)).get("scripts", {})
        except (json.JSONDecodeError, OSError):
            scripts = {}
        for key in gates:
            if key in scripts:
                gates[key] = f"npm run {key}" if key != "test" else "npm test"
    elif os.path.isfile(os.path.join(root, "pyproject.toml")):
        gates["test"] = "pytest" if os.path.isdir(os.path.join(root, "tests")) else None
    elif os.path.isfile(os.path.join(root, "Makefile")):
        body = open(os.path.join(root, "Makefile"), errors="replace").read()
        for key in gates:
            if re.search(rf"^{key}:", body, re.MULTILINE):
                gates[key] = f"make {key}"
    return gates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    args = ap.parse_args()
    root = os.path.abspath(os.path.expanduser(args.project))
    if not os.path.isdir(root):
        print(json.dumps({"error": f"not a directory: {root}"}))
        sys.exit(2)

    code, top = sh(["git", "rev-parse", "--show-toplevel"], root)
    git_ok = code == 0
    kind, target, host = probe_entry_point(root)

    fleet_dir = os.path.join(root, ".sagan")
    fleet = {"present": os.path.isdir(fleet_dir), "template_version": None}
    fy = os.path.join(fleet_dir, "sagan.yaml")
    if os.path.isfile(fy):
        try:
            body = open(fy, encoding="utf-8", errors="replace").read()
            m = re.search(r'^template_version:\s*"?([^"\n]+)"?', body,
                          re.MULTILINE)
            fleet["template_version"] = m.group(1) if m else "unknown"
        except OSError:
            fleet["template_version"] = "unreadable"

    marker = False
    if target and os.path.isfile(target):
        marker = MARKER_START in open(target, errors="replace").read()

    payload = {
        "project": root,
        "git": {"is_repo": git_ok, "toplevel": top if git_ok else None},
        "entry_point": {"kind": kind, "wire_target": target,
                        "claude_host": host},
        "sagan": fleet,
        "gates": detect_gates(root),
        "marker_present": marker,
    }
    print(f"probe: {kind} · git={'yes' if git_ok else 'NO'} · "
          f".sagan={'present' if fleet['present'] else 'absent'}",
          file=sys.stderr)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
