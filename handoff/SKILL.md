---
name: handoff
description: Write a resume-ready HANDOFF.md that captures the current session's state — goal, key decisions, what's done, what's next, open threads, and the files in play — so a fresh session can pick up sharp instead of context-rotted. Use when the user wants to checkpoint or hand off before clearing/compacting — "write a handoff", "/handoff", "checkpoint the session", "save state before I clear", "summarize where we are for a new session", "I'm about to /clear — capture this", "we're getting close to the context limit". Also updates a one-line task label the status line shows. Part of the context-hygiene setup (status line + PreCompact/SessionStart hooks + a lower auto-compact threshold) documented in references/setup.md; pairs with the file-based memory system and CLAUDE.md.
---

# handoff

Write a resume-ready `HANDOFF.md` so a fresh session continues sharp — the antidote to context rot (quality degrades as the window fills; refreshing earlier with a clean handoff keeps output "smart").

## What it does

Distills the *current* conversation into `HANDOFF.md`: the goal, decisions made (and why), what's done, what's next, open questions, and the key files/paths in play — everything a new session needs and nothing it doesn't. It also writes a one-line task label to `.claude/current-task.txt` for the status line. The model writes this (a hook can't summarize); the bundled hooks + status line (see `references/setup.md`) are the *automatic* safety net around it.

## How to run

Invoke `/handoff`, or say "checkpoint the session", "save state before I clear", "write a handoff". Run it when the status-line context meter goes yellow/red, or before a deliberate `/clear`. Then `/clear` (or let auto-compaction run) and the new session reloads the handoff.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | where to write the handoff (default: `./HANDOFF.md`) |
| `--append` | keep prior handoff content as a dated "Previous handoff" section instead of replacing |

## Step 0 — Mode

This is a model-driven writing skill — no mode probe and no per-run scripts. (The `assets/` scripts are the status line + hooks, wired once via `references/setup.md`, not run on each handoff.)

## Steps

1. **Gather state from the conversation** — read back over the session for: the overarching goal; decisions taken and their rationale; what is done and verified; what's next; open questions/risks; and the concrete files, paths, branches, commands in play. Prefer what is *non-obvious* and not already in CLAUDE.md / git. If in a git repo, capture `git status --short` and the current branch so uncommitted work isn't lost across the refresh.
2. **Write `HANDOFF.md`** — use the structure in [`references/handoff-template.md`](references/handoff-template.md), including the **Git state** line (branch + uncommitted files, or "clean"). Be specific and resume-oriented: a new session should be able to act from it without re-deriving context. Record the date.
3. **Update the task label** — write a single concise line (≤ ~60 chars) to `<project>/.claude/current-task.txt` so the status line shows what's in flight. Create `.claude/` if needed.
4. **Offer to commit (only if dirty + interactive)** — if there are uncommitted changes, offer to commit before the refresh so the work is checkpointed. **Defer to the project's git workflow** (branch/commit conventions in its CLAUDE.md; e.g. "commit only when asked", branch-then-merge, protected `main`) and get explicit confirmation. **Commit only — do not push**; pushing is a separate, explicit ask (it's outward and may hit protected branches / CI). The skill runs no git itself — you run it the normal way on confirmation. Under `--agent`: skip the offer entirely (just record the git state in HANDOFF.md).
5. **Tell the user the next move** — review `HANDOFF.md`, then `/clear` (or let auto-compaction run); the new session resurfaces the handoff via the SessionStart hook / CLAUDE.md / MEMORY.md. Under `--agent`: write the files and stop, no prompt.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Composition by reference — complements the file-based memory system (durable facts) and CLAUDE.md (project rules); `HANDOFF.md` holds *this task's* working state. Setup of the status line + hooks is delegated to `update-config` / `statusline-setup` (see `references/setup.md`).
- Honest scope (spec A12): the model writes the handoff because hooks run shell commands, not the model. The PreCompact hook only *preserves* what's been written; keep `HANDOFF.md` fresh so there's always something good to preserve.
- Git: handoff *records* git state and may *offer* to commit, but bundles no git script and never runs git itself or pushes — consistent with the house rule that skills don't run git. The commit (if any) is the user-confirmed, project-aware exception, done the normal way.
- Keyless; no network.
