# wire-sagan — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-08-06  ·  Generator: generate-skill @ CC 2.1.223

## 1. Purpose

Bolt the Sagan `.sagan/` overlay onto an existing project and wire its
Claude entry point with an idempotent, consent-gated marker block.

## 2. Reusable patterns (link to spec A1..A15)

This skill follows `~/.claude/skills/skill-architecture.md` patterns A1–A15;
deliberate notes:

- Marker-block pattern copied from wire-vault (probe → show block → consent →
  idempotent native edit; scripts never touch CLAUDE.md/AGENTS.md).
- Template bundled under `assets/template/` rather than referenced from
  `~/Development/sagan` so the skill is self-contained and the template
  version is pinned by the skills repo's own history.

## 3. Decision log

- 2026-08-06: scaffolded by generate-skill against the v3.4 Distribution
  section of the fleet design doc (vault `ideas/agent-org-pm-sme-fleet.md`).
- 2026-08-06: template synced from the `~/Development/sagan` v0 test
  bed (T-001 run), with paths renamed `.agent/` → `.sagan/` per the bolt-on
  decision, and the two T-001 learnings folded into the role specs (critic
  input-set rule; builders don't render-check their own work).
- 2026-08-06: `--update` detects local modification via a sha256 manifest
  written at install (`.sagan/.template-manifest.json`); modified files are
  flagged, never overwritten.
- 2026-08-06: commit policy in template `.gitignore` fragment — ledger
  JSONL/tickets/MEMORY.md committed, `ledger/*/` evidence media ignored.
- 2026-08-06: trigger mode = model-invoked (A14), deliberately. Although the
  skill is side-effectful, every write is consent-gated (Step 3 shows the
  full outside-`.sagan/` scope before anything lands), matching the
  wire-vault precedent; the trigger-rich description is what routes "wire
  this project to the fleet" correctly.
- 2026-08-06: post-audit fixes (skill-auditor, 0 critical / 1 important):
  corrected the write-scope "ONLY" claim in SKILL.md/README (the .gitignore
  append is the second outside-`.sagan/` write, now named in the consent
  round), folded the frontmatter description to a `>-` block scalar
  (lenient-frontmatter gotcha), guarded unreadable-file edges in
  probe/install, aligned stale comments/docstrings.

## 4. Known limitations / environment caveats

- NATIVE mode (no python3) installs but cannot hash → `--update`
  modification detection unavailable; disclosed at run time.
- Runtime enforcement of sagan.yaml (round caps, gates) is NOT this skill's
  job and does not exist yet anywhere — the installed sagan.yaml says so
  in its own comments (v0: PM-interpreted).
- Gate-command detection covers package.json scripts and pyproject/Makefile
  heuristics; anything else is captured via the setup interview.

## 5. Audit rubric coverage

See `skill-architecture.md` §B; this skill targets every PASS that applies.

## 6. Notes

Generated while claude-docs reconcile reported drift (baseline 2.1.144 →
live 2.1.223; new frontmatter fields background/compatibility/
disallowed-tools/license/metadata). Frontmatter here uses the conservative
`name` + `description` set, valid in both.
- 2026-08-06: standard named **Sagan** (sagan.run) — skill renamed
  wire-fleet → wire-sagan, overlay `.fleet/` → `.sagan/`, config
  `fleet.yaml` → `sagan.yaml`, marker `wire-fleet:*` → `wire-sagan:*`.
  Renamed pre-adoption (zero wired projects) so the cost never recurs.
  "Fleet" survives as concept vocabulary; "Sagan" is the standard's name.
