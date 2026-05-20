---
name: render-html
description: Render a Markdown file (or piped Markdown) into a polished, self-contained HTML page styled in Anthropic's anthropic.com brand look — ivory background, clay accent, serif headings, grotesque-sans body, light/dark aware. Use when the user wants to turn a Markdown report, doc, spec, or notes file into a branded, shareable HTML page — "make an HTML version of this report", "turn this markdown into a styled web page", "brand this doc as HTML", "export X.md to HTML", "give me a nice HTML version of this", "render this as an Anthropic-styled page". Pairs with the HTML companions emitted by deep-research, generate-prd, and scan-trends when a single on-brand visual style is wanted. Pure local file transform: no network and no secrets at run time.
---

# render-html

Turn a Markdown file into one self-contained, on-brand HTML page.

## What it does

Converts Markdown (a file or stdin) into a single dependency-free HTML
document in the anthropic.com brand look. All CSS is inline; the only optional
external reference is a Google Fonts `<link>` for the heading/body substitute
fonts, which degrades to the system serif/sans stack offline. The Markdown
parser is stdlib-only — no `pip install`, no network. Bulk detail (the full
brand palette, font choices, licensing caveat) lives in
`references/brand-style.md`.

## How to run

Trigger with phrases like "make an HTML version of `report.md`", "brand this
doc as HTML", or `/render-html report.md`. With a file input and no `--out`,
`render.py` writes alongside it as `<input>.html` (e.g. `report.md` →
`report.html`); pass `--out` to override or `--stdout` to print instead.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9). No-op here — nothing prompts |
| `--out=PATH` | output HTML location; defaults to `<input>.html` (spec A9) |
| `--stdout` | print HTML to stdout even for a file input |
| `--title=STR` | document title (overrides first H1 / filename) |
| `--no-webfonts` | omit the Google Fonts link → fully offline, system fonts |

## Step 0 — Mode probe

Run `python3 --version`. If python3 is available, mode = **SCRIPTS** (use
`scripts/render.py`). If not, mode = **NATIVE**: read
`references/brand-style.md`, convert the Markdown to HTML yourself, and wrap it
in the documented brand shell. Announce the mode in one line.

## Steps (SCRIPTS mode)

1. **Preflight** — `python3 scripts/preflight.py --in=<input> --out=<dest>`.
   Read the JSON. `down` (e.g. `INPUT_MISSING`, `OUT_UNWRITABLE`) → stop and
   report the gate; otherwise proceed.
2. **Render** — `python3 scripts/render.py <input>` (it writes `<input>.html`;
   add `--out`/`--title`/`--no-webfonts` if requested). The script prints
   `wrote <path>`.
3. **Report** — give the user the output path. Note if web fonts are in use
   (online-only) versus `--no-webfonts` (fully offline).

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- Self-contained artifact records the source file + render date (spec A10).
- Keyless: no secrets, no `_env.py`, no network at run time.
