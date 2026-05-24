# audit-skill

**What it is:** a reviewer for Claude skills. It checks a skill against our
house standard and tells you what's solid and what needs fixing.

## What you get

A clear, severity-grouped report:

- **Issues to address** — grouped high → low, each with the exact file/line and
  a concrete fix.
- **What's working well** — so you know what *not* to touch.

It's **report-only**: it never changes your skill unless you explicitly ask it
to. Reviewing is safe to run anytime.

## How to run it

Just ask, e.g.:

- "audit the scan-trends skill"
- "review skill X"
- "is this skill well-built?"
- "QA the skill in ./my-skill"

## What it needs

The canonical spec file must exist: `~/.claude/skills/skill-architecture.md`.
That file *is* the standard — the auditor reads it in full and checks the
target skill against it (structure, reliability, secret hygiene, setup gates,
preflight, conventions). The two ship together for this reason.

## How it works (high level)

1. Reads `skill-architecture.md` — the rulebook.
2. Reads the target skill's files.
3. Reports where the skill meets or misses the rulebook, with evidence and
   suggested fixes — and stops there. You decide what to act on.

## Related

- `skill-architecture.md` (repo root) — the standard it checks against.
- `generate-skill` — the counterpart that *creates* skills meeting this same
  standard, then runs this auditor on its own output.
