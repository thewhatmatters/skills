# handoff

**What it is:** writes a `HANDOFF.md` that captures where you are, so you can start a fresh session without losing the thread — and stay sharp instead of letting a full context window dull the output.

## What you get

- A resume-ready `HANDOFF.md`: goal, current state, next steps, key decisions, open questions, files in play, and dead-ends to avoid.
- A one-line task label (`.claude/current-task.txt`) that the status line shows.

## How to run

Say `/handoff`, "checkpoint the session", or "save state before I clear". Run it when the context meter goes yellow/red, or right before you `/clear`.

## What it needs

Nothing to run the skill itself — it just writes files. The *automatic* extras (a status-line context meter, snapshot-on-compaction and resurface-on-start hooks, and an earlier auto-compact threshold) are a one-time setup described in `references/setup.md`, wired through the `update-config` and `statusline-setup` skills.

## Why it exists

LLM output quality degrades as the context window fills — "context rot," a gradual slide that can begin well before the limit. The model can't see its own context level and can't restart itself, so the fix is: you get a visual cue (status line), you checkpoint with `/handoff`, you start fresh, and the new session reloads the handoff. The result stays "smart."

## How it works (high level)

1. Reads back over the session for the goal, decisions, what's done/next, and the files in play.
2. Writes `HANDOFF.md` in a resume-oriented structure (see `references/handoff-template.md`).
3. Updates the status-line task label.
4. Tells you to `/clear` (or lets auto-compaction run); the next session resurfaces the handoff.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/handoff-template.md` — the HANDOFF.md structure + writing guidance.
- `references/setup.md` — the one-time status-line + hooks + threshold setup.
