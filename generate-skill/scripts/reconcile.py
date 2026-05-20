#!/usr/bin/env python3
"""Report drift between Anthropic's *live* skill-authoring docs and our spec.

One concern: detect when the SKILL.md contract has changed upstream since we
last aligned `skill-architecture.md` to it — and surface it. NEVER edit the
spec; the human decides whether to update it. Same Recoverable-Setup-Gate
philosophy as the rest of the family (flag, don't silently degrade or rewrite).

USAGE
    python3 scripts/reconcile.py [--agent]

I/O CONTRACT
    stdout : a single JSON object — see KEYS below
    stderr : human-readable summary (one line per finding)
    exit   : 0 always when the report could be produced (drift is INFORMATIONAL,
             not a failure); 1 only if no docs are available at all to compare.

WHAT IS COMPARED
    "live"     = the most recent fetched copy in .cache/docs/ (what docs.py
                 left behind). If absent, falls back to the committed snapshot
                 (no drift can exist in that case).
    "baseline" = the committed `references/claude-docs-snapshot/` — the docs
                 as of the last time we audited `skill-architecture.md` against
                 upstream.

    Drift is computed on two axes:
      1. Frontmatter field set in `skills.md` (the structural contract).
      2. Changelog entries mentioning "skill" between baseline and live
         versions (the upstream signal that something skill-relevant moved).

JSON KEYS
    status                    aligned | drift | no-live | no-baseline
    live_version              CC version parsed from live changelog (str|null)
    baseline_version          CC version parsed from snapshot changelog
    frontmatter:
      live_fields             [str, ...]  sorted
      baseline_fields         [str, ...]  sorted
      added                   [str, ...]  in live, not in baseline
      removed                 [str, ...]  in baseline, not in live
    changelog_skill_mentions  [str, ...]  matching lines between versions
    notes                     [str, ...]  human-relevant remarks
"""

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import docs  # noqa: E402 - sibling module

# Match the first column of the frontmatter table in skills.md:
#   |  `name`                     |  No  | ...
# i.e. a leading "|" then optional space then a backtick-quoted identifier.
_FIELD_ROW = re.compile(r"^\s*\|\s*`([a-z][a-z0-9_-]*)`\s*\|")

# Changelog version headings look like "## 2.1.144" possibly followed by a date.
_VERSION_HEAD = re.compile(r"^##\s+(\d+\.\d+\.\d+)\b")


def log(msg):
    print(msg, file=sys.stderr)


def parse_frontmatter_fields(skills_md_text):
    """Extract the set of frontmatter fields documented in skills.md.

    Tolerant: if the table format moves, this may under-extract — caller treats
    an empty result as a parse-failure signal.
    """
    fields = []
    in_section = False
    for line in skills_md_text.splitlines():
        if not in_section:
            if re.match(r"^#{1,4}\s+Frontmatter\b", line, re.IGNORECASE):
                in_section = True
            continue
        # stop on the next heading of equal/higher level after the section
        if re.match(r"^#{1,4}\s+\w", line) and not line.strip().startswith("####"):
            if not re.match(r"^#{1,4}\s+Frontmatter\b", line, re.IGNORECASE):
                break
        m = _FIELD_ROW.match(line)
        if m:
            fields.append(m.group(1))
    return sorted(set(fields))


def changelog_skill_lines_between(changelog_text, baseline_ver, live_ver):
    """Return lines mentioning 'skill' in entries newer than baseline_ver.

    Heuristic: scan top-down. Once we hit `## <live_ver>` we're inside the
    range until we hit `## <baseline_ver>` (exclusive). Within that window,
    pick lines that mention skill word-boundary, case-insensitive.
    Returns [] if either version not found in the changelog headings.
    """
    if not baseline_ver or not live_ver or baseline_ver == live_ver:
        return []
    inside = False
    saw_live = False
    out = []
    for line in changelog_text.splitlines():
        m = _VERSION_HEAD.match(line)
        if m:
            ver = m.group(1)
            if ver == live_ver:
                inside = True
                saw_live = True
                continue
            if ver == baseline_ver:
                inside = False
                break
            continue
        if inside and re.search(r"\bskills?\b", line, re.IGNORECASE):
            stripped = line.strip()
            if stripped:
                out.append(stripped)
    if not saw_live:
        return []  # live version not present in this changelog — punt
    return out


def emit(payload, exit_code):
    print(json.dumps(payload, indent=2))
    sys.exit(exit_code)


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--agent", action="store_true")
    ap.parse_args()

    notes = []

    baseline_docs = docs.read_dir(docs.SNAPSHOT_DIR)
    live_docs = docs.read_dir(docs.CACHE_DIR)

    if not baseline_docs:
        log("FATAL: snapshot missing — cannot establish baseline")
        emit({
            "status": "no-baseline", "live_version": None,
            "baseline_version": None,
            "frontmatter": {"live_fields": [], "baseline_fields": [],
                            "added": [], "removed": []},
            "changelog_skill_mentions": [],
            "notes": ["committed snapshot missing — re-add "
                      "references/claude-docs-snapshot/"],
        }, 1)

    baseline_ver = docs.parse_version(baseline_docs.get("changelog.md", ""))
    baseline_fields = parse_frontmatter_fields(baseline_docs["skills.md"])

    if not live_docs:
        log("no live cache — comparing snapshot to itself is a no-op")
        emit({
            "status": "no-live", "live_version": baseline_ver,
            "baseline_version": baseline_ver,
            "frontmatter": {
                "live_fields": baseline_fields,
                "baseline_fields": baseline_fields,
                "added": [], "removed": [],
            },
            "changelog_skill_mentions": [],
            "notes": ["no .cache/docs/ — run scripts/docs.py first to compare "
                      "current upstream against snapshot"],
        }, 0)

    live_ver = docs.parse_version(live_docs.get("changelog.md", ""))
    live_fields = parse_frontmatter_fields(live_docs["skills.md"])

    if not baseline_fields or not live_fields:
        notes.append("frontmatter table parse returned empty — skills.md "
                     "format may have moved; treat field diff as unreliable")

    added = sorted(set(live_fields) - set(baseline_fields))
    removed = sorted(set(baseline_fields) - set(live_fields))
    skill_lines = changelog_skill_lines_between(
        live_docs.get("changelog.md", ""), baseline_ver, live_ver
    )

    drifted = bool(added or removed or skill_lines)
    status = "drift" if drifted else "aligned"

    log(f"baseline CC = {baseline_ver}  ({len(baseline_fields)} fields)")
    log(f"live     CC = {live_ver}  ({len(live_fields)} fields)")
    if added:
        log(f"  + added fields:   {', '.join(added)}")
    if removed:
        log(f"  − removed fields: {', '.join(removed)}")
    if skill_lines:
        log(f"  ! {len(skill_lines)} skill-mentioning changelog line(s) "
            "between baseline and live versions")
    if not drifted:
        log("→ aligned: spec matches upstream")
    else:
        log("→ DRIFT: review skill-architecture.md against the changes above; "
            "this script will NEVER edit the spec for you")

    emit({
        "status": status,
        "live_version": live_ver,
        "baseline_version": baseline_ver,
        "frontmatter": {
            "live_fields": live_fields,
            "baseline_fields": baseline_fields,
            "added": added,
            "removed": removed,
        },
        "changelog_skill_mentions": skill_lines,
        "notes": notes,
    }, 0)


if __name__ == "__main__":
    main()
