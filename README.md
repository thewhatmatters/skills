# skills

Personal [Claude Code](https://claude.com/claude-code) skills, version-controlled.

This repo lives at `~/.claude/skills/`. Each subdirectory is a skill Claude can
invoke. **Everything here is committed except secrets and generated junk** —
drop a new skill into the folder and it's tracked automatically.

## Tracked skills

| Skill | Status | What it does |
|-------|--------|--------------|
| [`scan-trends`](scan-trends/) | ✅ working | Deep-research engine that scans a recent time window (default 30 days) across 6+ sources — Reddit, X/Twitter, YouTube, Hacker News, Polymarket, and the web — then synthesizes grounded, cited reports. |
| [`audit-skill`](audit-skill/) | ✅ working | Audits a Claude skill against the canonical [`skill-architecture.md`](skill-architecture.md) spec — structure, reliability, secret hygiene, gates, preflight — and produces a severity-grouped findings report. |
| [`generate-skill`](generate-skill/) | ✅ working | Counterpart to `audit-skill`: scaffolds new skills against the same spec, consults the official Claude docs (with offline snapshot fallback), reports any upstream drift, and runs `audit-skill` on what it produces. End-to-end exercised by generating [`generate-prd`](generate-prd/) (below). See [`DESIGN.md`](generate-skill/DESIGN.md). |
| [`generate-prd`](generate-prd/) | ✅ working | Synthesizes a conversational product discussion into a structured PRD covering **problem, solution, UX flow, technical architecture, data model, pricing, roadmap, risks, open questions**. Outputs markdown (always) and self-contained HTML (optionally). Built by `generate-skill`; self-audited 0 critical / 0 important. |
| [`deep-research`](deep-research/) | ✅ working | Multi-pass, structured research on any topic (markets, products, competitors, regulations, opportunities, …). Tavily/Exa search via the shared `.env` with a NATIVE `WebSearch` fallback; composes with `/scan-trends` for recency. Outputs a cited markdown report (always) + self-contained HTML (optional). Built by `generate-skill`; self-audited 0 critical / 0 important. |
| [`render-html`](render-html/) | ✅ working | Renders a Markdown file (or piped Markdown) into a polished, self-contained HTML page in Anthropic's anthropic.com brand look — ivory background, clay accent, serif headings, light/dark aware. Stdlib-only Markdown converter that also renders images, with an opt-in `--inline-images` flag to embed them as base64 for true offline self-containment. Pairs with the HTML output of `deep-research` / `generate-prd` / `scan-trends` and with `source-ui`'s reference sets. Built by `generate-skill`; self-audited 0 critical / 0 important. |
| [`draw-diagram`](draw-diagram/) | ✅ working | Generates Mermaid diagrams (flowcharts, user flows, ERDs, sequence, state, architecture, requirement, …) and renders them through a graceful ladder: fenced ` ```mermaid ` block → SVG/PNG via `mmdc` (npx) → Kroki network render → fenced block. Brand theme matches `render-html`; composes with `render-html` / `generate-prd`. Built by `generate-skill`; self-audited 0 critical / 0 important; live-verified. |
| [`automate-browser`](automate-browser/) | ✅ working | Drives a real Chromium browser via Playwright with a persistent login profile — navigate, click, fill, extract, scrape, screenshot. Token-efficient page extraction; read-only `WebFetch` fallback when Playwright is absent. Rewritten from the Amp skill to house conventions via `generate-skill`; self-audited 0 critical / 0 important; live-verified. |
| [`source-ui`](source-ui/) | ✅ working | Sources real-world UI references — screens, components, user flows, and visual-style direction — by routing a design need to the right library (**Mobbin** or **Refero**) with the right tool, then returning a curated, cited set. Mobbin for fast component-level image sweeps; Refero for visual-style systems, page-level screens, and multi-step flows; built-in `WebSearch`/`WebFetch` fallback when neither MCP server is connected. Composes with `render-html` / `generate-prd`. Built by `generate-skill`; self-audited 0 critical / 0 important; live-verified. |
| [`decompose-prd`](decompose-prd/) | ✅ working | Decomposes a PRD into Ralph-compatible `prd.json` — small, dependency-ordered user stories each sized for one autonomous-agent iteration, with verifiable criteria. **Skill-aware**: discovers global + project skills and embeds the right one per story (e.g. verify UI with `automate-browser`). Optionally emits a `run-tasks.sh` loop runner. Consumes `generate-prd`'s output. Built by `generate-skill`; self-audited 0 critical / 0 important. |

## Setup

Some skills need API keys. Keys live in a single shared `.env` file that is
**never committed** (`.gitignore` blocks it). `.env.example` is the template:

```sh
cp ~/.claude/skills/.env.example ~/.claude/skills/.env
chmod 600 ~/.claude/skills/.env
# then fill in the keys you need
```

Resolution order (first hit wins): real env var → `~/.claude/.env` →
`~/.claude/skills/.env`. Empty values are skipped.
