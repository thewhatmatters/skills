# blueprint

**What it is:** presentation-grade architecture diagrams in the house
brand — described in plain English, drawn by deterministic code, and
guaranteed tidy by validators before anything renders.

## What you get

- A self-contained HTML artifact (no dependencies, works offline) with a
  light/dark theme toggle and one-click SVG / 2× PNG download.
- Optionally a standalone dual-theme SVG that adapts to the reader's
  system theme — drop it straight into a GitHub README.
- The JSON source file next to the artifact, so any future session can
  edit and re-render instead of redrawing.

## How to run

Say "blueprint this system" or "make a presentation-grade architecture
diagram of X". Example: "blueprint the tm-app runtime — clients, API,
queue, Postgres, and the external mail provider."

For quick sketches, flowcharts, or sequence diagrams use draw-diagram
instead — blueprint is the slow, polished tier and (in v1) draws
architecture diagrams only.

## What it needs

Nothing beyond Python 3 (present on macOS). No API keys, no network, no
Node, no third-party code — every line that runs is in this folder.

## How it works (high level)

1. Claude turns your description into a small JSON file: components on a
   grid, boundaries, connections.
2. A validator checks it — overlapping cards, labels too wide, boundaries
   that would swallow non-members, dangling connections — and says exactly
   what to fix.
3. Only when the checks pass does the renderer draw it: house-brand
   colors, serif title, muted kind accents, orthogonal arrows.
4. Feedback ("add Redis", "move the worker") edits the JSON and
   re-renders — the output file is never hand-edited.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `DESIGN.md` — the visual identity (shared with render-html's look).
- `references/ir-guide.md` — how the JSON source format works.
