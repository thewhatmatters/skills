# Handoff — codebase-design

_Created 2026-07-10_

## What this is

Vendored + adapted from Matt Pocock's public `mattpocock/skills` repo (MIT),
as the shared vocabulary dependency for the new `improve-codebase-architecture`
skill. See `NOTICE.md` for exactly what changed vs. the source.

Sibling skills from the same vendoring session: `grilling`,
`improve-codebase-architecture`. All three were pulled in together because
`improve-codebase-architecture` genuinely depends on this vocabulary and on
`grilling`'s interview loop — see that skill's SKILL.md "Process" section.

## Decisions

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
  "light dependency" instead. `CONTEXT-FORMAT.md` and `ADR-FORMAT.md` were
  copied into `improve-codebase-architecture/references/` instead, since
  that's the only consumer in this vendoring pass. If a future need for
  active domain-modeling (challenging terminology, sharpening fuzzy
  language) shows up independent of architecture review, port
  `domain-modeling` as its own skill then — don't retrofit it into
  `improve-codebase-architecture`.
- **Trigger mode: model-invoked** (no `disable-model-invocation`), matching
  the source. This is a pure reference/vocabulary skill with no side
  effects — cheap to have in context, and other skills should be able to
  pull it in without the user needing to know it exists.

## Self-audit (2026-07-10, same session)

`skill-auditor` fan-out found two issues, both fixed same-session: a LATENT
frontmatter YAML fold issue (description had an unquoted `: ` mid-line —
parsed fine by the lenient harness reader but failed strict
`yaml.safe_load`; folded with `>-`), and a LOW sediment duplication (the
"Boundary" avoid-note appeared verbatim in both the glossary and Rejected
framings; kept only in the glossary). See `improve-codebase-architecture/handoff.md`
for the fuller audit summary across all three vendored skills.

## Not done

- Not yet added to the vault's `claude/skills/skill-catalog.md` — that's a
  vault-curation step, out of scope for this session unless asked.
- No live-verification run yet (haven't exercised `improve-codebase-architecture`
  end-to-end against a real codebase to confirm the whole pipeline works).
