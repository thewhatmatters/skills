# wire-vault — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-07-02  ·  Generator: generate-skill @ CC 2.1.181

## 1. Purpose

Wire the current project to the personal OKF vault (Layer 2 of the
second-brain setup): a consent-gated marker block in the project CLAUDE.md +
an optional `projects/<name>/` vault area via curate-knowledge.

## 2. Reusable patterns (link to spec A1..A13)

Follows `~/.claude/skills/skill-architecture.md` A1–A13; deliberate deviations:

- **No scripts (A4/A6 by composition).** The only external dependency is the
  vault, and curate-knowledge's `preflight.py` already checks it — reused by
  reference with a native degrade path. Duplicating it here would violate the
  derive-orchestration-from-utilities principle (see the vault's
  compose-over-extend decision).
- **A10 artifact:** the artifact is the marker block itself (and the vault
  overview article, which curate-knowledge owns). No separate report file.

## 3. Decision log

- 2026-07-02: scaffolded by generate-skill.
- 2026-07-02: curate-knowledge's Step 8 now suggests this skill when a
  harvest files `projects/<name>/` articles into an unwired project. The
  suggestion lives on curate-knowledge's side; this skill needs no awareness
  of it.
- 2026-07-02: **`--agent` never edits.** Both write targets (a project's
  CLAUDE.md, the vault) are user-owned; unattended edits to either are
  unacceptable. `--agent` = probe + print the block.
- 2026-07-02: **Marker-block idempotency contract** — `<!-- wire-vault:start/
  end -->`; this skill owns only what's between its markers, craft-claude
  owns the rest of the file. Same pattern as ingest-source's CLAUDE.md
  @-import block.
- 2026-07-02: **Don't-over-wire is a first-class step**, not a footnote: the
  skill recommends against wiring knowledge-less projects because Layer 1
  (user-level ~/.claude/CLAUDE.md importing the vault root index) already
  covers baseline consumption in every session.

## 4. Known limitations / environment caveats

- Project-name probing is heuristic (package.json → git remote → dirname);
  always user-confirmed in interactive runs.
- macOS case-insensitivity gotcha applies to CLAUDE.md detection — compare
  filenames case-insensitively (see the vault's
  `macos/case-insensitive-filesystem.md`).

## 5. Audit rubric coverage

See `skill-architecture.md` §B; targets every PASS that applies. Scripts,
secrets, and network items are N/A (docs-only, keyless, offline).

## 6. Notes

Second-brain composition map: Layer 1 = user-level CLAUDE.md (global read
path) · Layer 2 = this skill (per-project read path) · writes =
curate-knowledge + ingest-source (gated) · session boundary = handoff's
harvest offer.
