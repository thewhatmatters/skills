#!/usr/bin/env python3
"""Extract user-facing copy strings from project source with file:line (spec A4).

One concern: heuristic extraction so the review step has a concrete, citable
string inventory. It EXTRACTS; judging the copy is the model's job
(references/floor.md + references/voice-pass.md). Heuristics miss copy built
from variables/i18n indirection — SKILL.md tells the model to disclose that.

Sources handled:
    .tsx/.jsx/.html/.vue/.svelte — JSX/HTML text nodes + a whitelist of
        user-facing attributes (placeholder, title, alt, aria-label, label, …)
    .xcstrings — Apple String Catalogs (JSON; en value, else the key)
    .strings  — legacy Apple "key" = "value"; pairs

I/O:
    stdin  : —
    stdout : JSON {project, files_scanned, strings:[{file, line, kind, text}],
             counts_by_kind, truncated}
    stderr : progress diagnostics
    exit   : 0 always (no sources still yields valid JSON)

Caps at 500 strings / 2000 files, disclosed via `truncated` (no silent caps).
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

MARKUP_EXTS = {".tsx", ".jsx", ".html", ".vue", ".svelte"}
SKIP_DIRS = {"node_modules", ".next", ".git", "dist", "build", "out", ".turbo",
             "coverage", ".vercel", ".cache", "public", "Pods", "DerivedData"}
ATTR_WHITELIST = ("placeholder", "title", "alt", "aria-label", "label",
                  "description", "helperText", "errorMessage", "emptyMessage",
                  "tooltip", "confirmText", "cancelText")
ATTR_RE = re.compile(
    r"(?P<attr>" + "|".join(ATTR_WHITELIST) + r")\s*=\s*[\"'](?P<text>[^\"'{}<>]{2,200})[\"']")
TEXT_NODE_RE = re.compile(r">\s*(?P<text>[^<>{}]{2,200}?)\s*<")
STRINGS_RE = re.compile(r'^\s*"(?P<key>[^"]+)"\s*=\s*"(?P<text>[^"]*)"\s*;')
WORD_RE = re.compile(r"[A-Za-z]{2,}")
CODEY_RE = re.compile(r"=>|;\s*$|\bclassName\b|\bconst\b|\breturn\b|^[\d\s.,:%/-]+$")
STRINGS_MAX = 500
FILES_MAX = 2000


def looks_like_copy(text):
    return bool(WORD_RE.search(text)) and not CODEY_RE.search(text)


def guess_kind(line, attr=None):
    if attr == "placeholder":
        return "placeholder"
    if attr in ("aria-label", "label"):
        return "label"
    if attr == "alt":
        return "alt"
    if attr in ("errorMessage", "emptyMessage"):
        return "error/empty"
    if attr in ("title", "tooltip", "description", "helperText"):
        return "helper"
    low = line.lower()
    if "<button" in low or 'role="button"' in low or "<dialogaction" in low:
        return "button"
    if re.search(r"<h[1-6]\b", low):
        return "heading"
    if "toast" in low or "alert" in low or "error" in low:
        return "error/empty"
    return "text"


def extract_markup(path, rel, out):
    for i, line in enumerate(path.read_text("utf-8", errors="replace").splitlines(), 1):
        for m in ATTR_RE.finditer(line):
            text = m.group("text").strip()
            if looks_like_copy(text):
                out.append({"file": rel, "line": i,
                            "kind": guess_kind(line, m.group("attr")), "text": text})
        for m in TEXT_NODE_RE.finditer(line):
            text = m.group("text").strip()
            if looks_like_copy(text):
                out.append({"file": rel, "line": i, "kind": guess_kind(line),
                            "text": text})


def extract_xcstrings(path, rel, out):
    raw = path.read_text("utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except ValueError:
        print(f"unparseable xcstrings: {rel}", file=sys.stderr)
        return
    lines = raw.splitlines()

    def line_of(key):
        needle = json.dumps(key)
        return next((i for i, ln in enumerate(lines, 1) if needle in ln), 0)

    for key, entry in (data.get("strings") or {}).items():
        text = key
        loc = ((entry or {}).get("localizations") or {}).get("en") or {}
        unit = loc.get("stringUnit") or {}
        if unit.get("value"):
            text = unit["value"]
        if looks_like_copy(text):
            out.append({"file": rel, "line": line_of(key), "kind": "ios-string",
                        "text": text})


def extract_strings_file(path, rel, out):
    for i, line in enumerate(path.read_text("utf-8", errors="replace").splitlines(), 1):
        m = STRINGS_RE.match(line)
        if m and looks_like_copy(m.group("text")):
            out.append({"file": rel, "line": i, "kind": "ios-string",
                        "text": m.group("text")})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".", help="project root (default: cwd)")
    ap.add_argument("--path", action="append", default=[],
                    help="scope to these subpaths/globs (repeatable; default: whole project)")
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    root = Path(args.project).expanduser().resolve()
    if args.path:
        candidates = []
        for spec in args.path:
            candidates.extend(root.glob(spec) if any(c in spec for c in "*?[")
                              else [root / spec])
        files = []
        for c in candidates:
            files.extend(sorted(c.rglob("*")) if c.is_dir() else [c])
    else:
        # os.walk with pruning: skip SKIP_DIRS subtrees entirely instead of
        # materializing node_modules and filtering afterwards.
        files = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            files.extend(Path(dirpath) / f for f in filenames)
        files.sort()

    strings, scanned = [], 0
    for p in files:
        if scanned >= FILES_MAX:
            print(f"note: stopped after {FILES_MAX} files", file=sys.stderr)
            break
        if not p.is_file() or any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
        try:
            if p.suffix in MARKUP_EXTS:
                scanned += 1
                extract_markup(p, rel, strings)
            elif p.suffix == ".xcstrings":
                scanned += 1
                extract_xcstrings(p, rel, strings)
            elif p.suffix == ".strings":
                scanned += 1
                extract_strings_file(p, rel, strings)
        except OSError as e:
            print(f"unreadable {rel}: {e}", file=sys.stderr)

    truncated = len(strings) > STRINGS_MAX
    kept = strings[:STRINGS_MAX]
    out = {
        "project": str(root),
        "files_scanned": scanned,
        "strings": kept,
        "counts_by_kind": dict(Counter(s["kind"] for s in kept)),
        "truncated": truncated,
    }
    print(f"extracted {len(kept)} strings from {scanned} files"
          + (" (truncated to 500)" if truncated else ""), file=sys.stderr)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
