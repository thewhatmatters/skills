---
name: draw-diagram
description: Turn intent into Mermaid diagrams — flowcharts, user flows, ERDs, sequence, state, architecture, and requirement diagrams — and render them as a fenced Markdown block, an SVG/PNG, or a self-contained HTML page. Use when the user wants to draw or generate a diagram, flow, or chart from a description — "draw a diagram", "make a flowchart", "diagram this", "user flow for X", "sequence/ER/state/architecture diagram", "visualize this process", "turn this into mermaid", "add a PRD diagram". Generates Mermaid syntax (the source of truth) and renders it through a graceful ladder: the fenced block always works; SVG/PNG come from the mmdc CLI (global or via npx) with a Kroki network fallback. Composes with render-html (branded embed) and generate-prd. Pure-stdlib Python core; Node and network are optional.
---

# draw-diagram

Generate a Mermaid diagram from intent and render it.

## What it does

The model writes **Mermaid syntax** (the artifact and source of truth); a small
stdlib script renders it through a degraded ladder — a fenced ```mermaid block
(zero dependency), an SVG/PNG via the `mmdc` CLI, a Kroki HTTP render, or a
self-contained HTML page. Node and the network are optional capabilities, never
required. Supported types, syntax guards, and the brand theme live in
[`references/mermaid-reference.md`](references/mermaid-reference.md) (spec A1).

## How to run

Trigger with "draw a flowchart for …", "diagram this process", "make an ERD of
…", or `/draw-diagram`. The model composes the Mermaid; the script renders it.
Default output is a fenced ```mermaid block; ask for `--format=svg|png|html` for
a rendered artifact.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9). No-op — nothing prompts |
| `--out=PATH` | output location (spec A9); default derives from input or stdout |
| `--format=` | `mermaid` (default) · `svg` · `png` · `html` |
| `--render=` | raster engine for svg/png: `auto` (default) · `mmdc` · `kroki` · `none` |
| `--theme=` | `brand` (ivory/clay, matches render-html) · `default` |
| `--title=STR` | diagram name / HTML title |
| `--no-network` | forbid Kroki egress (offline-safe) |

## Step 0 — Mode probe

Run `python3 --version`. If python3 + `scripts/` are present, mode = **SCRIPTS**
(use `scripts/diagram.py`). Otherwise mode = **NATIVE**: emit the Mermaid as a
fenced ```mermaid block yourself (it renders on GitHub and in many viewers) —
the zero-dependency path needs no script. Announce the mode in one line.

## Steps (SCRIPTS mode)

1. **Choose the type, then compose.** Pick the diagram type that fits the
   user's intent using the "Use when" table in
   [`references/diagram-types.md`](references/diagram-types.md). For common
   types (flowchart, sequence, class, state, ER, gantt, pie) write the Mermaid
   directly; if you're not fully confident of the syntax — **especially the
   newer/experimental types flagged there** — WebFetch that type's official doc
   URL first. Apply the syntax guards in
   [`references/mermaid-reference.md`](references/mermaid-reference.md).
2. **Preflight (only when rendering svg/png/html to a file):**
   `python3 scripts/preflight.py --out=<dest>` — probes output writability,
   mmdc/npx, and Kroki reachability. `down` only on an unwritable target.
3. **Render.** Pipe the Mermaid into `python3 scripts/diagram.py --format=…
   [--theme=brand] [--out=…]`. The ladder degrades automatically; an
   explicitly-requested engine (`--render=mmdc|kroki`) errors if unavailable.
4. **Report** the output path and which engine rendered it (or that it degraded
   to a fenced block).

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- Degraded path (A3) + layered binary resolution (A11): `$MMDC_BIN` → `mmdc` →
  `npx @mermaid-js/mermaid-cli` → Kroki → fenced block.
- Keyless: no secrets, no `_env.py`. Node via **npx on-demand** — **never a
  committed `node_modules`**.
- Composes (referenced, decoupled) with `render-html` (branded HTML embed) and
  `generate-prd` (PRD diagrams) — no hard cross-skill imports.
