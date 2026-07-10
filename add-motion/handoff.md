# add-motion — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-06-10  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose

Add motion to web UI as a deliberate craft — premium-feeling animation without jank.

## 2. Reusable patterns (link to spec A1..A13)

Follows `~/.claude/skills/skill-architecture.md` A1–A13. Deliberate shape notes:

- **A1**: per-tier craft in `references/` (css-animations / motion-library /
  view-transitions); SKILL.md holds only routing + guardrails.
- **A3/A7**: the official `/motion` skill deferral is **opportunistic, never a
  gate** — Motion+ is a paid product, so absence is the normal state; the skill
  surfaces it once and falls back to references with a cutoff caveat. This
  deviates from the shadcn/next-best-practices pattern (no `skills-lock.json`
  pin, no install command) because the skill isn't freely installable.
- **A6**: preflight is deliberately tiny (project dir + package.json) — the
  skill has no network/key/binary deps.

## 3. Decision log

- 2026-06-10: built per the 2026 frontend-skills research (deep-research run:
  `/tmp/research-frontend-skills-2026.md`) — vendor skills own API knowledge;
  this skill owns tier routing + guardrails.
- 2026-06-10: **own probe rather than reusing build-ui's** — build-ui's probe
  reports a `motion` boolean but not legacy-vs-current package, auto-animate,
  or incumbent libs (GSAP/react-spring), and its `DEFERRAL_TARGETS` doesn't
  include the Motion+ skill. A dedicated ~120-line probe beats coupling to a
  sibling's schema (composition by reference still applies at the SKILL level).
- 2026-06-10: **tier order is CSS → Motion → View Transitions**, lightest
  first — bundle cost and jank risk both rise with the heavier tiers; the
  premium feel comes from easing/duration discipline, not from the library.
- 2026-06-10: guardrails (compositor-only, reduced-motion, duration/easing
  discipline) are non-negotiable in every tier — mirrors remotion's
  determinism guardrails: cheap, stable, exactly what agents get wrong.

## 4. Known limitations / environment caveats

- Motion's API moves fast; without the Motion+ `/motion` skill the
  motion-library reference sticks to the stable core and flags currency.
- CSS scroll-driven animations (`animation-timeline`) and `@starting-style`
  support should be verified against the project's browser targets.
- iOS/Swift animation is explicitly out of scope (web + Tauri webviews only).

## 5. Audit rubric coverage

See `skill-architecture.md` §B; this skill targets every PASS that applies.
Keyless → secrets items N/A; no artifact emitted → A10 N/A (it edits the
user's project; the report is conversational).

## 6. Notes

Composes with: build-ui (names add-motion for animation asks), frontend-design
(taste), source-ui (motion precedent), automate-browser/webapp-testing
(visual verification), remotion (video — the negative case).
