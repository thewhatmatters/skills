#!/usr/bin/env python3
"""Probe a project's CLAUDE.md / memory ecosystem (spec A3 probe).

I/O: stdout JSON {root, scopes, line_counts, rules, imports, suggested_mode}
     · stderr human board · graceful failure · never hangs (no network).

Reports which CLAUDE.md scopes exist so SKILL.md can pick a mode:
  - no root CLAUDE.md            -> suggest AUTHOR
  - root CLAUDE.md present       -> suggest AUDIT (MAINTAIN if it looks healthy)

Pure stdlib, read-only. Does not edit anything.
"""
import argparse
import json
import os
import sys

# Soft target from the canonical spec (docs guidance ~200 lines; NOT a hard cap).
SOFT_LINE_TARGET = 200
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
             "dist", "build", ".next", ".cache"}


def _line_count(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return None


def _has_at_imports(path):
    """Count @-import lines (rough: a line whose first token starts with @)."""
    n = 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                tok = line.strip().split(" ", 1)[0] if line.strip() else ""
                if tok.startswith("@") and len(tok) > 1:
                    n += 1
    except OSError:
        return 0
    return n


def _find_nested(root):
    """Nested CLAUDE.md files below the root (loaded on-demand on read)."""
    nested = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if os.path.abspath(dirpath) == os.path.abspath(root):
            continue
        if "CLAUDE.md" in filenames:
            nested.append(os.path.relpath(os.path.join(dirpath, "CLAUDE.md"), root))
    return sorted(nested)


def _find_rules(root):
    """.claude/rules/*.md path-scoped rule files."""
    rules_dir = os.path.join(root, ".claude", "rules")
    if not os.path.isdir(rules_dir):
        return []
    out = []
    for name in sorted(os.listdir(rules_dir)):
        if name.endswith(".md"):
            p = os.path.join(rules_dir, name)
            scoped = False
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as fh:
                    head = fh.read(400)
                scoped = "paths:" in head
            except OSError:
                pass
            out.append({"file": os.path.relpath(p, root),
                        "lines": _line_count(p),
                        "has_paths_glob": scoped})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=os.getcwd(), help="target project root")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        print(json.dumps({"error": "TARGET_MISSING", "root": root}))
        print(f"craft-claude probe: target not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    root_md = os.path.join(root, "CLAUDE.md")
    dot_md = os.path.join(root, ".claude", "CLAUDE.md")
    local_md = os.path.join(root, "CLAUDE.local.md")

    scopes = {
        "root_claude_md": os.path.isfile(root_md),
        "dot_claude_md": os.path.isfile(dot_md),
        "claude_local_md": os.path.isfile(local_md),
    }
    line_counts = {
        "root": _line_count(root_md) if scopes["root_claude_md"] else None,
        "dot": _line_count(dot_md) if scopes["dot_claude_md"] else None,
        "local": _line_count(local_md) if scopes["claude_local_md"] else None,
    }
    nested = _find_nested(root)
    rules = _find_rules(root)

    primary = root_md if scopes["root_claude_md"] else (
        dot_md if scopes["dot_claude_md"] else None)
    imports = _has_at_imports(primary) if primary else 0
    primary_lines = (line_counts["root"] if scopes["root_claude_md"]
                     else line_counts["dot"])

    has_any = scopes["root_claude_md"] or scopes["dot_claude_md"]
    if not has_any:
        suggested = "author"
    elif primary_lines is not None and primary_lines > SOFT_LINE_TARGET:
        suggested = "audit"          # over soft target -> worth a real lint
    else:
        suggested = "maintain"       # exists and lean -> prune/staleness pass

    payload = {
        "root": root,
        "scopes": scopes,
        "line_counts": line_counts,
        "soft_line_target": SOFT_LINE_TARGET,
        "nested_claude_md": nested,
        "rules": rules,
        "at_imports_in_primary": imports,
        "suggested_mode": suggested,
    }

    print("craft-claude probe", file=sys.stderr)
    print(f"  root CLAUDE.md   : {'yes' if scopes['root_claude_md'] else 'no'}"
          f"  ({line_counts['root']} lines)" if scopes['root_claude_md']
          else "  root CLAUDE.md   : no", file=sys.stderr)
    print(f"  .claude/CLAUDE.md: {'yes' if scopes['dot_claude_md'] else 'no'}",
          file=sys.stderr)
    print(f"  CLAUDE.local.md  : {'yes' if scopes['claude_local_md'] else 'no'}",
          file=sys.stderr)
    print(f"  nested CLAUDE.md : {len(nested)}", file=sys.stderr)
    print(f"  .claude/rules/   : {len(rules)} file(s)", file=sys.stderr)
    print(f"  @-imports        : {imports}", file=sys.stderr)
    print(f"  → suggested mode : {suggested}", file=sys.stderr)

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
