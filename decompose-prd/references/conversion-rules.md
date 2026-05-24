# PRD → prd.json conversion rules

Loaded by `SKILL.md` Step 3 (progressive disclosure, spec A1). This is the craft
of the skill: how to size, order, and write stories, and how to make them
skill-aware.

## Output schema (Ralph-compatible)

```json
{
  "project": "[Project Name]",
  "branchName": "ralph/[feature-name-kebab-case]",
  "description": "[Feature description from PRD title/intro]",
  "generatedAt": "[YYYY-MM-DD]",
  "sourcePrd": "[path or short identifier of the input PRD]",
  "userStories": [
    {
      "id": "US-001",
      "title": "[Story title]",
      "description": "As a [user], I want [feature] so that [benefit]",
      "acceptanceCriteria": ["Criterion 1", "Criterion 2", "Typecheck passes"],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

`generatedAt` (today, ISO) and `sourcePrd` make the artifact self-contained — it
records when it was built and from what (spec A10). They are inert metadata a
runner ignores; the only keys a runner acts on are `project` / `branchName` /
`description` / `userStories`. Beyond those two metadata keys, add **no** other
top-level keys. Skill references (below) go inside `acceptanceCriteria` and
`notes` only, so the JSON stays runnable.

## Rule #1 — story size: one iteration each

Ralph spawns a **fresh agent instance per iteration with no memory of prior
work**. If a story is too big, the agent runs out of context before finishing
and ships broken code. So every story must be completable in ONE iteration.

- **Right-sized:** add a DB column + migration · add a UI component to an
  existing page · update a server action · add a filter dropdown.
- **Too big (split):** "build the dashboard" → schema, queries, components,
  filters. "add auth" → schema, middleware, login UI, session handling.
- **Rule of thumb:** if you can't describe the change in 2–3 sentences, split it.

## Rule #2 — order by dependency, not document order

Stories run in `priority` order; an earlier story must never depend on a later
one. Canonical order: **schema/migrations → server/backend logic → UI components
→ aggregate/summary views**. (Wrong: a UI story before the schema it renders.)

## Rule #3 — acceptance criteria must be verifiable

Each criterion is something the agent can CHECK, not a vibe.

- **Good:** "Add `status` column to tasks (default 'pending')" · "Filter dropdown
  has options: All, Active, Completed" · "Clicking delete shows a confirm dialog".
- **Bad:** "works correctly" · "good UX" · "handles edge cases".
- **Always** append `"Typecheck passes"`. For testable logic add `"Tests pass"`.

## Rule #4 — make stories skill-aware (discovered, never hard-coded)

`scripts/list_skills.py` returns the skills the executing agent will actually
have (global `~/.claude/skills` + project `<root>/.claude/skills`), each with a
description. Match each story's intent to that inventory and embed the relevant
skill **only if it is present**:

- **UI / frontend story** → if a browser-driving skill exists (e.g.
  `automate-browser`), add the criterion: `"Verify in browser using
  automate-browser skill"`. Frontend stories are not done until visually
  verified. If no such skill exists, use a generic `"Verify the UI renders and
  behaves as described"` instead — do not name a skill that isn't there.
- **Spreadsheet / tabular data** → name the spreadsheet skill (e.g. `xlsx`) if present.
- **Word doc / report** → the docx skill, if present.
- **Diagram / flowchart** → `draw-diagram`, if present.
- **Anything else** with a clear skill match → name it.

Record candidates in `notes`: `"Suggested skills: automate-browser, xlsx"`. The
match is judgment — read the skill's description, don't keyword-match blindly,
and prefer naming at most one skill per criterion.

## Splitting large features

> "Add user notification system" →
> US-001 notifications table · US-002 notification service · US-003 bell icon in
> header · US-004 dropdown panel · US-005 mark-as-read · US-006 preferences page.

Each is one focused, independently verifiable change.

## Conversion mechanics

1. One user story → one JSON entry. IDs sequential (`US-001`, `US-002`, …).
2. `priority` follows dependency order, then document order.
3. Every story starts `"passes": false` with empty `"notes"` (before skill hints).
4. `branchName` = `ralph/` + feature name in kebab-case.
5. Set `generatedAt` to today's date (ISO `YYYY-MM-DD`) and `sourcePrd` to the
   input PRD's path (or a short identifier if it was pasted text).

## Archiving a previous run (Ralph convention)

Before writing a new `prd.json`, if one already exists for a **different**
`branchName` with real progress (a `progress.txt` with content beyond its
header): copy the current `prd.json` + `progress.txt` into
`archive/YYYY-MM-DD-feature-name/`, then reset `progress.txt`. (A Ralph runner's
`ralph.sh` typically does this automatically; do it manually only when editing
`prd.json` between runs.) These are runner-side conventions — the runner, not
this skill, owns execution.

## Pre-save checklist

- [ ] Previous run archived if `prd.json` existed with a different `branchName`.
- [ ] Each story completable in one iteration.
- [ ] Stories dependency-ordered (schema → backend → UI); no forward deps.
- [ ] Every story has `"Typecheck passes"`.
- [ ] UI stories have a browser-verify criterion (naming a skill only if discovered).
- [ ] Acceptance criteria are verifiable, not vague.
- [ ] Skill references come from `list_skills.py`, not assumptions.
- [ ] `generatedAt` (today, ISO) and `sourcePrd` are set.

## Worked example

**Input PRD:** "Task Status Feature — mark tasks pending/in-progress/done; filter
by status; status badge per task; persist in DB."

**Output `prd.json`** (abbreviated; assumes `automate-browser` was discovered):

```json
{
  "project": "TaskApp",
  "branchName": "ralph/task-status",
  "description": "Task Status Feature - track task progress with status indicators",
  "generatedAt": "2026-05-24",
  "sourcePrd": "docs/task-status-prd.md",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add status field to tasks table",
      "description": "As a developer, I need to store task status in the database.",
      "acceptanceCriteria": [
        "Add status column: 'pending' | 'in_progress' | 'done' (default 'pending')",
        "Generate and run migration successfully",
        "Typecheck passes"
      ],
      "priority": 1, "passes": false, "notes": ""
    },
    {
      "id": "US-002",
      "title": "Display status badge on task cards",
      "description": "As a user, I want to see task status at a glance.",
      "acceptanceCriteria": [
        "Each task card shows a colored status badge",
        "Badge colors: gray=pending, blue=in_progress, green=done",
        "Typecheck passes",
        "Verify in browser using automate-browser skill"
      ],
      "priority": 2, "passes": false, "notes": "Suggested skills: automate-browser"
    }
  ]
}
```
