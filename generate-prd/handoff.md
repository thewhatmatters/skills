# generate-prd — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-19  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
Turn a conversational product discussion into a structured PRD (markdown +
optional HTML).

## 2. Reusable patterns (link to spec A1..A13)
This skill follows `~/.claude/skills/skill-architecture.md` patterns A1–A13;
note here any deliberate deviations.

Notable choices:

- **Synthesis layer is model-driven, not scripted.** The PRD is composed by
  Claude from the discussion in JSON shape; only the HTML render is a
  Python script (`report.py`). Rationale: synthesis is fundamentally about
  interpreting conversational context — not something a script does better.
- **Markdown path is NATIVE; HTML path is SCRIPTS.** Spec A3 dual-mode:
  markdown works with no Python; HTML degrades to "skipped" with a notice
  when python3 is missing.
- **No-clobber, never overwrite.** Re-running on the same slug writes
  `prd-<slug>-2.md`, `-3.md`, … (spec A11 layered fallback applied to
  filenames).
- **Honest "not discussed" labelling.** Sections with no signal from the
  conversation are written as "(not discussed — see open questions)" and
  pushed into `open_questions`, rather than synthesized speculation (spec A12).
- **Bulky output templates live in `references/output-templates.md`** so
  SKILL.md stays lean (spec A1 progressive disclosure).
- **`--dry-run` is implemented end-to-end**, not just listed in the flags
  table — Step 5 honors it explicitly and exits before any side effects.
- **`report.py` brace-safety.** User-derived strings are HTML-escaped *and*
  brace-doubled (`{` → `{{`, `}` → `}}`) before passing through `.format()`,
  so PRD content containing literal `{...}` (pseudocode, JSON examples,
  template placeholders) does not crash the renderer.

## 3. Decision log
- 2026-05-19: scaffolded by generate-skill (formal `/generate-skill`
  invocation, second run).
- 2026-05-19: prior attempt at this skill was deleted on user request after
  some confusion about which generator was used; this iteration is the
  clean rebuild. Old `~/.claude/skills/prd/` (Jan 11) had been deleted
  earlier under the "Replace it" path and is not being restored.
- 2026-05-19: three findings from that prior audit baked in here as design
  choices, not deferred — `--dry-run` implementation, report.py brace
  safety, templates moved to `references/`.

## 4. Known limitations / environment caveats
- NATIVE mode (no python3) skips HTML output, by design.
- Synthesis quality is bounded by the discussion's signal: if the user
  hasn't talked about pricing, the Pricing section will honestly say "(not
  discussed)" and the gap will show up in Open questions.

## 5. Audit rubric coverage
See `skill-architecture.md` §B. Items expected to be N/A for this skill:

- **A5/A7 secrets/setup-gate items** — keyless skill, no `.env`, no
  authentication. N/A.
- **A6 preflight breadth** — only one external dependency (target dir
  writability) plus the optional HTML-render availability check; preflight
  is minimal by design.
- **A8 user scope control** — no multi-source picker (single discussion
  source, optionally swappable via `--transcript=`).

## 6. Notes
Model-driven core; report.py renders PRD JSON → self-contained HTML; no
external APIs or secrets.
