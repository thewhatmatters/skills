---
name: wire-vault
description: >-
  Wire the current project to the personal OKF vault as a per-project knowledge
  layer. Use when the user wants a project connected to the second brain —
  "wire this project to the vault", "connect this project to the knowledge
  base", "set up the vault layer for this project", "link the vault here",
  "/wire-vault". Probes the project name, checks vault + AGENTS.md status, and
  idempotently inserts/updates a consent-gated marker block in the project's
  AGENTS.md pointing at <vault>/projects/<name>/; offers to create
  projects/<name>/overview.md through curate-vault's gate (this skill never
  writes vault articles itself). Recommends AGAINST wiring when the project has
  no accumulated knowledge yet — Cursor User Rules (Layer 1) already cover
  baseline vault consumption. Composes with curate-vault (owns all vault
  writes). Under --agent it never edits — prints the block for manual paste.
  Keyless, no network, no scripts of its own.
---

# wire-vault

Connect the current project to the OKF vault: a consent-gated marker block in
the project's `AGENTS.md` plus an optional `projects/<name>/` area in the vault,
created through curate-vault's gate.

## What it does

Layer 2 of the second-brain setup. Layer 1 (Cursor **User Rules**) already
points every session at the vault index; this skill adds a *project-specific*
pointer — "this project's decisions and gotchas live at
`<vault>/projects/<name>/`" — for projects whose accumulated knowledge earns
it. Idempotent: re-running updates the existing block in place. The block
template lives in `references/marker-block.md` (spec A1).

## How to run

Say "wire this project to the vault", "connect this project to the knowledge
base", or invoke `/wire-vault` from the project directory.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive (spec A7b): probe + report only; NEVER edits `AGENTS.md` or the vault — prints the marker block for manual paste |
| `--project=NAME` | override the probed project name |
| `--vault=PATH` | vault root override (default: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/OBSDN`) |

## Step 0 — Mode

Docs-only skill: no scripts of its own, no mode probe. Vault checks are
delegated to curate-vault's preflight (Step 2); everything else is
native file reads.

## Steps

1. **Probe the project** — derive the name from (in order) `package.json`
   `name`, the git remote basename, the directory name. Confirm it with the
   user (`--project=` or `--agent` skips the confirmation).
2. **Preflight by composition (spec A6/A8)** — run
   `python3 ~/.cursor/skills/curate-vault/scripts/preflight.py --vault=<vault>`
   for the vault checks (its gates apply: `VAULT_MISSING` → offer to run
   curate-vault's fix path or stop; `VAULT_READONLY` → stop). If python3
   is absent, degrade to a native existence/writability check of the vault
   dir — never block on the script. Natively check the project `AGENTS.md`:
   `present` / `absent` / `already wired` (marker block found).
3. **Idempotency check** — look for `<!-- wire-vault:start -->` …
   `<!-- wire-vault:end -->` in the project `AGENTS.md`. Found → this run is an
   UPDATE of that block only; never insert a second block, never touch
   content outside the markers.
4. **Don't-over-wire check** — if `<vault>/projects/<name>/` doesn't exist
   AND the session/project shows no accumulated durable knowledge to seed it
   with, recommend AGAINST wiring (Layer 1 already covers baseline
   consumption; empty scaffolding is noise). Proceed only if the user still
   wants it.
5. **Vault project area (optional, delegated)** — if `projects/<name>/` is
   missing and the user wants it, hand curate-vault a pre-drafted
   `type: Project` candidate for `projects/<name>/overview.md` (by reference,
   spec A8). This skill NEVER writes vault files itself.
6. **AGENTS.md consent gate (spec A7)** — render the marker block from
   `references/marker-block.md` with the project name and vault path, show it
   verbatim, and insert (or update) only on an explicit yes. If the project
   has no `AGENTS.md`, offer to create one containing just the block. Under
   `--agent`: print the block and stop — no edits.
7. **Report** — what was wired vs skipped, plus any degraded preflight items.

## Conventions this skill follows

- Spec is `~/.cursor/skills/skill-architecture.md`.
- **`WHY.md`:** read before changing this skill's design. After a run that locks a non-obvious choice (went unusually well or badly, reason not already in SKILL.md), append a dated line. Skip routine runs. Cross-project lessons go to `/curate-vault`.
- Composition by reference (spec A8): curate-vault owns all vault writes
  and the vault preflight. Broader `AGENTS.md` authoring is the project's
  (or `/create-rule`); this skill manages only its marker block.
- Keyless; no network; no scripts — the one reused script degrades to native
  checks when python3 is absent (spec A3).
