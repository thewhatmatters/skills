---
name: scan-trends
description: Deep research engine that scans a recent time window (default 30 days; configurable via --days, e.g. last day or last 7 days) across 6+ sources — Reddit, X/Twitter (via an authenticated browser session), YouTube, Hacker News, Polymarket, and the web (Tavily or Exa, DuckDuckGo fallback). Synthesizes findings into grounded, cited reports. Use when a user asks what's happening, trending, being discussed, recommended, compared, or debated about any topic recently. Trigger phrases include "scan-trends", "what are people saying about X", "what's trending in X", "research X lately/recently", "X in the last 7 days / last 30 days / past day / this week", or any request for recent community sentiment, comparisons, or trending discussion.
---

# scan-trends: Research Any Topic Across a Recent Window

Research ANY topic across Reddit, X/Twitter, YouTube, Hacker News, Polymarket,
and the web. Surface what people are actually discussing, recommending, betting
on, and debating right now.

Bulky detail lives in `references/` (spec A1) and is loaded only when a step
routes you there:

- [`references/error-handling.md`](references/error-handling.md) — SCRIPTS-mode
  per-source notes, fallbacks, and the failure→action table (read at Step 2).
- [`references/native-mode.md`](references/native-mode.md) — NATIVE-mode
  per-source queries + error handling (read at Step 2 in NATIVE mode).
- [`references/output-patterns.md`](references/output-patterns.md) — report
  layout, citation rules, stats block, results.html JSON, and the per-QUERY_TYPE
  formats (read at Step 4).
- [`references/gates.md`](references/gates.md) — gate anatomy + the registered
  gate walkthroughs (read when a gate fires).

## Environment

- `python3` with `requests`, `beautifulsoup4`, `playwright` (Chromium at `/opt/pw-browsers/`)
- `scripts/x.py` — authenticated X/Twitter scrape. Auth precedence: **(1) cookies
  (preferred)** — `X_AUTH_TOKEN` + `X_CT0` in the shared `.env`; **(2) persistent
  profile** — `python3 scripts/x.py --login` (saved to `~/.scan-trends/x-profile`,
  override `X_PROFILE_DIR`). No valid auth → `[]` + `NO_SESSION`; the skill falls
  back to a web `site:x.com` search.
- **Search keys (`.env`)** — `scripts/_env.py` loads keys in order: real env →
  `~/.claude/.env` → `~/.claude/skills/.env` (first hit wins; `chmod 600` the file,
  preflight warns if looser). Web search auto-selects **Tavily** (`TAVILY_API_KEY`) →
  **Exa** (`EXA_API_KEY`) → **DuckDuckGo** (no key, weak last resort).
- All other sources use public APIs, no credentials required.

**Scripts are in `scripts/` — one file per source.**

## Step 0: Detect Environment

Run this probe:

```bash
python3 -c "import requests; requests.get('https://www.reddit.com', timeout=5); print('SCRIPTS')" 2>/dev/null || echo "NATIVE"
```

- Output `SCRIPTS` → `MODE = SCRIPTS` (use the Python scripts in Step 2).
- Output `NATIVE` → `MODE = NATIVE` (use the native web_search tool in Step 2;
  all 6 sources are covered via targeted queries — slightly less granular,
  fully functional).

Announce the mode before proceeding: `Mode: {SCRIPTS | NATIVE}`

## Step 0.5: Preflight (SCRIPTS mode only)

Before the long run, verify every source is armed (**skip this step in NATIVE mode**):

```bash
python3 scripts/preflight.py
```

Render its readiness board. Each source's `status`: `ready` (good), `degraded`
(runs but weaker — note in stats), `down` (unreachable here, not user-fixable),
`gated` (recoverable setup gap — see **Recoverable Setup Gates**). Surface any
`env_warnings` (e.g. loose `.env` perms). If `preflight.py` itself errors: note
it and proceed with all `ready` sources — preflight never blocks.

#### Choose which sources to run

Determine the run scope by this precedence:

1. **`--agent`** → no prompt. Scope = all `ready` + `degraded`. Skip `gated`/`down`.
2. **`--sources=a,b,c`** → no prompt. Scope = exactly those.
3. **`--all`** → no prompt. Scope = all 6 sources.
4. **Otherwise (default interactive): the Source Picker.** Ask with ONE
   `AskUserQuestion` call containing **two `multiSelect` questions** (the UI caps
   options at 4, so split the 6 sources): Q1 = Reddit, X/Twitter, YouTube;
   Q2 = Hacker News, Polymarket, Web. Each option label is the source name; its
   description is the live preflight status, e.g. `✓ ready` / `⚠ degraded —
   DuckDuckGo` / `✗ needs setup: X cookies`. The selected set across both
   questions = scope. (Recommend selecting all non-`down` sources.)

Then reconcile scope against status: selected + `ready`/`degraded` → run it;
selected + `gated` → fire that source's gate now (batch if several); selected +
`down` → note it, exclude; **not selected → excluded silently, no gate**.

## Step 1: Parse User Intent

Before any tool calls, extract and display:

- `TOPIC` — what to research
- `QUERY_TYPE` — `RECOMMENDATIONS` ("best X"/"top X") | `COMPARISON` ("X vs Y") |
  `NEWS` ("X news"/"what's happening with X") | `PROMPTING` ("X prompts") |
  `GENERAL` (everything else)
- `WINDOW` — the lookback window from `--days` (default 30), rendered
  human-readably (`--days=7` → "7 days")
- `TOPIC_A` / `TOPIC_B` — only for `COMPARISON`

```
I'll research {TOPIC} over the last {WINDOW} across Reddit, X, YouTube, HN, Polymarket, and the web.

Parsed intent:
- TOPIC = {TOPIC}
- WINDOW = {WINDOW}
- QUERY_TYPE = {QUERY_TYPE}

Research typically takes 2-5 minutes. Starting now.
```

## Step 2: Run All Sources

Run every source in scope and capture output. Run all before synthesizing.

**MODE = SCRIPTS** — read
[`references/error-handling.md`](references/error-handling.md) first: it holds
the per-source interpretation notes (short keyword queries, x.py result markers,
the Reddit-403 and X web fallbacks, Polymarket relevance) and the
failure→action table. Let `DAYS` = `--days` (default 30) and run each in-scope
source, capturing JSON:

```bash
python3 scripts/reddit.py "{TOPIC}" --days={DAYS}
python3 scripts/x.py "{TOPIC}" --days={DAYS}
python3 scripts/youtube.py "{TOPIC}" --days={DAYS}
python3 scripts/hackernews.py "{TOPIC}" --days={DAYS}
python3 scripts/polymarket.py "{TOPIC}" --days={DAYS}
python3 scripts/web.py "{TOPIC}" "{QUERY_TYPE}" --days={DAYS}
```

Pass a tight 2–5 keyword distillation of `{TOPIC}` — the scrapers are keyword
matchers, not semantic search (full rule + retry guidance in the reference).

**MODE = NATIVE** — follow
[`references/native-mode.md`](references/native-mode.md): per-source
`web_search` queries with a computed `CUTOFF` date, plus the NATIVE
failure→action table.

## Step 3: Synthesize

Weigh findings internally before writing the report:

1. **Engagement signals rank higher** — Reddit upvotes, YouTube views, HN points > raw snippets
2. **Cross-platform patterns are strongest** — same theme on Reddit + HN + X: lead with it
3. **Polymarket odds are high-signal** — real money cuts through opinion; note specific % and movement
4. **Quote top Reddit comments directly** — usually the richest signal
5. **Note contradictions between sources explicitly**

## Step 4: Display Report

Open [`references/output-patterns.md`](references/output-patterns.md) and follow
it in display order:

1. **What I learned** — patterns + key patterns, with its citation rules.
2. **Stats block** — per-source counts; "(via web)" lines for fallback sources.
3. **Write `results.html`** — **always** persist the run (both modes; also under
   `--agent`) by piping the documented JSON to `scripts/report.py`. Report the
   absolute path; if `report.py` fails, note it but do not block.
4. **Invitation** — tailored to QUERY_TYPE.

For `COMPARISON`, `RECOMMENDATIONS`, or `PROMPTING`, use that type's format from
the same file (head-to-head / most-mentioned / ready-to-paste-prompt).

## Step 5: Wait, Then Answer

Stop after the invitation. Answer follow-ups from gathered research only — no new
searches. Only write prompts if explicitly asked.

## Options

| Flag | Behavior |
|---|---|
| `--days=N` | Look back N days (default: 30) |
| `--quick` | _(reserved — not yet implemented)_ Fewer results per source |
| `--deep` | _(reserved — not yet implemented)_ More results per source |
| `--agent` | Non-interactive: skip pauses & the source picker, output full report, stop |
| `--sources=a,b,c` | Run exactly these sources (no picker). Names: `reddit`, `x`, `youtube`, `hackernews`, `polymarket`, `web` |
| `--all` | Run all 6 sources, no picker (fires gates for any not ready) |
| `--out=PATH` | Where to write the HTML report (default: `results.html` in the working dir) |

## Recoverable Setup Gates

Some source failures are a **one-time setup gap** (not logged in, missing key) —
not a transient error. Do **not** silently degrade these: a one-time fix beats a
permanently worse report. Every gate has four parts (spec A7): **(1)** an
unambiguous trigger distinct from transient failures, **(2)** an `--agent`
bypass that never prompts, **(3)** ask-don't-degrade in interactive runs (*Fix
it for me / I'll do it myself / Skip it*), **(4)** a graceful dead-end — if the
fix fails, fall back anyway; a gate never blocks the run.

When a gate fires, open [`references/gates.md`](references/gates.md) for the
registered gates (X/Twitter auth, web search key) and their exact fix
walkthroughs and fallbacks.

## Error Handling

Per-source failure→action tables live in
[`references/error-handling.md`](references/error-handling.md) (SCRIPTS) and
[`references/native-mode.md`](references/native-mode.md) (NATIVE).

**Both modes:** if fewer than 3 sources return data, halt and report to the user
before synthesizing.
