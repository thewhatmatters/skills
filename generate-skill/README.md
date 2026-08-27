# generate-skill

**What it is:** a scaffolder for new Cursor Agent Skills. It bootstraps a
skill that already follows our house conventions, then has `audit-skill`
review it — so you start from a structure that's known to be solid.

## What you get

A new folder under `~/.cursor/skills/<name>/` (personal) or
`.cursor/skills/<name>/` (project), containing:

- `SKILL.md` — agent operating instructions, with YAML frontmatter validated
  against the **current** Cursor skills docs (no invented or non-Cursor fields).
- `README.md` — plain-language explainer (house convention; this file is one).
- `WHY.md` — a decision-log seed for recording the "why" as you build it.
- `scripts/` — only if the skill needs them, pre-wired with `_env.py`,
  `preflight.py`, and (if it produces output) `report.py`.

Plus the audit verdict from `audit-skill` on what was just generated.

## How to run it

- "create a new skill that summarizes my GitHub notifications"
- "scaffold a skill for X"
- "make me a skill that does Y"

The generator asks for the skill name, a one-line description, trigger mode,
and a few details (scripts? secrets? personal vs project?). Under `--agent`
it takes documented defaults and never prompts.

## What it needs

- `~/.cursor/skills/skill-architecture.md` — shared with `audit-skill`.
- Optional: network on first run to pull `cursor.com/docs/skills.md`. Offline
  falls back to `references/cursor-docs-snapshot/`.

No API keys required.

## How it works (high level)

1. **Preflight** — spec present, usable docs copy, destination writable.
2. **Docs** — fetch Cursor skill docs (or cache/snapshot).
3. **Reconcile** — diff live frontmatter fields vs the snapshot; never
   auto-edits the spec.
4. **Scaffold** — recipe in `references/generation-recipe.md`.
5. **Self-audit** — `audit-skill` on the new folder.
6. **Emit** — tree, honest verdict, `git add` reminder.

## Where to look next

- `SKILL.md` — operating instructions for this skill.
- `DESIGN.md` — design decisions and script contracts.
- `references/generation-recipe.md` — scaffold templates.
- `../skill-architecture.md` — house spec.
- `../audit-skill/` — the counterpart auditor.
