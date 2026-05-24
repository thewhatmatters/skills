# render-html

**What it is:** Renders a Markdown file into one polished, self-contained HTML page styled in Anthropic's anthropic.com brand look.

## What you get

- A single `.html` file with all CSS inline — open it in any browser, attach it, or host it as-is.
- The anthropic.com aesthetic: ivory page, clay accent, serif headings, clean sans body, automatic light/dark mode.
- Semantic HTML with deep-linkable headings, an automatic jump-link table of contents for longer docs, collapsible `::: details` accordions, and `::: tabs` tab groups — all with **no JavaScript**, so it truly stands alone.

## How to run

Say something like "make an HTML version of `report.md`" or run `/render-html report.md`. By default the HTML lands next to the input as `report.html`. You can add a custom title (`--title="Q2 Review"`), print to stdout instead (`--stdout`), embed images into the file with `--inline-images`, force fully-offline output with `--no-webfonts`, or control the table of contents with `--toc` / `--no-toc`.

## What it needs

Nothing to set up. It uses only the Python standard library — no packages, no API keys, and no network at render time *unless* you pass `--inline-images` (which fetches remote images to embed them, and quietly keeps the remote link if a fetch fails). Markdown images render either way. (The output page also links to Google Fonts when viewed online; offline it falls back to system fonts — use `--no-webfonts` to drop that link. For a fully standalone file, combine `--no-webfonts --inline-images`.)

## How it works (high level)

1. You point it at a Markdown file (or pipe Markdown in).
2. A preflight check confirms the input is readable and the output location is writable.
3. A small stdlib parser converts the Markdown — headings, lists, tables, code, blockquotes, links — to HTML.
4. The HTML is wrapped in the brand stylesheet and written to one self-contained file.

A note on fonts: Anthropic's real brand fonts (Styrene, Tiempos) are licensed and cannot be bundled, so the page uses close free substitutes (Hanken Grotesk, Source Serif 4) with a system-font fallback. The look is a faithful approximation, not a pixel-exact copy.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `DESIGN.md` — the brand spec (color/typography tokens + font-licensing caveat) in the [DESIGN.md](https://github.com/google-labs-code/design.md) format.
- `references/rendering.md` — rendering behavior: the NATIVE-mode HTML shell, semantic structure / TOC / accordion syntax, and parser limitations.
