# Agent fan-out — parallel sweep

Rules for running the Step-4 sweep (and Step-5 follow-up) as parallel
subagents instead of a serial loop. Loaded only when SKILL.md Step 4 chose
fan-out. Two invariants govern everything here:

1. **Parallel gathering, serial synthesis.** Agents search and distill;
   they never write report prose, never do gap analysis, never see each
   other's results mid-round. All judgment stays in the main session.
2. **Degrade, never block.** Any failure below falls back to doing that
   piece serially in the main session; a fan-out problem must never kill
   the research run.

## 1. Fan-out plan

| Rule | Value |
|------|-------|
| Agents per round | one per subquery angle, **cap 8** |
| More angles than 8 | bundle related angles (e.g. `pricing` + `business model`) into one agent |
| Spawn | all agents of a round in a **single message** so they run concurrently |
| Agent type | `research-worker` when the Agent tool offers it (its definition already carries the constraints + contract, so the brief can shrink to the variables: question, angle, sections, mode, budget); else `general-purpose` with the full §2 brief (needs Bash for SCRIPTS mode, WebSearch/WebFetch for NATIVE) |
| Recency angles | **excluded** from fan-out — run `/scan-trends` in the main session (its gates are interactive) and merge its findings at the barrier |

## 2. The agent brief

Fill this template per agent. Keep it self-contained — the agent has no
access to this conversation, the plan, or the other agents.

```
You are a research subagent gathering evidence for ONE angle of a larger
research report. Your final message is machine-read — return ONLY the JSON
described below, no prose around it.

RESEARCH QUESTION: <the overall question>
YOUR ANGLE: <angle name> — <one-line scope of what this angle must cover>
FEEDS SECTIONS: <template section(s) this angle maps to>

HOW TO SEARCH (<SCRIPTS|NATIVE> mode):
<SCRIPTS: run `python3 <ABSOLUTE_SKILL_PATH>/scripts/search.py "<query>"
 --n=10` via Bash; it prints JSON results. Issue 2–4 query variants for
 your angle.>
<NATIVE: use WebSearch with 2–4 query variants for your angle.>
Aim for ~<N> distinct sources. You may WebFetch 1–2 of the most
authoritative results if snippets are too thin to support a claim.

EVIDENCE RULES (non-negotiable):
- Every claim must carry the URL of the source that supports it.
- Mark each claim "quote" (source says this, include the verbatim text)
  or "inference" (you concluded it from the source).
- Do not invent or extrapolate beyond the sources. If your angle has holes,
  report them in "gaps" — an honest gap beats a padded finding.

RETURN EXACTLY THIS SHAPE:
{
  "angle": "<angle name>",
  "findings": [
    {"claim": "...", "url": "...", "kind": "quote|inference",
     "quote": "<verbatim text when kind=quote, else omit>"}
  ],
  "sources_seen": [{"url": "...", "title": "..."}],
  "gaps": ["<what this angle could not surface>"]
}
```

Per-agent source budget (`~<N>` above): `standard` ≈ 3–5, `exhaustive`
≈ 5–8. The totals land in the same ranges as the serial sweep.

## 3. Barrier — after each round

All of this happens in the main session, on the full result set:

1. Collect every agent's JSON; merge `findings` and `sources_seen`.
2. Deduplicate by URL (keep the richest claim per URL).
3. Map findings onto the type template's sections.
4. Build the gap list: sections still thin + every agent-reported `gaps`
   entry. This feeds Step 5.

## 4. Round 2 — focused follow-up (fan-out variant of Step 5)

- Turn the central gap list into targeted follow-up queries, then fan those
  out under the same brief + contract (`standard`: one follow-up round;
  `exhaustive`: up to two).
- Full-content extraction: for the top-cited sources, spawn one agent per
  source (bundle 2–3 small ones) whose brief is "WebFetch this URL and
  extract specifics — pricing, exact quotes, contract terms — under the
  same findings contract."
- Fewer than ~3 follow-up queries? Just run them serially in the main
  session — a round of one agent isn't worth the overhead.

## 5. Failure handling

| Failure | Response |
|---------|----------|
| Agent returns non-JSON or empty output | retry once with a terser brief; still bad → run that angle serially in the main session |
| Agent errors/dies | run its angle serially; never re-spawn more than once |
| `Agent` tool unavailable at Step 4 | entire sweep runs serial (SKILL.md already says so) |
| One angle stalls the round | proceed with the barrier once the others return; chase the straggler's angle serially |

## 6. Why fan-out exists (and what it costs)

- **Wall-clock:** angles run concurrently instead of summing.
- **Context isolation — the bigger win:** each agent burns its own context
  reading pages and returns only distilled findings, so the main context
  stays fresh for synthesis. This matters most at `exhaustive`, which is
  why it's the default there.
- **Cost:** token spend multiplies roughly with agent count. That's why
  `quick` never fans out and `standard` requires `--parallel`.
