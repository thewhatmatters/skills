# curate-knowledge — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-07-02  ·  Generator: generate-skill @ CC 2.1.181

## 1. Purpose

Harvest durable, non-derivable knowledge from sessions/projects into the OKF
vault, behind a mandatory per-article human confirmation gate.

## 2. Reusable patterns (link to spec A1..A13)

This skill follows `~/.claude/skills/skill-architecture.md` patterns A1–A13;
deliberate deviations:

- **A7b vs the mandatory HITL gate.** `--agent` cannot bypass the
  confirmation gate (the user made the gate the skill's contract). Resolution:
  `--agent` never writes to the vault — it emits a proposals file to `--out`
  that a later interactive run consumes. This is a deliberate narrowing of
  A7b, not a missing bypass.
- **A10 artifact.** The "artifact" of an interactive run is the set of vault
  articles themselves (plus the log entry); no separate HTML report is
  generated. In `--agent`/`--dry-run`, the proposals file is the artifact.

## 3. Decision log

- 2026-07-02: scaffolded by generate-skill.
- 2026-07-02: `handoff` step 5 now offers to run this skill at session
  boundaries (interactive only, only when durable knowledge exists). The
  suggestion lives on handoff's side; this skill needs no awareness of it.
- 2026-07-02: **Fence tracking is CommonMark-correct** in `scan_vault.py` +
  `verify_bundle.py`: a block opened with N backticks closes only on ≥N, so
  nested fences (``` inside ````) stay inside. Found when the second-brain
  blueprint (which embeds fenced files inside 4-backtick fences) produced 13
  spurious info-level broken links from example paths inside embeds.
- 2026-07-02: **Step 8 suggests `/wire-vault`** when a run files articles
  under `projects/<name>/` and the current project's CLAUDE.md lacks the
  marker block. Placed HERE, not in handoff — this skill is the one that
  knows where articles landed (compose-over-extend, again). Suggestion only;
  interactive only.
- 2026-07-02: **Added Step 5 (Relate) + `--relink` maintenance mode.**
  `scan_vault.py` now emits each concept's outgoing links (backlinks
  computable by inversion). Policy: links are curation, not indexing —
  forward links woven into drafts freely, reverse links only for hub
  relationships, each reverse edit individually gated. `--relink` sweeps
  existing articles for missing links as a batch.
- 2026-07-02: **`CLAUDE.md`/`HANDOFF.md` are tool files**, exempt from the
  frontmatter rule (added to RESERVED in `verify_bundle.py`, skipped by
  `scan_vault.py`). Deliberate deviation from strict OKF §9 rule 1 —
  frontmatter on these files would be overwritten by the tools that own
  them. Documented in `references/okf-conventions.md`.
- 2026-07-02: **Vault layout switched to topic-first** (user's explicit choice
  over provenance-first): external captures go in topic directories
  (e.g. `claude/best-practices/`), provenance carried by `type: Reference`;
  `<vault>/reference/` is reserved for format ground truth (the OKF spec
  mirror) and must not receive new captures. Path recommendations at the HITL
  gate should prefer existing topics before inventing new ones.
- 2026-07-02: `ingest-source` gained a destination gate (project/vault/both);
  its vault path hands this skill a pre-drafted `type: Reference` candidate
  for `<vault>/reference/`. Incoming pre-drafted candidates skip extraction
  (Step 3) but still go through dedupe and the HITL gate.
- 2026-07-02: skill created as a **separate skill** rather than an extension
  of `handoff` — different lifecycles (state capture vs knowledge curation),
  triggering clarity, and handoff must stay fast at the context limit.
  handoff may *suggest* running this at session boundaries.
- 2026-07-02: vault path hard-defaulted to the user's Obsidian bundle with
  `--vault=` override (spec A11 layered resolution: flag → default).
- 2026-07-02: frontmatter parsing in scripts is stdlib-only (no PyYAML) —
  simple `key: value` extraction is sufficient for OKF's flat fields and
  keeps the skill dependency-free.
- 2026-07-02: dedupe favors proposing an UPDATE to an existing concept over
  creating a near-duplicate file; the update is still gated.

## 4. Known limitations / environment caveats

- **Gotcha (observed 2026-07-02):** macOS's case-insensitive filesystem means
  a Write to `CLAUDE.md` lands in a pre-existing `claude.md` and keeps the
  lowercase on-disk name — which case-sensitive filename checks then miss
  (it got inventoried as a knowledge concept and failed conformance). Tool-
  file comparisons are now case-insensitive in both scripts; if a tool file
  shows up in the scan inventory, check its on-disk casing first.

- Title-similarity dedupe is heuristic; the HITL gate is the real safety net.
- `scan_vault.py`/`verify_bundle.py` parse only top-level flat frontmatter
  keys (all OKF requires); nested YAML extensions are preserved but ignored.
- `DEFAULT_VAULT` is intentionally duplicated in all three scripts (stdlib-only,
  no shared module by design); if the vault ever moves, update it in
  `preflight.py`, `scan_vault.py`, and `verify_bundle.py` — or just pass
  `--vault=`.
- The vault lives in Dropbox (CloudStorage); writes are local-first and sync
  is Dropbox's problem, but rapid successive runs may race sync on slow links.

## 5. Audit rubric coverage

See `skill-architecture.md` §B; this skill targets every PASS that applies.
Secrets/env items are N/A (keyless, no network).

## 6. Notes

Composes with: `handoff` (session-boundary harvest point), `ingest-source`
(external sources → vault `reference/`). The vault's own format documentation
is the OKF wiki inside the vault itself, including the mirrored spec at
`reference/okf-spec-v0.1.md`. Generated while upstream docs showed additive
frontmatter drift vs spec baseline (`disallowed-tools` added in CC 2.1.181);
field not used here.
