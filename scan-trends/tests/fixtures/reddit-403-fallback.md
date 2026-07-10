# Regression: Reddit 403-block must be recoverable via web

## Origin
scan-trends run 2026-06-07 (conan-marketing project). reddit.py returned `[]`
with stderr `403 Client Error: Blocked` on every query. The orchestrator tried
`web.py "<topic>" GENERAL` as a manual fallback — but GENERAL (and every query
type except the fallbacks) lists reddit.com in SKIP_DOMAINS, so Reddit was
filtered out. Result: Reddit was unrecoverable; the run lost its most important
source for a community-sentiment question.

## Failing input
    python3 scripts/web.py "Claude Code cost usage tracker" GENERAL --days=30
    -> 5 results, 0 from reddit.com   (reddit.com is excluded by SKIP_DOMAINS)

## Fix
Add a REDDITFALLBACK query type (mirrors XFALLBACK) that sets the include-domain
to reddit.com across Tavily / Exa / DDG. SKILL.md wires reddit.py's 403 (`[]` +
stderr contains `403`) to this fallback, tagged "Reddit (via web)".

## Expected after fix
    python3 scripts/web.py "Claude Code cost usage tracker" REDDITFALLBACK --days=30
    -> results, all from reddit.com

## Verified 2026-06-07
GENERAL -> 5 results / 0 reddit hits;  REDDITFALLBACK -> 5 results / 5 reddit hits.
