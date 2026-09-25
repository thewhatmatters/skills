---
name: mdxcn
description: Use this when a shadcn + Next.js App Router app's MDX content (docs pages, blog posts, changelogs, RFCs, postmortems, READMEs) needs framed callouts, steps, terminal sessions, changelogs, quotes, or ASCII-style charts/tables/timelines/trees from mdxcn (mdxcn.dev), or when the user mentions mdxcn, GraphTable, GraphTimeline, GraphFlow, ::graph-* blocks, or framed ASCII figures. It adds content components on top of an MDX pipeline; it is not the MDX pipeline itself.
---

# mdxcn

mdxcn is a free, MIT-licensed set of content components for MDX: callouts, quotes, steps, terminals, changelogs, and about 30 ASCII-style charts, tables, timelines, and trees. You copy them into a shadcn project with the shadcn CLI. There is no npm package of components. Each figure sits in a dashed frame with `+` corners and a `[ TITLE ]` on the top edge. The glyphs are characters, not SVG. The same figures can be written four ways: JSX in MDX, `::graph-*` blocks for Comark, `graph_*` filters for Knap, and official fenced ASCII for plain Markdown.

## When to use / when not to

Use it when:
- MDX pages in a shadcn app need an aside (`Callout`), a procedure (`Steps`), a shell session (`Terminal`), a release note (`Changelog`), a quote (`Quote`), or a small figure that scans faster than bullets (timeline, flow, table, tree, diff, and so on).
- A README, PR comment, or other plain-Markdown host needs the same figure. Paste the official fenced ASCII there.
- The content is Comark-rendered `.md` or Knap-generated Markdown (see Plugins/adapters).

Don't use it for:
- **The MDX pipeline itself.** mdxcn does not ship `@next/mdx` config, remark/rehype plugins, prose typography, or syntax highlighting. Set those up separately (see Install and wire).
- Source code blocks. Upstream rule: "Source code is a fenced code block"; `Terminal` is only for commands and their output.
- One-sentence notes, pie charts (use `GraphStack` or `GraphWaffle`), or anything that needs SVG, Mermaid, Recharts, or canvas.
- More than two figures in one section. Put prose between figures, and don't build a gallery.

## Install and wire

Before you start, you need an existing shadcn project (`components.json`, `@/lib/utils` `cn`) and the `motion` dependency. The CLI installs `motion` for you because every item lists it as a dependency.

```bash
# everything: all components, the shared frame, and the Comark + Knap adapters
pnpm dlx shadcn@latest add https://mdxcn.dev/r/all.json
# or one item (slug = registry name, e.g. callout, steps, terminal, graph-table)
pnpm dlx shadcn@latest add https://mdxcn.dev/r/graph-table.json
```

Optional namespace (from the mdxcn README):

```bash
pnpm dlx shadcn@latest registry add @mdxcn=https://mdxcn.dev/r/{name}.json
pnpm dlx shadcn@latest add @mdxcn/graph-table
```

This produces `"registries": { "@mdxcn": "https://mdxcn.dev/r/{name}.json" }` in `components.json`. The shadcn CLI docs don't list a `registry add` subcommand. If it fails, add that `registries` entry to `components.json` by hand (a documented shadcn feature), or use the full URLs.

Where the files go:
- Files land under `@/registry/default/<slug>/<slug>.tsx`, and every item also copies `graph-frame`.
- Import by folder, with no barrel. Add your own barrel if you want one.

```tsx
import { GraphTable } from "@/registry/default/graph-table/graph-table"
```

**MDX pipeline (Next.js App Router, from the Next.js MDX guide).** mdxcn only says to "register the parent once in mdx-components.tsx". It doesn't document `next-mdx-remote`, content-collections, or other loaders. With `@next/mdx`:

```bash
pnpm add @next/mdx @mdx-js/loader @mdx-js/react @types/mdx
```

```js
// next.config.mjs (remark/rehype plugins are ESM-only, so use .mjs or .ts)
import createMDX from "@next/mdx"
const nextConfig = { pageExtensions: ["js", "jsx", "md", "mdx", "ts", "tsx"] }
const withMDX = createMDX({
  // With Turbopack, plugins must be given as strings with serializable options.
  options: { remarkPlugins: ["remark-gfm"], rehypePlugins: [] },
})
export default withMDX(nextConfig)
```

`remark-gfm` is not an mdxcn plugin. Plain MDX doesn't parse pipe tables or `- [x]` task lists. The table-reading components (`GraphTable`, `GraphSheet`, `GraphCompare`, `GraphMatrix`, `GraphInvoice`, `GraphHeatmap`) look for a real `<table>`, and `GraphCheck` reads GFM checkbox `<input>`s. So enable GFM if you write those as markdown children.

**Register the parent once** (the pattern from the mdxcn docs MDX tab). Also register the child tags a component exports if you use them as JSX, e.g. `Step`, `Change`, or `Event`:

```tsx
// mdx-components.tsx (project root, or src/). Required by @next/mdx in the App Router.
import type { MDXComponents } from "mdx/types"
import { Callout } from "@/registry/default/callout/callout"
import { Step, Steps } from "@/registry/default/steps/steps"
import { Terminal } from "@/registry/default/terminal/terminal"
import { GraphTable } from "@/registry/default/graph-table/graph-table"
import { GraphTimeline } from "@/registry/default/graph-timeline/graph-timeline"

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return { ...components, Callout, Step, Steps, Terminal, GraphTable, GraphTimeline }
}
```

RSC vs client:
- The components are `"use client"` because they animate with `motion/react`. MDX pages stay Server Components, and the graphs arrive as client references.
- The parent reads its markdown children by tag name (`ul`/`ol`/`li`, `p`, `table`, `h1`–`h6`, `input`), and also matches RSC client-reference ids. You don't need extra imports for the lists or tables inside.

## Main components and patterns

All of these are verified from the docs, the registry, and `/api/v1/components`.
- **Content:** `Callout` (`type`: note | tip | warning | danger, `title`), `Quote` (`by`, `source`, `title`), `Steps`/`Step`, `Terminal` (`title` default "shell", `prompt` default "$"), `Changelog`/`Change` (`version`, `date`).
- **Graphs:** `GraphFlow`, `GraphTimeline`, `GraphTree`, `GraphGantt`, `GraphStat`, `GraphSpec`, `GraphCheck`, `GraphDiff`, `GraphKpi`, `GraphTable`, `GraphSheet`, `GraphCompare`, `GraphMatrix`, `GraphInvoice`, `GraphRank`, `GraphFunnel`, `GraphSlope`, `GraphBullet`, `GraphWaterfall`, `GraphStack`, `GraphSpark`, `GraphPlot`, `GraphMeter`, `GraphWaffle`, `GraphCells`, `GraphBars`, `GraphHeatmap`, `GraphActivity`, `GraphUptime`, `GraphCalendar`, `GraphTimer`, `GraphCountdown`.
- **Primitive:** `graph-frame`, which you only need for custom figures.

Common props:
- Every graph takes `title`, `corner` (default `"+"`), and `className`.
- Drawing graphs also take `palette` (`"mono"` default, or `"duo"` / `"multi"`) and `glyphs` (`shade`, `ascii`, `hash`, `bar`, or your own characters).
- Don't pass `palette` to Table, Sheet, Invoice, Spec, Stat, Tree, or Frame.

Most graphs accept either typed props (e.g. `events`, `rows`, `headers`) or markdown children. Copy the props from the component's docs page (`https://mdxcn.dev/docs/<slug>`) or `https://mdxcn.dev/llms.txt`. Don't guess prop shapes.

````mdx
<Callout type="warning">
  The CLI copies files into registry/default. It does not add an npm
  dependency, so there is nothing to update later — edit the source.
</Callout>

<GraphTimeline title="NIGHT">

- 14:02: p95 crossed 800ms
- **14:11: rolled back the cache flag**
- *14:40: write the postmortem*

</GraphTimeline>

<GraphTable title="COST">

| Agent | Tokens |
| --- | ---: |
| Inks and paper | 115,207 |

</GraphTable>

<Terminal title="SHELL">
```
$ pnpm dlx shadcn@latest add @mdxcn/callout
✓ registry/default/callout/callout.tsx
```
</Terminal>
````

Conventions:
- In lists, bold marks the current item and italic marks the next one (Timeline, Steps).
- Keep blank lines around markdown inside JSX tags.
- Titles are 1–2 words, uppercase, no punctuation.
- Labels are lowercase and plain.

Chooser (upstream recipes):

| Writing | Figures |
| --- | --- |
| refactor | `GraphFlow` + `GraphTimeline` |
| incident | `GraphTimeline` + `GraphUptime` |
| A vs B | `GraphCompare` + `GraphRank` |
| PR | `GraphDiff` + `GraphSlope` |
| sprint | `GraphGantt` + `GraphStat` |
| migration | `GraphMeter` + `GraphKpi` |
| files | `GraphTree` |
| RFC or launch list | `GraphSheet` + `GraphCheck` |

**Plain Markdown hosts** (README, GitHub, PR comments, Linear): don't paste JSX. Paste the official fenced ASCII from `llms.txt` `## MDX` (or the docs MDX tab), swap the labels, and keep the frame. These have no fenced ASCII, so pick another figure or skip it: Flow, Plot, Activity, Heatmap, Calendar, Timer, Countdown, Frame.

## Plugins

mdxcn ships **no remark or rehype plugins** and **no code-highlighting approach**. Its only integrations are two registry adapters, both included in `all.json`:
- **`graph-comark`** is for Comark-rendered plain `.md` files (`::graph-*` blocks with YAML props, and `::row{cols=2}` for side-by-side figures).
  - Wire it on the server: `import { parseMarkdown } from "comark"`, `import { MarkdownDocument } from "@comark/react"`, then `<MarkdownDocument components={graphComponents} value={doc.document} />`.
  - Import `graphComponents` from `@/registry/default/graph-comark/graph-comark`. For a subset of graphs, use `createGraphComponents({...})`.
  - Install the graphs first. `graph-comark.tsx` imports every graph.
- **`graph-knap`** is for Knap templates (`{{ events | graph_timeline:"NIGHT" }}`).
  - Run `pnpm add knap`, then `createEngine({ filters: { ...standardFilters, ...graphFilters } })`. For a subset, use `createGraphFilters([...])`.
  - The Knap CLI (`npx knap render`) does not load these filters.

For syntax highlighting, frontmatter, heading slugs, and similar, pick your own remark/rehype plugins through `@next/mdx` `options`. That choice is outside mdxcn, and its docs don't recommend any.

## Pitfalls

- **Not a package.** Updates mean re-running the CLI or editing the copied source. The docs don't say how re-adding interacts with local edits, so diff before you overwrite.
- **Tailwind v4 in practice.** Each item injects `cssVars.theme` (`--color-graph-*`), `:root`/`.dark` values (`--graph-accent`, `--graph-accent-2`, `--graph-accent-3`, `--graph-frame`, `--graph-muted`, `--graph-faint`, `--contrast-14/23/45/70`), and `@utility graph-frame`, `graph-rule`, and `graph-rule-y`. shadcn documents `cssVars.theme` as the Tailwind v4 mechanism. The mdxcn docs don't state a minimum version. The reference site runs Next 16.3.4, React 19.2.4, motion ^13, Tailwind 4, and shadcn CLI ^4.19. Treat that as the tested stack, not a hard floor.
- **Depends on shadcn tokens.** Components use `bg-background`, `text-foreground`, `text-destructive`, and `font-mono`. The upstream design assumes Geist Mono as the mono font, and alignment depends on a true monospace font.
- **Overriding markdown elements.** If `mdx-components.tsx` overrides `ul`, `li`, `p`, `table`, `h*`, or `input` (e.g. for prose styling), a graph can render an empty frame if its children no longer arrive as those tags. Test each graph after adding overrides. This is inferred from the `graph-frame.tsx` parser, not stated in the docs.
- **GFM.** Markdown tables and task lists inside graphs need `remark-gfm` (see above).
- **Turbopack.** Only serializable, string-named remark/rehype plugins work (Next.js docs).
- **Namespace installs** (`@mdxcn/...`) fail until the `@mdxcn` registry is in `components.json`.
- **Comark streaming.**
  - Scalars from Markdown arrive as strings (`coerceProps` handles the listed numeric props).
  - YAML that is cut off mid-key can throw, so hold the last good tree.
  - Missing required props render an empty frame.
- **Don't restyle the frame** (no extra borders, rounded cards, or new corner marks) and don't add animation. Motion is built in: transform and opacity, about 220 ms, no loops, and `prefers-reduced-motion` sets it to 0.
- `GraphTimer`/`GraphCountdown` start ticking only after mount (the time is `null` during SSR), so a blank value on first paint is expected.

## WMDS guardrail

In any product built on WMDS (WhatMatters Design System, github.com/thewhatmatters/wmds):
- **Style mdxcn output with WMDS tokens and components.** Point the mdxcn CSS variables (`--graph-accent*`, `--graph-frame`, `--graph-muted`, `--graph-faint`, `--contrast-*`) and the shadcn tokens they rely on (`background`, `foreground`, `destructive`, the mono font) at existing WMDS tokens. Don't keep the upstream oklch defaults, and don't hard-code new colors.
- **Map mdxcn elements onto existing WMDS components and tokens.** Where WMDS already has an equivalent (e.g. a callout/alert, quote, steps, code/terminal, table, headings, links), use or wrap the WMDS component instead of shipping a parallel mdxcn look. Use mdxcn figures only where WMDS has no counterpart, and only after token mapping.
- **Don't invent new atoms or molecules in the app.** No local forks, restyles, or new primitives built from mdxcn source.
- **Any gap goes to the Design System Manager as a WMDS gap.** That covers a missing token, a missing component, or an mdxcn element with no WMDS mapping. Don't build it locally.

## Verify

1. `pnpm build` (and the typecheck) passes with no unresolved `@/registry/default/...` imports.
2. Render a sample MDX page that uses at least `Callout`, `Steps`, `Terminal`, one table graph, and one list graph (e.g. `GraphTimeline`). Nothing should render as an empty frame.
3. Headings, inline code, fenced code, tables, and links render with the right tokens (WMDS tokens in WMDS products) in light and dark mode. The frame, title ink, and accent come from the mapped variables, and the mono font keeps the frame aligned.
4. The browser console shows no hydration errors or warnings. Check reduced motion too.
5. Any plain-Markdown output uses the official fenced ASCII, not JSX or `::graph-*`.

## Sources

- https://mdxcn.dev/ and https://mdxcn.dev/docs
- https://mdxcn.dev/docs/installation
- https://mdxcn.dev/llms.txt
- https://mdxcn.dev/skill.md and https://mdxcn.dev/docs/skill
- https://mdxcn.dev/agents.md
- https://mdxcn.dev/docs/comark and https://mdxcn.dev/docs/knap
- https://mdxcn.dev/docs/examples
- https://mdxcn.dev/api/v1/components
- https://mdxcn.dev/r/all.json
- https://github.com/keshav-exe/mdxcn (README.md, AGENTS.md, registry.json, registry/default/*; commit 2928126, 2026-09-19)
- https://nextjs.org/docs/app/guides/mdx
- https://ui.shadcn.com/docs/components-json, https://ui.shadcn.com/docs/registry/namespace, https://ui.shadcn.com/docs/registry/registry-item-json, https://ui.shadcn.com/docs/cli
