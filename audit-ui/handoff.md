# audit-ui — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-06-10  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose

Layered pre-ship UI audit: a11y + responsive visual + Core Web Vitals +
token drift, severity-grouped, report-only.

## 2. Reusable patterns (link to spec A1..A13)

Follows `~/.claude/skills/skill-architecture.md` A1–A13. Deliberate shape notes:

- **A1**: one reference per dimension, loaded only for scoped dimensions.
- **A3**: NATIVE mode = static dimensions only (tokens by hand-grep + judgment
  a11y on source); live dimensions honestly unavailable without scripts.
- **A6**: preflight is per-dimension — a gated check disables its dimension,
  never the run. `overall` is the worst state but anything except `down` is
  runnable-in-part.
- **A7**: `SERVER_UNREACHABLE` is the canonical gate — the fix (start the dev
  server) is the user's; the skill never starts servers or mutates the project.
- **A8**: dimension picker = one AskUserQuestion multiSelect (4 options, fits
  the UI cap) annotated with live preflight status — scan-trends' pattern.
- **A11**: axe-core `$AXE_JS → .cache → CDN-once`; Lighthouse
  `$LIGHTHOUSE_BIN → PATH → npx`. No committed vendored JS, no node_modules.

## 3. Decision log

- 2026-06-10: built per the 2026 frontend-skills research
  (`/tmp/research-frontend-skills-2026.md`): the consensus layered pattern is
  "deterministic engine as the floor + agent judgment for what tools can't
  decide" — encoded as the two-layer a11y dimension and the model-reviews-
  screenshots visual dimension.
- 2026-06-10: **token drift folded in as a dimension**, not a separate skill —
  anti-sprawl; it's the enforcement layer of the design-md → build-ui pipeline.
- 2026-06-10: **no pixel-diff baselines in v1** — baseline management is CI
  machinery (Docker font determinism, update workflows); the model reading
  breakpoint screenshots catches the pre-ship breakage class. Revisit only if
  regressions slip through repeated audits.
- 2026-06-10: **own Playwright scripts rather than automate-browser's
  browser.py** — cross-skill *imports* are forbidden (A8) and its CLI doesn't
  do axe injection or viewport sweeps; the persistent login profile isn't
  needed for localhost dev audits. Limitation: auth-walled pages aren't
  reachable in v1 (noted below).
- 2026-06-10: **INP honesty rule** — Lighthouse is lab; TBT is the proxy; the
  skill never reports "INP" from lab data (references/vitals.md leads with it).
- 2026-06-10: vitals on a dev server is directional-only, never 🔴 — dev
  builds fail budgets by design.

## 4. Known limitations / environment caveats

- Auth-walled pages: no login profile in v1 — audit public/dev routes, or use
  automate-browser to verify auth flows separately.
- axe ≈ 30–50% WCAG coverage; the judgment layer narrows, never closes, the
  gap. Not a conformance certification.
- Lighthouse run-to-run variance ±10%; near-miss budgets are re-run before 🟠.
- token_drift caps at 200 findings / 2000 files, disclosed in output
  (`truncated`) — no silent caps.
- Dark-mode captures are opt-in; default screenshots are OS-light only.

## 5. Audit rubric coverage

See `skill-architecture.md` §B; targets every applicable PASS. Keyless →
secrets items N/A. Artifact (A10) = the findings report markdown (records
target, date, dimensions run/skipped) + screenshots under `--out`'s dir;
written outside the skills repo.

## 6. Notes

Composes with: automate-browser (Playwright sibling; auth flows + interaction
checks), build-ui (applies the fixes), design-md (produces the token spec),
add-motion (reduced-motion findings route to it), render-html (branded report),
decompose-prd (embed "audit-ui passes" as a story criterion). Negative cases:
audit-skill audits skills; build-ui implements.
