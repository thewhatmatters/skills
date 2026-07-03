# wire-vault

**What it is:** Connects a project to your knowledge vault — adds a small,
clearly-marked section to the project's CLAUDE.md pointing at that project's
area in the vault, and optionally creates that area.

## What you get

- A `wire-vault` marker block in the project's CLAUDE.md so every session in
  that project knows where its decisions and gotchas live — and checks there
  before re-deriving them.
- Optionally, a `projects/<name>/overview.md` article in the vault (created
  through curate-knowledge, so you approve it first).

## How to run

From the project directory, say "wire this project to the vault" or invoke
`/wire-vault`. Run it once per project, whenever a project has accumulated
enough knowledge to deserve its own vault area — it's safe to re-run
(updates its own block in place, touches nothing else).

## What it needs

Nothing beyond the vault and the curate-knowledge skill (both part of the
second-brain setup). No API keys, no network.

## How it works (high level)

1. Figures out the project's name and confirms it with you.
2. Checks the vault is reachable (reusing curate-knowledge's readiness check)
   and whether the project is already wired.
3. Advises against wiring if the project has no real knowledge to point at
   yet — the global vault block already covers the basics everywhere.
4. Offers to create the project's vault area (you approve the article).
5. Shows you the exact CLAUDE.md block and inserts it only on your yes.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/marker-block.md` — the block that gets inserted.
