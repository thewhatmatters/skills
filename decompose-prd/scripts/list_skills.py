#!/usr/bin/env python3
"""Inventory the skills the executing agent will have (spec A4).

One concern: scan the global and project skill directories and report each
skill's name + description + scope, so decompose-prd can embed the *right*,
*actually-present* skill into each story instead of hard-coding one. This is the
source of truth for "skill-aware" task generation.

Scanned (deduped, project shadows global on name collision):
    global   : ~/.claude/skills/<name>/SKILL.md
    project  : <root>/.claude/skills/<name>/SKILL.md   (--project, default cwd;
               walks up to the nearest ancestor containing .claude/)

I/O: stdout JSON [{name, scope, description}] · stderr human list · exit 0
(an empty inventory is a valid answer, not an error).
"""
import argparse
import json
import re
import sys
from pathlib import Path

_NAME = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
_DESC = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)


def parse_frontmatter(text):
    """Return (name, description) from a SKILL.md YAML frontmatter block."""
    if text.startswith("---"):
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        block = m.group(1) if m else text
    else:
        block = text
    nm = _NAME.search(block)
    dm = _DESC.search(block)
    name = nm.group(1).strip().strip("\"'") if nm else None
    desc = dm.group(1).strip().strip("\"'") if dm else ""
    return name, desc


def scan(skills_dir, scope, found, order):
    base = Path(skills_dir).expanduser()
    if not base.is_dir():
        return
    for sk in sorted(base.glob("*/SKILL.md")):
        try:
            name, desc = parse_frontmatter(sk.read_text("utf-8", errors="replace"))
        except OSError:
            continue
        name = name or sk.parent.name
        # project shadows global: a later project entry overwrites a global one.
        if name not in found:
            order.append(name)
        found[name] = {"name": name, "scope": scope,
                       "description": (desc[:240] + "…") if len(desc) > 240 else desc}


def find_project_root(start):
    cur = Path(start).expanduser().resolve()
    for parent in [cur, *cur.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".", help="project root (default: cwd)")
    ap.add_argument("--global-dir", default="~/.claude/skills",
                    help="global skills dir (override for testing)")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    found, order = {}, []
    scan(args.global_dir, "global", found, order)
    proj_root = find_project_root(args.project)
    scan(proj_root / ".claude" / "skills", "project", found, order)

    result = [found[n] for n in order]
    print(f"skills available to the executor ({len(result)}): "
          f"project root {proj_root}", file=sys.stderr)
    for s in result:
        print(f"  [{s['scope']:7}] {s['name']}", file=sys.stderr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
