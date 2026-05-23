# Rendering behavior — render-html

Progressive-disclosure home (spec A1) for *how* `render-html` builds the
document. The **visual identity** (colors, typography, font licensing) lives in
the brand spec [`../DESIGN.md`](../DESIGN.md); this file covers structure,
navigation, accordions, and the Markdown the parser accepts.

## Document shell (NATIVE-mode template)

When python3 is unavailable, convert the Markdown by hand and wrap it in this
shell so the output matches the SCRIPTS path:

```
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escaped title}</title>
{Google Fonts link — omit if --no-webfonts}
<style>{the CSS from scripts/render.py}</style>
<header>
<h1 id="top">{escaped title}</h1>
<p class="doc-meta">Rendered {date} &middot; from {source}</p>
</header>
{table-of-contents <nav> — see below; omit for short docs}
<main>
{converted body HTML}
</main>
<footer class="doc-footer">Rendered by render-html.</footer>
</html>
```

The canonical CSS string and the fonts `<link>` live in `scripts/render.py`
(`CSS` and `FONTS_LINK`); the CSS values are the `DESIGN.md` tokens, hand-applied
(the script does not parse `DESIGN.md`). In NATIVE mode, copy `CSS`/`FONTS_LINK`
from the script verbatim — do not paraphrase the stylesheet.

## Semantic structure, anchors & TOC (no JavaScript)

- The doc is wrapped in `<header>` / `<nav class="doc-toc">` / `<main>` /
  `<footer>`; every heading gets a slug `id` (e.g. `## Stock outlook` →
  `id="stock-outlook"`, deduped with `-2`, `-3` on collision) so it's
  individually deep-linkable.
- A jump-link **table of contents** (`<nav class="doc-toc">`, listing H2 with
  nested H3) is emitted **under the title** for longer docs. Default: auto when
  the doc has **≥3 H2** sections; `--toc` forces it on, `--no-toc` off.
- CSS uses `scroll-behavior: smooth` + `scroll-margin-top`; all pure HTML/CSS —
  no script, so it works in any viewer and prints cleanly.

## Accordions (`::: details`)

A container directive compiles to a **native `<details>`/`<summary>`** (no JS):

```
::: details Optional summary text
…collapsible markdown (parsed normally)…
:::
```

Native `<details>` is chosen over a JS accordion deliberately: zero scripts,
built-in keyboard/screen-reader support, and it degrades/prints with the
content visible — which is what "stands alone" requires.

## Markdown coverage

Headings (`#`–`####`, each slug-id'd), paragraphs, **bold**, *italic*, `inline
code`, fenced code blocks, links, blockquotes, horizontal rules,
unordered/ordered lists, GFM pipe tables (with `:--`/`--:` alignment), and
`::: details` accordion containers. Title is taken from `--title`, then YAML
frontmatter `title:`, then the first H1, then the filename.

### Known limitations (recorded so they are not re-litigated)

- Lists are single-level (no nested list rendering).
- No image (`![]()`) or raw-HTML pass-through — text is always escaped.
- Code spans inside link text render (e.g. ``[`name`](url)``), but **bold/italic
  inside link text** are not applied (link text is escaped, not re-parsed for
  emphasis).
