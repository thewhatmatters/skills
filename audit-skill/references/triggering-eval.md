# Triggering evaluation (the `--triggers` mode)

Loaded by `SKILL.md` only when a triggering check is requested (progressive
disclosure, spec A1). The structural audit never needs this file.

## What this measures

Whether each skill's `description` actually causes Claude to route real user
prompts to it — and, crucially, whether **overlapping skills steal each other's
queries** (cross-triggering). Example battleground: `deep-research` ("research
X", "map the landscape") vs `scan-trends` ("what are people saying about X this
week"). A greedy description fires on the sibling's territory.

## Why NOT skill-creator's run_eval / run_loop

skill-creator's `run_eval.py` registers an ad-hoc command named
`<skill>-skill-<uuid>` and counts a trigger only when the `Skill` tool fires
with **that** name. Our skills are already installed (user-scope skills load on
every `claude -p`), so Claude fires the **real** skill — `{"skill":"deep-research"}`
— whose name ≠ the ad-hoc name. Every real trigger goes undetected → a false
`0/3` on every query, including obvious ones, even at long timeouts. run_eval is
built for skills that are **not yet installed**; it cannot audit installed ones.

## The method we use instead: all-skills bake-off

`scripts/trigger_eval.py` presents **all** real skills (the live environment) and
records whichever one each query routes to:

1. For each query, `claude -p "<q>" --output-format stream-json`.
2. Parse the first assistant `tool_use` named `Skill`; record `input.skill`.
3. Kill the process immediately — we want the routing *decision*, not to run the
   skill (which would be slow + costly). A wall-clock timer guarantees no hang.

This reflects exactly what the user experiences, and it captures cross-triggering
because every skill is present at once (run_eval's isolated test never could).

## Building a good eval set

`trigger_eval.py` takes JSON: `[{"query": "...", "expected": "<skill|none>"}, ...]`.
Design it to probe the boundary, not just easy wins:

- **Should-trigger** (per target skill): realistic, detailed, varied phrasing —
  formal and casual, with file paths / company names / backstory. Cover the
  skill's range.
- **Cross-seeded negatives** (the valuable ones): queries that belong to an
  *overlapping sibling*. For `deep-research`, seed `expected: scan-trends` items
  like "what's everyone saying about the new Claude model on HN this week". If
  deep-research fires on these, that's the false-positive you're hunting.
- **Pure negatives** (`expected: none`): simple/other-domain prompts (fix a test,
  weather, explain OAuth) that should route to no skill.
- Aim ~30 queries with a real mix. `expected` may name any skill (e.g.
  `generate-prd`) — a query routing to a *different correct* skill is not a
  false positive for the pair under test.

## Running it (gated — costs real money/time)

```
python3 scripts/preflight.py            # gates on the `claude` CLI; notes cost
python3 scripts/trigger_eval.py --eval-set <set.json> --model <session-model> \
    --out /tmp/trigger-result.json
```

- Preflight gate `CLAUDE_CLI_MISSING` → triggering unavailable (structural audit
  still works); never blocks the rest of an audit.
- Use the **session model** (e.g. `claude-opus-4-7`) so results match what the
  user experiences. A cheaper model is a close-but-not-identical proxy.
- This fires one `claude -p` per query. Run it **on description changes**, not on
  a schedule — triggering only moves when a description does.
- Default is 1 run/query (a single sample). For a variance-controlled rate,
  duplicate the eval set entries or re-run and average.

## Reading results

`routing match: N/total` plus a per-query table (`OK`/`XX`, expected vs fired).
A clean result is high match with **zero** cross-fires on the seeded negatives.
Failures point at description wording: an over-greedy description fires on a
sibling's queries; an under-specified one lets complex queries fall through to
`none`. Fix the wording (sharpen the trigger phrases / add the boundary cue),
then re-run. For systematic wording optimization, hand off to
`example-skills:skill-creator` (which owns description optimization).
