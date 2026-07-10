---
name: wire-vault
description: Wire the current project to the personal OKF vault as a per-project knowledge layer. Use when the user wants a project connected to the second brain — "wire this project to the vault", "connect this project to the knowledge base", "set up the vault layer for this project", "link the vault here", "/wire-vault". Probes the project name, checks vault + CLAUDE.md status, and idempotently inserts/updates a consent-gated wire-vault marker block in the project's CLAUDE.md pointing at <vault>/projects/<name>/; offers to create projects/<name>/overview.md through curate-knowledge's gate (this skill never writes vault articles itself). Recommends AGAINST wiring when the project has no accumulated knowledge yet — the global Layer 1 block in ~/.claude/CLAUDE.md already covers baseline vault consumption everywhere. Composes with curate-knowledge (owns all vault writes) and craft-claude (owns broader CLAUDE.md authoring; this skill manages only its own marker block). Under --agent it never edits — prints the block for manual paste. Keyless, no network, no scripts of its own.
---

# wire-vault

Connect the current project to the OKF vault: a consent-gated marker block in
the project's CLAUDE.md plus an optional `projects/<name>/` area in the vault,
created through curate-knowledge's gate.

## What it does

Layer 2 of the second-brain setup. Layer 1 (the user-level `~/.claude/CLAUDE.md`
block) already gives every session the vault index; this skill adds a
*project-specific* pointer — "this project's decisions and gotchas live at
`<vault>/projects/<name>/`" — for projects whose accumulated knowledge earns
it. Idempotent: re-running updates the existing block in place. The block
template lives in `references/marker-block.md` (spec A1).

## How to run

Say "wire this project to the vault", "connect this project to the knowledge
base", or invoke `/wire-vault` from the project directory.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive (spec A7b): probe + report only; NEVER edits the project CLAUDE.md or the vault — prints the marker block for manual paste |
| `--project=NAME` | override the probed project name |
| `--vault=PATH` | vault root override (default: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/OBSDN`) |

## Step 0 — Mode

Docs-only skill: no scripts of its own, no mode probe. Vault checks are
delegated to curate-knowledge's preflight (Step 2); everything else is
native file reads.

## Steps

1. **Probe the project** — derive the name from (in order) `package.json`
   `name`, the git remote basename, the directory name. Confirm it with the
   user (`--project=` or `--agent` skips the confirmation).
2. **Preflight by composition (spec A6/A8)** — run
   `python3 ~/.claude/skills/curate-knowledge/scripts/preflight.py --vault=<vault>`
   for the vault checks (its gates apply: `VAULT_MISSING` → offer to run
   curate-knowledge's fix path or stop; `VAULT_READONLY` → stop). If python3
   is absent, degrade to a native existence/writability check of the vault
   dir — never block on the script. Natively check the project `CLAUDE.md`:
   `present` / `absent` / `already wired` (marker block found).
3. **Idempotency check** — look for `<!-- wire-vault:start -->` …
   `<!-- wire-vault:end -->` in the project CLAUDE.md. Found → this run is an
   UPDATE of that block only; never insert a second block, never touch
   content outside the markers (craft-claude owns the rest of the file).
4. **Don't-over-wire check** — if `<vault>/projects/<name>/` doesn't exist
   AND the session/project shows no accumulated durable knowledge to seed it
   with, recommend AGAINST wiring (Layer 1 already covers baseline
   consumption; empty scaffolding is noise). Proceed only if the user still
   wants it.
5. **Vault project area (optional, delegated)** — if `projects/<name>/` is
   missing and the user wants it, hand curate-knowledge a pre-drafted
   `type: Project` candidate for `projects/<name>/overview.md` (by reference,
   spec A8 — its HITL gate, index/log wiring, and verification apply). This
   skill NEVER writes vault files itself — if curate-knowledge is unavailable,
   skip this step and report the gap; do not write the vault directly as a
   fallback.
6. **CLAUDE.md consent gate (spec A7)** — render the marker block from
   `references/marker-block.md` with the project name and vault path, show it
   verbatim, and insert (or update) only on an explicit yes. If the project
   has no CLAUDE.md, offer to create one containing just the block. Under
   `--agent`: print the block and stop — no edits.
7. **Report** — what was wired vs skipped (block inserted/updated/declined,
   vault area created/existing/skipped), plus any degraded preflight items.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Composition by reference (spec A8): curate-knowledge owns all vault writes
  and the vault preflight; craft-claude owns project CLAUDE.md authoring
  beyond this skill's own marker block.
- Keyless; no network; no scripts — the one reused script degrades to native
  checks when python3 is absent (spec A3).
