# audit-vault — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-07-18  ·  Generator: generate-skill @ CC 2.1.181

## 1. Purpose
Read-only health report for the OKF vault — conformance, links, staleness,
growth, structure — ending in groom handoffs, with zero writes to the vault.

## 2. Reusable patterns (link to spec A1..A15)
This skill follows `~/.claude/skills/skill-architecture.md` A1–A15. Notable:
- **A1:** report structure lives in `references/report-template.md`, loaded
  only at write time.
- **A3:** NATIVE mode degrades to a partial, honestly-labeled report (no
  metrics engine) rather than blocking.
- **A4:** `healthscan.py` (metrics engine, read-only walker) and
  `preflight.py` — JSON stdout, diagnostics stderr, graceful.
- **A8 composition by reference:** `verify_bundle.py` is run as curate-vault's
  documented entry point (single conformance authority — deliberately NOT
  reimplemented); `vault-verifier` agents do `--deep` claim checks;
  `render-html` owns `--html`; every fix routes to `/curate-vault --groom`.
- **A15:** every dependency degrades: curate-vault tools
  (`VAULT_TOOLS_MISSING` → conformance skipped), vault-verifier agent
  (`DEEP_UNAVAILABLE` preflight check → Claim spot-check skipped, labeled),
  render-html ("if installed" in Step 5). Deviation recorded: preflight
  self-checks these single files inline instead of routing through the
  shared `preflight-deps.py` helper — same gate-id + degrade contract,
  fewer moving parts for a 3-path check; revisit if the dependency list
  grows.

## 3. Decision log
- 2026-07-18: scaffolded by generate-skill (drift note: live docs added
  `disallowed-tools` frontmatter field vs 2.1.144 baseline; unused here).
- 2026-07-18: **Report-only by contract; assessment and repair split by
  lifecycle.** curate-vault's `--groom` already finds + fixes through its
  gate; what was missing was a zero-gate, cron-safe assessment layer.
  Keeping this skill write-free means `--agent` runs need no HITL carve-outs
  and can never damage the vault (per the compose-over-extend vault
  decision: separate skill + suggestion hook, not a new mode on
  curate-vault).
- 2026-07-18: **Snapshots live in `~/.claude/.cache/audit-vault/`** — outside
  the vault (a report must not mutate its subject), gitignored in the repo
  (`**/.cache/`), disposable (deleting state only resets deltas).
- 2026-07-18: **Own read-only walker instead of scan_vault.py dependency.**
  healthscan needs timestamps, citations, index parsing, and log cadence
  that scan_vault's inventory JSON doesn't carry; depending on its exact
  schema would couple the skills. verify_bundle (conformance rules) IS
  reused — that's the part where a second implementation would drift
  dangerously. Trade-off recorded: two walkers exist, but with different
  jobs (inventory-for-dedupe vs metrics).
- 2026-07-18: **`--deep` never runs implicitly** — deep_candidates ranks by
  age × inbound links (old AND load-bearing first), but firing
  vault-verifier agents costs tokens, so cron/`--agent` paths stay
  script-only.
- 2026-07-18: **`documentation/` mirrors flagged separately in the report** —
  regenerable Reference shelves would otherwise dominate staleness/orphan
  scores and mask real curation debt (per the vault's doc-mirrors-central-
  shelf decision).

## 4. Known limitations / environment caveats
- Frontmatter parsing is lenient key:value (stdlib, no YAML dep) — exotic
  frontmatter may under-report timestamps; verify_bundle remains the
  conformance authority.
- Inbound-link counting resolves absolute and relative .md links; anchors
  and embeds are ignored by design.
- Growth deltas compare same-scope snapshots only (a `--folder` run never
  diffs against a full-vault snapshot).

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.
Secrets rows are N/A (keyless, no network).

## 6. Notes
Composes with: curate-vault (verify_bundle entry point + all fixes via
`--groom`/`--relink`), vault-verifier agent (`--deep`), render-html
(`--html`). Candidate cron pairing: weekly `/audit-vault --agent --out=...`
via the schedule skill.
