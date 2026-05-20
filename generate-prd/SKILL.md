---
name: generate-prd
description: Synthesize a conversational product discussion into a structured Product Requirements Document covering problem, solution, UX flow, technical architecture, data model, pricing, roadmap, risks, and open questions. Use when the user wants to turn a chat-style brainstorm or product conversation into a written PRD — "turn this discussion into a PRD", "write a PRD from our conversation", "create a PRD for X based on what we've been discussing", "spec this product idea out", "document this product idea as a PRD", "I've been thinking about a product — make a PRD". Outputs a markdown file (for Claude Code consumption) and optionally a self-contained HTML version.
---

# generate-prd

Turn a conversational product discussion into a structured PRD — one markdown
file (always) and optionally one self-contained HTML file. Synthesis is
model-driven; the script layer only handles the HTML render so the markdown
path works with no Python.

The detailed output shapes (the JSON the model produces internally, the
markdown layout, the HTML structure) live in
[`references/output-templates.md`](references/output-templates.md) and are
loaded only when needed at Step 4 (spec A1 — progressive disclosure).

## Flags

| Flag | Meaning |
|------|---------|
| `--out=PATH` | output directory (default: current working dir). Files written as `prd-<slug>.md` and (optionally) `prd-<slug>.html`. |
| `--name=<slug>` | explicit kebab slug for the output filenames; default = derived from the PRD's primary product/feature |
| `--no-html` | skip the HTML render; markdown only |
| `--transcript=PATH` | load discussion from a saved transcript file instead of the current session |
| `--agent` | non-interactive; never prompt; use the documented defaults |
| `--dry-run` | print the plan + would-be file paths + the proposed PRD outline; write nothing (see Step 5) |

## Step 0 — Mode probe

Try `python3 --version` and look for `scripts/report.py`. If both present →
mode = **SCRIPTS** (full functionality, markdown + HTML). Otherwise →
mode = **NATIVE** (markdown only; HTML is skipped with a one-line notice —
spec A3 degraded path). Announce the mode.

## Step 1 — Preflight

`python3 scripts/preflight.py --out=<out>` — confirms the output dir is
writable. Stop only on `overall: down`. Under `--agent` use the documented
defaults and never prompt.

## Step 2 — Identify the discussion source

- Default: the **current session's preceding turns** — the chat that motivated
  this run. Quote the lines you're treating as the source so the user can
  confirm you got the right scope.
- `--transcript=PATH`: read the file and use that instead. If the file is
  missing or empty, STOP with a clear error.

## Step 3 — Confirm scope (interactive only)

State the proposed product/feature title and the discussion span you're
synthesizing. Ask once: *Looks right? / Narrow the scope / Cancel.*
Under `--agent`: proceed silently with what you've identified.

## Step 4 — Synthesize the PRD (model-driven)

Open [`references/output-templates.md`](references/output-templates.md) for the
exact JSON shape, the markdown layout, and the synthesis rules. The short
version of the rules:

- Stay grounded in what the discussion actually said. If a section has no
  signal from the conversation, write **"(not discussed — see open
  questions)"** rather than inventing content; add the gap as an item under
  `open_questions`.
- `problem` first, in user terms. `solution` describes the product, not the
  implementation. `technical_architecture` and `data_model` use code-fence
  blocks where shape matters. `roadmap` is phased (e.g. v0 / v1 / later).
- Honesty discipline (spec A12): never present synthesized speculation as
  decided. Flag inferred items clearly.

## Step 5 — Write the markdown PRD (or dry-run)

**If `--dry-run`** was passed: print the proposed file paths and the section
inventory from Step 4 (which sections have content vs "not discussed") —
**then stop**. No files written. No HTML render. (See
[`references/output-templates.md` §5](references/output-templates.md) for
the exact dry-run output shape.)

Otherwise: emit `<out>/prd-<slug>.md` following the markdown layout in
[`references/output-templates.md`](references/output-templates.md). **No
clobber** — if `prd-<slug>.md` already exists, write to `prd-<slug>-2.md`,
`-3.md`, … (spec A11 layered fallback applied to filenames).

## Step 6 — Render the HTML (optional)

If `--no-html` was passed → skip. NATIVE mode → skip with a one-line notice.
`--dry-run` → already exited at Step 5.

Otherwise: pipe the JSON from Step 4 into `python3 scripts/report.py
--out=<out>/prd-<slug>.html`. The result is a single self-contained HTML
file (inline CSS, escaped content, light/dark friendly) recording the
original product, the date, and every section — spec A10.

> Branded alternative (opt-in): for the anthropic.com brand look instead of
> this skill's default HTML, render the `prd-<slug>.md` file with the
> `/render-html` skill. Optional and decoupled — this skill does not depend on
> it.

## Step 7 — Emit

Print, in this order:

1. The output paths (markdown + HTML if rendered).
2. A short "sections written" line so missing or "not discussed" sections
   are visible, not silently empty.
3. Any open-questions count, so the user knows there's follow-up.

Example:

```
wrote:
  /Users/you/prd-generate-prd.md
  /Users/you/prd-generate-prd.html
sections: problem ✓  solution ✓  ux_flow ✓  technical_architecture ✓
          data_model ⚠ (not discussed)  pricing ⚠ (not discussed)
          roadmap ✓  risks ✓  open_questions: 4 items
```

## Conventions this skill follows

- Synthesis layer is model-driven; the script layer (`report.py`) only does
  the HTML render (single concern, JSON-stdin → HTML-stdout, spec A4).
- Dual-mode (spec A3): markdown always works; HTML degrades gracefully when
  Python is absent.
- Honest fallbacks: missing sections labelled, never invented (spec A12).
- No clobber: never overwrite an existing `prd-<slug>.md` (spec A11).
- This skill doesn't run git; it doesn't write outside `<out>`.
