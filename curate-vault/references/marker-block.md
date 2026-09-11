# Project-layer marker block template

Loaded by [`wire.md`](wire.md). Substitute `<name>` (project name) and
`<vault>` (the `--vault` value or the default shown below). Keep the HTML
comment markers EXACTLY as written — they are the idempotency contract.

```markdown
<!-- wire-vault:start -->
## Knowledge vault — project layer

This project's durable knowledge (overview, decisions, gotchas) lives in the
cross-project vault at `<vault>/projects/<name>/`
(default vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/OBSDN`).

- **Read first:** before re-deriving an architecture decision or re-debugging
  a non-obvious issue, check `projects/<name>/index.md` there.
- **Write path:** durable insights go through `/curate-vault` (gated) —
  never write vault articles directly.
<!-- wire-vault:end -->
```

Rules:

- Insert at the END of an existing `AGENTS.md` (least disruptive to the
  project's own rules), or as the sole content of a new one.
- On update, replace only marker-to-marker; never touch anything outside.
- If the user renames the project, re-run `/curate-vault --wire` — the
  block updates in place.
