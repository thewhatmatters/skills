---
name: render-html
description: Render a Markdown file (or piped Markdown) into a polished, self-contained HTML page styled in Anthropic's anthropic.com brand look — ivory background, clay accent, serif headings, grotesque-sans body, light/dark aware. Use when the user wants to turn a Markdown report, doc, spec, or notes file into a branded, shareable HTML page — "make an HTML version of this report", "turn this markdown into a styled web page", "brand this doc as HTML", "export X.md to HTML", "give me a nice HTML version of this", "render this as an Anthropic-styled page". Pairs with the HTML companions emitted by deep-research, generate-prd, and scan-trends when a single on-brand visual style is wanted. Renders Markdown images too. Pure local file transform with no secrets and no network by default; an opt-in --inline-images flag fetches remote images to embed them as base64 (true offline self-containment).
---

# render-html

Turn a Markdown file into one self-contained, on-brand HTML page.

## What it does

Converts Markdown (a file or stdin) into a single dependency-free HTML
document in the anthropic.com brand look. All CSS is inline; the only optional
external reference is a Google Fonts `<link>` for the heading/body substitute
fonts, which degrades to the system serif/sans stack offline. The Markdown
parser is stdlib-only — no `pip install`, no network. The output uses
**semantic HTML** (`<header>`/`<nav>`/`<main>`/`<footer>`), gives every heading
a slug `id` (deep-linkable), and adds a jump-link **table of contents** for
longer docs — **no JavaScript**. A `::: details` container compiles to a native
`<details>`/`<summary>` **accordion**, and a `::: tabs` container (panels split
by `=== Label` lines) compiles to CSS-only **tabs**. The brand (palette, fonts, licensing) is
the DESIGN.md spec at [`DESIGN.md`](DESIGN.md); rendering behavior (NATIVE shell,
TOC/accordion syntax, markdown coverage) lives in
[`references/rendering.md`](references/rendering.md).

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
| `--toc` / `--no-toc` | force / suppress the table of contents (default: auto when ≥3 H2s) |
| `--inline-images` | embed images as base64 data-URIs — **opt-in network** for remote URLs; without it `![](url)` renders as a remote `<img>` (no network) |

## Step 0 — Mode probe

Run `python3 --version`. If python3 is available, mode = **SCRIPTS** (use
`scripts/render.py`). If not, mode = **NATIVE**: read the brand spec `DESIGN.md`
and the shell template in `references/rendering.md`, convert the Markdown to HTML
yourself, and wrap it in that documented shell. Announce the mode in one line.

## Steps (SCRIPTS mode)

1. **Preflight** — `python3 scripts/preflight.py --in=<input> --out=<dest>`.
   Read the JSON. `down` (e.g. `INPUT_MISSING`, `OUT_UNWRITABLE`) → stop and
   report the gate; otherwise proceed.
2. **Render** — `python3 scripts/render.py <input>` (it writes `<input>.html`;
   add `--out`/`--title`/`--no-webfonts`/`--inline-images` if requested). The
   script prints `wrote <path>`. Markdown images (`![alt](url)`) render as
   `<img>`; `--inline-images` fetches remote ones and embeds them as base64
   (and degrades to the remote reference on any fetch failure, logging a WARN).
3. **Report** — give the user the output path. Note the offline status: web
   fonts (online-only) vs `--no-webfonts`; remote `<img>` references (online-only)
   vs `--inline-images` (embedded). For a fully offline file, pass both
   `--no-webfonts --inline-images`.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- Self-contained artifact records the source file + render date (spec A10).
- Keyless: no secrets, no `_env.py`. No network by default; network only when
  `--inline-images` is passed, and it degrades gracefully if a fetch fails.
