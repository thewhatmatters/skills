# audit-vault

**What it is:** a read-only health report for your OKF vault — conformance, broken links, staleness, orphans, growth, link structure — ending in targeted groom suggestions. It measures; it never touches a vault file.

## What you get

- A markdown health report: verdict line, per-folder staleness heat table, link-graph hubs and isolates, growth since the last run, activity cadence — every number computed, none invented.
- Growth tracking over time via local snapshots (stored in `~/.claude/.cache/audit-vault/`, never inside the vault; delete anytime — you only lose deltas).
- A ranked to-do of groom commands (`run /curate-vault --groom=<folder>`) so fixes go through curate-vault's confirmation gate, not behind your back.

## How to run

Say "how healthy is the vault", "vault health report", or "which folders need grooming" — or invoke `/audit-vault`. Weekly cron: `/audit-vault --agent --out=~/vault-health.md`. Add `--deep` when you want actual claim verification on the stalest load-bearing articles (uses agents, costs tokens).

## What it needs

Nothing to set up — Python standard library only. It reuses curate-vault's `verify_bundle.py` for conformance (if that skill is missing, the section is skipped and says so). `--html` needs the `render-html` skill.

## How it works (high level)

1. Preflight: vault reachable, curate-vault's verifier present, state dir writable.
2. Runs `verify_bundle.py` (curate-vault's own conformance authority) for errors + broken links.
3. Its `healthscan.py` walks the vault read-only: timestamps → staleness buckets per folder, links → inbound/orphans/hubs, index files → coverage, `log.md` → cadence; then diffs against the newest snapshot and records a new one.
4. Optional `--deep`: fans out `vault-verifier` agents over the oldest, most-linked concepts for claim-level verdicts.
5. Writes the report (markdown; `--html` via render-html) and closes with the groom commands — every fix routes to curate-vault's gate.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/report-template.md` — the report structure.
