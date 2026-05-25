# decompose-prd

**What it is:** turns a PRD into `prd.json` — a list of small, ordered tasks an autonomous agent loop can execute one at a time, each in a fresh context.

## What you get

- A `prd.json` of user stories, each sized to finish in a single agent iteration, ordered so nothing depends on a later task, with checkable acceptance criteria.
- **Skill-aware tasks:** each story names the right tool the executing agent should use (e.g. "verify in browser using automate-browser") — discovered from what's actually installed, not hard-coded.

## How to run

Point it at a PRD: "convert this PRD to prd.json", "decompose this spec into agent-loop tasks", or `/decompose-prd path/to/prd.md`. It pairs naturally with `generate-prd`, which produces the PRD in the first place.

## What it needs

Nothing to set up — Python standard library only, no keys, no network. It reads your PRD and writes `prd.json` (location via `--out`, default `./prd.json`).

## How it works (high level)

1. Reads your PRD (markdown or text).
2. Lists the skills available globally and in your project, so it knows what the executing agent can use.
3. Splits the PRD into one-iteration stories, ordered by dependency (database → backend → UI), with verifiable criteria.
4. Embeds the relevant discovered skill into each story (only skills that actually exist).
5. Validates the JSON structure, then writes `prd.json`.
6. If your project has no runner yet, offers to drop a `run-tasks.sh` in the project root — a loop that runs the stories one at a time with a fresh agent until they all pass. It's created only if you say yes, never overwrites an existing one, and is never run for you.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/conversion-rules.md` — the schema, sizing/ordering rules, splitting heuristics, and a worked example.
