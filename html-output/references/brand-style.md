# Brand style — the anthropic.com look

This is the progressive-disclosure home (spec A1) for the visual system that
`scripts/render.py` emits. It is also the **NATIVE-mode contract**: when
python3 is unavailable, convert the Markdown to HTML by hand and wrap it in the
shell described here so the output matches the SCRIPTS path.

## The look, in one paragraph

Warm ivory/kraft page, near-black slate text, a single clay/terracotta accent
for links and rules, serif display headings over a clean grotesque-sans body,
generous line-height, a narrow reading column. Editorial and calm — the
anthropic.com reading aesthetic, not a dashboard.

## Color tokens

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `--bg` | `#F0EEE6` | `#1F1E1B` | page background (ivory / warm dark) |
| `--surface` | `#F7F6F2` | `#26241F` | table header / raised fills |
| `--fg` | `#191917` | `#EDEAE0` | body text |
| `--muted` | `#6B6A63` | `#A7A498` | meta, captions, footer |
| `--accent` | `#CC785C` | `#E0937A` | Crail/clay — rules, blockquote bar |
| `--accent-ink` | `#B0613F` | `#E0937A` | link text (darker for contrast on ivory) |
| `--line` | `#DEDBD0` | `#3A372F` | hairline borders |
| `--code-bg` | `#E7E4D8` | `#2A2823` | code background |

Light/dark switch is driven by `@media (prefers-color-scheme: dark)` plus
`color-scheme: light dark`.

## Typography

- **Headings:** `"Tiempos Headline"` → `"Source Serif 4"` → `Georgia` →
  `serif`.
- **Body:** `"Styrene B"` → `"Hanken Grotesk"` → `ui-sans-serif, system-ui,
  -apple-system, "Segoe UI", Helvetica, Arial, sans-serif`.
- **Code:** `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace`.
- Body 17px / line-height 1.65; reading column `max-width: 720px`.

### Font licensing (important, non-negotiable)

Anthropic's real brand fonts — **Styrene** (grotesque sans) and **Tiempos**
(serif) — are **licensed/proprietary** and are **not** bundled or embedded.
The stacks above name them *first* so they render for anyone who already has
them installed, then fall back to close **free** substitutes served from Google
Fonts (Source Serif 4 ≈ Tiempos; Hanken Grotesk ≈ Styrene), then to the system
serif/sans stack when offline or when `--no-webfonts` is passed. The result
approximates the brand; it is not pixel-identical, by design and by license.

The Google Fonts `<link>` is the *only* external reference in the output. It
loads at view time, not render time — `render.py` itself never touches the
network. Use `--no-webfonts` for a fully offline file.

## Document shell (NATIVE-mode template)

```
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escaped title}</title>
{Google Fonts link — omit if --no-webfonts}
<style>{the CSS below}</style>
<h1>{escaped title}</h1>
<p class="doc-meta">Rendered {date} &middot; from {source}</p>
{converted body HTML}
<div class="doc-footer">Rendered by html-output.</div>
```

The canonical CSS string and the fonts `<link>` live in `scripts/render.py`
(`CSS` and `FONTS_LINK`). In NATIVE mode, copy them from there verbatim so the
two paths stay identical — do not paraphrase the stylesheet.

## Markdown coverage

Headings (`#`–`####`), paragraphs, **bold**, *italic*, `inline code`, fenced
code blocks, links, blockquotes, horizontal rules, unordered/ordered lists, and
GFM pipe tables (with `:--`/`--:` alignment). Title is taken from `--title`,
then YAML frontmatter `title:`, then the first H1, then the filename.

### Known limitations (recorded so they are not re-litigated)

- Lists are single-level (no nested list rendering).
- No image (`![]()`) or raw-HTML pass-through — text is always escaped.
- Emphasis inside link text is not rendered (link text is escaped literally).

These cover the constructs the repo's own Markdown reports use; extend
`render.py` if a source needs more.
