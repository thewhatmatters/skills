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
| [`render-html`](render-html/) | ✅ working | Renders a Markdown file (or piped Markdown) into a polished, self-contained HTML page in Anthropic's anthropic.com brand look — ivory background, clay accent, serif headings, light/dark aware. Stdlib-only Markdown converter; pairs with the HTML output of `deep-research` / `generate-prd` / `scan-trends`. Built by `generate-skill`; self-audited 0 critical / 0 important. |
| [`automate-browser`](automate-browser/) | ✅ working | Drives a real Chromium browser via Playwright with a persistent login profile — navigate, click, fill, extract, scrape, screenshot. Token-efficient page extraction; read-only `WebFetch` fallback when Playwright is absent. Rewritten from the Amp skill to house conventions via `generate-skill`; self-audited 0 critical / 0 important; live-verified. |

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
