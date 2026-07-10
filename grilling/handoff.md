# Handoff — grilling

_Created 2026-07-10_

## What this is

Vendored + adapted from Matt Pocock's public `mattpocock/skills` repo (MIT),
pulled in specifically because `improve-codebase-architecture` uses it for
its post-selection interview loop. See `NOTICE.md` for what changed (almost
nothing — the source was already minimal).

Sibling skills from the same vendoring session: `codebase-design`,
`improve-codebase-architecture`.

## Decisions

- **Kept as its own skill, not folded into `karpathy-spec`.** There's real
  overlap (both are interview-driven alignment tools), but they operate at
  different scopes and different points in the lifecycle: `karpathy-spec`
  is a full spec-first method that drafts and locks a `PRD.md` + `CLAUDE.md`
  for a whole project or feature; `grilling` is a lightweight, reusable
  interview primitive with no document output, meant to be invoked
  standalone *or* embedded inside other skills (as
  `improve-codebase-architecture` does). Composing a separate skill here
  follows this house's compose-over-extend convention (see the vault:
  `/claude/best-practices/compose-over-extend.md`) rather than growing
  `karpathy-spec` a second mode.
- **Trigger mode: model-invoked**, matching the source. No side effects, no
  cost beyond conversation turns — fine to let the model reach for it.

## Not done

- Not yet added to the vault's `claude/skills/skill-catalog.md`.
- Haven't field-tested it standalone (only as part of designing
  `improve-codebase-architecture`, which itself hasn't had a live run yet).
