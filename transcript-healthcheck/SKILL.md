---
name: transcript-healthcheck
description: >-
  Use on weekday (or on-demand) mining of agent conversation transcripts for
  repeated friction that should become a skill, bot tweak, or routine.
---
# Transcript healthcheck

Mine recent agent conversation transcripts for repeated friction. Propose fleet changes only — never create skills, bots, or routines until the user picks. Stay quiet when the corpus is healthy and nothing actionable appears.

## 1. Window

Determine the mining window:

1. Prefer **since last successful run** of this check (routine last-success / automation status if present).
2. Else default to **last 1 weekday**.

Record the window start clearly in the handoff so the parent can show it.

## 2. Corpus sources (unblind)

Discover profiled agents from `/home/box/agent-data/agents/*/profile.json` (and the same tree under `/home/box/sand-data/agents/` if present). Skip `sand-subagent-*`.

**Primary (required):** live transcripts via the host transcript reader (`ReadTranscript` with each agent's id). Page newest-first within the window. This is the source of truth when chats are active.

**Secondary (cross-check only):**
- `/home/box/sand-data/agents/<id>/store.db` and `/home/box/agent-data/agents/<id>/store.db` — table `transcript_entries` (JSON in `entry`; timestamps live inside that JSON as `timestampMs`)
- jsonl under `/home/box/*/agent-transcripts/<id>/` — treat as a legacy mirror

If live ReadTranscript has recent turns but on-disk `store.db` / jsonl max `timestampMs` (or mtime) is older than the window, treat **on-disk as stale** and still mine the live reader. Note the desync as an **infra** finding.

Fan out agent reads in parallel.

## 3. Stale-corpus alarm

Compute newest evidence:

1. Newest turn from live ReadTranscript across profiled agents
2. Else max `timestampMs` parsed from `transcript_entries.entry`
3. Else newest jsonl mtime

**If the best available corpus is older than the window start, or older than N=3 days:**

- Report **LOUDLY** that the mine is blind — do **not** quietly say “nothing to propose.”
- List agents with empty live transcripts, missing folders, empty `store.db`, or mirrors older than the window.
- Hand this alarm to the parent as the primary finding.

A stale or empty corpus is never “healthy quiet.”

## 4. Mine

Within the window, look for repeated patterns:

- Repeated friction / workarounds the user or agents keep reinventing
- Skills named in lore but missing on disk
- Broken or never-firing routines
- Stub bots that exist only as placeholders
- Process pain that a skill, bot tweak, or routine would remove

Cluster findings into proposals of type **skill | bot | routine** (or **infra** when the fix is environment/path/auth/mirroring, not a new recipe).

## 5. Output

Hand off to the parent to contact the user with **numbered proposals**. Each proposal should include:

- Type: skill | bot | routine | infra
- One-line title
- Why (evidence from transcripts: frequency / agents / example friction)
- Suggested next step (draft only — do not create)

**Quiet when empty:** If the corpus is fresh (non-stale) and there is no actionable repeated friction, produce no filler report.

**Do not** create skills, bots, or routines from this check.

## 6. Anti-patterns

- **No new bot seats from vibes.** Freeze headcount: only propose a new bot seat when there is a genuinely new job that is **not** inventable from chat friction alone — and even then propose only; never create.
- **Delete-stub / tidy existing** is cleanup of placeholders, not a new seat.
- No assistant-specific names, Slack channels, or bot ids hardcoded in this recipe — stay generic and reusable across the fleet.
- Do not invent proposals from a single one-off complaint.
