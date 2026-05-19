# Output Patterns

## Comparison Format (QUERY_TYPE = COMPARISON)

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

## Recommendations Format (QUERY_TYPE = RECOMMENDATIONS)

```
Most mentioned:

**[Name]** — {N}x mentions
Use case: [what it does]
Sources: @handle, r/sub, sitename

**[Name]** — {N}x mentions
Use case: [what it does]
Sources: @handle, r/sub
```

## Prompt Output Format (QUERY_TYPE = PROMPTING)

Write a single, ready-to-paste prompt. Use patterns and terminology actually found in research.

```
Here's your prompt for {TARGET_TOOL}:

---

[The prompt itself]

---

This uses [1-line explanation of the research insight applied].
```
