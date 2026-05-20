# html-output — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-19  ·  Generator: skill-generator @ CC 2.1.145

## 1. Purpose
Render a Markdown file into one self-contained, on-brand (anthropic.com) HTML page.

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` patterns A1–A13. Notable points:
- **A1** progressive disclosure: the full brand system + CSS shell live in
  `references/brand-style.md`, not SKILL.md.
- **A3** mode probe: SCRIPTS (python3 + `render.py`) with a real NATIVE
  fallback — Claude hand-converts the Markdown and wraps it in the documented
  shell.
- **A10** self-contained artifact: one HTML file, inline CSS, records source
  filename + render date.

## 3. Decision log
- 2026-05-19: scaffolded by skill-generator.
- 2026-05-19: **Markdown input, not JSON.** Unlike deep-research/prd-generator
  (which render structured JSON from the model), this skill ingests an existing
  Markdown file, so it needs a real Markdown→HTML converter. Written stdlib-only
  (no `markdown` pip dep) to honor "no heavyweight dependency" (spec A4/A11).
- 2026-05-19: **Brand fonts are licensed → free substitutes.** Styrene and
  Tiempos are not bundled. Stacks name them first (render if installed), then
  Hanken Grotesk / Source Serif 4 from Google Fonts, then system fonts. The
  Google Fonts `<link>` is the only external reference and loads at *view* time,
  never at render time. `--no-webfonts` produces a fully offline file.
- 2026-05-19: **Standalone skill, not a shared asset.** Decided with the user:
  this does not refactor the inline CSS in deep-research/prd-generator/trendscan
  `report.py`. It is an on-demand Markdown→HTML transform. Those scripts could
  later be pointed at this style, but that was explicitly out of scope.
- 2026-05-19: **CSS as a plain (unformatted) string.** `render.py` assembles the
  document by concatenation and keeps `CSS` out of any `.format()`/f-string, so
  the large stylesheet needs no brace-doubling — less error-prone than the
  `.format()` TEMPLATE approach used by the older report.py scripts.
- 2026-05-19: **Web fonts ON by default (conscious A10 waiver).** The output's
  one external reference is the Google Fonts `<link>`. Spec A10 favors fully
  inline assets, but the user chose the brand look as the default over literal
  self-containment. Mitigations: the system serif/sans stack renders fine if
  the link fails (offline), and `--no-webfonts` produces a zero-external-ref
  file. Rejected alternatives: flipping the default to offline (weaker brand
  match out of the box) and base64-embedding the fonts (output bloat + an
  embedding-license question). Auditor flagged this 🟡; resolved as waiver,
  not a bug.
- 2026-05-19: **Referenced opt-in by deep-research & prd-generator.** Those two
  write a Markdown file (`research-<slug>.md` / `prd-<slug>.md`), so their
  SKILL.md now notes /html-output as a branded-HTML alternative to render that
  `.md`. Chose *reference*, not *invocation*: no script-to-script coupling,
  each skill stays self-contained, and their JSON→HTML report.py (with
  source-badge fidelity) is retained. trendscan was deliberately excluded — its
  HTML is the primary deliverable in a card/dashboard layout with no markdown
  intermediate, a poor fit for this article renderer.
- 2026-05-19: **Audit follow-ups.** `render.py` now auto-derives `<input>.html`
  when `--out` is omitted (docs matched to reality), with `--stdout` to force
  stdout; `--agent` is accepted as a documented no-op for flag consistency
  (the renderer never prompts).

## 4. Known limitations / environment caveats
- Markdown converter is intentionally small: single-level lists only; no image
  or raw-HTML pass-through; no emphasis inside link text. Covers the constructs
  the repo's own reports use. Extend `render.py` if a source needs more.
- Output is a brand *approximation* — not pixel-identical to anthropic.com,
  by font license and by design.

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.
Secrets rows are N/A (keyless, no network).

## 6. Notes
Pure local file transform: no network, no secrets at run time. Pairs with the
HTML companions emitted by deep-research / prd-generator / trendscan when a
single on-brand visual style is wanted.
