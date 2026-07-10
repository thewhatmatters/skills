# generate-skill

**What it is:** a scaffolder for new Claude skills. It bootstraps a skill that
already follows our house conventions, then has `audit-skill` review it —
so you start from a structure that's known to be solid.

## What you get

A new folder under `~/.claude/skills/<name>/` (or wherever you point it),
containing:

- `SKILL.md` — Claude's operating instructions, with valid YAML frontmatter
  validated against the **current** Claude docs (no invented fields).
- `README.md` — plain-language explainer (house convention; this file is one).
- `handoff.md` — a decision-log seed for recording the "why" as you build it.
- `scripts/` — only if the skill needs them, pre-wired with `_env.py`,
  `preflight.py`, and (if it produces output) `report.py`.

Plus the audit verdict from `audit-skill` on what was just generated, so
you know up front whether anything needs attention.

## How to run it

Just ask, e.g.:

- "create a new skill that summarizes my GitHub notifications"
- "scaffold a Claude skill for X"
- "make me a skill that does Y"

The generator will ask for the skill name, a one-line description, and a few
details (does it need scripts? secrets? external deps?). Under `--agent` it
takes the documented defaults and never prompts.

## What it needs

- `~/.claude/skills/skill-architecture.md` — the house spec it scaffolds
  against. The generator and the auditor share this file.
- Optional but recommended: network access on first run, so it can pull the
  latest Claude docs. Offline still works — it falls back to the committed
  snapshot under `references/claude-docs-snapshot/`.

No API keys required.

## How it works (high level)

1. **Preflight** — check the spec is present, that a usable copy of the
   Claude docs is available, and that the destination is writable.
2. **Docs** — fetch the current Claude skill-authoring docs (or use the
   cached/snapshot copy when offline); record the Claude Code version.
3. **Reconcile** — diff the current docs against our spec; if anything has
   moved upstream, surface it. Never auto-edits the spec — you decide.
4. **Scaffold** — write the new skill following the recipe in
   `references/generation-recipe.md`; frontmatter fields are validated
   against the live docs, so nothing invented sneaks in.
5. **Self-audit** — run `audit-skill` on the new skill and attach its
   report. The generator always finishes; the status line tells the truth.
6. **Emit** — show the file tree, the honest verdict, and the one `.gitignore`
   line you need to add to publish the new skill.

## Where to look next

- `SKILL.md` — Claude's operating instructions for this skill.
- `DESIGN.md` — design decisions, the resolution chain, and what each script
  does in detail (living record, like scan-trends's `handoff.md`).
- `references/generation-recipe.md` — the scaffold templates the generator
  follows when creating a new skill.
- `../skill-architecture.md` — the house spec; the standard of "correct".
- `../audit-skill/` — the counterpart that *reviews* skills against the
  same spec.
