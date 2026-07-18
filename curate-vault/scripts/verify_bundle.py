#!/usr/bin/env python3
"""Verify OKF conformance + link integrity for the vault (read-only).

Checks the v0.1 conformance floor: (1) every non-reserved .md has a parseable
frontmatter block, (2) with a non-empty `type`, (3) the block parses as STRICT
YAML — Obsidian rejects invalid YAML (e.g. an unquoted value containing `: `)
and renders the whole block as body text, so lenient acceptance here hides
user-visible breakage. Strict parsing uses PyYAML when importable; otherwise a
narrow heuristic catches the known-fatal unquoted-`: ` pattern (disclosed on
stderr). Also resolves every bundle-absolute link (and relative links in index
files) outside fenced code blocks. Broken links are reported as `info` — OKF
tolerates them by design.
I/O: stdout JSON {conformant, errors, broken_links, stats} · stderr board ·
exit 1 only when conformance errors exist (broken links never fail the run).
"""
import argparse
import json
import os
import re
import sys

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

# plain (unquoted, non-block) scalar value that contains `: ` — invalid YAML
_COLON_SPACE = re.compile(r"^(\w[\w-]*):\s+(?![\"'|>#])(?=.*: ).*$", re.M)


def yaml_errors(fm, rel):
    """Strict-parse a frontmatter block; return conformance error strings."""
    if _yaml is not None:
        try:
            _yaml.safe_load(fm)
            return []
        except _yaml.YAMLError as e:
            detail = str(e).split("\n")[0]
            return [f"{rel}: frontmatter is not valid YAML ({detail}) — "
                    f"quote values containing `: `"]
    hits = [m.group(1) for m in _COLON_SPACE.finditer(fm)]
    return [f"{rel}: `{k}` value contains unquoted `: ` (invalid YAML) — "
            f"double-quote it" for k in hits]

DEFAULT_VAULT = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/OBSDN"
)
# Tool files (CLAUDE.md, HANDOFF.md) are a documented producer deviation:
# infrastructure with externally-defined formats, exempt from the frontmatter
# rule like reserved files. Their links are still checked. Compared
# case-insensitively — macOS's filesystem preserves whatever casing the file
# was first created with.
RESERVED = {"index.md", "log.md"}
TOOL_FILES = {"claude.md", "handoff.md"}


_HAZ = re.compile(r"(?<!\\)\$\$|(?<!\\)\$\S[^$\n]*\S\$|(?<!\\)<[a-zA-Z/][a-zA-Z0-9/-]*( [^>]*)?>")
_HAZ_OK = re.compile(r"^</?(br|hr|b|i|em|strong|sub|sup|code|pre|kbd|details|summary|img|a)( |/|>)", re.I)

# Human-confirmed false positives, keyed (vault-relative path, reported
# fragment) — path not line number, so entries survive edits elsewhere in the
# file. Known mode: an inline code span wrapping across lines defeats the
# per-line backtick stripping. Groomed 2026-07-18.
_HAZ_ALLOWLIST = {
    ("projects/prive/tm-app/net-new-scraper-playbook.md", "<slug>"),
    ("projects/prive/tm-app/net-new-scraper-playbook.md", "<PORT>"),
}


def render_hazards(text, rel):
    """Per-line candidate sweep for Obsidian render hazards in the body.

    Report-only: false positives are expected (multi-line code spans defeat
    any regex approach) — callers surface these for human review, never fail
    the run on them.
    """
    lines = text.splitlines()
    fm_end = 0
    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i] == "---":
                fm_end = i
                break
    out, in_fence = [], False
    for i, line in enumerate(lines[fm_end + 1:], fm_end + 2):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = re.sub(r"`[^`]*`", "", line)
        for m in _HAZ.finditer(stripped):
            frag = m.group(0)
            if frag.startswith("<") and _HAZ_OK.match(frag):
                continue
            if (rel, frag[:40]) in _HAZ_ALLOWLIST:
                continue
            out.append(f"{rel}:{i} {frag[:40]}")
    return out


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

    errors, broken, hazards, n_concepts, n_reserved = [], [], [], 0, 0

    for path in md_files(vault):
        rel = os.path.relpath(path, vault)
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            errors.append(f"{rel}: unreadable ({e})")
            continue

        if not rel.startswith("archive/"):
            hazards.extend(render_hazards(text, rel))

        base = os.path.basename(path)
        if base in RESERVED or base.lower() in TOOL_FILES:
            n_reserved += 1
        else:
            n_concepts += 1
            m = re.match(r"^---\n(.*?)\n---(\n|$)", text, re.S)
            if not m:
                errors.append(f"{rel}: no parseable frontmatter block")
            else:
                if not re.search(r"^type:\s*\S", m.group(1), re.M):
                    errors.append(f"{rel}: missing or empty `type`")
                errors.extend(yaml_errors(m.group(1), rel))

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
    if _yaml is None:
        print("strict YAML unavailable (no PyYAML) — heuristic check only",
              file=sys.stderr)
    print(f"concepts: {n_concepts}  reserved: {n_reserved}", file=sys.stderr)
    print(f"conformance errors: {len(errors)}", file=sys.stderr)
    for e in errors:
        print(f"  ⛔ {e}", file=sys.stderr)
    print(f"render hazards (info — human-review candidates): {len(hazards)}", file=sys.stderr)
    for h in hazards:
        print(f"  ⚠ {h}", file=sys.stderr)
    print(f"broken links (info — legal in OKF): {len(broken)}", file=sys.stderr)
    for b in broken:
        print(f"  ℹ {b}", file=sys.stderr)
    print(f"→ {'conformant' if conformant else 'NOT conformant'}", file=sys.stderr)

    print(json.dumps({
        "conformant": conformant,
        "errors": errors,
        "broken_links": broken,
        "render_hazards": hazards,
        "stats": {"concepts": n_concepts, "reserved": n_reserved},
    }, indent=2))
    sys.exit(0 if conformant else 1)


if __name__ == "__main__":
    main()
