# House markdown style spec

Canonical formatting standard for markdown this family of skills writes or
rewrites. Base: [Google's documentation markdown style guide][google-style],
distilled. House overlays are marked **[HOUSE]** and **win wherever they
diverge from Google** (the biggest divergence: we are tables-forward; Google
is lists-forward). Loaded by `format-markdown` SKILL.md Step 2, and referenced
by document-writing skills at authoring time.

[google-style]: https://google.github.io/styleguide/docguide/style.html

## Scope and deference boundaries

This spec governs **document structure and formatting only**. It never wins
against a format another skill owns:

| Target | Owner — defer entirely |
|--------|------------------------|
| OKF reserved files (`index.md`, `log.md`) and article frontmatter | `curate-knowledge/references/okf-conventions.md` |
| Vault article *bodies* | This spec (structure) within OKF's body rules (absolute links, `# Citations`) |
| `CLAUDE.md` / `.claude/rules/` | `craft-claude` |
| Copy *content* quality (word choice, tone, CTAs) | `polish-copy` |
| HTML rendering of markdown | `render-html` |
| `SKILL.md` files | `skill-architecture.md` (audited by `audit-skill`) |

## Document skeleton

- One `#` H1 as the document title, first line (after any frontmatter).
- **ATX headings** (`##`), never setext (`===`/`---` underlines).
- Heading levels descend without skipping (`##` → `###`, never `##` → `####`).
- Blank line before and after every heading, list, table, and code block.
- Unique, descriptive heading names within a document (anchors depend on it).
- No trailing whitespace; end the file with a single newline.
- Line length: wrap prose at ~80 characters where practical **[HOUSE: soft]** —
  never break a link or table row mid-line to satisfy it.

## Choosing a structure — table vs. list vs. prose [HOUSE]

The core overlay. Google says "prefer lists; do not abuse tables". The house
rule is tables-forward for data, and it overrides Google:

| Content shape | Use | Test |
|---------------|-----|------|
| Repeating records with the same fields (skills, flags, endpoints, options) | **Table** | Could it be a spreadsheet row? |
| Sequential steps, ranked items, nested reasoning | **Bulleted / numbered list** | Does order or hierarchy carry meaning? |
| Items whose "cell" would exceed ~1–2 sentences | **List** (bold lead-in per item) | Long cells make tables unreadable — fall back |
| Narrative, context, rationale, caveats | **Prose** | Is it an argument, not data? |

- Enumerations of ≥3 parallel facts default to a table or list, never a
  paragraph with commas.
- Keep table cells short; push explanation into surrounding prose or a
  footnote-style bullet below the table.
- Prose is for *connecting* structure, not replacing it.

## Table of contents [HOUSE threshold]

- Add a `## Contents` (bulleted, links to H2s) only when the document exceeds
  **~3 screens or ~8 H2 sections**.
- Never in vault articles (the directory `index.md` is the TOC), `SKILL.md`
  (must stay lean), or README-length docs.

## Lists

- `-` (dash) for unordered lists, consistently.
- **Lazy numbering** (`1.` on every item) for ordered lists likely to change;
  real numbers only when items are referenced by number elsewhere.
- Indent wrapped list content / nested blocks 4 spaces so renderers keep them
  inside the item.
- A "list" of one item is a sentence.

## Code

- Fenced code blocks (```` ``` ````), never 4-space-indented blocks; always
  declare the language (` ```bash `, ` ```python `; ` ```text ` if none).
- Inline code spans for filenames, flags, identifiers, and literal values:
  `--agent`, `SKILL.md`, `chmod 600`.
- In command samples, escape line-ends with `\` rather than letting commands
  soft-wrap.

## Links

- Link text names the destination: `[the OKF spec](…)`, never
  [click here / this link / here].
- Use reference-style links (`[text][label]` + a label block) when the same
  long URL repeats or inline URLs hurt the ~80-char wrap.
- Vault articles: absolute `/path/from/root.md` links (OKF rule — defer).

## Tables (mechanics)

- Header row + delimiter row always; one space padding inside pipes.
- Alignment colons only when alignment matters.
- No merged/multi-line cells — if the data needs them, it isn't a table
  (see structure choice above).

## Markdown over HTML

Prefer pure markdown. Inline HTML only for the rare thing markdown cannot do
(e.g. `<details>`, `<kbd>`) — and note it, because some renderers strip it.

## Mechanical rule mapping (markdownlint)

The lint pass (`scripts/lint.py`) enforces the mechanical subset via
[markdownlint][mdl]; everything above it can't see (structure choice, TOC
threshold, link-text quality, cell length) is the judgment pass.

[mdl]: https://github.com/DavidAnson/markdownlint

| markdownlint rule | Spec rule |
|-------------------|-----------|
| `MD003` (style: atx) | ATX headings |
| `MD004` (style: dash) | Dash bullets |
| `MD001` | No skipped heading levels |
| `MD012`, `MD022`, `MD031`, `MD032` | Blank-line discipline |
| `MD009`, `MD047` | No trailing whitespace; trailing newline |
| `MD040` | Fenced blocks declare a language |
| `MD024` (siblings_only) | Unique headings |
| `MD013` **disabled** | Line length is a soft house rule — judgment, not lint |
