# checkpoint

**What it is:** checkpoints where you are into project memory, so you can start a fresh session without losing the thread — and stay sharp instead of letting a full context window dull the output. (Successor to the retired `handoff` skill; there is no more `HANDOFF.md` in your repo.)

## What you get

- A resume-ready `checkpoint.md` memory entry (in `~/.claude/projects/<project>/memory/`): goal, current state, next steps, key decisions, open questions, files in play, and dead-ends to avoid — plus its one-liner on the auto-loaded MEMORY.md index.
- A one-line task label (`.claude/current-task.txt`) that the status line shows.

## How to run

Say `/checkpoint`, "checkpoint the session", or "save state before I clear". Run it when the context meter goes yellow/red, or right before you `/clear`.

## What it needs

Nothing to run the skill itself — it just writes files. The *automatic* extras (a status-line context meter, snapshot-on-compaction and resurface-on-start hooks, and an earlier auto-compact threshold) are a one-time setup described in `references/setup.md`, wired through the `update-config` and `statusline-setup` skills.

## Why it exists

LLM output quality degrades as the context window fills — "context rot," a gradual slide that can begin well before the limit. The model can't see its own context level and can't restart itself, so the fix is: you get a visual cue (status line), you checkpoint with `/checkpoint`, you start fresh, and the new session reloads the checkpoint. The result stays "smart."

## How it works (high level)

1. Reads back over the session for the goal, decisions, what's done/next, and the files in play.
2. Writes the `checkpoint.md` memory entry in a resume-oriented structure (see `references/checkpoint-template.md`) and upserts its MEMORY.md index line.
3. Updates the status-line task label.
4. Tells you to `/clear` (or lets auto-compaction run); the next session's SessionStart hook resurfaces the checkpoint in full.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why" (per-skill decision log; the filename is the suite-wide convention, unrelated to the retired skill).
- `references/checkpoint-template.md` — the memory-entry structure + writing guidance.
- `references/setup.md` — the one-time status-line + hooks + threshold setup.
