# SCRIPTS mode — per-source notes, fallbacks, and error handling

Loaded by `SKILL.md` Step 2 when `MODE = SCRIPTS`. Read this before treating any
source result as empty or failed. (NATIVE-mode handling lives in
`references/native-mode.md`; gate walkthroughs in `references/gates.md`.)

## Per-source interpretation notes

- **Keep the query SHORT — these scrapers are keyword matchers, not semantic
  search.** Pass a tight 2–5 keyword distillation of `{TOPIC}`, not a long
  natural-language sentence. A long query returns `[]` from reddit/x/hackernews
  even when the topic is well-covered (e.g. a paragraph-long query returns nothing;
  `"Claude Code"` returns dozens). If a source comes back empty, retry once with a
  shorter/broader keyword set before treating it as genuinely empty.
- `x.py` (X/Twitter) honors `--days` via X's native `since:` operator. Interpret its
  result per the gate registry in `references/gates.md`:
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

## Failure → action table

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
