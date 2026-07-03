#!/usr/bin/env python3
"""Inventory every concept in the OKF vault (single concern: read, never write).

Parses flat top-level frontmatter keys with stdlib only (no PyYAML) — all OKF
requires. Nested/unknown keys are ignored, not errors. Tags are parsed from
the inline form only (`tags: [a, b]`); block-style YAML lists yield no tags.
Also extracts each concept's outgoing links (absolute + relative, outside
fenced code blocks, .md targets only) so backlinks are computable by the
consumer. Tool files (CLAUDE.md, HANDOFF.md) are infrastructure, not
knowledge — skipped like reserved files.
I/O: stdout JSON {vault, count, concepts:[{path, concept_id, type, title,
description, tags, timestamp, links}]} · stderr diagnostics · exit 0 unless
the vault is absent.
"""
import argparse
import json
import os
import re
import sys

DEFAULT_VAULT = os.path.expanduser(
    "~/Library/CloudStorage/Dropbox/Documents/Obsidian"
)
RESERVED = {"index.md", "log.md"}
TOOL_FILES = {"claude.md", "handoff.md"}  # compared case-insensitively (macOS FS)
FLAT_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")


def extract_links(text, dirpath, vault):
    """Outgoing links as vault-root-relative .md paths, skipping code fences."""
    # CommonMark fences: close only on a run of >= the opening length, so
    # nested shorter fences (``` inside ````) stay inside the block.
    links, in_fence, fence_len = set(), False, 0
    for line in text.split("\n"):
        m = re.match(r"^\s*(`{3,})", line)
        if m:
            if not in_fence:
                in_fence, fence_len = True, len(m.group(1))
            elif len(m.group(1)) >= fence_len:
                in_fence = False
            continue
        if in_fence:
            continue
        for target in re.findall(r"\]\(([^)#\s]+\.md)\)", line):
            if target.startswith(("http://", "https://")):
                continue
            if target.startswith("/"):
                rel = target.lstrip("/")
            else:
                rel = os.path.relpath(os.path.normpath(
                    os.path.join(dirpath, target)), vault)
            if not rel.startswith(".."):
                links.add(rel)
    return sorted(links)


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---(\n|$)", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).split("\n"):
        km = FLAT_KEY.match(line)
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        if key == "tags":
            fields[key] = [t.strip() for t in val.strip("[]").split(",") if t.strip()]
        else:
            fields[key] = val.strip("'\"")
    return fields


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    args = ap.parse_args()
    vault = os.path.expanduser(args.vault)

    if not os.path.isdir(vault):
        print(f"vault not found: {vault}", file=sys.stderr)
        print(json.dumps({"vault": vault, "count": 0, "concepts": [],
                          "error": "VAULT_MISSING"}))
        sys.exit(1)

    concepts = []
    for dirpath, dirs, files in os.walk(vault):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for f in sorted(files):
            if (not f.endswith(".md") or f in RESERVED
                    or f.lower() in TOOL_FILES):
                continue
            path = os.path.join(dirpath, f)
            rel = os.path.relpath(path, vault)
            try:
                text = open(path, encoding="utf-8").read()
            except OSError as e:
                print(f"unreadable, skipped: {rel} ({e})", file=sys.stderr)
                continue
            fm = parse_frontmatter(text) or {}
            concepts.append({
                "path": rel,
                "concept_id": rel[:-3],
                "type": fm.get("type"),
                "title": fm.get("title"),
                "description": fm.get("description"),
                "tags": fm.get("tags", []),
                "timestamp": fm.get("timestamp"),
                "links": extract_links(text, dirpath, vault),
            })

    print(f"scanned {len(concepts)} concepts under {vault}", file=sys.stderr)
    print(json.dumps({"vault": vault, "count": len(concepts),
                      "concepts": concepts}, indent=2))


if __name__ == "__main__":
    main()
