# Recency pass

Loaded by SKILL.md when RECENCY is on (`--recent`, `--days=N`, or Step 1
classifies the question as recent discussion). `/scan-trends` is this pass —
there is no sibling skill.

Run it in the **main session**, never inside a fan-out subagent. Merge
findings into the working set with explicit `provider` values.

`DAYS` = `--days` if given, else 30. `CUTOFF` = today minus DAYS
(`YYYY-MM-DD`). Distill `{TOPIC}` to 2–5 keywords for the scrapers (they
are keyword matchers, not semantic search).

## Hard sources (scripts; NATIVE → WebSearch)

From `scripts/` next to this skill (JSON on stdout, `[]` on failure):

```bash
python3 scripts/reddit.py "{TOPIC}" --days={DAYS}
python3 scripts/hackernews.py "{TOPIC}" --days={DAYS}
python3 scripts/polymarket.py "{TOPIC}" --days={DAYS}
```

| Script | Provider tag | Notes |
|--------|--------------|--------|
| `reddit.py` | `reddit` | Empty/`[]` or 429 on stderr → WebSearch `site:reddit.com {TOPIC} after:{CUTOFF}` |
| `hackernews.py` | `hn` | Algolia date filter is the window |
| `polymarket.py` | `polymarket` | Active markets only; `--days` is ignored by the API — say so in the report |

No python3 → skip the scripts and use the WebSearch queries below for all
three as well.

## Soft sources (always WebSearch)

Do **not** scrape X or YouTube. No cookie Playwright.

- X: `site:x.com OR site:twitter.com {TOPIC} since:{CUTOFF}` → `websearch`
- YouTube: `site:youtube.com {TOPIC} {YEAR}` → `websearch`
- Web: two queries from the research type (news / discussion / `{TOPIC} {YEAR}`)

## Weighing (before synthesis)

1. Engagement ranks higher — Reddit score, HN points, YouTube views in
   snippets beat raw mentions.
2. The same theme on Reddit + HN + X is the lead.
3. Polymarket odds are high-signal; quote % and volume; they are not a
   date window.
4. Quote top Reddit / HN comments when present.
5. Name contradictions between sources.

## Working-set shape

Each item: `url`, `title`, `snippet` or quote, `provider` in
`reddit | hn | polymarket | websearch | webfetch`. In the report, put
discussion-derived claims in a **Community signals** subsection (usually
under `trends` or `gaps`) so they are not read as authoritative.

If the **whole question** is recency, still pick a type template (often
`landscape`) and let this pass supply most of the evidence. Filename stays
`research-<slug>.md` — no separate trends HTML.
