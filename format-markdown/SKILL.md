---
name: format-markdown
description: Format, restructure, or audit a markdown document against the house markdown style spec — Google's documentation style guide distilled plus house overlays; tables for structured, repeating-shape data; bulleted lists over dense prose; a table-of-contents threshold for long docs. Use when the user wants a markdown file cleaned up, restructured, or checked — "format this markdown", "clean up this doc", "make this doc follow our style", "restructure this README", "convert this prose to tables/bullets", "add a TOC", "lint this markdown", "audit this doc's formatting", "is this doc well-formatted". Two modes — FORMAT (meaning-preserving rewrite to spec) and AUDIT (report-only, severity-grouped findings with file:line evidence). Also the house standard document-WRITING skills reference — when a skill (curate-knowledge, ingest-source, handoff, deep-research, generate-prd) authors markdown for the vault or a project, it follows references/markdown-style.md here. Scope is document structure and formatting only — copy content quality is polish-copy; HTML rendering is render-html; CLAUDE.md authoring is craft-claude; OKF reserved files (index.md, log.md) and article frontmatter defer to curate-knowledge's okf-conventions. Mechanical rules via markdownlint when available (env override → PATH → npx ladder); degrades to a judgment-only pass natively.
---

# format-markdown

Formats and audits markdown documents against the house style spec —
Google's docguide distilled plus house overlays (tables for structured data,
tight bullets, a TOC threshold).

## What it does

Applies `references/markdown-style.md` — the single source of truth this
skill and the document-writing skills share — to a markdown file, in one of
two modes: **FORMAT** (rewrite the file to spec, meaning-preserving) or
**AUDIT** (report-only findings). A mechanical pass (markdownlint, optional)
catches syntax rules; a judgment pass applies what a linter can't see:
table-vs-list-vs-prose choice, the TOC threshold, link-text quality (A1:
the spec's detail lives in the reference, loaded at Step 2).

## How to run

Say "format this markdown", "clean up this doc", "audit this README's
formatting", or invoke `/format-markdown <file>`. Other skills compose by
adding one authoring line: *"author markdown per
`format-markdown/references/markdown-style.md`"* — they read the spec, they
never run this skill's scripts (spec A8).

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | write the formatted copy / audit report here instead of in place |
| `--mode=format\|audit` | skip inference; force a mode |
| `--toc=auto\|on\|off` | override the spec's TOC threshold (default `auto`) |

## Step 0 — Mode probe

Run `python3 --version` and check `scripts/` exists. Both → **SCRIPTS**.
Otherwise **NATIVE**: skip `lint.py` (judgment pass only) and do the
preflight checks with built-in tools. Announce the mode in one line.

## Steps

1. **Preflight** — SCRIPTS: `python3 scripts/preflight.py`. `lint`
   degraded (no markdownlint/npx) → proceed judgment-only and say so; only
   a missing style spec is `down`.
2. **Load the spec** — read `references/markdown-style.md`. It is the
   rulebook for everything below; do not improvise rules not in it.
3. **Deference check** — if the target is a file another skill owns (OKF
   `index.md`/`log.md`, `CLAUDE.md`, `SKILL.md` — table in the spec §Scope),
   stop and route there; this skill formats only what it owns. Vault article
   *bodies* are in scope, within OKF's body rules.
4. **Pick the mode** — `--mode=` wins; else infer ("format/clean
   up/restructure" → FORMAT; "audit/lint/check/is this well-formatted" →
   AUDIT; ambiguous interactive → ask once; ambiguous `--agent` → AUDIT,
   the non-destructive default).
5. **Mechanical pass** — SCRIPTS: `python3 scripts/lint.py <file>`; read
   the JSON findings. `status: unavailable` → note it and continue.
6. **Judgment pass** — walk the spec top-to-bottom (skeleton, structure
   choice, TOC threshold, lists, code, links, tables). Every finding gets
   `file:line` and the spec rule it violates.
7. **Deliver** —
   - AUDIT: severity-grouped findings (🔴 breaks rendering / 🟠 violates a
     house rule / 🟡 polish), each with `file:line` + concrete fix. Report
     only; offer FORMAT as the follow-up.
   - FORMAT: rewrite **meaning-preserving** — restructure, never reword
     (rewording is polish-copy's job). Interactive: show a change summary,
     get a yes, then write (in place, or `--out`). `--agent`: write to
     `--out` if given, else in place; list every change class applied.
8. **Report honestly** (spec A12) — mode used, lint available or skipped,
   rules applied vs. deferred, anything left for polish-copy/render-html.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- Composition by reference, not import (A8): writing skills read this
  skill's style spec; this skill routes content-quality work to
  `polish-copy`, rendering to `render-html`, owned formats per §Scope of
  the spec. Runs no other skill's code.
- Layered binary resolution (A11): markdownlint via `$MARKDOWNLINT_BIN` →
  `markdownlint` on PATH → `npx --yes markdownlint-cli`; its absence only
  degrades the mechanical pass.
- Keyless; network only if `npx` downloads the linter on first use.
