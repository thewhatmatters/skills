# One-time setup: the context-hygiene system

`/handoff` works on its own (it just writes `HANDOFF.md` + the task label). This
file documents the *automatic* pieces around it — a status line, two hooks, and
a lower auto-compact threshold. Wire them once via the `update-config` skill
(hooks/env) and `statusline-setup` (status line); they all live in
`~/.claude/settings.json`. The scripts they point at are bundled in this skill's
`assets/`, so they stay version-controlled.

> **Merge, don't paste.** The four snippets below are shown separately for
> clarity, but in `settings.json` they're keys of **one** object: a single
> `statusLine`, a single `hooks` (with `PreCompact` *and* `SessionStart` inside
> it), and a single `env`. `update-config` merges them into your existing
> settings correctly — let it, rather than hand-pasting these as-is.

## Why this exists

Output quality degrades as the context window fills ("context rot" — a gradient,
not a cliff; it can start well before the limit). You can't fully automate a
"refresh now" because: the **model can't read its own context %**, **hooks run
shell commands (not the model) so they can't summarize**, and **session restart
is user-driven**. So the design is: keep state in a model-written `HANDOFF.md`,
*show* the human the context fill so they know when to refresh, *preserve* state
automatically at the compaction boundary, and *resurface* it on the next session.

## 1. Status line — the context meter + task label

Shows model · branch · **context fill % (green→yellow→red)** · cost · current
task. It reads `context_window.used_percentage` (provided on stdin) and
`<cwd>/.claude/current-task.txt`. Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/skills/handoff/assets/statusline.py"
  }
}
```

Thresholds live at the top of `assets/statusline.py` (`YELLOW=50`, `RED=75`).
When it's red it appends a "⚠ /handoff" nudge — your cue to checkpoint + `/clear`.

## 2. PreCompact hook — snapshot before compaction

Fires before auto (~95%, or your override) or manual `/compact`. Copies the
current `HANDOFF.md` to a timestamped archive so state survives the boundary
(it can only *preserve* what the model wrote — keep `HANDOFF.md` fresh). Add:

```json
{
  "hooks": {
    "PreCompact": [
      { "hooks": [ { "type": "command",
        "command": "python3 ~/.claude/skills/handoff/assets/precompact_handoff.py" } ] }
    ]
  }
}
```

## 3. SessionStart hook — resurface the handoff

On a new/resumed/cleared session, injects `HANDOFF.md` back as additional
context so you resume sharp. Add:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command",
        "command": "python3 ~/.claude/skills/handoff/assets/sessionstart_handoff.py" } ] }
    ]
  }
}
```

(If a Claude Code version doesn't honor `additionalContext` for SessionStart,
the handoff is still on disk; add `@HANDOFF.md` to the project's CLAUDE.md as a
guaranteed reload path.)

## 4. Lower the auto-compact threshold — the highest-leverage knob

Refresh *before* rot bites instead of at ~95%. Set in `~/.claude/settings.json`:

```json
{ "env": { "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "65" } }
```

Tune to taste (lower = fresher but more frequent refreshes).

## The loop in practice

1. Status line creeps yellow→red → run `/handoff` (or before any deliberate `/clear`).
2. `/handoff` writes `HANDOFF.md` + the task label.
3. `/clear` (or auto-compaction at your threshold fires the PreCompact snapshot).
4. New session → SessionStart hook resurfaces the handoff → continue sharp.
