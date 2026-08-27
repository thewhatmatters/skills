# skills

Personal Agent Skills, version-controlled. Canonical clone:
`~/Development/skills`. Cursor discovery: `~/.cursor/skills` → this folder.

Each subdirectory is a skill. **Everything here is committed except secrets
and generated junk** — drop a new skill in and it's tracked.

## Tracked skills

| Skill | What it does |
|-------|----------------|
| [`audit-skill`](audit-skill/) | Audits a skill against [`skill-architecture.md`](skill-architecture.md). |
| [`audit-vault`](audit-vault/) | Read-only health report for the OKF vault. |
| [`automate-browser`](automate-browser/) | Playwright browser automation with a persistent login profile. |
| [`codebase-design`](codebase-design/) | Vocabulary for designing deep modules. |
| [`curate-vault`](curate-vault/) | Gated harvest of durable knowledge into the Obsidian OKF vault. |
| [`deep-research`](deep-research/) | Multi-pass cited research (Tavily/Exa, WebSearch fallback). |
| [`gauntlet`](gauntlet/) | Sustained adversarial pass on code or an artifact. |
| [`generate-prd`](generate-prd/) | Conversation → structured PRD (markdown, optional HTML). |
| [`generate-skill`](generate-skill/) | Scaffold a new skill to the house spec + Cursor skills docs. |
| [`grilling`](grilling/) | One-question-at-a-time design interview. |
| [`improve-codebase-architecture`](improve-codebase-architecture/) | Find shallow modules; propose deepening refactors. |
| [`ingest-source`](ingest-source/) | YouTube / web / PDF / image → `docs/sources/` (+ optional vault). |
| [`polish-copy`](polish-copy/) | Luxury-bar product microcopy review. |
| [`refine-skill`](refine-skill/) | Improve a skill from one real session transcript. |
| [`remotion`](remotion/) | Remotion video workflow (defers API to `remotion-best-practices`). |
| [`scaffold-studio`](scaffold-studio/) | Wire Motion (Cursor plugin) and CSS Studio into a web project. |
| [`scan-trends`](scan-trends/) | Recency scan across Reddit, X, YouTube, HN, Polymarket, web. |
| [`use-grid-system`](use-grid-system/) | Josef Müller-Brockmann modular grid. |
| [`wire-vault`](wire-vault/) | Layer-2 vault pointer in the project's `AGENTS.md`. |

## External skills (composed, not vendored)

Well-maintained upstream skills are installed via [skills.sh](https://www.skills.sh),
pinned in [`skills-lock.json`](skills-lock.json), and gitignored — the same posture
as `node_modules` + a lockfile. Pinned: **`shadcn`**, **`next-best-practices`**,
**`design-md`**, and **`remotion-best-practices`**. Probe-gate deferral is in
[`AGENTS.md`](AGENTS.md).

## Setup

Some skills need API keys. Keys live in a single shared `.env` that is
**never committed**. `.env.example` is the template:

```sh
cp ~/.cursor/skills/.env.example ~/.cursor/skills/.env
chmod 600 ~/.cursor/skills/.env
# then fill in the keys you need
```

Resolution order (first hit wins): real env var → `~/.cursor/skills/.env`.
Empty values are skipped.
