# draw-diagram — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-21  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
Turn intent into a Mermaid diagram and render it through a graceful degraded
ladder (fenced block → mmdc SVG/PNG → Kroki → fenced block).

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Notable:
- **A1** progressive disclosure: types/guards/brand theme in
  `references/mermaid-reference.md`, not SKILL.md.
- **A3** degraded path: the fenced ```mermaid block is the always-works core;
  Node and network are optional capabilities.
- **A11** layered binary resolution: `$MMDC_BIN` → `mmdc` → `npx`.
- **A10** self-contained artifact (HTML/SVG/MD).

## 3. Decision log
- 2026-05-21: scaffolded by generate-skill.
- 2026-05-21: **Mermaid as the source of truth, multiple render targets.**
  Scope is open-source Mermaid (local) — not the hosted Mermaid AI/Chart
  product (the user's reference, mermaid.ai/open-source/intro, documents the
  distinction). Targets: `mermaid` (default) / `svg` / `png` / `html`.
- 2026-05-21: **No committed `node_modules` — npx on demand.** Decided with the
  user. `node_modules` is gitignored generated junk, and mmdc's Puppeteer
  Chromium is large + platform-specific. mmdc runs via `npx -y
  @mermaid-js/mermaid-cli` (Node v22 + npx verified present in this env). If a
  pinned renderer is ever wanted, the only acceptable form is a committed
  `package.json` + gitignored `node_modules` via a preflight setup gate.
- 2026-05-21: **Kroki is opt-in egress.** The HTTP fallback sends the diagram
  off-box, so it's gated behind `--render` selection and disabled by
  `--no-network`; never the silent default over the local/fenced paths.
- 2026-05-21: **One theming mechanism.** `--theme=brand` prepends a single
  `%%{init}%%` directive (matching the render-html ivory/clay palette) so mmdc,
  Kroki, and the browser theme identically; mmdc additionally gets `-b #F0EEE6`.

## 4. Known limitations / environment caveats
- First `npx mmdc` run downloads mermaid-cli + a Puppeteer Chromium (one-time,
  slow); the fenced block stays instant.
- `png` requires `--out` (binary, not streamed to stdout).
- Syntax validation is lightweight (type check + a few guards), not a full
  parse; malformed Mermaid surfaces as an mmdc/Kroki error.
- The Figma FigJam path is NOT implemented; if added later, its
  `generate_diagram` supports only a subset of types (validate first).

## 5. Audit rubric coverage
See `skill-architecture.md` §B. Secrets rows are N/A (keyless). Network/Node are
optional, gated, and degrade — not setup gates that block.

## 6. Notes
Pure-stdlib Python core. Composes (referenced, decoupled) with `render-html`
(branded HTML embed) and `generate-prd` (PRD diagrams). Node optional via npx;
network optional via Kroki.
