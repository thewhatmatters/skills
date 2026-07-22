# Checkpoint memory-entry structure

Loaded by `SKILL.md` Step 2. The goal is an entry a *fresh* session can act
from without re-deriving the conversation. Be specific; favour the non-obvious.
Omit a section if it's genuinely empty rather than padding it.

The entry is a standard memory file: frontmatter + body. The frontmatter
`description` is the one-liner that also goes on the MEMORY.md index line —
make it say the current task **and** the very next step.

```markdown
---
name: checkpoint
description: <task in flight — next step. e.g. "US-003 orders API half-built — finish handler, then typecheck">
metadata:
  type: project
---

# Checkpoint — <short task title>

_Updated <YYYY-MM-DD> · session refresh checkpoint_

## Goal
<1–3 sentences: what we're trying to accomplish overall.>

## Current state
<What is done AND verified, vs. in progress. Be concrete — name the files,
functions, branches, endpoints touched. "US-002 done & typechecked; US-003
half-written in src/api/orders.ts".>

## Next steps
<Ordered, actionable. The first line should be the very next thing to do.>

## Key decisions (and why)
<Decisions that would be expensive to re-litigate or re-derive. Include the
*why*, briefly. This is the part context rot destroys first.>

## Open questions / risks
<Unresolved choices, things to watch, known sharp edges.>

## Files & commands in play
<Paths, branches, the build/test/run commands, any URLs or IDs. So the next
session doesn't have to rediscover the workspace.>

## Git state
<Current branch + `git status --short` (or "clean"). So a refresh never loses
track of uncommitted work. If anything is uncommitted, note whether it was
committed during checkpoint or deliberately left.>

## Don't redo
<Dead ends already tried, so the next session doesn't repeat them.>
```

## Writing guidance

- **Resume test:** after writing, ask "could a new session take the next step
  from this alone?" If not, add what's missing.
- **Decisions > narrative.** A log of *what we decided and why* is worth more
  than a play-by-play of what happened.
- **Don't duplicate** CLAUDE.md (project rules), the *other* memory entries
  (durable one-fact files), or git history. Checkpoint = *this task's*
  working state — the one deliberately ephemeral entry in the memory dir,
  overwritten each run.
- **Keep it tight.** A bloated checkpoint reintroduces the rot you're
  escaping. Aim for something a reader skims in under a minute. (The
  SessionStart hook truncates past ~8k chars.)
- **MEMORY.md upsert:** replace the existing `- [Checkpoint](checkpoint.md) — …`
  line if present, else append it. Never let two checkpoint lines accumulate.
- `--append` mode: prepend the new checkpoint and demote the old one under
  `## Previous checkpoint (<date>)` rather than deleting it.
