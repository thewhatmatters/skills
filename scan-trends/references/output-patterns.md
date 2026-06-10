# Output Patterns

Loaded by `SKILL.md` Step 4 (every run). §1–§4 apply to all runs in display
order; §5 adds the QUERY_TYPE-specific formats.

## 1. "What I learned" — layout + citation rules

Ground everything in actual research — exact names, specific quotes, what
sources actually say.

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

## 2. Stats block

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

## 3. results.html

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

## 4. Invitation

Tailor to QUERY_TYPE using specifics from the research:

- **RECOMMENDATIONS**: Offer to compare top items, explain trending items, help get started
- **NEWS**: Follow-up on biggest story, implications, what happens next
- **COMPARISON**: Deep dives on each side, focus on a specific dimension
- **PROMPTING**: Write a ready-to-paste prompt based on found patterns
- **GENERAL**: Most discussed angle, practical application, deeper dive on a debate

## 5. QUERY_TYPE-specific formats

### Comparison Format (QUERY_TYPE = COMPARISON)

```
# {TOPIC_A} vs {TOPIC_B}: What the Community Says (Last {WINDOW})

## Quick Verdict
[1-2 sentence data-driven summary with source counts]

## {TOPIC_A}
**Community Sentiment:** Positive/Mixed/Negative ({N} mentions across {sources})

**Strengths**
- [strength with source attribution]

**Weaknesses**
- [weakness with source attribution]

## {TOPIC_B}
**Community Sentiment:** Positive/Mixed/Negative ({N} mentions across {sources})

**Strengths**
- [strength with source attribution]

**Weaknesses**
- [weakness with source attribution]

## Head-to-Head
| Dimension       | {TOPIC_A} | {TOPIC_B} |
|-----------------|-----------|-----------|
| [dimension]     | [finding] | [finding] |
| [dimension]     | [finding] | [finding] |

## The Bottom Line
Choose {TOPIC_A} if...
Choose {TOPIC_B} if...
```

### Recommendations Format (QUERY_TYPE = RECOMMENDATIONS)

```
Most mentioned:

**[Name]** — {N}x mentions
Use case: [what it does]
Sources: @handle, r/sub, sitename

**[Name]** — {N}x mentions
Use case: [what it does]
Sources: @handle, r/sub
```

### Prompt Output Format (QUERY_TYPE = PROMPTING)

Write a single, ready-to-paste prompt. Use patterns and terminology actually found in research.

```
Here's your prompt for {TARGET_TOOL}:

---

[The prompt itself]

---

This uses [1-line explanation of the research insight applied].
```
