# Mermaid reference — types, guards, brand theme

Progressive-disclosure home (spec A1) for `draw-diagram`. Loaded only when
composing/rendering a diagram.

## Pick the type for the intent

> Full type catalog with official syntax-doc URLs (and which to WebFetch when
> unsure): [`diagram-types.md`](diagram-types.md). The quick table below covers
> the everyday ones.

| Intent | Mermaid type | Notes |
|---|---|---|
| Process / decision / **user flow** | `flowchart LR` (or `graph TD`) | LR default reads well |
| Interactions over time | `sequenceDiagram` | no notes if targeting FigJam later |
| Data model | `erDiagram`, `classDiagram` | |
| State machine | `stateDiagram-v2` | |
| Timeline / planning | `gantt`, `timeline`, `kanban` | |
| Architecture | `architecture-beta`, `block-beta`, `C4Context` | |
| **PRD-friendly** | `requirementDiagram`, `journey` (user journey), `mindmap`, `quadrantChart`, `pie` | |

The script validates the first token against this set and warns (does not fail)
on anything unknown.

## Syntax guards (avoid common parse breaks)

- **Quote edge and node-label text:** `A["Hard step"] -->|"Yes"| B(["Done"])`.
- **Never use a bare `end`** as a node id in flowcharts — it breaks the parser;
  wrap it: `["end"]`. (The script warns if it sees a bare `end`.)
- **No literal newlines inside labels** — use `<br/>`.
- Keep diagrams **simple by default**; add detail only when asked.
- For `flowchart`/`graph`, default to `LR` direction.

## Rendering ladder (what the script does)

1. `--format=mermaid` (default) → fenced ` ```mermaid ` block. Zero dependency;
   renders on GitHub/GitLab and in `render-html` via mermaid.js.
2. `--format=svg|png` → `mmdc` (resolved as `$MMDC_BIN` → `mmdc` → `npx -y
   @mermaid-js/mermaid-cli`). First npx run downloads mermaid-cli + a Puppeteer
   Chromium (one-time, slow).
3. If no Node/mmdc → **Kroki** HTTP render (`--render=auto`), unless
   `--no-network`. Kroki sends the diagram off-box — opt-in by design.
4. If neither → degrade to the fenced block with a notice (never hard-fail
   unless `--render=mmdc|kroki` was explicitly requested).

## Brand theme (matches render-html)

`--theme=brand` prepends a one-line init directive so mmdc, Kroki, and the
browser all theme identically:

```
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#F7F6F2",
"primaryTextColor":"#191917","primaryBorderColor":"#CC785C",
"lineColor":"#B0613F","secondaryColor":"#E7E4D8","tertiaryColor":"#F0EEE6"}} }%%
```

Palette mirrors `render-html`: ivory background `#F0EEE6`, clay accent `#CC785C`,
slate text `#191917`. For SVG/PNG the script also passes `mmdc -b #F0EEE6`.

## Composition

- **render-html:** drop a ` ```mermaid ` block into the Markdown you pass to
  `render-html`; it embeds mermaid.js so the diagram renders in the branded
  page. Or generate `--format=html` directly here.
- **generate-prd:** include diagram blocks in PRD sections (the "product
  requirement diagrams" use case).
- **FigJam (possible future target):** the Figma MCP `generate_diagram` accepts
  Mermaid but supports only `graph`/`flowchart`, `sequenceDiagram`,
  `stateDiagram`, `gantt`, `erDiagram` — validate against that narrower set
  before exporting there.

## Node policy

Node is used **only** via `npx` on demand. There is **no committed
`node_modules`** (it's gitignored generated junk, and mmdc's Puppeteer Chromium
is large and platform-specific). If a pinned local renderer is ever wanted, the
only acceptable form is a committed `package.json` + a gitignored `node_modules`
installed through a preflight setup gate — never a committed dependency tree.
