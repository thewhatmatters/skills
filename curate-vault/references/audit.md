# Audit mode — read-only health report

Loaded by SKILL.md when `--audit` is set, or when the user asks about vault
health. `/audit-vault` is this pass. **Never writes a vault file** — not even
a "harmless" fix. Snapshots live in `~/.cursor/cache/audit-vault/` (keep
that path so prior deltas still work).

`--audit` is exclusive with harvest, `--groom`, `--relink`, and `--wire`.

`--agent` **runs** this pass (cron-safe). That is the opposite of harvest,
where `--agent` must not write. `--deep` is ignored under `--agent`.

`--html` is not offered (no `render-html` skill). Markdown only.

## Preflight

```bash
python3 scripts/preflight.py --vault=<vault> --audit
```

- `VAULT_MISSING` / `SYNC_UNMOUNTED` → **down**. Stop. Do not offer to create
  a vault (that is harvest's decision).
- `VAULT_READONLY` → **ready** here (we only read).
- `STATE_UNWRITABLE` → degraded; report without growth deltas.
- `DEEP_UNAVAILABLE` → degraded; `--deep` skipped and labeled.

NATIVE (no python3): skip healthscan; read `index.md` / `log.md`, spot-check
links; say which sections are not measured.

## Steps

1. Preflight as above.
2. Conformance: `python3 scripts/verify_bundle.py --vault=<vault>` → capture
   stdout to `~/.cursor/cache/audit-vault/verify.json` (never into the vault).
3. Metrics: `python3 scripts/healthscan.py --vault=<vault>
   [--verify=<verify.json>] [--folder=SUB] [--no-snapshot]` — vault files
   opened read-only; writes only to the state dir.
4. `--deep[=N]` (interactive only): fan out `vault-verifier` agents over
   `deep_candidates` (default 10). Skip if the agent is missing; label the
   section.
5. Report per [`report-template.md`](report-template.md). `--out` writes the
   markdown; otherwise present in-conversation.
6. Close with the engine's `suggestions` (`--groom=<folder>`, `--relink`).
   Offer to continue into Groom mode in this run (interactive, not `--agent`).
   Do not execute grooms from an audit pass.
