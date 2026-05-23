#!/usr/bin/env python3
"""Render a Markdown document to one self-contained, on-brand HTML file (spec A10).

One concern: convert Markdown (a file or stdin) into a single dependency-free
HTML document styled in the anthropic.com brand look — ivory background, clay
accent, serif headings, grotesque-sans body, light/dark aware. The Markdown
parser is a small stdlib-only converter (no pip install, no network at run time).

USAGE
    python3 scripts/render.py [INPUT.md] [--out=PATH] [--title=STR]
        [--no-webfonts] [--toc | --no-toc] [--stdout]

    INPUT.md       path to a Markdown file; if omitted, Markdown is read from stdin
    --out=PATH     write the HTML to PATH and print "wrote PATH"; otherwise HTML
                   is written to stdout (default for a file input: <input>.html)
    --stdout       write HTML to stdout even for a file input
    --title=STR    document title (overrides the first H1 / the filename)
    --no-webfonts  omit the Google Fonts <link> so the file is fully offline
    --toc          force a table-of-contents nav (default: auto when ≥3 H2s)
    --no-toc       suppress the table-of-contents

SEMANTIC HTML / NAVIGATION (so the .html stands alone)
    Output uses <header>/<nav>/<main>/<footer>; every heading gets a slug id so
    it's individually deep-linkable; a jump-link table of contents (H2 + nested
    H3) appears under the title for longer docs. Pure HTML/CSS — no JavaScript.

ACCORDIONS
    A container directive compiles to a native <details>/<summary> (no JS):
        ::: details Optional summary
        …collapsible markdown…
        :::

FONTS / LICENSING
    Anthropic's real brand fonts (Styrene, Tiempos) are licensed and are NOT
    bundled. The CSS names them first, then falls back to free Google-Fonts
    substitutes, then to the system serif/sans stack (offline / --no-webfonts).
    Brand tokens + licensing live in DESIGN.md; behavior in references/rendering.md.

ESCAPING
    All text is HTML-escaped inside the inline pass; inline code spans and link
    targets are stashed before escaping and restored after. Only markup this
    script itself emits is ever unescaped.
"""

import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path

# --- Brand stylesheet -------------------------------------------------------
# Plain string: never fed to .format()/f-strings, so literal { } need no
# escaping. The full rationale + tokens live in DESIGN.md (the brand spec).
CSS = """
:root {
  color-scheme: light dark;
  --bg: #F0EEE6; --surface: #F7F6F2; --fg: #191917; --muted: #6B6A63;
  --accent: #CC785C; --accent-ink: #B0613F; --line: #DEDBD0; --code-bg: #E7E4D8;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1F1E1B; --surface: #26241F; --fg: #EDEAE0; --muted: #A7A498;
    --accent: #E0937A; --accent-ink: #E0937A; --line: #3A372F; --code-bg: #2A2823;
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
html, body { background: var(--bg); color: var(--fg); }
body {
  font-family: "Styrene B", "Hanken Grotesk", ui-sans-serif, system-ui,
    -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 17px; line-height: 1.65; max-width: 720px;
  margin: 0 auto; padding: 4rem 1.25rem 6rem; -webkit-font-smoothing: antialiased;
}
h1, h2, h3, h4 {
  font-family: "Tiempos Headline", "Source Serif 4", Georgia,
    "Times New Roman", serif;
  font-weight: 600; line-height: 1.2; color: var(--fg); scroll-margin-top: 1.25rem;
}
h1 { font-size: 2.4rem; margin: 0 0 1.5rem; letter-spacing: -0.01em; }
h2 { font-size: 1.6rem; margin: 2.75rem 0 0.75rem; }
h3 { font-size: 1.25rem; margin: 2rem 0 0.5rem; }
h4 { font-size: 1.05rem; margin: 1.5rem 0 0.4rem; color: var(--muted); }
p { margin: 0 0 1.1rem; }
a { color: var(--accent-ink); text-underline-offset: 2px; }
a:hover { text-decoration: none; }
strong { font-weight: 600; }
em { font-style: italic; }
hr { border: none; border-top: 1px solid var(--line); margin: 2.5rem 0; }
ul, ol { margin: 0 0 1.1rem; padding-left: 1.4rem; }
li { margin: 0.3rem 0; }
blockquote {
  margin: 1.5rem 0; padding: 0.4rem 0 0.4rem 1.1rem;
  border-left: 3px solid var(--accent); color: var(--muted);
}
blockquote p:last-child { margin-bottom: 0; }
code {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  font-size: 0.88em; background: var(--code-bg); padding: 0.1em 0.35em;
  border-radius: 4px;
}
pre {
  background: var(--code-bg); border: 1px solid var(--line); border-radius: 8px;
  padding: 1rem 1.1rem; overflow-x: auto; margin: 0 0 1.3rem;
}
pre code { background: none; padding: 0; font-size: 0.85rem; line-height: 1.5; }
table {
  border-collapse: collapse; width: 100%; margin: 0 0 1.3rem; font-size: 0.95rem;
}
th, td {
  border: 1px solid var(--line); padding: 0.5rem 0.7rem; text-align: left;
  vertical-align: top;
}
th { background: var(--surface); font-weight: 600; }
.doc-meta { color: var(--muted); font-size: 0.9rem; margin: 0 0 2.5rem; }
.doc-toc {
  margin: 0 0 2.75rem; padding: 0.9rem 1.1rem; background: var(--surface);
  border: 1px solid var(--line); border-radius: 8px; font-size: 0.95rem;
}
.doc-toc-title {
  font-weight: 600; color: var(--muted); font-size: 0.78rem;
  text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 0.5rem;
}
.doc-toc ul { margin: 0; padding-left: 1.1rem; list-style: none; }
.doc-toc > ul { padding-left: 0; }
.doc-toc li { margin: 0.2rem 0; }
.doc-toc a { color: var(--fg); text-decoration: none; }
.doc-toc a:hover { color: var(--accent-ink); text-decoration: underline; }
details {
  margin: 0 0 1.1rem; border: 1px solid var(--line); border-radius: 8px;
  background: var(--surface); padding: 0 1.1rem;
}
details[open] { padding-bottom: 0.4rem; }
summary {
  cursor: pointer; padding: 0.7rem 0; font-weight: 600; color: var(--fg);
  list-style: none;
}
summary::-webkit-details-marker { display: none; }
summary::before {
  content: "\\25B8"; color: var(--accent); margin-right: 0.5rem;
  display: inline-block; transition: transform 0.15s;
}
details[open] > summary::before { transform: rotate(90deg); }
main > :first-child { margin-top: 0; }
.doc-footer {
  margin-top: 4rem; padding-top: 1rem; border-top: 1px solid var(--line);
  color: var(--muted); font-size: 0.85rem;
}
.doc-footer a { color: var(--muted); }
"""

FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    "family=Hanken+Grotesk:wght@400;500;600&"
    "family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap\">"
)


def log(msg):
    print(msg, file=sys.stderr)


# --- Inline (span-level) markdown ------------------------------------------
def inline(s):
    """Render inline markdown to safe HTML.

    Code spans and links are stashed as NUL-delimited tokens *before* escaping
    so their contents are never re-parsed for emphasis and their tags survive
    html.escape(); they are restored last (iteratively, to resolve a code span
    nested inside link text).
    """
    tokens = []

    def stash(frag):
        tokens.append(frag)
        return f"\x00{len(tokens) - 1}\x00"

    s = re.sub(r"`([^`]+)`",
               lambda m: stash(f"<code>{html.escape(m.group(1))}</code>"), s)
    s = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: stash(
            f'<a href="{html.escape(m.group(2), quote=True)}" '
            f'rel="noopener">{html.escape(m.group(1))}</a>'),
        s,
    )
    s = html.escape(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"(?<!_)_([^_\s][^_]*?)_(?!_)", r"<em>\1</em>", s)
    for _ in range(len(tokens) + 1):
        new = re.sub(r"\x00(\d+)\x00", lambda m: tokens[int(m.group(1))], s)
        if new == s:
            break
        s = new
    return s


# --- Block-level markdown ---------------------------------------------------
_HR = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_QUOTE = re.compile(r"^\s*>")
_UL = re.compile(r"^\s*[-*+]\s+(.*)$")
_OL = re.compile(r"^\s*\d+\.\s+(.*)$")
_FENCE = re.compile(r"^\s*```")
_DETAILS = re.compile(r"^:::\s*details\b(.*)$")


def _is_block_start(line):
    return bool(
        _FENCE.match(line) or _HR.match(line) or _HEADING.match(line)
        or _QUOTE.match(line) or _UL.match(line) or _OL.match(line)
        or _is_table_header(line) or line.lstrip().startswith(":::")
    )


def _is_table_header(line):
    return "|" in line


def _table_delim(line):
    return bool(re.match(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$",
                         line)) and "-" in line


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def _aligns(delim_cells):
    out = []
    for c in delim_cells:
        c = c.strip()
        left, right = c.startswith(":"), c.endswith(":")
        if left and right:
            out.append("center")
        elif right:
            out.append("right")
        else:
            out.append("")
    return out


# --- Headings / TOC ---------------------------------------------------------
def _plain(text):
    """Strip inline markdown for slugs and TOC labels."""
    t = re.sub(r"`([^`]+)`", r"\1", text)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*_]+", "", t)
    return t.strip()


def _slugify(text):
    t = re.sub(r"[^a-z0-9\s-]", "", _plain(text).lower())
    t = re.sub(r"\s+", "-", t).strip("-")
    return t or "section"


def make_slugger():
    """Return a function assigning unique slugs (deduped with -2, -3, …)."""
    seen = {}

    def slug(text):
        base = _slugify(text)
        if base in seen:
            seen[base] += 1
            return f"{base}-{seen[base]}"
        seen[base] = 1
        return base
    return slug


def build_toc(headings):
    """Build a <nav> jump list from collected (level, text, slug) — H2 + H3."""
    items = [h for h in headings if h[0] in (2, 3)]
    if not items:
        return ""
    parts = ['<nav class="doc-toc" aria-label="Contents">',
             '<p class="doc-toc-title">Contents</p>', "<ul>"]
    open_sub = started = False
    for lvl, text, slug in items:
        label = html.escape(_plain(text))
        if lvl == 2:
            if open_sub:
                parts.append("</ul></li>")
                open_sub = False
            elif started:
                parts.append("</li>")
            parts.append(f'<li><a href="#{slug}">{label}</a>')
            started = True
        else:  # h3
            if not started:
                parts.append(f'<li><a href="#{slug}">{label}</a></li>')
                continue
            if not open_sub:
                parts.append("<ul>")
                open_sub = True
            parts.append(f'<li><a href="#{slug}">{label}</a></li>')
    parts.append("</ul></li>" if open_sub else ("</li>" if started else ""))
    parts.append("</ul></nav>")
    return "".join(parts)


def md_to_html(text, slugger=None, headings=None):
    """Convert Markdown to HTML. Recursive for blockquotes and ::: details.

    `slugger` + `headings` are shared across the whole document (incl. nested
    blocks) so heading ids stay unique and the TOC reflects every heading.
    """
    if slugger is None:
        slugger = make_slugger()
    if headings is None:
        headings = []
    lines = text.split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]

        if _FENCE.match(line):
            i += 1
            buf = []
            while i < n and not _FENCE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            out.append(f"<pre><code>{html.escape(chr(10).join(buf))}</code></pre>")
            continue

        if _HR.match(line):
            out.append("<hr>")
            i += 1
            continue

        m = _HEADING.match(line)
        if m:
            lvl = min(len(m.group(1)), 4)
            htext = m.group(2).strip()
            slug = slugger(htext)
            headings.append((lvl, htext, slug))
            out.append(f'<h{lvl} id="{slug}">{inline(htext)}</h{lvl}>')
            i += 1
            continue

        dm = _DETAILS.match(line)
        if dm:
            summary = dm.group(1).strip()
            i += 1
            buf = []
            while i < n and lines[i].strip() != ":::":
                buf.append(lines[i])
                i += 1
            i += 1  # closing :::
            inner = md_to_html(chr(10).join(buf), slugger, headings)
            sm = inline(summary) if summary else "Details"
            out.append(f"<details><summary>{sm}</summary>{inner}</details>")
            continue

        if _QUOTE.match(line):
            buf = []
            while i < n and _QUOTE.match(lines[i]):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>"
                       + md_to_html(chr(10).join(buf), slugger, headings)
                       + "</blockquote>")
            continue

        # GFM pipe table: header row + delimiter row
        if (_is_table_header(line) and i + 1 < n and _table_delim(lines[i + 1])):
            header = _split_row(line)
            aligns = _aligns(_split_row(lines[i + 1]))
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1

            def cell(tag, val, idx):
                a = aligns[idx] if idx < len(aligns) else ""
                style = f' style="text-align:{a}"' if a else ""
                return f"<{tag}{style}>{inline(val)}</{tag}>"

            thead = "".join(cell("th", h, j) for j, h in enumerate(header))
            tbody = "".join(
                "<tr>" + "".join(cell("td", c, j) for j, c in enumerate(r))
                + "</tr>"
                for r in rows
            )
            out.append(
                f"<table><thead><tr>{thead}</tr></thead>"
                f"<tbody>{tbody}</tbody></table>"
            )
            continue

        if _UL.match(line):
            items = []
            while i < n and _UL.match(lines[i]):
                items.append(inline(_UL.match(lines[i]).group(1).strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
            continue

        if _OL.match(line):
            items = []
            while i < n and _OL.match(lines[i]):
                items.append(inline(_OL.match(lines[i]).group(1).strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{it}</li>" for it in items) + "</ol>")
            continue

        if line.strip() == "":
            i += 1
            continue

        # paragraph: gather until a blank line or the start of another block
        para = [line]
        i += 1
        while i < n and lines[i].strip() != "" and not _is_block_start(lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>" + inline(" ".join(p.strip() for p in para)) + "</p>")

    return "\n".join(out)


# --- Document assembly ------------------------------------------------------
def strip_frontmatter(text):
    """Drop a leading YAML frontmatter block; return (title_or_None, body)."""
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not m:
        return None, text
    title = None
    tm = re.search(r"^title:\s*(.+)$", m.group(1), re.MULTILINE)
    if tm:
        title = tm.group(1).strip().strip("\"'")
    return title, text[m.end():]


def extract_h1(text):
    """If the body's first non-empty line is an H1, return (title, rest)."""
    lines = text.split("\n")
    j = 0
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if j < len(lines):
        m = re.match(r"^#\s+(.*)$", lines[j])
        if m:
            return m.group(1).strip(), "\n".join(lines[:j] + lines[j + 1:])
    return None, text


def build_document(title, body_html, meta_line, footer_line, webfonts, toc_html=""):
    fonts = (FONTS_LINK + "\n") if webfonts else ""
    toc = (toc_html + "\n") if toc_html else ""
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{title}</title>\n"
        f"{fonts}"
        f"<style>{CSS}</style>\n"
        "<header>\n"
        f'<h1 id="top">{title}</h1>\n'
        f'<p class="doc-meta">{meta_line}</p>\n'
        "</header>\n"
        f"{toc}"
        f"<main>\n{body_html}\n</main>\n"
        f'<footer class="doc-footer">{footer_line}</footer>\n'
        "</html>\n"
    )


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("input", nargs="?", help="Markdown file (default: stdin)")
    ap.add_argument("--out", help="output HTML path; for a file input, "
                    "defaults to the input name with a .html extension")
    ap.add_argument("--stdout", action="store_true",
                    help="write HTML to stdout even for a file input")
    ap.add_argument("--title")
    ap.add_argument("--no-webfonts", action="store_true")
    ap.add_argument("--toc", action="store_true",
                    help="force a table of contents (default: auto when ≥3 H2s)")
    ap.add_argument("--no-toc", action="store_true",
                    help="suppress the table of contents")
    ap.add_argument("--agent", action="store_true",
                    help="accepted for flag consistency; this renderer never "
                    "prompts, so it is a no-op")
    args = ap.parse_args()

    source = "stdin"
    if args.input:
        try:
            text = Path(args.input).expanduser().read_text("utf-8")
        except OSError as e:
            log(f"FATAL: cannot read input ({e.__class__.__name__}: {e})")
            sys.exit(1)
        source = Path(args.input).name
    else:
        text = sys.stdin.read()
    if not text.strip():
        log("FATAL: empty input")
        sys.exit(1)

    fm_title, text = strip_frontmatter(text)
    title = args.title or fm_title
    if not title:
        h1, text = extract_h1(text)
        title = h1 or (Path(args.input).stem if args.input else "Document")

    slugger = make_slugger()
    headings = []
    body_html = md_to_html(text, slugger, headings)

    h2_count = sum(1 for h in headings if h[0] == 2)
    if args.no_toc:
        show_toc = False
    elif args.toc:
        show_toc = True
    else:
        show_toc = h2_count >= 3
    toc_html = build_toc(headings) if show_toc else ""

    today = date.today().isoformat()
    meta_line = f"Rendered {html.escape(today)} &middot; from {html.escape(source)}"
    footer_line = "Rendered by render-html."

    doc = build_document(
        html.escape(str(title)), body_html, meta_line, footer_line,
        webfonts=not args.no_webfonts, toc_html=toc_html,
    )

    # Resolve destination: explicit --out wins; otherwise a file input defaults
    # to <input>.html; stdin (or --stdout) goes to stdout.
    target = None
    if args.out:
        target = Path(args.out).expanduser()
    elif args.input and not args.stdout:
        target = Path(args.input).expanduser().with_suffix(".html")

    if target:
        try:
            target.write_text(doc, "utf-8")
        except OSError as e:
            log(f"FATAL: write failed ({e.__class__.__name__}: {e})")
            sys.exit(1)
        print(f"wrote {target}")
    else:
        sys.stdout.write(doc)


if __name__ == "__main__":
    main()
