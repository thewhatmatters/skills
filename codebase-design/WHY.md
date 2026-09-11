# Why — codebase-design

_Created 2026-07-10_

## What this is

Vendored + adapted from Matt Pocock's public `mattpocock/skills` repo (MIT),
as the shared vocabulary for deep-module work (scan lives on `--improve`).
See `NOTICE.md` for exactly what changed vs. the source.

Sibling from the same vendoring session (`grilling`) was retired
2026-09-11; `--improve` interviews in-skill.

## Decisions

- **`--improve` folded in (2026-09-11).** The former sibling
  `improve-codebase-architecture` is a flag on this skill. Vocabulary stays
  the default (model-invoked, cheap). The scan stays opt-in (`--improve` /
  old slash name) so a vague "design this module" never launches an
  Explore-over-the-repo. Interview after a pick is in-skill (no
  `grilling` sibling).
- **Vendor + adapt, not a from-scratch rewrite.** The user chose this over a
  simplified standalone version or a full 4-skill port (which would have
  also included `domain-modeling` as its own skill). Rationale: Matt's
  version is more mature than what he described live in the conference talk
  that prompted this (see the vault article at
  `/claude/best-practices/matt-pocock-ai-coding-workflow.md`) — it has the
  deletion test, the dependency-category classification, and the
  design-it-twice pattern, none of which were in the talk. Reinventing it
  would have been strictly worse.
- **`domain-modeling` was NOT ported as its own skill** — deliberately a
  "light dependency" instead. `CONTEXT-FORMAT.md` and `ADR-FORMAT.md`
  live in this skill's `references/` (consumed by `--improve`). If a
  future need for active domain-modeling shows up independent of
  architecture review, port Matt's `domain-modeling` skill then — don't
  retrofit it into `--improve`.
- **Trigger mode: model-invoked** (no `disable-model-invocation`). Cheap
  in context. The expensive path is gated by `--improve`, not by hiding
  the whole skill. Do not enter `references/improve.md` unless the user
  asked for a scan.

## Self-audit (2026-07-10, same session)

`skill-auditor` fan-out found two issues, both fixed same-session: a LATENT
frontmatter YAML fold issue (description had an unquoted `: ` mid-line —
parsed fine by the lenient harness reader but failed strict
`yaml.safe_load`; folded with `>-`), and a LOW sediment duplication (the
"Boundary" avoid-note appeared verbatim in both the glossary and Rejected
framings; kept only in the glossary).

## Not done

- No live-verification run yet of `--improve` against a real codebase.
