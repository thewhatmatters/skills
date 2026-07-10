# Mermaid diagram types — index & when to use

Authoritative syntax lives at mermaid.js.org. **Pick the type from the
"Use when" column.** For the *common* types you can write the syntax directly;
for anything you're not fully confident of — especially the **Newer / verify**
rows — **WebFetch the Docs URL first**, then compose. Don't fetch docs for a
plain flowchart; only when the type or syntax is uncertain.

## Common / stable (write directly; fetch only if unsure)

| Keyword | Use when | Docs |
|---|---|---|
| `flowchart` / `graph` | Process flows, decision trees, **user flows** | https://mermaid.js.org/syntax/flowchart.html |
| `sequenceDiagram` | Interactions/messages over time between actors | https://mermaid.js.org/syntax/sequenceDiagram.html |
| `classDiagram` | OO class models, relationships, methods | https://mermaid.js.org/syntax/classDiagram.html |
| `stateDiagram-v2` | State machines, lifecycles | https://mermaid.js.org/syntax/stateDiagram.html |
| `erDiagram` | Entity-relationship / data models | https://mermaid.js.org/syntax/entityRelationshipDiagram.html |
| `journey` | User-journey maps (steps × satisfaction) | https://mermaid.js.org/syntax/userJourney.html |
| `gantt` | Schedules, timelines, project plans | https://mermaid.js.org/syntax/gantt.html |
| `pie` | Proportions / share | https://mermaid.js.org/syntax/pie.html |
| `quadrantChart` | 2×2 prioritization (effort/impact, etc.) | https://mermaid.js.org/syntax/quadrantChart.html |
| `requirementDiagram` | **PRD** requirements + verification links | https://mermaid.js.org/syntax/requirementDiagram.html |
| `gitGraph` | Branch/commit/merge history | https://mermaid.js.org/syntax/gitgraph.html |
| `C4Context` (/`C4Container`/`C4Component`) | Software architecture (C4 model) | https://mermaid.js.org/syntax/c4.html |
| `mindmap` | Idea/topic hierarchies | https://mermaid.js.org/syntax/mindmap.html |
| `timeline` | Chronological events / history | https://mermaid.js.org/syntax/timeline.html |
| `sankey-beta` | Flow volumes between stages | https://mermaid.js.org/syntax/sankey.html |
| `xychart-beta` | Line/bar charts (x/y data) | https://mermaid.js.org/syntax/xyChart.html |
| `block-beta` | Block layouts / system blocks | https://mermaid.js.org/syntax/block.html |
| `kanban` | Kanban boards (columns of cards) | https://mermaid.js.org/syntax/kanban.html |
| `architecture-beta` | Cloud/service architecture w/ groups + icons | https://mermaid.js.org/syntax/architecture.html |
| `radar` | Multi-axis comparison (spider chart) | https://mermaid.js.org/syntax/radar.html |
| `packet-beta` | Network packet / byte-field layouts | https://mermaid.js.org/syntax/packet.html |

## Newer / verify (always WebFetch the URL before composing — keyword and availability may vary by mermaid version)

| Topic | Use when | Docs |
|---|---|---|
| treemap | Nested proportion / hierarchy areas | https://mermaid.js.org/syntax/treemap.html |
| venn | Set overlaps | https://mermaid.js.org/syntax/venn.html |
| ishikawa (fishbone) | Root-cause / cause-effect | https://mermaid.js.org/syntax/ishikawa.html |
| wardley | Wardley value-chain maps | https://mermaid.js.org/syntax/wardley.html |
| treeView | Tree/file-tree views | https://mermaid.js.org/syntax/treeView.html |
| eventmodeling | Event-modeling flows | https://mermaid.js.org/syntax/eventmodeling.html |

> These are recent/experimental: the exact keyword, options, and even page
> availability can change between Mermaid releases — confirm against the live
> doc (and that the installed mermaid version supports them) before relying on
> them. The renderer only *warns* on unknown types; it doesn't block.

## More

- Worked examples across types: https://mermaid.js.org/syntax/examples.html
- Syntax guards (quote labels, the `end` gotcha) + the brand theme:
  see [`mermaid-reference.md`](mermaid-reference.md).
- **FigJam note:** if exporting to FigJam via the Figma MCP later, only
  `graph`/`flowchart`, `sequenceDiagram`, `stateDiagram`, `gantt`, `erDiagram`
  are supported there — map/validate first.
