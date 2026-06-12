#!/usr/bin/env python3
"""Persist an ingestion into the project's docs/sources/ knowledge base (spec A4).

One concern: deterministic persistence. Takes a finished summary (stdin or
--file) plus its metadata, then:
  1. writes `<docs-dir>/<slug>.md` with YAML frontmatter (source, type, title,
     ingested, tier) — re-ingesting the same `source` UPDATES the existing
     file instead of duplicating it;
  2. upserts the one-line entry in `<docs-dir>/INDEX.md`;
  3. reports (but NEVER edits) the project CLAUDE.md wiring: whether the
     marker-delimited @-import block is present, absent, or there is no
     CLAUDE.md — and emits the exact block to insert. Editing the user's
     CLAUDE.md is a consent-gated step the caller performs (spec A7).

I/O: --source URL|PATH --type T --title S --tier S [--hook S] [--file PATH]
     [--docs-dir P] [--project-root P] [--date YYYY-MM-DD]
     · stdout JSON {written, action, index, claude_md} · stderr diagnostics
     · exit 0 on success, 1 on failure. No network.
"""
import argparse
import datetime
import json
import os
import re
import sys

MARKER_START = "<!-- ingest-source:start -->"
MARKER_END = "<!-- ingest-source:end -->"

TYPES = ("youtube", "webpage", "pdf", "image", "document")


def slugify(text, fallback="source"):
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug[:60].rstrip("-") or fallback


def frontmatter_source(path):
    """Return the `source:` value from a file's leading YAML block, or None."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = fh.read(2048)
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    block = head.split("---", 2)[1] if head.count("---") >= 2 else head
    m = re.search(r"^source:\s*(.+?)\s*$", block, re.M)
    return m.group(1).strip('"') if m else None


def target_path(docs_dir, slug, source):
    """Existing file for this source (update), else a collision-free new path."""
    for name in sorted(os.listdir(docs_dir)):
        if name.endswith(".md") and name != "INDEX.md":
            if frontmatter_source(os.path.join(docs_dir, name)) == source:
                return os.path.join(docs_dir, name), "updated"
    path = os.path.join(docs_dir, f"{slug}.md")
    n = 2
    while os.path.exists(path):
        path = os.path.join(docs_dir, f"{slug}-{n}.md")
        n += 1
    return path, "created"


def upsert_index(docs_dir, filename, title, typ, date, hook):
    index = os.path.join(docs_dir, "INDEX.md")
    line = f"- [{title}]({filename}) — {typ} · {date}" + (f" · {hook}" if hook else "")
    lines = []
    if os.path.exists(index):
        with open(index, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    if not lines:
        lines = ["# Source index",
                 "",
                 "One line per ingested source — read the linked file when it is",
                 "relevant to the task at hand. Maintained by the ingest-source skill.",
                 ""]
    pat = re.compile(r"\]\(" + re.escape(filename) + r"\)")
    for i, existing in enumerate(lines):
        if pat.search(existing):
            lines[i] = line
            break
    else:
        lines.append(line)
    with open(index, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    return index


def claude_md_block(rel_docs_dir):
    return (
        f"{MARKER_START}\n"
        "## Ingested sources\n"
        "\n"
        f"Captured source material (videos, articles, PDFs, images) lives in\n"
        f"`{rel_docs_dir}/`, ingested by the ingest-source skill. The index below\n"
        "is imported every session; read the underlying file when a listed source\n"
        "is relevant to the task at hand.\n"
        "\n"
        f"@{rel_docs_dir}/INDEX.md\n"
        f"{MARKER_END}\n"
    )


def claude_md_status(project_root, docs_dir):
    path = os.path.join(project_root, "CLAUDE.md")
    rel = os.path.relpath(os.path.abspath(docs_dir), os.path.abspath(project_root))
    block = claude_md_block(rel.replace(os.sep, "/"))
    if not os.path.exists(path):
        return {"path": path, "status": "no-file", "block": block}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            status = "present" if MARKER_START in fh.read() else "absent"
    except OSError:
        status = "absent"
    return {"path": path, "status": status, "block": block}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="URL or file path ingested")
    ap.add_argument("--type", required=True, choices=TYPES)
    ap.add_argument("--title", required=True)
    ap.add_argument("--tier", required=True,
                    help="how content was obtained, e.g. 'transcript (yt-dlp)'")
    ap.add_argument("--hook", default="", help="one-line INDEX.md hook")
    ap.add_argument("--file", help="summary markdown (default: stdin)")
    ap.add_argument("--out", help="explicit target path (overrides slug naming; "
                                  "outside --docs-dir the index is skipped)")
    ap.add_argument("--docs-dir", default="docs/sources")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--date", default=None, help="ISO date (default: today)")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    try:
        body = (open(args.file, encoding="utf-8").read() if args.file
                else sys.stdin.read())
    except OSError as e:
        print(f"  ⛔ cannot read summary: {e}", file=sys.stderr)
        sys.exit(1)
    if not body.strip():
        print("  ⛔ empty summary — nothing to persist", file=sys.stderr)
        sys.exit(1)

    date = args.date or datetime.date.today().isoformat()
    try:
        os.makedirs(args.docs_dir, exist_ok=True)
    except OSError as e:
        print(f"  ⛔ cannot create {args.docs_dir}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.out:
        path = args.out
        action = "updated" if os.path.exists(path) else "created"
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    else:
        slug = slugify(args.title, fallback=slugify(args.source))
        path, action = target_path(args.docs_dir, slug, args.source)
    title_q = args.title.replace('"', "'")
    doc = (f"---\n"
           f'source: "{args.source}"\n'
           f"type: {args.type}\n"
           f'title: "{title_q}"\n'
           f"ingested: {date}\n"
           f"tier: {args.tier}\n"
           f"---\n\n"
           f"{body.strip()}\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    in_docs_dir = (os.path.dirname(os.path.abspath(path))
                   == os.path.abspath(args.docs_dir))
    index = (upsert_index(args.docs_dir, os.path.basename(path), args.title,
                          args.type, date, args.hook)
             if in_docs_dir else None)
    cm = claude_md_status(args.project_root, args.docs_dir)

    print("ingest-source persist", file=sys.stderr)
    print(f"  ✅ {action}: {path}", file=sys.stderr)
    print(f"  {'✅ index:   ' + index if index else '⚠  index:   skipped (--out is outside --docs-dir)'}",
          file=sys.stderr)
    mark = {"present": "✅", "absent": "🔒", "no-file": "🔒"}[cm["status"]]
    print(f"  {mark} CLAUDE.md wiring: {cm['status']}", file=sys.stderr)

    print(json.dumps({"written": path, "action": action, "index": index,
                      "claude_md": cm}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
