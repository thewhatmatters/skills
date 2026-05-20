# skills

Personal [Claude Code](https://claude.com/claude-code) skills, version-controlled.

This repo lives at `~/.claude/skills/`. Each subdirectory is a skill Claude can
invoke. **Everything here is committed except secrets and generated junk** —
drop a new skill into the folder and it's tracked automatically.

## Tracked skills

| Skill | Status | What it does |
|-------|--------|--------------|
| [`trendscan`](trendscan/) | ✅ working | Deep-research engine that scans a recent time window (default 30 days) across 6+ sources — Reddit, X/Twitter, YouTube, Hacker News, Polymarket, and the web — then synthesizes grounded, cited reports. |
| [`skill-auditor`](skill-auditor/) | ✅ working | Audits a Claude skill against the canonical [`skill-architecture.md`](skill-architecture.md) spec — structure, reliability, secret hygiene, gates, preflight — and produces a severity-grouped findings report. |
| [`skill-generator`](skill-generator/) | ✅ working | Counterpart to `skill-auditor`: scaffolds new skills against the same spec, consults the official Claude docs (with offline snapshot fallback), reports any upstream drift, and runs `skill-auditor` on what it produces. End-to-end exercised by generating [`prd-generator`](prd-generator/) (below). See [`DESIGN.md`](skill-generator/DESIGN.md). |
| [`prd-generator`](prd-generator/) | ✅ working | Synthesizes a conversational product discussion into a structured PRD covering **problem, solution, UX flow, technical architecture, data model, pricing, roadmap, risks, open questions**. Outputs markdown (always) and self-contained HTML (optionally). Built by `skill-generator`; self-audited 0 critical / 0 important. |
| [`deep-research`](deep-research/) | ✅ working | Multi-pass, structured research on any topic (markets, products, competitors, regulations, opportunities, …). Tavily/Exa search via the shared `.env` with a NATIVE `WebSearch` fallback; composes with `/trendscan` for recency. Outputs a cited markdown report (always) + self-contained HTML (optional). Built by `skill-generator`; self-audited 0 critical / 0 important. |
| [`dev-browser`](dev-browser/) | ✅ working | Drives a real Chromium browser via Playwright with a persistent login profile — navigate, click, fill, extract, scrape, screenshot. Token-efficient page extraction; read-only `WebFetch` fallback when Playwright is absent. Rewritten from the Amp skill to house conventions via `skill-generator`; self-audited 0 critical / 0 important; live-verified. |

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
