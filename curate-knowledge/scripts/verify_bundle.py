#!/usr/bin/env python3
"""Verify OKF conformance + link integrity for the vault (read-only).

Checks the v0.1 conformance floor: (1) every non-reserved .md has a parseable
frontmatter block, (2) with a non-empty `type`. Also resolves every
bundle-absolute link (and relative links in index files) outside fenced code
blocks. Broken links are reported as `info` — OKF tolerates them by design.
I/O: stdout JSON {conformant, errors, broken_links, stats} · stderr board ·
exit 1 only when conformance errors exist (broken links never fail the run).
"""
import argparse
import json
import os
import re
import sys

DEFAULT_VAULT = os.path.expanduser(
    "~/Library/CloudStorage/Dropbox/Documents/Obsidian"
)
# Tool files (CLAUDE.md, HANDOFF.md) are a documented producer deviation:
# infrastructure with externally-defined formats, exempt from the frontmatter
# rule like reserved files. Their links are still checked. Compared
# case-insensitively — macOS's filesystem preserves whatever casing the file
# was first created with.
RESERVED = {"index.md", "log.md"}
TOOL_FILES = {"claude.md", "handoff.md"}


def md_files(vault):
    for dirpath, dirs, files in os.walk(vault):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for f in sorted(files):
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    args = ap.parse_args()
    vault = os.path.expanduser(args.vault)

    if not os.path.isdir(vault):
        print(f"vault not found: {vault}", file=sys.stderr)
        print(json.dumps({"conformant": False, "errors": ["VAULT_MISSING"],
                          "broken_links": [], "stats": {}}))
        sys.exit(1)

    errors, broken, n_concepts, n_reserved = [], [], 0, 0

    for path in md_files(vault):
        rel = os.path.relpath(path, vault)
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            errors.append(f"{rel}: unreadable ({e})")
            continue

        base = os.path.basename(path)
        if base in RESERVED or base.lower() in TOOL_FILES:
            n_reserved += 1
        else:
            n_concepts += 1
            m = re.match(r"^---\n(.*?)\n---(\n|$)", text, re.S)
            if not m:
                errors.append(f"{rel}: no parseable frontmatter block")
            elif not re.search(r"^type:\s*\S", m.group(1), re.M):
                errors.append(f"{rel}: missing or empty `type`")

        # CommonMark fences: a block opened with N backticks closes only on a
        # run of >= N — nested shorter fences stay inside (e.g. ``` in ````).
        in_fence, fence_len = False, 0
        for i, line in enumerate(text.split("\n"), 1):
            fm2 = re.match(r"^\s*(`{3,})", line)
            if fm2:
                if not in_fence:
                    in_fence, fence_len = True, len(fm2.group(1))
                elif len(fm2.group(1)) >= fence_len:
                    in_fence = False
                continue
            if in_fence:
                continue
            for target in re.findall(r"\]\((/[^)#\s]+)", line):
                cand = os.path.join(vault, target.rstrip("/").lstrip("/"))
                if not (os.path.isfile(cand) or os.path.isdir(cand)):
                    broken.append(f"{rel}:{i} -> {target}")
            if os.path.basename(path) == "index.md":
                for target in re.findall(r"\]\((?!/|https?:)([^)#\s]+)", line):
                    cand = os.path.join(os.path.dirname(path), target.rstrip("/"))
                    if not (os.path.isfile(cand) or os.path.isdir(cand)):
                        broken.append(f"{rel}:{i} -> {target}")

    conformant = not errors
    print(f"concepts: {n_concepts}  reserved: {n_reserved}", file=sys.stderr)
    print(f"conformance errors: {len(errors)}", file=sys.stderr)
    for e in errors:
        print(f"  ⛔ {e}", file=sys.stderr)
    print(f"broken links (info — legal in OKF): {len(broken)}", file=sys.stderr)
    for b in broken:
        print(f"  ℹ {b}", file=sys.stderr)
    print(f"→ {'conformant' if conformant else 'NOT conformant'}", file=sys.stderr)

    print(json.dumps({
        "conformant": conformant,
        "errors": errors,
        "broken_links": broken,
        "stats": {"concepts": n_concepts, "reserved": n_reserved},
    }, indent=2))
    sys.exit(0 if conformant else 1)


if __name__ == "__main__":
    main()
