# handoff — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-24  ·  built against the spec (CC 2.1.145)

## 1. Purpose
Write a resume-ready `HANDOFF.md` so a fresh session continues sharp instead of
context-rotted, and maintain the status-line task label. The model-driven core
of a "context-hygiene" system (status line + hooks + lower auto-compact).

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Notable points:
- **A1 progressive disclosure:** the HANDOFF.md structure and the one-time
  config setup live in `references/`; SKILL.md stays a lean flow.
- **A8 composition by reference:** complements the file-based memory system
  (durable facts) + CLAUDE.md (rules); delegates settings wiring to
  `update-config` / `statusline-setup`. The PreCompact hook references this
  skill's bundled scripts.
- **A12 honesty:** the skill is explicit that the model writes the handoff
  because hooks can't summarize, and that session restart is user-driven.

## 3. Decision log
- 2026-05-24: built. Prompted by the user wanting to "stay smart" as context fills.
- 2026-05-24: **Researched the premise first.** Context degradation ("context
  rot") is real and multiply-documented (Liu 2023 "Lost in the Middle"; Chroma
  "Context Rot" 2025 incl. Claude 4; Anthropic 2025) — but a *gradient, not a
  fixed %*. So the design targets "refresh earlier," not "detect a magic
  threshold." Claude tends to abstain rather than hallucinate when overloaded.
- 2026-05-24: **Verified Claude Code limits before designing** (via
  claude-code-guide): a subagent CANNOT see the parent session's context (full
  isolation); the model/hooks CANNOT read live context %; session restart is
  user-driven. So the user's original "concurrent sub-agent that watches our
  context and auto-restarts" is **not buildable** — redesigned around what is.
- 2026-05-24: **The status line is the exception** — its command receives
  `context_window.used_percentage` pre-calculated on stdin (CC 2.1.132+), so a
  context meter is clean (no transcript parsing). That's the human's cue, since
  the model can't see it.
- 2026-05-24: **Scripts in Python, not jq-bash.** `jq` isn't guaranteed
  installed; the bundled scripts parse JSON with python3 stdlib for portability.
- 2026-05-24: **Hooks preserve, model summarizes.** PreCompact only snapshots
  the model-written HANDOFF.md (a hook can't run the model). SessionStart emits
  `additionalContext` to resurface it (with a CLAUDE.md `@import` fallback if a
  CC version doesn't honor it).

## 4. Known limitations / environment caveats
- No magic threshold: defaults (compact 65%, status line yellow 50 / red 75) are
  starting points, tune per workload.
- A hook can't generate a smart summary — keep HANDOFF.md fresh so PreCompact
  always preserves something good.
- SessionStart `additionalContext` injection should be verified on the user's CC
  version; the on-disk HANDOFF.md + CLAUDE.md `@import` is the guaranteed path.
- Status line shows context % to the *human*; nothing exposes it to the model.

## 5. Audit rubric coverage
See `skill-architecture.md` §B. The skill itself is keyless/no-network; the
`assets/` scripts (status line + 2 hooks) follow A4 (graceful, never hang, never
block compaction/session start). Secrets rows N/A.

## 6. Notes
Research sources: Liu et al. *Lost in the Middle* (arXiv 2307.03172); Chroma
*Context Rot* (2025); NoLiMa (2025); Anthropic *Effective context engineering*
(2025). Setup is delegated to `update-config` (hooks/env) + `statusline-setup`.
