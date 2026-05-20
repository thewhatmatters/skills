---
name: deep-research
description: Conduct deep, structured research on any topic — markets, products, features, competitors, problems, industries, regulations, or opportunities. Trigger whenever the user wants to research, explore, investigate, analyze, or understand something. This includes entering new markets, evaluating products or services, exploring features, solving business problems, competitive landscapes, regulatory research, or any "I need to understand X" scenario. Also trigger for "look into", "dig into", "explore whether", "map out the landscape", "what are the options for X", "how does Y work in practice". Trigger aggressively — if there's research intent, use this skill. Covers market research, competitive analysis, feature exploration, regulatory deep-dives, product evaluation, problem-solving, opportunity assessment, landscape mapping. Outputs a structured markdown report with inline citations (always) and a self-contained HTML version (optional). Composes with /trendscan when the question is about recent discussion specifically.
---

# deep-research

Conduct deep, structured research on a topic — a multi-pass loop that scopes,
searches broadly, fills gaps, and synthesizes a cited report. Synthesis is
model-driven; the script layer handles search and HTML render. Spec A3
dual-mode: SCRIPTS-with-keys is preferred, NATIVE (Claude's built-in
`WebSearch`/`WebFetch`) is a real fallback that produces the same artifact.

The detailed templates and rules live in `references/` and are loaded only
when needed (spec A1 — progressive disclosure):
- [`references/research-templates.md`](references/research-templates.md) — one
  section template per research type (market / competitive / feature /
  regulatory / product-eval / problem-solving / opportunity / landscape).
- [`references/synthesis-rules.md`](references/synthesis-rules.md) — citation
  discipline, honesty rules, gap-flagging conventions.

## Flags

| Flag | Meaning |
|------|---------|
| `--type=<kind>` | research type: `market`, `competitive`, `feature`, `regulatory`, `product`, `problem`, `opportunity`, `landscape`, `auto` (default `auto` — detect from question) |
| `--depth=<level>` | `quick` (1 broad sweep, ~5 sources), `standard` (default — broad sweep + focused follow-up, ~12-20 sources), `exhaustive` (multi-pass, ~30+ sources, may take minutes) |
| `--out=PATH` | output directory (default: current working dir). Files written as `research-<slug>.md` and (optionally) `research-<slug>.html`. |
| `--name=<slug>` | explicit kebab slug for the output filenames; default = derived from the research question |
| `--no-html` | skip the HTML render; markdown only |
| `--transcript=PATH` | load the research question from a file instead of the current session |
| `--agent` | non-interactive; never prompt; use documented defaults |
| `--dry-run` | print the research plan + would-be file paths; write nothing. (See [`references/research-templates.md` §9](references/research-templates.md) for the exact dry-run shape.) |

## Step 0 — Mode probe

Try `python3 --version` and look for `scripts/search.py`. Also check whether
`TAVILY_API_KEY` (or `EXA_API_KEY`) is loadable via `scripts/_env.py`. Then:

| python3 | scripts | keys | mode |
|---------|---------|------|------|
| ✓ | ✓ | TAVILY or EXA set | **SCRIPTS** (full quality) |
| ✓ | ✓ | both missing | **NATIVE** (use built-in WebSearch; same artifact) |
| ✗ | — | — | **NATIVE** |

Announce the mode in one line. NATIVE mode is real and supported — never block
on missing keys (spec A3 + A7d graceful dead-end).

## Step 1 — Resolve the question, then scope it (anti-overtrigger guard)

**Resolve the question source first.** Default: the user's request in the
current session. With `--transcript=PATH`: read that file and treat its
contents as the research question + supporting context; if the file is
missing or empty, STOP with a clear error.

The description triggers aggressively by design. The rest of Step 1 keeps
that honest by assessing whether deep-research is the right tool for THIS
prompt — classify the question along three axes:

1. **Type.** Match to one of `market | competitive | feature | regulatory |
   product | problem | opportunity | landscape`. If `--type` was given, use
   it; otherwise infer from the question's keywords and structure.
2. **Recency.** If the question is fundamentally about "what people are
   saying lately" / "what's trending recently in X" — **suggest /trendscan
   instead** (interactive: offer *Use trendscan / Stay here / Cancel*;
   `--agent`: stay and note the recency angle in the report).
3. **Single-fact lookup.** If the question is answerable in one sentence
   from general knowledge ("what year did Y ship?", "who founded Z?"), this
   skill is overkill. **Gracefully exit** with a one-line answer + a note:
   *"This was a quick fact, not deep research. If you want a deeper dive,
   say so explicitly."* Under `--agent` proceed anyway (the user asked).

## Step 2 — Preflight

`python3 scripts/preflight.py --out=<out>` — checks target writability, key
presence, network, and report.py availability (the full per-check state
table lives in the script's docstring). Act on `overall`:

- `ready` / `degraded` → proceed; note any degraded item in the run summary.
- `gated` (`KEYS_MISSING`) → interactive: *Set keys / Proceed in NATIVE /
  Cancel*; `--agent`: proceed in NATIVE. **Graceful dead-end (spec A7d):
  NATIVE produces the same artifact, so the gate never blocks.**
- `down` → STOP; show the ⛔ item; do not research.

## Step 3 — Plan the research

Load `references/research-templates.md` and pick the template for the
classified type. The template specifies the section structure and a starter
set of subquery angles (e.g. for `market`: market size, segmentation, growth
drivers, key players, customer needs, trends, risks).

Generate the subquery list:
- `--depth=quick`: 3–5 subqueries, no follow-up phase.
- `--depth=standard`: 5–8 subqueries + 3–5 focused follow-ups after the
  broad sweep.
- `--depth=exhaustive`: 8–12 subqueries, multiple follow-up rounds, fetch
  full content via WebFetch for the top-cited sources.

Show the plan to the user (interactive) and confirm: *Looks right? / Adjust
angles / Cancel*. `--agent` proceeds silently with the plan.

`--dry-run` prints the plan + would-be file paths and **stops here** — no
search, no synthesis, no files written.

## Step 4 — Broad sweep

For each subquery in the plan, run search:

- **SCRIPTS:** `python3 scripts/search.py "<query>" [--provider=tavily|exa]
  [--n=10]` — returns `[{url, title, snippet, score, provider}, ...]` on
  stdout as JSON. Defaults to Tavily; falls back to Exa if Tavily key
  missing.
- **NATIVE:** use Claude's built-in `WebSearch` with the same query.

Collect results across all subqueries into a working set. Deduplicate by URL.

If recency is one of the angles (e.g. "recent regulatory changes"), **invoke
`/trendscan`** for that subquery instead of search.py — this is normal skill
composition, not a cross-skill import.

## Step 5 — Focused follow-up (standard & exhaustive only)

Read the broad-sweep snippets. Identify 3–5 gaps where the type template's
sections aren't yet well-covered. Issue targeted follow-up queries to fill
those gaps. For the most authoritative sources, **fetch full content** via
`WebFetch` (NATIVE) to extract specifics — pricing, exact quotes, contract
terms, etc. — that snippets alone won't carry.

## Step 6 — Synthesize the report

Open [`references/synthesis-rules.md`](references/synthesis-rules.md) for the
honesty discipline. The short version:

- **Every claim cites a source URL** inline (markdown link or `[1]` footnote).
- **Stay grounded.** Don't synthesize beyond what the sources actually said.
- **Flag gaps.** Sections where the search couldn't surface a clear answer
  are written verbatim as `(not surfaced in sources — see open questions)`
  and the gap is pushed into Open questions.
- **Distinguish inference from quotation** with explicit markers.

Produce the structured JSON (see
[`references/research-templates.md` §1](references/research-templates.md))
holding the title, type, depth, slug, date, sources used, the type-specific
sections, and the open questions.

## Step 7 — Write the markdown report (or dry-run)

`--dry-run` was already handled at Step 3; not reachable here.

Otherwise: emit `<out>/research-<slug>.md` following the markdown layout for
the chosen research type in `references/research-templates.md`. **No
clobber** — if the file exists, write `research-<slug>-2.md`, `-3.md`, …
(spec A11 layered fallback).

## Step 8 — Render HTML (optional)

If `--no-html` was passed → skip. NATIVE mode → skip with a one-line notice.

Otherwise: pipe the JSON from Step 6 into `python3 scripts/report.py
--out=<out>/research-<slug>.html`. Single self-contained HTML file, inline
CSS, escaped content, citations rendered as clickable links — spec A10.

## Step 9 — Emit

Print, in this order:

1. The output paths (markdown + HTML if rendered).
2. **Sources used:** count + a one-line provider breakdown (e.g.
   `Tavily ×12, Exa ×3, WebFetch ×4`).
3. **Sections written:** which type-template sections came through with
   solid sourcing vs. were marked "not surfaced".
4. **Open questions:** the count, so the user knows what didn't get answered.

Example:

```
wrote:
  /Users/you/research-pet-insurance-2026.md
  /Users/you/research-pet-insurance-2026.html
sources: 19 total (Tavily ×14, WebFetch ×5)
sections: market_size ✓ growth_drivers ✓ key_players ✓
          pricing ⚠ (not surfaced)  regulatory ✓  trends ✓
open questions: 4 items
```

## Conventions this skill follows

- **Composes with `/trendscan`** for recency-focused subqueries; otherwise
  uses bundled `search.py` (Tavily → Exa). No cross-skill imports.
- Synthesis is model-driven; the script layer (`search.py`, `report.py`)
  does one concern each (spec A4).
- Dual-mode (spec A3): SCRIPTS-with-keys preferred; NATIVE produces the same
  artifact via built-in WebSearch/WebFetch. NATIVE never gated.
- Setup-Gate pattern (spec A7): `KEYS_MISSING` is recoverable via the gate,
  but never blocks — NATIVE is always a real path.
- Honest citations: every claim links to its source; gaps are surfaced, not
  invented (spec A12).
- No clobber: never overwrite an existing `research-<slug>.md` (spec A11).
- This skill does not run git; it doesn't write outside `<out>`.
