# skills

Personal Agent Skills, version-controlled. Canonical clone:
`~/Development/skills`. Cursor discovery: `~/.cursor/skills` → this folder.

Each subdirectory is a skill. **Everything here is committed except secrets
and generated junk** — drop a new skill in and it's tracked. House
conventions live in [`AGENTS.md`](AGENTS.md). New skills: Cursor
`/create-skill` (or a folder + `SKILL.md`). Durable knowledge about the
collection goes through `/curate-vault` into the OKF vault shelf
`skills/`.

## Tracked skills

| Skill | What it does |
|-------|----------------|
| [`automate-browser`](automate-browser/) | Playwright browser automation with a persistent login profile. |
| [`codebase-design`](codebase-design/) | Deep-module vocabulary; `--improve` scans for shallow modules. |
| [`curate-vault`](curate-vault/) | Gated harvest into the OKF vault; `--audit` / `--groom` / `--wire`. |
| [`deep-research`](deep-research/) | Multi-pass cited research, including recency (`--recent` / `--days`). |
| [`use-grid-system`](use-grid-system/) | Josef Müller-Brockmann modular grid. |

## External skills (composed, not vendored)

Upstream skills via [skills.sh](https://www.skills.sh) (`npx skills add …`)
are gitignored like `node_modules`. In use: **`shadcn`**,
**`next-best-practices`**, **`design-md`**. Remotion comes from the Cursor
Remotion plugin, not a house skill. Probe-gate deferral is in
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
