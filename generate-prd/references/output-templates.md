# Output templates

Loaded by `SKILL.md` Step 4. Progressive disclosure (spec A1) — these stay
out of the main SKILL.md so the lean orchestration path stays readable.

---

## 1. Internal PRD JSON shape

The model synthesizes the discussion into this structure (in its head — no
file written for this artifact directly; it's the source for both the
markdown and the HTML in Steps 5–6):

```
{
  "title": "<product / feature name>",
  "slug":  "<kebab — used in filenames>",
  "date":  "<YYYY-MM-DD>",
  "summary": "<one-line elevator>",
  "discussion_source": "in-session" | "transcript:<path>",
  "sections": {
    "problem":                "...",
    "solution":               "...",
    "ux_flow":                "...",
    "technical_architecture": "...",
    "data_model":             "...",
    "pricing":                "...",
    "roadmap":                "...",
    "risks":                  "...",
    "open_questions":         "..."
  }
}
```

The same JSON is what gets piped into `scripts/report.py` for the HTML render.

## 2. Markdown PRD layout

Write the markdown PRD at `<out>/prd-<slug>.md` with this exact layout (the
heading order matches the JSON section order in §1):

```
# <title>

> <one-line summary>
>
> *Generated <date> by generate-prd from <discussion_source>.*

## Problem
...

## Solution
...

## UX flow
...

## Technical architecture
...

## Data model
...

## Pricing
...

## Roadmap
...

## Risks
...

## Open questions
...
```

Section bodies are whatever the synthesis produced — prose, bullet lists,
fenced code blocks where the shape matters (entities, endpoints, sample
records). Sections with no discussion signal are written verbatim as
`(not discussed — see open questions)` and their gap is added as a bullet
under **Open questions**.

## 3. Synthesis rules (spec A12 — honesty discipline)

- **Stay grounded.** Every claim should be traceable to something the
  discussion actually said. If a claim is inferred, mark it as such
  (e.g. *"(inferred from X)"*).
- **Don't invent.** When a section has no signal, the placeholder string is
  required — do NOT make up a plausible-sounding answer.
- **Problem in user terms; solution in product terms.** "User can't widget
  their thumb in motorized form" (problem), not "API endpoint
  `/widget` returns 500".
- **Technical sections use code fences** when shape matters (table schemas,
  endpoint signatures, file layouts, message contracts).
- **Roadmap is phased.** `v0` / `v1` / `later`, or `MVP` / `next` / `someday`.
- **Risks are concrete.** "Battery life under 4h in cold weather" beats
  "performance risk".
- **Open questions are bullets** — one per unresolved point, including the
  gaps surfaced by "not discussed" sections.

## 4. HTML render — input/output contract

`scripts/report.py` reads the §1 JSON on stdin and produces a single
self-contained HTML file (inline CSS, no external assets, light/dark
friendly) recording title, date, source, summary, and every section.

Required JSON keys: `title`, `date`, `summary`, `sections`. The script
validates these and exits with a clear FATAL message if any are missing.

User-derived strings (title, summary, section bodies) are both HTML-escaped
*and* brace-doubled (`{` → `{{`, `}` → `}}`) before passing through
`.format()` — so PRD content containing literal `{...}` (pseudocode, JSON
examples, template placeholders) does not crash the renderer with a
`KeyError`.

## 5. Dry-run summary shape (Step 5)

When `--dry-run` is set, SKILL.md Step 5 prints something like:

```
DRY RUN — no files written

would write:
  <out>/prd-<slug>.md
  <out>/prd-<slug>.html   (skipped — --no-html / NATIVE)

section inventory:
  problem                 ✓
  solution                ✓
  ux_flow                 ✓
  technical_architecture  ✓
  data_model              ⚠ (not discussed)
  pricing                 ⚠ (not discussed)
  roadmap                 ✓
  risks                   ✓
  open_questions          3 items

re-run without --dry-run to write the files.
```

No HTML render, no audit, no side effects. The point is to let the user
sanity-check section coverage before committing to disk.
