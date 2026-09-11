# Wire mode — project `AGENTS.md` marker

Loaded by SKILL.md when `--wire` is set, or when Step 8 of a harvest offers
to wire after filing under `projects/<name>/`. The marker template is
[`marker-block.md`](marker-block.md).

Layer 1 (Cursor User Rules) already points every session at the vault index.
Wire is Layer 2: a *project-specific* pointer so sessions in that repo check
`<vault>/projects/<name>/` before re-deriving decisions.

`--wire` skips harvest, `--groom`, and `--relink`.

## Steps

1. **Probe the project** — derive the name from (in order) `package.json`
   `name`, the git remote basename, the directory name. Confirm it with the
   user (`--project=` or `--agent` skips the confirmation).
2. **Preflight** — same as SKILL.md Step 1 (`scripts/preflight.py`, native
   degrade if python3 is absent). Also check the project `AGENTS.md`:
   `present` / `absent` / `already wired` (marker block found).
3. **Idempotency** — look for `<!-- wire-vault:start -->` …
   `<!-- wire-vault:end -->` (case-insensitive). Found → UPDATE that block
   only; never insert a second block; never touch content outside the markers.
   Comment names stay `wire-vault` so existing projects keep matching.
4. **Don't-over-wire** — if `<vault>/projects/<name>/` doesn't exist AND the
   session/project shows no accumulated durable knowledge to seed it with,
   recommend AGAINST wiring (Layer 1 already covers baseline consumption;
   empty scaffolding is noise). Proceed only if the user still wants it.
5. **Vault project area (optional)** — if `projects/<name>/` is missing and
   the user wants it, draft a `type: Project` candidate for
   `projects/<name>/overview.md` and run it through the SKILL.md Step 6
   gate (and Step 7 write if approved). `--agent` / `--dry-run`: include it
   in the proposals file; write nothing.
6. **AGENTS.md consent gate** — render the block from `marker-block.md` with
   the project name and vault path, show it verbatim, insert or update only
   on an explicit yes. If the project has no `AGENTS.md`, offer to create
   one containing just the block. `--agent`: print the block and stop — no
   edits to `AGENTS.md` or the vault.
7. **Report** — wired vs skipped, plus any degraded preflight items.

Broader `AGENTS.md` authoring is the project's (or `/create-rule`). This
mode manages only its marker block. Compare `AGENTS.md` filenames
case-insensitively on macOS.
