---
name: scan-trends
description: Deep research engine that scans a recent time window (default 30 days; configurable via --days, e.g. last day or last 7 days) across 6+ sources — Reddit, X/Twitter (via an authenticated browser session), YouTube, Hacker News, Polymarket, and the web (Tavily or Exa, DuckDuckGo fallback). Synthesizes findings into grounded, cited reports. Use when a user asks what's happening, trending, being discussed, recommended, compared, or debated about any topic recently. Trigger phrases include "scan-trends", "what are people saying about X", "what's trending in X", "research X lately/recently", "X in the last 7 days / last 30 days / past day / this week", or any request for recent community sentiment, comparisons, or trending discussion.
---

# scan-trends: Research Any Topic Across a Recent Window

Research ANY topic across Reddit, X/Twitter, YouTube, Hacker News, Polymarket,
and the web. Surface what people are actually discussing, recommending, betting on, and debating
right now.

## Environment

- `python3` with `requests`, `beautifulsoup4`, `playwright` (Chromium at `/opt/pw-browsers/`)
- `scripts/x.py` — authenticated X/Twitter scrape. Auth precedence:
  **(1) cookies (preferred)** — `X_AUTH_TOKEN` + `X_CT0` in the shared `.env`
  (copy `auth_token`/`ct0` from a logged-in x.com browser via DevTools → Cookies);
  no login flow runs, so nothing for X to block.
  **(2) persistent profile** — `python3 scripts/x.py --login` (browser opens once;
  saved to `~/.scan-trends/x-profile`, override `X_PROFILE_DIR`).
  No valid auth → `[]` + `NO_SESSION`; skill falls back to a web `site:x.com` search.
- **Search keys (`.env`)** — `scripts/_env.py` loads keys in order: real env →
  `~/.claude/.env` → `~/.claude/skills/.env` (first hit wins; `chmod 600` the file,
  preflight warns if looser). Web search auto-selects **Tavily** (`TAVILY_API_KEY`) →
  **Exa** (`EXA_API_KEY`) → **DuckDuckGo** (no key, weak last resort) by which key is present.
- All other sources use public APIs, no credentials required

**Scripts are in `scripts/` — one file per source.**

---

## Step 0: Detect Environment

Before anything else, determine which execution mode to use.

Run this probe:

```bash
python3 -c "import requests; requests.get('https://www.reddit.com', timeout=5); print('SCRIPTS')" 2>/dev/null || echo "NATIVE"
```

- If output is `SCRIPTS` → set `MODE = SCRIPTS`. Use the Python scripts in Step 2.
- If output is `NATIVE` → set `MODE = NATIVE`. Use the native web_search tool in Step 2.

Announce the mode before proceeding:
```
Mode: {SCRIPTS | NATIVE}
```

In NATIVE mode: Reddit, X, YouTube, HN, Polymarket, and Web are all covered via
targeted web_search queries. Coverage is slightly less granular than scripts but fully functional.

---

## Step 0.5: Preflight (SCRIPTS mode only)

Before the long run, verify every source is armed. **Skip this step entirely in NATIVE mode.**

```bash
python3 scripts/preflight.py
```

Render its readiness board. Each source's `status` means: `ready` (good),
`degraded` (runs but weaker — note in stats), `down` (unreachable here, not
user-fixable), `gated` (recoverable setup gap — see **Recoverable Setup Gates**).
Surface any `env_warnings` (e.g. loose `.env` perms). If `preflight.py` itself
errors: note it and proceed with all `ready` sources — preflight never blocks.

#### Choose which sources to run

Determine the run scope by this precedence:

1. **`--agent`** → no prompt. Scope = all `ready` + `degraded`. Skip `gated`/`down`.
2. **`--sources=a,b,c`** → no prompt. Scope = exactly those (names: `reddit`, `x`,
   `youtube`, `hackernews`, `polymarket`, `web`).
3. **`--all`** → no prompt. Scope = all 6 sources.
4. **Otherwise (default interactive): the Source Picker.** Ask with ONE
   `AskUserQuestion` call containing **two `multiSelect` questions** (the UI caps
   options at 4, so split the 6 sources): Q1 "Sources 1/2" = Reddit, X/Twitter,
   YouTube; Q2 "Sources 2/2" = Hacker News, Polymarket, Web. Each option label is
   the source name; its description is the live preflight status, e.g.
   `✓ ready` / `⚠ degraded — DuckDuckGo` / `✗ needs setup: X cookies` /
   `✗ blocked from this environment`. The user's selected set across both
   questions = scope. (Recommend selecting all non-`down` sources.)

Then reconcile scope against status:

- selected + `ready`/`degraded` → run it (note `degraded` in stats).
- selected + `gated` → fire that source's **Recoverable Setup Gate** now (batch if
  several). Fixed → run it; skipped/failed → its documented fallback.
- selected + `down` → can't run; note it, exclude.
- **not selected → excluded silently, no gate** (only nag about gaps for sources the
  user actually wants).

Step 2 then runs only the resolved source set.

---

## Step 1: Parse User Intent

Before any tool calls, extract and display:

- `TOPIC` — what to research
- `QUERY_TYPE` — one of: `RECOMMENDATIONS`, `NEWS`, `COMPARISON`, `PROMPTING`, `GENERAL`
- `WINDOW` — the lookback window, derived from `--days` (default 30 days). Render human-readably: `--days=1` → "24 hours", `--days=7` → "7 days", `--days=30` → "30 days"
- `TOPIC_A` / `TOPIC_B` — only for `COMPARISON`

Common patterns:
- "best X" / "top X" → `RECOMMENDATIONS`
- "X vs Y" → `COMPARISON`
- "X news" / "what's happening with X" → `NEWS`
- "X prompts" / "prompting for X" → `PROMPTING`
- Everything else → `GENERAL`

Display before running any tools:

```
I'll research {TOPIC} over the last {WINDOW} across Reddit, X, YouTube, HN, Polymarket, and the web.

Parsed intent:
- TOPIC = {TOPIC}
- WINDOW = {WINDOW}
- QUERY_TYPE = {QUERY_TYPE}

Research typically takes 2-5 minutes. Starting now.
```

---

## Step 2: Run All Sources

Run each source and capture output. Run all before synthesizing.

---

### MODE = SCRIPTS

Let `DAYS` = the value of `--days` (default 30). Pass it to every script so the
lookback window is honored end-to-end. Run each and capture JSON output:

```bash
python3 scripts/reddit.py "{TOPIC}" --days={DAYS}
python3 scripts/x.py "{TOPIC}" --days={DAYS}
python3 scripts/youtube.py "{TOPIC}" --days={DAYS}
python3 scripts/hackernews.py "{TOPIC}" --days={DAYS}
python3 scripts/polymarket.py "{TOPIC}" --days={DAYS}
python3 scripts/web.py "{TOPIC}" "{QUERY_TYPE}" --days={DAYS}
```

Notes:
- **Keep the query SHORT — these scrapers are keyword matchers, not semantic
  search.** Pass a tight 2–5 keyword distillation of `{TOPIC}`, not a long
  natural-language sentence. A long query returns `[]` from reddit/x/hackernews
  even when the topic is well-covered (e.g. a paragraph-long query returns nothing;
  `"Claude Code"` returns dozens). If a source comes back empty, retry once with a
  shorter/broader keyword set before treating it as genuinely empty.
- `x.py` (X/Twitter) honors `--days` via X's native `since:` operator. Interpret its
  result per the **Recoverable Setup Gates** section:
  - non-empty JSON → use it
  - `[]` + stderr contains `NO_SESSION` → trigger the X/Twitter gate (ask the user,
    unless `--agent`)
  - `[]` + stderr `TIMEOUT`, or `[]` with no marker → skip X and take the web fallback
    silently: `python3 scripts/web.py "{TOPIC}" XFALLBACK --days={DAYS}`
- `reddit.py` — if it prints `[]` **and** its stderr contains `403` (Reddit blocking
  this IP/UA — common, not user-fixable, NOT rate-limiting), take the web fallback
  silently: `python3 scripts/web.py "{TOPIC}" REDDITFALLBACK --days={DAYS}`, tag the
  results as Reddit, and render the stats line as `|- Reddit (via web): {N} pages`.
  (REDDITFALLBACK is the ONLY web path that returns Reddit — every other query type
  excludes reddit.com, so a plain `GENERAL` retry recovers nothing.) This is a silent
  fallback, not a gate: the user can't fix Reddit's block, so don't prompt.
- `polymarket.py` accepts `--days` for consistency but cannot date-filter
  (no usable date API); it returns best-effort active markets. **Omit Polymarket
  entirely if no returned market is topically relevant** — for off-domain topics it
  returns unrelated active markets (e.g. novelty bets), not an empty list.

See individual script docstrings for output schemas.

---

### MODE = NATIVE

First compute the lookback window — never hardcode a date:
- `CUTOFF` = today's date minus N days (N = `--days`, default 30), formatted `YYYY-MM-DD`
- `YEAR` = the current calendar year; if `CUTOFF` falls in the prior year, use both years

Use the built-in `web_search` tool with targeted queries. Run each search separately and note
which source it corresponds to. Capture titles, snippets, and URLs for synthesis.

**Source 1 — Reddit**
```
site:reddit.com {TOPIC} after:{CUTOFF}
```
Look for: thread titles, subreddit names, comment sentiment in snippets.

**Source 2 — X/Twitter**
```
site:x.com OR site:twitter.com {TOPIC} since:{CUTOFF}
```
Look for: post text, handles, engagement signals in snippets.

**Source 3 — YouTube**
```
site:youtube.com {TOPIC} {YEAR}
```
Look for: video titles, channel names, view count signals.

**Source 4 — Hacker News**
```
site:news.ycombinator.com {TOPIC}
```
Look for: story titles, point counts, top comment excerpts.

**Source 5 — Polymarket**
```
site:polymarket.com {TOPIC}
```
Look for: market questions and odds. If no results, skip.

**Source 6 — Web**
Run 2 queries based on QUERY_TYPE:
- GENERAL: `{TOPIC} {YEAR}` and `{TOPIC} discussion guide`
- NEWS: `{TOPIC} news {YEAR}` and `{TOPIC} latest announcement`
- RECOMMENDATIONS: `{TOPIC} best recommendations {YEAR}` and `{TOPIC} top list`
- COMPARISON: `{TOPIC} comparison review {YEAR}`
- PROMPTING: `{TOPIC} prompts examples {YEAR}`

In NATIVE mode, after each search, note: source tag, number of results found, and any
high-signal snippets. Track these per-source for the stats block.

---

## Step 3: Synthesize

Weigh findings internally before writing the report:

1. **Engagement signals rank higher** — Reddit upvotes, YouTube views, HN points > raw snippets
2. **Cross-platform patterns are strongest** — same theme on Reddit + HN + X: lead with it
3. **Polymarket odds are high-signal** — real money cuts through opinion; note specific % and movement
4. **Quote top Reddit comments directly** — usually the richest signal
5. **Note contradictions between sources explicitly**

For `COMPARISON`, `RECOMMENDATIONS`, or `PROMPTING` queries, see
`references/output-patterns.md` for the expected output format (head-to-head /
most-mentioned / ready-to-paste-prompt respectively).

---

## Step 4: Display Report

Show in this exact sequence:

### What I learned

Ground everything in actual research — exact names, specific quotes, what sources actually say.

Citation rules:
- Prefer `per @handle` (X) or `per r/subreddit` (Reddit)
- YouTube: `per [Channel] on YouTube`
- HN: `per HN`
- Polymarket: `Polymarket has X at Y% (up/down Z% this month)`
- Web: source name only, never raw URLs
- Max 1-2 citations per pattern. No citation chains.

```
What I learned:

**{Pattern 1}** — [1-2 sentences, per @handle or r/sub]
**{Pattern 2}** — [1-2 sentences, per r/sub or HN]
**{Pattern 3}** — [1-2 sentences, per Polymarket or source]

KEY PATTERNS:
1. [Pattern] — per @handle
2. [Pattern] — per r/sub
3. [Pattern] — per source
```

### Stats block

```
---
All sources reported back!
{use "Most sources reported back!" if any source was down, omitted, or fell to a web fallback}
|- Reddit: {N} threads | {N} upvotes | {N} comments
|- X/Twitter: {N} posts | {N} likes | {N} reposts
|- YouTube: {N} videos | {N} views | {N} with transcripts
|- HN: {N} stories | {N} points | {N} comments
|- Polymarket: {N} markets | [top 1-2 market odds]
|- Web: {N} pages — Source, Source, Source
|- Top voices: @{handle}, r/{sub}, r/{sub}
---
```

Omit any source line with 0 results entirely. If X/Twitter came from the web
fallback (x.py had no session), render it as `|- X/Twitter (via web): {N} pages`
instead — it has no like/repost counts. Likewise, if Reddit came from the web
fallback (reddit.py was 403-blocked), render it as `|- Reddit (via web): {N} pages`
— it has no upvote/comment counts.

### Write results.html

After the stats block, **always** persist the run as a self-contained HTML file
(both modes; also under `--agent`). Build this JSON from the report you just
displayed — do not re-research — and pipe it to `report.py` (default output
`results.html` in the working directory, or the `--out=` path):

```bash
python3 scripts/report.py --out=results.html <<'JSON'
{
  "topic": "{TOPIC}",
  "query_type": "{QUERY_TYPE}",
  "window": "{WINDOW}",
  "requested_at": "{today's date YYYY-MM-DD}",
  "mode": "{SCRIPTS|NATIVE}",
  "learned": [ {"title": "Pattern", "body": "1-2 sentences", "citation": "per r/sub"} ],
  "key_patterns": ["Pattern — per @handle", "..."],
  "stats": ["Reddit: N threads | N upvotes | N comments", "..."],
  "top_voices": "r/sub, HN, @handle",
  "notes": "include ONLY for a partial/degraded run, else omit"
}
JSON
```

Then tell the user the absolute path it printed. If `report.py` fails, note it
but do not block the run.

### Invitation

Tailor to QUERY_TYPE using specifics from the research:

- **RECOMMENDATIONS**: Offer to compare top items, explain trending items, help get started
- **NEWS**: Follow-up on biggest story, implications, what happens next
- **COMPARISON**: Deep dives on each side, focus on a specific dimension
- **PROMPTING**: Write a ready-to-paste prompt based on found patterns
- **GENERAL**: Most discussed angle, practical application, deeper dive on a debate

---

## Step 5: Wait, Then Answer

Stop after the invitation. Answer follow-ups from gathered research only — no new searches.
Only write prompts if explicitly asked.

---

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

---

## Recoverable Setup Gates

Some source failures are a **one-time setup gap** (not logged in, missing key) — not a
transient error. For these, do **not** silently degrade to a weaker fallback. A one-time
fix beats a permanently worse report, so pause and let the user decide.

A gate has four required parts:

1. **Unambiguous trigger** — a specific signal that means *recoverable setup gap*,
   distinct from a genuine empty result or a transient error. Never gate on a vague
   failure (e.g. a timeout) — that would nag the user for no reason.
2. **`--agent` bypass** — if `--agent` is set, do **not** prompt. Take the documented
   fallback and note it in the stats block. A human-in-the-loop gate must never hang
   an unattended run.
3. **Ask, don't degrade** — in interactive runs, stop *before* the fallback and ask
   the user (use the interactive question UI) with exactly three choices:
   - **Fix it for me** — run the gate's fix command yourself, wait for it to finish,
     then re-run the source command and use the real result.
   - **I'll do it myself** — print the exact fix command, pause, and wait for the user
     to confirm they're done; then re-run the source command.
   - **Skip it** — take the documented fallback for this source now.
4. **Graceful dead-end** — if the chosen fix fails or times out, fall back anyway and
   note it. A gate never blocks the rest of the run.

### Registered gates

**X/Twitter — `x.py` not authenticated**
- **Trigger:** `x.py` prints `[]` on stdout **and** its stderr contains the literal
  token `NO_SESSION`. (`[]` with stderr `TIMEOUT`, or `[]` with no marker, is **not**
  this gate — skip X and take the web fallback without prompting.)
- **Fix it for me:** not applicable — cookies can't be read from your browser
  automatically (and X blocks automated logins).
- **I'll do it myself:** tell the user to add `X_AUTH_TOKEN` and `X_CT0` to
  `~/.claude/skills/.env` — copy `auth_token`/`ct0` from a logged-in x.com tab
  (DevTools → Application/Storage → Cookies → x.com). `chmod 600` the file. (Or, if
  they can complete it, `python3 scripts/x.py --login` for the profile path.) Wait
  for their go-ahead, then re-run `python3 scripts/x.py "{TOPIC}" --days={DAYS}`.
- **Skip / fix failed / `--agent`:** run
  `python3 scripts/web.py "{TOPIC}" XFALLBACK --days={DAYS}`, tag results as X/Twitter,
  and render the stats line as `|- X/Twitter (via web): {N} pages`.

**Web — no search-provider key**
- **Trigger:** `preflight.py` reports Web `status:"gated"`, `gate:"web_key"` (no
  `TAVILY_API_KEY` or `EXA_API_KEY` found).
- **Fix it for me:** not applicable — an API key can't be provisioned automatically.
- **I'll do it myself:** tell the user to add one line to `~/.claude/.env` (create it,
  then `chmod 600 ~/.claude/.env`): `TAVILY_API_KEY=...` (free tier at tavily.com) or
  `EXA_API_KEY=...` (exa.ai). Then re-run `python3 scripts/preflight.py` to confirm `ready`.
- **Skip / `--agent`:** proceed on DuckDuckGo; mark Web `degraded` in the stats block.
  If DDG is also blocked in this environment, Web is `down` — omit it.

---

## Error Handling

### SCRIPTS mode

| Source | Failure | Action |
|---|---|---|
| Reddit | `[]` + stderr `403` (IP/UA blocked) | Skip the scraper — `web.py REDDITFALLBACK`, mark "(via web)". No prompt (not user-fixable) |
| Reddit | Rate limited (429) | Retry once after 3s, then `web.py REDDITFALLBACK`, mark "(via web)" |
| X/Twitter (x.py) | `[]` + stderr `NO_SESSION` | **Recoverable Setup Gate** — ask the user (unless `--agent`); on skip/fail/agent → `web.py XFALLBACK`, mark "(via web)" |
| X/Twitter (x.py) | `[]` + `TIMEOUT` / no marker | Skip — `web.py XFALLBACK`, mark "(via web)". No prompt |
| YouTube | Playwright timeout | Skip (returns `[]`; no retry) |
| Polymarket | API unavailable | Skip |
| Web | no Tavily/Exa key | **Recoverable Setup Gate** (`web_key`) — ask unless `--agent`; else DuckDuckGo |
| Web | provider hard error | Auto fail-over: Tavily → Exa → DuckDuckGo |
| Web | DDG also blocked / all fail | Web `down` — omit from report |

### NATIVE mode

| Source | Failure | Action |
|---|---|---|
| Any source | 0 results from site: query | Try broader query without site: filter, tag result as "Web" |
| Polymarket | 0 results | Skip entirely — prediction markets don't always have coverage |
| X/Twitter | Paywalled snippets | Use what's visible in snippet, note limited signal |
| Environment probe | Proxy error on probe itself | Default to NATIVE mode |

### Both modes

If fewer than 3 sources return data, halt and report to user before synthesizing.
