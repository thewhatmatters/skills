# polish-copy — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-06-10  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose

Two-layer microcopy review — universal craft floor + per-project voice pass —
proposing before→after rewrites the user approves.

## 2. Reusable patterns (link to spec A1..A13)

Follows `~/.claude/skills/skill-architecture.md` A1–A13. Deliberate shape notes:

- **A1**: two references = the two layers; both load at the review step.
- **A3**: NATIVE = read the scoped files by eye; the scripts are convenience
  (inventory + spec location), not capability.
- **A6/A7**: `NO_VOICE_SPEC` is *degraded, not gated* by design — the floor
  layer is voice-independent, so a missing spec never blocks; the bootstrap is
  an interactive offer only (never under `--agent`).
- **A12**: extraction is heuristic — the report must disclose what wasn't
  covered (i18n indirection, copy built from variables).

## 3. Decision log

- 2026-06-10: **voice convention settled** (session discussion): the skill is
  project-agnostic machinery; voice lives per-project as a `## Voice` section
  in DESIGN.md (default — brand is visual *and* verbal identity, one file,
  already probed by build-ui/audit-ui) with standalone VOICE.md as the
  override for copy-heavy products. Mirrors the DESIGN.md/visual-tokens split;
  enforces refine-skill's "preferences never bake into shared skills".
- 2026-06-10: **two layers, mirroring audit-ui** — a deterministic-ish floor
  every project gets (per the 2026 research: most microcopy failure is
  voice-independent) + the voice pass that personalizes on top.
- 2026-06-10: **reviews, never authors** — research record is explicit that
  premium copy needs human tone-ownership; even the bootstrap drafts a *spec*,
  not copy, and is propose-only.
- 2026-06-10: **one rewrite per finding, not options** — Randy's house style
  (a recommendation, never a menu).
- 2026-06-10: severity grammar — 🔴 only for copy that misleads or blocks
  (lying labels, misdirecting errors, vague destructive confirms); 🟠 floor;
  🟡 voice. Voice violations never outrank floor ones.
- 2026-06-10: `.xcstrings`/`.strings` extraction in v1 — the iOS carryover is
  cheap (JSON + regex) and makes the same skill serve Swift projects.

## 4. Known limitations / environment caveats

- Heuristic extraction misses copy assembled from variables, i18n keys
  (`t('errors.email')`), and server-driven strings — the model spot-checks and
  discloses; pointing `--path` at locale JSON works around the i18n case.
- `kind` guessing (button/heading/error) is best-effort from the line's
  markup; the model re-judges kind from context when it matters.
- Bootstrap quality depends on the surfaces sampled — it describes the
  product's voice *at its best*, so sample the proudest screens, not all of them.

## 5. Audit rubric coverage

See `skill-architecture.md` §B; targets every applicable PASS. Keyless, no
network, no binaries → those items N/A. Artifact (A10) = the findings report
(records project, date, scope, spec source, disclosed gaps), written outside
the skills repo.

## 6. Notes

Composes with: design-md (DESIGN.md producer — a future version could grow a
voice section generator), audit-ui (label *presence* is its a11y dimension;
polish-copy owns label *quality*), build-ui/generate-prd (surfaces feed it),
render-html (branded report). Negative cases: long-form marketing/docs
authoring; generating copy from scratch.
