# HANDOFF.md structure

Loaded by `SKILL.md` Step 2. The goal is a document a *fresh* session can act
from without re-deriving the conversation. Be specific; favour the non-obvious.
Omit a section if it's genuinely empty rather than padding it.

```markdown
# Handoff — <short task title>

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
committed during handoff or deliberately left.>

## Don't redo
<Dead ends already tried, so the next session doesn't repeat them.>
```

## Writing guidance

- **Resume test:** after writing, ask "could a new session take the next step
  from this alone?" If not, add what's missing.
- **Decisions > narrative.** A log of *what we decided and why* is worth more
  than a play-by-play of what happened.
- **Don't duplicate** CLAUDE.md (project rules), the memory files (durable
  cross-session facts), or git history. Handoff = *this task's* working state.
- **Keep it tight.** A bloated handoff reintroduces the rot you're escaping.
  Aim for something a reader skims in under a minute.
- `--append` mode: prepend the new handoff and demote the old one under
  `## Previous handoff (<date>)` rather than deleting it.
