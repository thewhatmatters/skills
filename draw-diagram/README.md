# draw-diagram

**What it is:** Turns a description into a Mermaid diagram (flowchart, user flow, ERD, sequence, state, architecture, requirement) and renders it as a fenced Markdown block, an SVG/PNG, or a self-contained HTML page.

## What you get

- A ` ```mermaid ` block by default — renders on GitHub, in docs, and inside `render-html`. Zero dependencies.
- Optionally a rendered **SVG/PNG** image, or a standalone **HTML** page.
- An optional **brand theme** (ivory/clay) that matches `render-html`.

## How to run

Say "draw a flowchart for our onboarding", "make an ERD of these tables", or run `/draw-diagram`. By default you get a Mermaid block; add `--format=svg`, `--format=png`, or `--format=html` for a rendered artifact, and `--theme=brand` for the house look.

## What it needs

Nothing to start — the default fenced block is pure Python standard library. For rendered **images**: Node 18+ (used on demand via `npx @mermaid-js/mermaid-cli`; the first run downloads the renderer). With no Node, it falls back to the Kroki web service (unless you pass `--no-network`), and if that's unavailable too, it still emits the Mermaid block. **No npm packages are committed** to the repo.

## How it works (high level)

1. Claude writes Mermaid syntax for the diagram type that fits your request.
2. A preflight (only when rendering to a file) checks the output location and what render engines are available.
3. The renderer walks a ladder: fenced block → `mmdc` image → Kroki web render → back to the fenced block — so it never hard-fails.
4. The result is written to your chosen path (or printed).

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/mermaid-reference.md` — diagram types, syntax guards, the brand theme, and composition notes.
