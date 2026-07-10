# refine-skill

**What it is:** Improve a skill by learning from one real session that used it —
propose an evidence-grounded, validated diff for the user to approve.

## What you get

- A markdown findings report, grouped by class (skill bug / routing-doc / user
  preference), each finding citing the transcript and carrying a proposed action.
- For skill bugs: a *validated* diff (re-run on the captured failing input,
  compiled, and re-audited) that you approve before anything is written.
- For preferences: a proposed memory entry instead of a skill edit.

## How to run

Say "refine the `<skill>` skill", "reflect on this session and improve `<skill>`",
or `/refine-skill <skill>`. Example: right after an `ingest-source` run, `/refine-skill
ingest-source` reads the session, finds where you had to fix things by hand, and
proposes the fix.

## What it needs

Nothing to set up for the manual command — it is keyless and reads only local
files: your session transcripts under `~/.claude/projects/<project>/` and the
target skill's own directory. `audit-skill` should be present so proposed code
changes can be checked for spec compliance; without it, that one validation step
is skipped (and said so).

**To enable the optional Stop-hook offer** (e.g. after cloning to a new machine):

```
python3 refine-skill/scripts/install_hook.py        # wire it
python3 refine-skill/scripts/install_hook.py --remove   # unwire it
```

This edits `~/.claude/settings.json` — user-global config that lives *outside* this
repo, so it does not travel with a clone. The installer is idempotent, preserves
your other settings, backs up before writing, and computes the handler's absolute
path from its own location (portable across machines/users — no hardcoded home
dir). `preflight.py` reports `HOOK_NOT_INSTALLED` when it isn't wired.

## How it works (high level)

1. Find the session transcript and the skill it used.
2. Extract concrete friction: one-off workarounds Claude wrote, gates that fired,
   output that needed hand-fixing, errors.
3. Classify each finding as a skill bug, a routing/description gap, or a user/task
   preference — and resist changing the skill on the strength of a single session.
4. For real bugs, draft a fix and prove it (re-run on the failing input, compile,
   re-audit) before showing it.
5. Report the findings and proposed actions for you to approve. It never commits,
   and never edits a skill without your go-ahead.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/reflection-model.md` — the classification taxonomy, evidence signals,
  validation ladder, and the n=1 overfitting guard.
