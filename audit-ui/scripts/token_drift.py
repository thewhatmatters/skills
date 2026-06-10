#!/usr/bin/env python3
"""Scan project source for color/font literals that drift from DESIGN.md (spec A4).

One concern: extract the allowed token set from DESIGN.md and report source
literals outside it, with file:line. Judging which drift matters is the
model's job (references/token-drift.md).

DESIGN.md flavors handled (both reduce to "the set of declared values"):
  - google-labs design.md — YAML frontmatter; colors/fonts pulled by regex
    (stdlib only — no YAML parser)
  - Stitch natural-language — hex codes + font names anywhere in the body

No DESIGN.md → "no-spec" mode: nothing to diff against, so report the
most-repeated hard-coded colors/fonts as an internal-consistency signal
instead, and let SKILL.md point the user at the design-md skill.

I/O:
    stdin  : —
    stdout : JSON {mode: "spec"|"no-spec", design_md, allowed:{colors,fonts},
             findings:[{file, line, kind: "color"|"font", value, context}],
             top_values (no-spec mode), counts, truncated}
    stderr : progress diagnostics
    exit   : 0 always (an empty project yields valid JSON)

Caps findings at 200 (disclosed via `truncated` — no silent caps).
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

SCAN_EXTS = {".tsx", ".ts", ".jsx", ".js", ".css", ".scss", ".html", ".vue", ".svelte"}
SKIP_DIRS = {"node_modules", ".next", ".git", "dist", "build", "out", ".turbo",
             "coverage", ".vercel", "public", ".cache"}
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
OKLCH_RE = re.compile(r"oklch\([^)]*\)")
FONT_DECL_RE = re.compile(r"""(?:font-family\s*:|fontFamily\s*:)\s*["']?([^;"'\n}]+)""")
GENERIC_FONTS = {"serif", "sans-serif", "monospace", "system-ui", "ui-sans-serif",
                 "ui-serif", "ui-monospace", "cursive", "fantasy", "inherit",
                 "initial", "unset", "var"}
FINDINGS_MAX = 200
FILES_MAX = 2000


def norm_hex(h):
    h = h.lower()
    if len(h) == 4:                      # #abc -> #aabbcc
        h = "#" + "".join(c * 2 for c in h[1:])
    if len(h) == 5:                      # #abcd -> #aabbccdd
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def norm_oklch(s):
    return re.sub(r"\s+", " ", s.lower().strip())


def find_design_md(project, explicit):
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.is_file() else None
    for cand in ("DESIGN.md", "design.md"):
        p = Path(project).expanduser() / cand
        if p.is_file():
            return p
    return None


def parse_design(path):
    """Extract allowed colors + font names from either DESIGN.md flavor."""
    text = path.read_text("utf-8", errors="replace")
    colors = {norm_hex(m) for m in HEX_RE.findall(text)}
    colors |= {norm_oklch(m) for m in OKLCH_RE.findall(text)}
    fonts = set()
    for m in re.finditer(r"fontFamily\s*:\s*[\"']?([^\"',\n}]+)", text):
        fonts.add(m.group(1).strip().strip('"').strip("'").lower())
    # Stitch flavor: quoted Capitalized names near typography talk; cheap pass —
    # any quoted multi-letter token in a line that mentions font
    for line in text.splitlines():
        if re.search(r"font", line, re.IGNORECASE):
            for q in re.findall(r"[\"']([A-Z][A-Za-z ]{2,30})[\"']", line):
                fonts.add(q.lower())
    return colors, fonts


def first_font(decl):
    return decl.split(",")[0].strip().strip('"').strip("'").lower()


def iter_source_files(project):
    n = 0
    for p in sorted(Path(project).expanduser().rglob("*")):
        if n >= FILES_MAX:
            print(f"note: stopped after {FILES_MAX} files", file=sys.stderr)
            return
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix in SCAN_EXTS and p.is_file():
            n += 1
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".", help="project root (default: cwd)")
    ap.add_argument("--design", help="explicit DESIGN.md path (default: <project>/DESIGN.md)")
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    project = Path(args.project).expanduser()
    design = find_design_md(project, args.design)
    allowed_colors, allowed_fonts = (parse_design(design) if design else (set(), set()))
    mode = "spec" if design else "no-spec"
    print(f"token drift @ {project} — mode={mode}"
          + (f", spec={design} ({len(allowed_colors)} colors, "
             f"{len(allowed_fonts)} fonts)" if design else ""),
          file=sys.stderr)

    findings, seen_values = [], Counter()
    for path in iter_source_files(project):
        try:
            lines = path.read_text("utf-8", errors="replace").splitlines()
        except OSError:
            continue
        rel = str(path.relative_to(project))
        for i, line in enumerate(lines, 1):
            for m in HEX_RE.findall(line):
                v = norm_hex(m)
                seen_values[("color", v)] += 1
                if mode == "spec" and v not in allowed_colors:
                    findings.append({"file": rel, "line": i, "kind": "color",
                                     "value": v, "context": line.strip()[:120]})
            for m in OKLCH_RE.findall(line):
                v = norm_oklch(m)
                seen_values[("color", v)] += 1
                if mode == "spec" and v not in allowed_colors:
                    findings.append({"file": rel, "line": i, "kind": "color",
                                     "value": v, "context": line.strip()[:120]})
            for decl in FONT_DECL_RE.findall(line):
                f = first_font(decl)
                if not f or f in GENERIC_FONTS or f.startswith("var("):
                    continue
                seen_values[("font", f)] += 1
                if mode == "spec" and f not in allowed_fonts:
                    findings.append({"file": rel, "line": i, "kind": "font",
                                     "value": f, "context": line.strip()[:120]})

    truncated = len(findings) > FINDINGS_MAX
    out = {
        "mode": mode,
        "design_md": str(design) if design else None,
        "allowed": {"colors": sorted(allowed_colors), "fonts": sorted(allowed_fonts)},
        "findings": findings[:FINDINGS_MAX],
        "counts": {"total": len(findings),
                   "colors": sum(1 for f in findings if f["kind"] == "color"),
                   "fonts": sum(1 for f in findings if f["kind"] == "font")},
        "truncated": truncated,
        "top_values": [{"kind": k, "value": v, "uses": c}
                       for (k, v), c in seen_values.most_common(15)] if mode == "no-spec" else [],
    }
    print(f"findings: {out['counts']}" + (" (truncated to 200)" if truncated else ""),
          file=sys.stderr)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
