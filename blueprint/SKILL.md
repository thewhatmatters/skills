---
name: blueprint
description: Produce a presentation-grade, house-branded architecture diagram as a self-contained themed HTML/SVG artifact — the agent authors a typed JSON IR (grid-placed components, boundaries, connections), deterministic validators gate it (overlaps, label budgets, boundary honesty), and a stdlib renderer draws it in the anthropic.com look with light/dark toggle and SVG/PNG export. Use when the user wants a polished, shareable, exportable system diagram — "blueprint this system", "blueprint the architecture", "presentation-grade architecture diagram", "polished system map I can share", "branded architecture diagram", "diagram this for the deck/README", "make a proper architecture artifact of X". Iterates by editing the IR and re-rendering, never by touching output. NOT for quick inline diagrams, flowcharts, sequence/ER/state charts, or Mermaid fences — that is draw-diagram; blueprint is the slow, beautiful tier for architecture only (v1).
---

# blueprint

Validation-first architecture diagrams: author a typed **IR**, pass the
**gates**, render the artifact. **Fix-the-JSON** — never the output.

## Leading words

- **IR** — the typed `<name>.architecture.json` the agent authors against `schemas/architecture.schema.json`; the single source of truth.
- **gates** — `validate.py`'s structural + layout checks; every error names the JSON path and proposes the fix. Render only after the gates pass.
- **fix-the-JSON** — all iteration (including user feedback) edits the IR and re-renders; generated output is never hand-edited.

## How to run

"blueprint this system", "presentation-grade architecture diagram of X",
or `/blueprint`. Quick/inline/Mermaid asks route to **draw-diagram**, not
here.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | artifact path (default `./<name>.blueprint.html`; no clobber — suffix `-2`, `-3`, …) |
| `--svg` | also emit a standalone dual-theme SVG (`prefers-color-scheme`-aware) |

## Step 0 — Mode probe

`python3 --version` + `scripts/` present → **SCRIPTS**. No python3 →
**NATIVE**: hand-place SVG into `assets/template.html` following
`DESIGN.md`'s classes and tokens — disclose that the gates didn't run.

## Step 1 — Preflight

`python3 scripts/preflight.py` — asset presence + a live validate+render
self-test. `down` → STOP (broken install; suggest `git -C ~/.claude pull`).
No setup gates: keyless, no network, no external binaries.

## Step 2 — Fit check

Architecture/system-map ask → proceed. Flowchart, sequence, ER, state,
user-flow, or "quick diagram" ask → hand off to **draw-diagram** (soft
compose) and stop. Both apply → offer both tiers in one line.

## Step 3 — Author the IR

Read `references/ir-guide.md` + the example, then write
`<name>.architecture.json`: grid placement, one main path left→right, few
labeled edges, detail in sublabels, honest boundaries. Confirm scope with
the user only if the component list is ambiguous (`--agent`: proceed with
the most load-bearing ≤12 components).

## Step 4 — Gates, then render

1. `python3 scripts/validate.py <ir>.json` — apply each error's suggested
   fix to the IR; re-run until clean. Never render past failing gates.
2. Pick `<out>`: if the target file exists, suffix `-2`, `-3`, … —
   render.py itself overwrites. Then
   `python3 scripts/render.py <ir>.json --out=<out>` (+ rerun with `--svg`
   if asked). Report the artifact path; on macOS offer `open <out>`.

## Step 5 — Iterate

User feedback ("add Redis", "move the queue left", "rename that box") →
edit the IR → Step 4 again. The IR file stays next to the artifact as its
source of truth.

## Conventions this skill follows

- Spec is `~/.cursor/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4); pure stdlib, keyless, no network.
- The visual identity lives in `DESIGN.md` (house brand); scripts hard-code the token values to stay stdlib — change both together.
- Composes with draw-diagram (quick Mermaid tier) and render-html (documents); blueprint owns only the presentation-grade architecture artifact.
