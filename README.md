# skills

Personal [Claude Code](https://claude.com/claude-code) skills, version-controlled.

This repo lives at `~/.claude/skills/`. Each subdirectory is a skill Claude can
invoke. Not every local skill is tracked here — the repo uses an **opt-in
whitelist** so only deliberately published skills are committed.

## Tracked skills

| Skill | Status | What it does |
|-------|--------|--------------|
| [`trendscan`](trendscan/) | ✅ working | Deep-research engine that scans a recent time window (default 30 days) across 6+ sources — Reddit, X/Twitter, YouTube, Hacker News, Polymarket, and the web — then synthesizes grounded, cited reports. |
| [`skill-auditor`](skill-auditor/) | ✅ working | Audits a Claude skill against the canonical [`skill-architecture.md`](skill-architecture.md) spec — structure, reliability, secret hygiene, gates, preflight — and produces a severity-grouped findings report. |
| [`skill-generator`](skill-generator/) | 🚧 design only | Planned counterpart to `skill-auditor`: scaffolds new skills against the same spec, consults the official Claude docs for drift, and self-audits its output. Only [`DESIGN.md`](skill-generator/DESIGN.md) exists so far — not yet built. |

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

## How the whitelist works

[`.gitignore`](.gitignore) ignores **everything** by default, then re-includes
specific paths. This keeps `git status` clean and prevents unfinished or
machine-specific skills from being committed by accident.

To publish another skill:

```sh
# 1. add an opt-in line to .gitignore
echo '!/my-skill/' >> .gitignore

# 2. stage and commit
git add my-skill .gitignore
git commit -m "Add my-skill"
```

Always-ignored even inside tracked skills: `.env`, `**/settings.local.json`,
`__pycache__/`, `*.pyc`, `results.html`, `.DS_Store`.
