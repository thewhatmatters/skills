# blueprint — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-07-17  ·  Generator: hand-built to the generate-skill recipe @ CC 2.1.181

## 1. Purpose

Presentation-grade, house-branded architecture diagrams via the
validation-first pattern: agent-authored typed JSON IR → deterministic
gates (structural + layout) → stdlib renderer → self-contained themed
HTML/SVG. The slow, beautiful tier above draw-diagram's quick Mermaid
tier.

## 2. Reusable patterns (link to spec A1..A15)

Follows `~/.claude/skills/skill-architecture.md` A1–A15. Deliberate notes:
- A5/A7: keyless, no network, no external binaries → no setup gates at
  all; a failing preflight means a broken install (`down`), not a gap.
- A15c: draw-diagram and render-html are soft composes (routing/handoff
  only, never required).

## 3. Decision log

- 2026-07-17: **Built in-house instead of installing archify** — user
  declined third-party skill code on security grounds (archify runs
  bundled Node; the research's own open question #4). Every line here is
  ours, stdlib-only. Research basis:
  `<vault>/research/synthesis/archify-agent-diagram-skill.md`.
- 2026-07-17: **Pattern adopted from archify, code from scratch** — typed
  IR + path-prefixed validator errors + fix-the-JSON iteration + CSS-
  classes-only styling + dual-theme standalone SVG (their best technique;
  reimplemented, not copied).
- 2026-07-17: **Grid placement only** (rows 0–7, cols 0–5, spans) — no
  free coordinates; archify's own iteration lesson is that grid mode
  avoids coordinate arithmetic errors. Geometry constants are duplicated
  validate.py ↔ render.py deliberately (each script stays standalone;
  change both together).
- 2026-07-17: **v1 = architecture type only** (user's scope call);
  workflow/sequence/etc. ladder in later behind the same IR pattern.
  draw-diagram remains the router for those.
- 2026-07-17: **House brand, not archify's dark-neon** (user's call) —
  tokens shared with render-html's "Anthropic Reading" DESIGN.md; kind
  palette (clay/sage/violet/slate/ochre/gray) chosen muted to match.
- 2026-07-17: **Python stdlib renderer, not Node** (user's call + house
  convention): SVG is string assembly; no runtime beyond python3.
- 2026-07-17: Verified end-to-end at build time: example validates clean
  and renders both themes (screenshot-checked); 4-fault planted-error IR
  caught with exact paths + fixes; validator caught a real boundary-stray
  fault in the first draft of the bundled example (dogfood catch).

## 4. Known limitations / environment caveats

- Label-width gating is a char-count heuristic (7.5px/char at 14px sans),
  not text measurement — long all-caps labels can still run tight.
- Connection routing is single-elbow midpoint routing with no collision
  avoidance; dense meshes (>24 edges warns) can overlap lines. The
  spatial-narrative guidance (one main path) is the real mitigation.
- Design tokens are hard-coded in `render.py` (SVG_STYLE/SVG_VARS) and
  `assets/template.html` to stay stdlib — a DESIGN.md token change must
  touch both (called out in DESIGN.md Do's and Don'ts).
- PNG export happens client-side in the artifact (canvas); headless
  export isn't provided — use the artifact's buttons or `--svg`.
- Theme-toggle detection in template JS keys off the computed `--bp-bg`
  value; changing the background token requires updating that check.

## 5. Audit rubric coverage

See `skill-architecture.md` §B; secrets/network items N/A (keyless,
offline). Self-test lives in preflight (validate+render the bundled
example).

## 6. Notes

Roadmap candidates (not commitments): workflow type (swimlanes), sequence
type, a `--png` headless export via Playwright if ever needed, and a
draw-diagram handoff line once the user approves editing that skill.
