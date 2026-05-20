---
name: generate-skill
description: Scaffold a new Claude Code skill against the house spec at ~/.claude/skills/skill-architecture.md, then self-audit it. Use when the user wants to create, scaffold, generate, bootstrap, or seed a new skill — "create a new skill", "make me a skill that …", "scaffold a Claude skill", "generate a skill that does X", "skeleton a skill", "spin up a skill", "I want a skill for Y". Pulls the live Claude docs (offline fallback), validates frontmatter against the upstream field list, follows the 13 architecture patterns, and runs audit-skill on the output. Reports honestly — never claims success when the auditor finds high-severity issues.
---

# generate-skill

Scaffold a new skill that satisfies `~/.claude/skills/skill-architecture.md`,
using the live Claude docs as the upstream contract. Generator ↔ auditor share
the spec — generator emits against it; auditor checks against it. Last step
runs `audit-skill` on what was just produced.

## Flags

| Flag | Meaning |
|------|---------|
| `--name=<kebab>` | name of the new skill (≤64 chars, lowercase + digits + hyphens) |
| `--out=PATH` | parent dir for the new skill (default: `~/.claude/skills`) |
| `--refresh-docs` | force `scripts/docs.py --refresh` before scaffolding |
| `--no-scripts` | scaffold a docs-only skill (no `scripts/` dir) |
| `--dry-run` | print the plan + file tree, write nothing |
| `--agent` | non-interactive: take documented defaults, never prompt |

## Step 0 — Mode probe

Try `python3 --version`. If python3 works and `scripts/` is present, mode =
**SCRIPTS**. Otherwise mode = **NATIVE** (no Python; read the committed
`references/claude-docs-snapshot/` directly via your built-in file tools).
Announce the mode in one line.

## Step 1 — Preflight

SCRIPTS: `python3 scripts/preflight.py --out=<destination>`. Read the JSON.

| overall | action |
|---------|--------|
| `ready` | proceed |
| `degraded` | proceed; note the degraded item in the run summary |
| `gated` (e.g. `DOCS_STALE`) | interactive: *Refresh / Use as-is / Cancel*. `--agent`: proceed and record the gate. **Graceful dead-end (spec A7d):** if *Refresh* fails, `docs.py`'s own fallback chain (cache → snapshot) covers it — the gate never blocks. |
| `down` | STOP. Show the ⛔ item; do not scaffold. |

NATIVE: confirm `~/.claude/skills/skill-architecture.md` is readable and the
snapshot is present; otherwise STOP.

## Step 2 — Docs

SCRIPTS: `python3 scripts/docs.py` (add `--refresh` if the flag was passed).
Capture the JSON manifest from stdout — you need `claude_code_version`,
`source`, and the per-doc set later.

NATIVE: use the snapshot. Parse the version from
`references/claude-docs-snapshot/changelog.md` (first `\d+\.\d+\.\d+` token).

## Step 3 — Reconcile against the spec

SCRIPTS: `python3 scripts/reconcile.py`. If `status == "drift"`:
**flag — never edit** `skill-architecture.md`. Surface added / removed
frontmatter fields and any skill-mentioning changelog lines.

- Interactive: offer *Show full diff / I will update the spec myself /
  Proceed on current spec*.
- `--agent`: proceed on current spec and record the drift in the final
  summary (spec A12 — honest verification).

NATIVE: skip reconcile (no "live" to compare).

## Step 4 — Gather inputs

Required (any not supplied via flags):
- **name** — kebab-case, ≤64 chars, matches `^[a-z][a-z0-9-]*$`.
- **one-line "what it does"** — used in `README.md` and the handoff seed.
- **trigger-rich description** — verbs + example phrases users may say;
  this is what Claude sees in the skill listing. Combined `description` +
  `when_to_use` ≤ 1536 chars (live docs).

Optional:
- needs **scripts**? (if no → `--no-scripts`)
- needs **secrets**? (drives whether to copy `_env.py` and add a key block)
- external deps / sources / dual-mode considerations.

`--agent` uses the supplied flags + the recipe's documented defaults; never
prompt.

## Step 5 — Scaffold

Open `references/generation-recipe.md` and follow it. The recipe enforces the
13 architecture patterns and uses the LIVE frontmatter field list from Step 2
— **never invent a field that is not in the live docs**.

Files created under `<out>/<name>/`:

- `SKILL.md` — frontmatter validated against the live field set; lean body.
- `README.md` — plain-language (spec A13 — audited, required).
- `handoff.md` — decision-log seed (rubric checklist + decision log placeholder).
- `references/` — empty dir, ready for progressive disclosure (spec A1).
- `scripts/_env.py`, `scripts/preflight.py`, `scripts/report.py` — written
  only when "needs scripts" was true (omit the whole dir otherwise).

`--dry-run`: print the would-be tree + the proposed `SKILL.md` frontmatter +
the opt-in line. Write nothing.

## Step 6 — Self-audit

Invoke the **audit-skill** skill on the new skill directory:

> "audit the skill at `<out>/<name>`"

Capture its severity-grouped findings. The generator **always emits** the
skill — never refuses, never gates (DESIGN.md decision #2). The final status
line is honest:

- `✅ ready` — auditor returned zero 🔴 critical and 🟠 important findings, OR
- `⚠ generated — N high-severity items to address` — list them with file:line.

Interactive mode MAY offer to fix the high-severity items immediately;
`--agent` reports and stops.

## Step 7 — Emit

Print, in this order:

1. The created tree (or dry-run plan).
2. The honest verdict line from Step 6.
3. The exact opt-in line for the user to add to `~/.claude/skills/.gitignore`:
   `!/<name>/` — followed by `git add <name> .gitignore`.

This skill does **not** run git.

## Conventions this skill itself follows

- Single source of truth: `~/.claude/skills/skill-architecture.md`. Editing it
  changes both the generator and the auditor (spec A1).
- Scripts: stdout = JSON, stderr = diagnostics, single concern, graceful
  failure, never hang (spec A4).
- Keyless. `scripts/_env.py` here is a **template** the recipe copies into
  generated skills that need secrets; this skill itself does not load it.
- Live docs from `code.claude.com` are pinned in `scripts/docs.py`. Changes
  upstream require either `--refresh-docs` at the user's request or a
  `reconcile.py` drift review — never silently re-aligned (DESIGN.md §5).
