# NATIVE mode — per-source web_search queries

Loaded by `SKILL.md` Step 2 when `MODE = NATIVE`. In NATIVE mode every source is
covered via targeted `web_search` queries — slightly less granular than the
scripts, but fully functional.

First compute the lookback window — never hardcode a date:

- `CUTOFF` = today's date minus N days (N = `--days`, default 30), formatted `YYYY-MM-DD`
- `YEAR` = the current calendar year; if `CUTOFF` falls in the prior year, use both years

Run each search separately and note which source it corresponds to. Capture
titles, snippets, and URLs for synthesis.

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

After each search, note: source tag, number of results found, and any
high-signal snippets. Track these per-source for the stats block.

## NATIVE-mode error handling

| Source | Failure | Action |
|---|---|---|
| Any source | 0 results from site: query | Try broader query without site: filter, tag result as "Web" |
| Polymarket | 0 results | Skip entirely — prediction markets don't always have coverage |
| X/Twitter | Paywalled snippets | Use what's visible in snippet, note limited signal |
| Environment probe | Proxy error on probe itself | Default to NATIVE mode |
