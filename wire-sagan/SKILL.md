---
name: wire-sagan
description: >-
  Bolt the Sagan orchestration overlay onto an existing project as a
  self-contained .sagan/ directory (sagan.yaml, role specs, tickets, memory,
  ledger), then wire the project's Claude entry point with an idempotent
  consent-gated marker block. Use when the user wants a project connected to
  the fleet — "wire this project to sagan", "wire this project to the fleet", "add sagan here",
  "install .sagan in this repo", "set up the fleet", "bolt the fleet onto X",
  "/wire-sagan" — or to refresh an existing overlay ("update the fleet
  template", "--update"). Probes before touching anything — project entry
  point (root CLAUDE.md, .claude/CLAUDE.md, AGENTS.md-with-import, or none),
  git status, existing .sagan/, and the project's real gate commands
  (test/typecheck/build) which are captured into sagan.yaml so verify runs
  this project's floor. Pins the bundled template version; --update resyncs
  files the project hasn't modified and flags the ones it has. Day-one commit
  policy — JSONL audit trail committed, evidence media gitignored. NOT the
  vault wiring (that's wire-vault), NOT the fleet design doc (vault
  ideas/agent-org-pm-sme-fleet.md), and it never runs the fleet loop itself —
  it only installs and wires.
---

# wire-sagan

Bolt the Sagan `.sagan/` overlay onto an existing project and wire its
Claude entry point with an idempotent, consent-gated marker block.

## Leading words

- **overlay** — the self-contained `.sagan/` directory; one dir to add, one to delete to un-wire. Everything Sagan-owned lives inside it.
- **entry point** — the file Claude actually loads for this project (root `CLAUDE.md`, `.claude/CLAUDE.md`, or an `AGENTS.md` it imports); probed, never assumed.
- **marker block** — the `<!-- wire-sagan:start/end -->` block; the only *entry-point* edit this skill makes, always shown for consent first, idempotent on re-run. Exactly one other write lands outside `.sagan/`: the `.gitignore` commit-policy append (Step 4) — both are named in the Step 3 consent round.
- **pinned template** — `assets/template/` version recorded in the installed sagan.yaml; `--update` resyncs unmodified files and flags modified ones, never overwrites local edits.

## How to run

"wire this project to the fleet", "install .sagan here", or
`/wire-sagan [--project=PATH]`. Refresh with `/wire-sagan --update`.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9). Never edits the entry point — prints the marker block for manual paste |
| `--project=PATH` | target project root (default: cwd) |
| `--roles=a,b,c` | role specs to install (default: frontend,critic,verify) |
| `--update` | resync an existing overlay against the bundled template |
| `--dry-run` | print the plan and probe results; write nothing |

## Step 0 — Mode probe

`python3 --version` + `scripts/` present → **SCRIPTS**. Otherwise **NATIVE**:
do the probe and install with built-in file tools (read the template from
`assets/template/`, copy by hand, compute no hashes — note that `--update`
modification detection is unavailable natively).

## Step 1 — Preflight

`python3 scripts/preflight.py`. `down` (template assets missing) → STOP,
suggest `git -C ~/.claude pull`. Keyless, no network.

## Step 2 — Probe

`python3 scripts/probe.py --project=<path>`. Read the JSON: entry point
location, git status, existing `.sagan/` (+ pinned version), detected gate
commands, marker-block presence. Announce findings in 2–3 lines. Not a git
repo → gate: warn that SHA-bound evidence needs git; offer `git init` /
proceed anyway / cancel (`--agent`: proceed, record the gate).

## Step 3 — Setup interview (skip under `--agent`: take probe defaults)

Confirm with the user in ONE question round: roles to install, gate commands
(pre-filled from the probe), ticket backend (local `.sagan/tickets/` default;
Linear ids if they name them). Show the exact marker block and where it will
be inserted, AND state that Step 4 also appends the commit-policy lines to
the project's `.gitignore` — the full outside-`.sagan/` write scope is on
the table before consent. Nothing is written before this gate.

## Step 4 — Install the overlay

`python3 scripts/install.py --project=<path> --roles=<list>
[--gates-test=… --gates-typecheck=… --gates-build=…] [--tickets=…]`.
Copies the pinned template into `.sagan/`, substitutes project config into
sagan.yaml, writes the template manifest (hashes) for future `--update`,
merges the commit-policy lines into the project's `.gitignore`. Refuses to
clobber an existing `.sagan/` (that's `--update`'s job).

## Step 5 — Wire the entry point (interactive only)

Insert the approved marker block into the probed entry point natively (the
Edit tool — scripts never edit CLAUDE.md/AGENTS.md). Idempotent: if markers
exist, replace only between them. No entry point at all → offer to create a
minimal CLAUDE.md containing the block. Under `--agent`: print the block and
the target path instead.

## Step 6 — Update mode (`--update`)

`python3 scripts/install.py --project=<path> --update`: compares installed
files against the manifest — unmodified → resync from the bundled template;
locally modified → leave and flag. Report both lists honestly; never
overwrite a local edit.

## Step 7 — Report

Installed tree, entry point wired or block-printed, gates captured, template
version, and the un-wire line (`delete .sagan/ + remove the marker block`).
Suggest the first ticket: copy `.sagan/tickets/T-000-example.md`.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- Keyless, no network. Composes by reference with wire-vault (same marker
  pattern), curate-vault (fleet MEMORY.md → vault harvests), and the fleet
  design doc in the vault.
- Writes outside `.sagan/` are limited to the marker block (consent-gated,
  native edit) and `.gitignore` commit-policy lines.
