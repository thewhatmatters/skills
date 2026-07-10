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

## Tabs (`::: tabs`)

A container directive compiles to **CSS-only radio tabs** (no JS). Panels are
split by `=== Label` lines; the first tab is open by default:

```
::: tabs
=== Mobbin
…markdown…
=== Refero
…markdown…
:::
```

Implementation: one hidden `<input type="radio">` per tab (same `name`, so they
are mutually exclusive), each followed by its `<label>` and a `<section
class="tab-panel">`. A `.tab-radio:checked + .tab-label + .tab-panel` rule shows
the active panel; flexbox `order` lifts the labels into a tab bar above the
panels. The radios stay in the DOM (1px, transparent) so the tab strip is
keyboard-navigable (arrow keys). Each `::: tabs` block gets a unique radio-group
name, so multiple tab sets on one page don't interfere.

**Single-level only:** a tab panel's markdown is parsed normally (headings flow
into the TOC, images/tables/lists all work), but do **not** nest another `:::`
block (tabs or details) inside a tab — the parser closes on the first bare
`:::` line. Lines before the first `=== ` are ignored; a block with no `=== `
markers falls back to plain rendering.

## Markdown coverage

Headings (`#`–`####`, each slug-id'd), paragraphs, **bold**, *italic*, `inline
code`, fenced code blocks, links, images (`![alt](url)` → `<img loading="lazy">`),
blockquotes, horizontal rules, unordered/ordered lists, GFM pipe tables (with
`:--`/`--:` alignment), `::: details` accordion containers, and `::: tabs`
containers. Title is taken
from `--title`, then YAML frontmatter `title:`, then the first H1, then the
filename.

### Images

`![alt](url)` becomes an `<img>` styled to fit the column. By default the `src`
is left as-is — a remote URL renders online with **no network at render time**.
Pass `--inline-images` to fetch remote images (and read local files) and embed
them as base64 data-URIs for a truly offline-self-contained file; this is the
*only* path that touches the network, it is opt-in, and any failed fetch
(timeout, SSL, 404, >10 MB) logs a WARN and falls back to the remote reference
so the page always renders. For a fully standalone file: `--no-webfonts
--inline-images`.

### Known limitations (recorded so they are not re-litigated)

- Lists are single-level (no nested list rendering).
- Raw-HTML is not passed through — non-image text is always escaped.
- Code spans inside link text render (e.g. ``[`name`](url)``), but **bold/italic
  inside link text** are not applied (link text is escaped, not re-parsed for
  emphasis).
