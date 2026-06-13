# use-grid-system — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-06-13  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
Make a real Müller-Brockmann modular grid load-bearing in a web project — one
`@theme` source of truth, subgrid bands placed by column line, an 8px baseline,
a toggleable overlay, and runtime optical alignment — then prove it adheres.

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Notable applications:
- **A1 progressive disclosure** — the canon + Tailwind layer + profiles + optical
  + verification + non-Tailwind fallback all live in `references/`; SKILL.md stays
  lean and routes to them.
- **A3 dual-mode + degraded ladder** — SCRIPTS (`grid_tokens.py`/`probe.py`) →
  NATIVE (emit by hand from references); Tailwind v4 → v3 → vanilla `:root`.
- **A7/A8 setup-gate + no-monoculture** — probe first; never impose Tailwind,
  never silently re-scale a live project's `--spacing`.
- **A8 composition by reference** — build-ui (execution), frontend-design (taste),
  audit-ui/automate-browser (verification), design-md (token spec), source-ui
  (reference). Runs none of their code; no bespoke Puppeteer verifier.

## 3. Decision log
- 2026-06-13: scaffolded by generate-skill.
- **Built from research, not from scratch.** Architecture is the proposal in
  `references/research-rationale.md`; the canon is `references/canon.md`. Both
  grounded against the canonical book (162-pp scan, OCR'd — the scratch ingest
  folder was reference-only and removed; recoverable from git history @ 3515745)
  and a live working example (`hyperagent.com/s/koRV0F0BWOD12os3U2L74w`,
  validated via Playwright).
- **In Tailwind v4 the grid IS tokens.** v4's spacing scale is
  `calc(var(--spacing) * n)` off one base, so the 8px baseline tokenizes directly;
  the prior skill's hand-rolled `--bl/--lh` source of truth becomes one `@theme`
  block. Subgrid is Baseline (Mar 15 2026) → "place by column line" is
  `grid-cols-subgrid` + `col-start/col-end` with an `@supports` fallback.
- **Keep the runtime optical-alignment JS.** `text-box-trim`/`text-box-edge`
  (renamed from `leading-trim`) is NOT Baseline as of Apr 2026, so the canvas
  `actualBoundingBoxLeft` nudge stays the cross-browser path; `text-box-trim` is
  progressive enhancement only.
- **Compose the overlay + verifier, don't rebuild.** `tailwindcss-react-grid-
  overlay` already ships a `g`-key column overlay (React); we add the baseline
  layer and standardize on `g`. Verification runs as an audit-ui dimension, not a
  parallel Chrome driver (the export's platform-foreign Puppeteer flags are dropped
  on the way in).
- **Two profiles in v1.** `editorial` (strict whole-field) and `app` (column-line
  + baseline, relaxed rows) — the user's target is web apps, but the canon and the
  live example are editorial, so both ship.
- **needs_design = No.** Visual taste defers to frontend-design / design-md; the
  `## Grid` DESIGN.md block this skill emits is a *project* token spec (consumed),
  not the skill's own brand identity.

## 4. Known limitations / environment caveats
- **`--spacing` re-scale footgun.** Setting `--spacing: 0.5rem` doubles every
  default Tailwind spacing utility. Default to keeping the 4px base + an additive
  grid namespace; the probe surfaces the current base so we don't re-scale silently.
- **Optical alignment is font-specific & headless-fragile.** Measuring with the
  wrong font gives the wrong nudge (≈ −16px fallback vs −7px real Inter for the
  same `H`). Verification must embed the real webfont or measure in-browser.
- **Subgrid `@supports` fallback** must be tested above and below `--maxw` (the
  centered-container drift the prior export documents).
- Published artifacts in sandboxed iframes (e.g. `pub.hyperagent.com`) can't auth
  thread-scoped URLs — moot for in-project rendering, but the reason the overlay
  must read only `@theme` CSS variables and make no external calls.

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.
Verification (the four adherence checks) is delegated to audit-ui by design — see
`references/verification.md`.

## 6. Notes
Upstream knowledge (do not re-derive): the prior `müller-brockmann.json` skill
export (vanilla-CSS + Puppeteer, editorial-scoped, foreign platform) is the source
of the overlay CSS, the subgrid-band trick, and the optical-alignment JS, ported
here to Tailwind + house composition. Open scope questions tracked in the research
report's "Open questions" section.
