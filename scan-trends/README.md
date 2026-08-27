# scan-trends

**What it is:** a research assistant that tells you what people have actually
been saying about a topic *recently*, with sources you can click.

## What you get

A grounded, cited summary of the last N days of discussion on any topic — plus
a self-contained HTML report you can open in a browser (records your exact
question, the date, and every finding with links). Interactive runs ask where
it lives — project `docs/research/`, the vault's `research/synthesis/` (with a
markdown companion), or the working dir; `--agent`/no-flag runs keep the
historical `results.html` in the working dir.

## How to run it

```
/scan-trends <topic> [--days=N] [--sources=a,b,c | --all] [--agent] [--out=PATH]
```

Examples:

- `/scan-trends "AI browser agents"` — last 30 days, you pick sources
- `/scan-trends "vision pro" --days=7 --all` — last week, every source
- `/scan-trends "rust async" --agent` — unattended, no prompts

## What it needs (one-time)

Nothing is strictly required, but more keys = more sources. Put what you have in
`~/.cursor/skills/.env` (`chmod 600`; see `.env.example`):

- `TAVILY_API_KEY` (or `EXA_API_KEY`) — better web results
- `X_AUTH_TOKEN` / `X_CT0` — include X/Twitter
- No keys at all still works via a built-in fallback.

Check readiness anytime: `python3 scripts/preflight.py`.

## How it works (high level)

1. It looks across up to **6 sources**: Reddit, X/Twitter, YouTube, Hacker
   News, Polymarket, and the web.
2. It picks the best way to run each source for your machine, and if a source
   isn't set up it tells you clearly instead of silently skipping (you choose:
   fix it, do it yourself, or skip).
3. It synthesizes everything into one cited report and an HTML file.

Two modes: **SCRIPTS** (fast Python scrapers/APIs, preferred) and **NATIVE**
(built-in web search fallback) — picked automatically.

## Where to look next

- `SKILL.md` — the instructions the agent follows when running it.
- `WHY.md` — the design decisions and the "why" behind them.
