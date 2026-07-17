# Authoring the blueprint IR

Loaded when authoring a diagram (spec A1). The schema is
`schemas/architecture.schema.json`; the worked example is
`examples/web-app.architecture.json`. Study both before writing your first
IR — field shapes are learned, not guessed.

## The grid

Placement is `row`/`col` only (rows 0–7, cols 0–5) with optional
`rowspan` (≤4) / `colspan` (≤3). There are no free coordinates and no
pixel arithmetic — the renderer computes geometry from the grid. Cell
180×90, gutters 70. Max 16 components; past that, split the system into
two diagrams.

## Spatial narrative

- **Flow reads left→right** (clients on the left, stores on the right) or
  top→bottom for pipelines. Pick one axis and keep it.
- **One main path.** The primary request/data path should be traceable
  without crossing lines. Side concerns hang off it on short edges.
- **Label few edges.** Label the edges whose protocol/action isn't obvious;
  leave the rest bare. More than ~8 labels reads as noise.
- **Sublabels carry detail.** Tech names, roles, and qualifiers go in
  `sublabel`, not in longer labels.
- **Spans express importance.** A hub component (API, bus) may span 2 rows
  or cols so edges meet it cleanly; don't span for decoration.

## Kinds

`client`, `gateway`, `service`, `queue`, `store`, `external` — drives the
accent color and the legend. `external` also renders with a dashed card.
Omit `kind` for neutral cards. Don't invent kinds; the validator rejects
them.

## Boundaries

A boundary draws a dashed box around its members (trust zone, VPC, team
ownership). The members' grid cells must form a clean rectangle-ish
cluster: any non-member sitting inside the members' bounding box is a
validation error — restructure the grid so the boundary is honest. Nested
boundaries are allowed when one's members are a subset of the other's;
interlocking boundaries are rejected.

## Iteration rules (the loop)

1. `python3 scripts/validate.py <ir>.json` — **gates first.** Errors name
   the JSON path and propose the fix; apply the suggested fix rather than
   guessing (e.g. "shorten to ≤20 chars, or set colspan: 2").
2. `python3 scripts/render.py <ir>.json --out=<name>.blueprint.html` —
   only after the gates pass.
3. **Fix the JSON, never the output.** The HTML/SVG is generated; editing
   it forfeits regeneration. All refinement (user feedback included) is an
   IR edit followed by re-validate + re-render.
4. `--layout` on validate.py dumps computed boxes when you need to reason
   about geometry; `--svg` on render.py emits a standalone dual-theme SVG
   (honors the reader's `prefers-color-scheme` — good for GitHub READMEs).

## Naming

IR files are `<name>.architecture.json`; artifacts are
`<name>.blueprint.html` / `.svg`. Keep the IR next to the artifact — it is
the source of truth.
