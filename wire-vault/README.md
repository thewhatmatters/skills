# wire-vault

**What it is:** Connects a project to your knowledge vault — adds a small,
clearly-marked section to the project's `AGENTS.md` pointing at that project's
area in the vault, and optionally creates that area.

## What you get

- A `wire-vault` marker block in the project's `AGENTS.md` so sessions in
  that project know where its decisions and gotchas live — and check there
  before re-deriving them.
- Optionally, a `projects/<name>/overview.md` article in the vault (created
  through curate-vault, so you approve it first).

## How to run

From the project directory, say "wire this project to the vault" or invoke
`/wire-vault`. Run it once per project, whenever a project has accumulated
enough knowledge to deserve its own vault area — it's safe to re-run
(updates its own block in place, touches nothing else).

## What it needs

Nothing beyond the vault and the curate-vault skill. No API keys, no network.
Layer 1 (vault-before-web) lives in Cursor User Rules, not in this file.

## How it works (high level)

1. Figures out the project's name and confirms it with you.
2. Checks the vault is reachable (reusing curate-vault's readiness check)
   and whether the project is already wired.
3. Advises against wiring if the project has no real knowledge to point at
   yet — User Rules already cover the basics everywhere.
4. Offers to create the project's vault area (you approve the article).
5. Shows you the exact `AGENTS.md` block and inserts it only on your yes.

## Where to look next

- `SKILL.md` — operating instructions the agent follows.
- `handoff.md` — design decisions and the "why".
- `references/marker-block.md` — the block that gets inserted.
