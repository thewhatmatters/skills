# format-markdown — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-07-03  ·  Generator: generate-skill @ CC 2.1.181

## 1. Purpose

Formats and audits markdown documents against the house style spec —
Google's docguide distilled plus house overlays (tables for structured data,
tight bullets, a TOC threshold).

## 2. Reusable patterns (link to spec A1..A13)

This skill follows `~/.claude/skills/skill-architecture.md` patterns A1–A13;
deliberate shape notes:

- A1: the style spec (`references/markdown-style.md`) IS the skill's core
  asset — SKILL.md stays a thin router over it.
- A3/A11: markdownlint is optional muscle ($MARKDOWNLINT_BIN → PATH → npx);
  its absence degrades only the mechanical pass, never blocks.
- A8: consumed *by reference* from document-writing skills — they read the
  spec at authoring time; nothing imports across skill dirs.
- A10 deviation: no `report.py` — the artifact is the formatted markdown
  file itself (FORMAT) or an in-chat findings report (AUDIT); a styled HTML
  report would be render-html's job by composition.

## 3. Decision log

- 2026-07-03: **Tables-forward overlay overrides Google.** Google's guide
  says "prefer lists, do not abuse tables"; the user's standing preference
  (memory: format-tables-and-lists) is tables for structured, repeating-shape
  data. The spec encodes the divergence explicitly ([HOUSE] markers) with a
  fallback: cells exceeding ~1–2 sentences → back to lists. Alternatives
  considered: adopting Google verbatim (rejected — contradicts the user's
  actual preference), or leaving it implicit (rejected — the two rules would
  silently conflict depending on which section was read).
- 2026-07-03: **Deference table, not feature creep.** OKF reserved files +
  frontmatter belong to curate-knowledge's okf-conventions; CLAUDE.md to
  craft-claude; copy content to polish-copy; SKILL.md to skill-architecture.
  This skill formats only what nothing else owns — same boundary discipline
  as wire-vault's marker block.
- 2026-07-03: **FORMAT is meaning-preserving by contract.** Restructure,
  never reword — rewording is polish-copy's lane. Keeps the two skills
  composable on the same file without fighting.
- 2026-07-03: **MD013 (line length) disabled in lint.** The ~80-char wrap is
  a soft house rule; enforcing it mechanically would spam findings on tables
  and links. Judgment pass handles it.
- 2026-07-03: **Ambiguous `--agent` runs default to AUDIT** — the
  non-destructive choice when nobody can confirm a rewrite.
- 2026-07-03: scaffolded by generate-skill (docs cache CC 2.1.181; reconcile
  flagged upstream drift: `disallowed-tools` added to live frontmatter fields
  since spec baseline 2.1.144 — unused here, conservative frontmatter only).

## 4. Known limitations / environment caveats

- markdownlint-cli emits `--json` results on **stderr**; `lint.py` parses
  stderr first, stdout as fallback. If the CLI changes this, update
  `parse_json_output` call order.
- First `npx --yes markdownlint-cli` run downloads the package (network);
  `lint.py` allows 120s for it. Offline + no local install → `unavailable`,
  judgment-only.
- TOC generation is manual (judgment pass); no doctoc-style tooling wired.
- Preflight's `lint` check is presence-based (`shutil.which`), not a live
  probe — `npx` on PATH can still fail offline on first fetch. Accepted:
  lint.py degrades gracefully at run time, so the worst case is a late
  `unavailable` instead of an early `degraded`.

## 5. Audit rubric coverage

See `skill-architecture.md` §B; this skill targets every PASS that applies.
N/A items: secrets/`_env.py` (keyless), user scope control (single-file
target; mode + `--out` are the scope).

## 6. Notes

Composition line for writing skills to adopt (one line, by reference):
"Author markdown per `~/.claude/skills/format-markdown/references/markdown-style.md`."
Candidates: curate-knowledge (article bodies), ingest-source (summaries),
handoff (HANDOFF.md), deep-research / generate-prd (reports). Adopt on next
touch of each skill rather than a big-bang edit.
