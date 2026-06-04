# remotion — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-06-03  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose

Make real videos programmatically with Remotion — author React motion-graphics
from a script, preview them in Studio, and render them to MP4. The skill owns the
**workflow**; Remotion's API knowledge is deferred to the official skill.

## 2. Reusable patterns (link to spec A1..A13)

Follows `~/.claude/skills/skill-architecture.md` A1–A13. Closest sibling is
`build-ui` — same **compose-with-external-skill** posture (A3/A7/A8) and the same
`detect_user_skill` probe pattern. Deliberate notes:

- **A1 progressive disclosure** — SKILL.md is the spine; the four references
  (compose / guardrails / workflow / render-and-export) load only when their step
  needs them.
- **A3 dual-mode + degraded ladder** — SCRIPTS (probe.py + preflight.py) vs NATIVE
  (probe by hand). The official-skill deferral degrades to general-knowledge +
  install command + a training-cutoff caveat; never blocks.
- **A7 setup gate** — `NODE_MISSING` is a gate (author-only fallback), not `down`.
  The missing-official-skill case is a gate that surfaces the install command.
- **A8 composition by reference** — defers to `remotion-best-practices`; never
  imports or re-enumerates it.

## 3. Decision log

- 2026-06-03: scaffolded by generate-skill.
- 2026-06-03: **Compose, don't vendor** (the load-bearing call). Remotion ships an
  official, maintained Claude Code skill, `remotion-best-practices`
  (`npx skills add remotion-dev/skills`; 1 SKILL.md + ~37 rules). Per CLAUDE.md's
  5-step external-skill convention, `remotion` probe-gates and defers all API
  knowledge to it, keeping local references thin to avoid per-release drift. Chosen
  over standalone (drifts) and hybrid (double maintenance). User asked "what do you
  recommend"; this was the recommendation, accepted.
- 2026-06-03: **Value-add is the workflow**, not the API — the script→scenes→render
  →composite pipeline + determinism guardrails are what `remotion` carries; the
  official skill carries the API. Clean, non-overlapping split.
- 2026-06-03: **Determinism guardrails live in `guardrails.md` and are declared
  non-negotiable** — cheap, stable, and the #1 thing agents get wrong (Math.random/
  Date.now, non-frame-driven animation, CSS/Tailwind animation classes).
- 2026-06-03: **No-monoculture** — won't add Remotion to a non-Remotion project
  without consent (mirrors build-ui's refusal to introduce shadcn/Next/Tailwind).
- 2026-06-03: **Third-party "anti-gravity" skill excluded** — it's a community
  token-efficiency skill from the seeding tutorial, not a Remotion product; noted as
  optional only.
- 2026-06-03: Frontmatter kept conservative (`name` + `description`) per the recipe;
  spec reconcile reported `aligned` (CC 2.1.145), no drift.

## 4. Known limitations / environment caveats

- Render flag/codec specifics can change between Remotion releases; the skill defers
  to `npx remotion render --help` + the official skill rather than freezing them.
- Remotion Lambda (cloud render) is documented as an advanced opt-in only; full AWS
  setup is out of scope for the core flow.
- `probe.py` shells out to `node --version` (5s timeout) — the only subprocess; still
  keyless and network-free.

## 5. Audit rubric coverage

See `skill-architecture.md` §B; this skill targets every PASS that applies. Seeded
from a deep-research report (`/tmp/research-remotion.md`) + a tutorial-video summary
(`/tmp/oWkUwno6b0E-summary.md`).

## 6. Notes

Knowledge sources: remotion.dev/docs (the-fundamentals, composition, register-root,
cli/render, renderer/render-media, using-randomness, license, player, ai/skills,
ai/coding-agents), the `remotion-dev/remotion/packages/skills` repo, and the
Chronixel "Claude + Remotion" tutorial (workflow only).
