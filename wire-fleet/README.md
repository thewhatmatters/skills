# wire-fleet

**What it is:** Bolts the agent-fleet orchestration overlay onto an existing
project as a self-contained `.fleet/` directory and wires the project's
Claude entry point with a small consent-gated marker block.

## What you get

- A `.fleet/` directory in your project: fleet.yaml (with your project's real
  test/typecheck/build commands captured for the verify role), role specs,
  a tickets directory, memory tiers, and the events ledger.
- One marker block in your CLAUDE.md (or AGENTS.md) pointing Claude at it —
  the only edit made outside `.fleet/`.
- A pinned template version, so `/wire-fleet --update` can refresh unmodified
  files when the fleet protocol improves, without touching your local edits.

## How to run

Say "wire this project to the fleet" from the project directory, or
`/wire-fleet --project=~/Development/myapp`. Nothing is written until you
approve the plan and the marker block.

## What it needs

Nothing — no keys, no network. A git repo is strongly recommended (evidence
binds to commit SHAs); it will offer `git init` if missing.

## How it works (high level)

1. Probes the project: where CLAUDE.md/AGENTS.md live, git status, existing
   `.fleet/`, and the gate commands in package.json/pyproject.
2. Asks one round of setup questions (roles, gates, ticket backend) and shows
   the exact marker block for approval.
3. Copies the bundled template into `.fleet/`, substituting your config.
4. Inserts the marker block into the entry point (idempotent; re-runs replace
   only between the markers).
5. `--update` later resyncs template files you haven't modified and flags the
   ones you have.

Un-wiring is symmetrical: delete `.fleet/` and remove the marker block.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `assets/template/` — the `.fleet/` template that gets installed.
- The design doc: vault `ideas/agent-org-pm-sme-fleet.md` (v3.4, Distribution).
