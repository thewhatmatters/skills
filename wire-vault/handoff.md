# wire-vault — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-07-02  ·  Cursor-retargeted 2026-08-21

## 1. Purpose

Wire the current project to the personal OKF vault (Layer 2): a consent-gated
marker block in the project `AGENTS.md` + an optional `projects/<name>/`
vault area via curate-vault.

## 2. Reusable patterns

Follows `~/.cursor/skills/skill-architecture.md`. Deliberate deviations:

- **No scripts (A4/A6 by composition).** Vault checks reuse curate-vault's
  `preflight.py`, with a native degrade path.
- **A10 artifact:** the marker block itself (and the vault overview article,
  which curate-vault owns).

## 3. Decision log

- 2026-08-21: **Target `AGENTS.md`, not a Claude-specific project file.**
  Layer 1 is Cursor User Rules. This skill does not author the rest of
  `AGENTS.md`.
- 2026-07-02: scaffolded; `--agent` never edits; marker-block idempotency;
  don't-over-wire is a first-class step.

## 4. Known limitations

- Project-name probing is heuristic; always user-confirmed interactively.
- Compare `AGENTS.md` filenames case-insensitively on macOS.

## 5. Audit rubric coverage

See `skill-architecture.md` §B. Scripts, secrets, and network items are N/A.

## 6. Notes

Layer 1 = User Rules · Layer 2 = this skill · writes = curate-vault +
ingest-source (gated).
