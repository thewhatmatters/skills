# build-ui — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-31  ·  built against the spec (CC 2.1.145)

## 1. Purpose
Implement UI in a real project, following its existing stack and conventions
instead of imposing new ones. Owns the *execution* axis of frontend work.

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Notable points:
- **A1 progressive disclosure:** per-stack guidance (Tailwind, shadcn, vanilla
  CSS, a11y) lives in `references/`, loaded only for the libraries the project
  actually uses. SKILL.md stays a lean flow.
- **A3 dual-mode:** SCRIPTS (python3 + probe.py + preflight.py) vs NATIVE (read
  the configs by hand). The decomposition itself is always NATIVE reasoning.
- **A4 scripts:** `probe.py` (project inventory), `preflight.py` (project root
  found + writable) — JSON stdout, diagnostics stderr, graceful.
- **A8 composition by reference:** names `frontend-design` (taste), `add-motion`
  (planned, animation), `source-ui` (visual reference); imports none. The
  boundary is explicit so the descriptions don't cross-fire.

## 3. Decision log
- 2026-05-31: scaffolded against the spec. **Split by job, not stack.**
  Frontend has many libraries (Tailwind, shadcn, GSAP, Motion, …); making a
  skill per library would balkanize and age badly. Instead one workflow skill
  (`build-ui` = execution) owns the job; libraries live in `references/` and
  are loaded by probe-driven matching. Animation is the one craft worth its own
  sibling later (`add-motion`).
- 2026-05-31: **Scoped existing `example-skills:frontend-design` first.** It is
  a 42-line taste/direction prompt — owns aesthetic intentionality (bold,
  distinctive, anti-AI-slop) but **says essentially nothing about Tailwind /
  shadcn workflow, project-probe, scaffolding, or a11y mechanics**. So `build-ui`
  fills the execution gap with effectively zero overlap. The descriptions point
  to different intents (taste vs execution); we can validate the boundary later
  via `audit-skill --triggers` if cross-fire surfaces in practice.
- 2026-05-31: **Probe-driven, not user-told.** Like `decompose-prd` discovers
  the available skill set, `build-ui` discovers the project's stack from
  `package.json` + `tailwind.config.*` + `components.json` + `tsconfig.json` +
  `src/` shape. Stops the skill from guessing or imposing.
- 2026-05-31: **Reject any-stack monoculture.** Refuses to introduce a
  dependency the project doesn't already use (no surprise `shadcn add ...` in a
  vanilla-CSS repo). Adding deps is a separate explicit user decision.
- 2026-05-31: **Browser verification deferred.** When UI changes need visual
  proof, build-ui doesn't run a browser — it points at `automate-browser` or
  `example-skills:webapp-testing`. Keeps the skill scoped.
- 2026-05-31: **A10 self-contained artifact: deliberate deviation.** The spec
  expects "one dependency-free output file" per run. build-ui's artifact is the
  **code change in the project**, not a separate report file — same pattern
  `automate-browser`'s handoff §5 records. The "request + date + results" trio
  is captured by the project's own git history; build-ui defers to that rather
  than duplicating it.
- 2026-05-31: **Adopted a comprehensive a11y checklist.** The initial slim
  `a11y.md` (~80 lines, principles + anti-patterns) was upgraded to a full
  component-pattern checklist: Universal Pre-Flight + per-pattern (Forms,
  Button, Link, Modal, Disclosure/Accordion, Tabs, Menu, Combobox, Tooltip,
  Live Regions, Tables, Cards, Carousels) + WCAG 2.2 deltas + verification
  protocol. The structure lets build-ui pull *only* the section matching the
  component being built — and pairs cleanly with `shadcn.md`'s note that Radix
  primitives already implement most keyboard/ARIA mechanics (checklist then
  shifts to "verify you didn't break it + cover what primitives can't:
  labels, alt, contrast, copy, errors, focus targets"). Source: a vetted
  standards doc the user supplied; preserved verbatim with light framing for
  the references/ idiom.

## 4. Known limitations / environment caveats
- **Library coverage** in `references/` is intentionally lean — Tailwind,
  shadcn, vanilla CSS, a11y. CSS-in-JS (styled-components, vanilla-extract,
  CSS modules) and stack-specific component libraries (Radix without shadcn,
  Headless UI, Mantine, Chakra) are not yet covered; probe surfaces them so
  the skill says "no reference yet — falling back to general knowledge."
- The probe is **best-effort** — it reads configs as text, doesn't execute
  `tailwind.config.ts`. Computed configs may need hints (`--stack=`).
- Cross-trigger risk with `example-skills:frontend-design` is low (different
  intent) but not zero — verify with `audit-skill --triggers` if needed.

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.
Secrets/gate rows are N/A (keyless, no network, no external binaries; python3
is the only runtime).

## 6. Notes
Pairs with `frontend-design` (taste), `source-ui` (visual reference, Mobbin +
Refero), `decompose-prd` (iteration-sized story slicing for the build), and an
eventual `add-motion` (animation craft). Browser verification lives in
`automate-browser` / `example-skills:webapp-testing`.
