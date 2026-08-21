---
name: audit-vault
description: 'Read-only health report for the personal OKF vault (the Obsidian
  knowledge bundle) — assesses, never writes, safe under cron and --agent. Use
  when the user asks about vault health or state — "how healthy is the vault",
  "vault health report", "audit the vault", "vault status", "check the vault
  for broken links / stale articles / orphans", "how has the vault grown",
  "which vault folders need grooming", "/audit-vault". Quick tier is pure
  scripts: conformance + broken links (via curate-vault''s verify_bundle),
  per-folder staleness heat, orphan rate, index coverage, link-graph shape
  (hubs, isolates), log cadence, and growth deltas against locally-snapshotted
  prior runs (state in ~/.cursor/cache — never inside the vault). --deep
  opt-in fans out vault-verifier agents over the stalest-suspect claims (costs
  tokens; never on the cron path). Markdown report by default; --html renders
  via render-html. Ends with targeted handoffs — "run /curate-vault
  --groom=<folder>" — and fixes nothing itself. NOT for writing or fixing
  vault content (curate-vault owns every write, merge, and archive) and NOT
  for auditing skills (audit-skill).'
---

# audit-vault

Read-only health report for the OKF vault — conformance, links, staleness, growth, structure — ending in groom handoffs, with zero writes to the vault.

## What it does

Measures the vault and reports; it never repairs. A quick run is pure scripts: `verify_bundle` conformance + broken links, then `healthscan.py` walks the vault read-only for staleness heat, orphans, index coverage, link-graph shape, log cadence, and growth deltas against prior snapshots (state lives in `~/.cursor/cache/audit-vault/`, never inside the vault). `--deep` adds model-cost claim verification via `vault-verifier` agents. Every finding routes to `curate-vault` (the sole write path) as a suggested groom command. Report structure lives in [`references/report-template.md`](references/report-template.md) (spec A1).

## How to run

Trigger phrases: "how healthy is the vault", "vault health report", "audit the vault", "check the vault for broken links", "which folders need grooming". Or invoke `/audit-vault` directly. Cron-friendly: `/audit-vault --agent --out=PATH`.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9); `--deep` is ignored under `--agent` — claim verification never runs on the cron path |
| `--out=PATH` | write the markdown report to PATH (default: present in-conversation only) |
| `--vault=PATH` | vault root override. Default: `/Users/digitalalchemist/Library/Mobile Documents/iCloud~md~obsidian/Documents/OBSDN` |
| `--folder=SUB` | scope the report to one vault-relative folder (link graph still computed vault-wide so inbound counts stay true) |
| `--deep[=N]` | ALSO verify claims: fan out `vault-verifier` agents over the N (default 10) stalest-suspect, most-linked concepts. Costs tokens — opt-in, never default |
| `--html` | after writing the markdown report, render it via the `render-html` skill (requires `--out`) |
| `--no-snapshot` | compute deltas but do not record this run in the snapshot state |

## Step 0 — Mode probe

Run `python3 --version`. python3 + `scripts/` present → **SCRIPTS**. Otherwise **NATIVE**: skip the metrics engine and degrade honestly — run only what built-in tools cover (read the root `index.md`/`log.md`, spot-check links in the scoped folder), and say plainly which sections are missing (spec A12). Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py --vault=<vault>`. Gates:
   - `VAULT_MISSING` / `SYNC_UNMOUNTED` (down for this skill — there is nothing to measure): stop and report; never offer to create a vault (that is curate-vault's decision).
   - `VAULT_TOOLS_MISSING` (degraded) — curate-vault's `verify_bundle.py` not found: skip the conformance section, mark it "not measured" in the report, continue.
   - `STATE_UNWRITABLE` (degraded) — `~/.cursor/cache/audit-vault/` not writable: report without growth deltas, continue.
   - `DEEP_UNAVAILABLE` (degraded) — `vault-verifier` agent not installed: `--deep` skips the Claim spot-check and the report labels it not measured.
2. **Conformance + broken links** — run curate-vault's documented entry point: `python3 ~/.cursor/skills/curate-vault/scripts/verify_bundle.py --vault=<vault>`, capturing stdout to `~/.cursor/cache/audit-vault/verify.json` (the state dir — NEVER into the vault or the skills repo); pass that path to the engine. (Composition by reference: verify_bundle stays the single conformance authority; this skill never reimplements its rules.)
3. **Metrics engine** — `python3 scripts/healthscan.py --vault=<vault> [--verify=<verify.json>] [--folder=SUB] [--no-snapshot]` → one JSON payload: totals by type/folder, staleness heat, orphan + index-coverage rates, hubs/isolates, log cadence, citation coverage, growth deltas vs the latest snapshot, and ranked groom suggestions. The engine is read-only by contract: it opens vault files only for reading and writes solely to the state dir.
4. **`--deep` (opt-in)** — if the `vault-verifier` agent is available (preflight `deep` check; otherwise skip and label the section not measured): take the engine's `deep_candidates` list (stalest-suspect × most-inbound-linked); fan out one `vault-verifier` agent per concept (batch ≤ N), each returning structured claim verdicts. Merge verdicts into the report's Claim spot-check section. Ignored under `--agent`/cron; requires the explicit flag in an interactive run.
5. **Write the report** — compose the markdown per [`references/report-template.md`](references/report-template.md): verdict line first, then sections in template order; every number from the JSON, no invented figures (spec A12 — sections not measured say so). To `--out` if given, else present in-conversation. `--html`: hand the written file to the `render-html` skill (if installed; otherwise say so and leave the markdown).
6. **Hand off, don't fix** — close with the engine's groom suggestions verbatim (`run /curate-vault --groom=<folder>` per worst offender, plus `--relink` when missing-cross-link counts dominate). This skill proposes; curate-vault's gate decides.

## Conventions this skill follows

- Spec is `~/.cursor/skills/skill-architecture.md`.
- **Read-only is the contract**: no file inside the vault is ever created, modified, or deleted by this skill — that includes "harmless" fixes. All writes belong to curate-vault's gated flow (composition by reference, spec A8).
- Scripts: JSON stdout / diagnostics stderr / graceful failure, never hang (spec A4).
- State (snapshots) lives in `~/.cursor/cache/audit-vault/` — gitignored, outside the vault, safe to delete (first run after deletion simply has no deltas).
- Reports default to markdown; HTML is opt-in via `render-html` (house rule).
- Keyless; no network.
