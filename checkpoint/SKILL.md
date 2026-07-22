---
name: checkpoint
description: Checkpoint the current session's working state into project memory — goal, key decisions, what's done, what's next, open threads, and the files in play — as a `checkpoint.md` memory entry that auto-reloads next session, so a fresh session picks up sharp instead of context-rotted. Use when the user wants to checkpoint before clearing/compacting — "checkpoint", "/checkpoint", "checkpoint the session", "save state before I clear", "summarize where we are for a new session", "I'm about to /clear — capture this", "we're getting close to the context limit", or legacy "write a handoff" / "/handoff". Also updates a one-line task label the status line shows. Replaces the retired handoff skill (HANDOFF.md is gone; state lives in the project's memory dir). Part of the context-hygiene setup (status line + PreCompact/SessionStart hooks + a lower auto-compact threshold) documented in references/setup.md; pairs with CLAUDE.md and curate-vault.
---

# checkpoint

Checkpoint the session's working state into **project memory** so a fresh session continues sharp — the antidote to context rot (quality degrades as the window fills; refreshing earlier with a clean checkpoint keeps output "smart"). Successor to the retired `handoff` skill: same job, but the artifact is a memory entry, not a `HANDOFF.md` in the repo's working tree.

## What it does

Distills the *current* conversation into a `checkpoint.md` entry in the project's memory directory (`~/.claude/projects/<munged-cwd>/memory/`): the goal, decisions made (and why), what's done, what's next, open questions, and the key files/paths in play — everything a new session needs and nothing it doesn't. Updates the `MEMORY.md` index line so the checkpoint is visible in the auto-loaded index, and writes a one-line task label to `<project>/.claude/current-task.txt` for the status line. The model writes all of this (a hook can't summarize); the bundled hooks + status line (see `references/setup.md`) are the *automatic* safety net: SessionStart injects the full checkpoint into the next session, PreCompact snapshots it before compaction.

## How to run

Invoke `/checkpoint`, or say "checkpoint the session", "save state before I clear". Run it when the status-line context meter goes yellow/red, or before a deliberate `/clear`. Then `/clear` (or let auto-compaction run) and the new session reloads the checkpoint.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | *additionally* write a plain markdown copy (no memory frontmatter) to PATH — for handing off to a human teammate or another tool. The memory entry is still written; PATH gets no hook safety net |
| `--append` | keep prior checkpoint content as a dated "Previous checkpoint" section in the entry body instead of replacing |
| `--harvest` | run the step-5 knowledge harvest unconditionally after writing the checkpoint — skips the ask, not the gates (curate-vault's per-article confirmation still applies). For milestone checkpoints: `/checkpoint --harvest` |

## Step 0 — Mode

This is a model-driven writing skill — no mode probe and no per-run scripts. (The `assets/` scripts are the status line + hooks, wired once via `references/setup.md`, not run on each checkpoint.)

## Steps

1. **Gather state from the conversation** — read back over the session for: the overarching goal; decisions taken and their rationale; what is done and verified; what's next; open questions/risks; and the concrete files, paths, branches, commands in play. Prefer what is *non-obvious* and not already in CLAUDE.md / git / other memory entries. If in a git repo, capture `git status --short` and the current branch so uncommitted work isn't lost across the refresh.
2. **Write the checkpoint memory entry** — to `<memory-dir>/checkpoint.md`, where `<memory-dir>` is `~/.claude/projects/<munged-cwd>/memory/` and `<munged-cwd>` is the project cwd with every character outside `[A-Za-z0-9-]` replaced by `-` (e.g. `/Users/me/dev/app` → `-Users-me-dev-app`). Create the directory if missing. Use the structure in [`references/checkpoint-template.md`](references/checkpoint-template.md): memory frontmatter (`name: checkpoint`, a one-line `description` of current state + next step, `metadata.type: project`) plus the sectioned body including the **Git state** line (branch + uncommitted files, or "clean"). Overwrite the previous checkpoint — it is ephemeral by design (`--append` demotes it instead). Be specific and resume-oriented: a new session should be able to act from it without re-deriving context. Record the date. Then upsert the index line in `<memory-dir>/MEMORY.md`: `- [Checkpoint](checkpoint.md) — <same one-liner>` (replace an existing Checkpoint line; append if absent). If a legacy `<cwd>/HANDOFF.md` exists, fold anything still-relevant into the entry and delete the file — HANDOFF.md is retired. With `--out=PATH`, also write the body (sans frontmatter) to PATH.
3. **Update the task label** — write a single concise line (≤ ~60 chars) to `<project>/.claude/current-task.txt` so the status line shows what's in flight. Create `.claude/` if needed.
4. **Offer to commit (only if dirty + interactive)** — if there are uncommitted changes, offer to commit before the refresh so the work is checkpointed. **Defer to the project's git workflow** (branch/commit conventions in its CLAUDE.md; e.g. "commit only when asked", branch-then-merge, protected `main`) and get explicit confirmation. **Commit only — do not push**; pushing is a separate, explicit ask (it's outward and may hit protected branches / CI). The skill runs no git itself — you run it the normal way on confirmation. Under `--agent`: skip the offer entirely (just record the git state in the checkpoint).
5. **Offer a knowledge harvest (interactive only)** — if the session produced durable, non-derivable knowledge (a decision with real alternatives, a gotcha that cost time, a repeatable procedure), ask once: *"Anything here worth curating into the vault? I can run `/curate-vault` before you clear."* Run it only on yes — it has its own per-article confirmation gate. This must happen **before** `/clear` (the skill reads the live session). If nothing qualifies, don't ask. With `--harvest`: skip the question and run `/curate-vault` directly — frequent milestone runs are cheap because its dedupe turns re-captures into updates or nothing (an honest "nothing new since the last harvest" is a valid outcome; say so in one line). Under `--agent`: skip the offer (and ignore `--harvest` — the harvest's gate needs a human).
6. **Tell the user the next move, verbatim** — close with: *"Next: `/clear` when ready. The checkpoint is in project memory and the SessionStart hook reloads it in full. Skip `/compact` — with a fresh checkpoint, `/clear` + the reload beats a machine summary (compacting first just spends tokens on a worse summary the clear discards)."* If this was a mid-task checkpoint rather than a session end, say they can simply keep working instead. The model cannot run `/clear`/`/compact` itself (they're user-side CLI commands) and must not pretend otherwise; the pause is deliberate — clearing is irreversible and the live context is the last chance to catch anything the checkpoint missed. Under `--agent`: write the files and stop, no prompt.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Composition by reference — complements CLAUDE.md (project rules) and `curate-vault` (durable insights → the OKF vault; offered at the session boundary in step 5). The checkpoint entry lives *inside* the file-based memory system but is deliberately ephemeral: one `project`-type entry, overwritten per checkpoint, holding *this task's* working state — unlike the durable one-fact-per-file entries around it. Setup of the status line + hooks is delegated to `update-config` / `statusline-setup` (see `references/setup.md`).
- Honest scope (spec A12): the model writes the checkpoint because hooks run shell commands, not the model. Memory's native loading is the index line + relevance recall only — the SessionStart hook is what guarantees the *full* checkpoint lands in the next session's context; keep the entry fresh so there's always something good to inject, and the PreCompact hook snapshots it (to `~/.claude/.cache/checkpoint/`) so compaction never eats the only copy.
- Git: checkpoint *records* git state and may *offer* to commit, but bundles no git script and never runs git itself or pushes — consistent with the house rule that skills don't run git. The commit (if any) is the user-confirmed, project-aware exception, done the normal way.
- Keyless; no network.
