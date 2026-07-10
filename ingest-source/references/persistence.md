# Persistence — docs/sources/, INDEX.md, and the CLAUDE.md gate

Loaded by `SKILL.md` Steps 5–6 (progressive disclosure, spec A1). This is the
contract that makes ingestions *project knowledge* instead of loose files.

## Layout (in the user's project, never in ~/.claude/skills)

```
<project root>/
  CLAUDE.md                  ← gets the marker block ONCE, with consent
  docs/sources/
    INDEX.md                 ← one line per ingestion; @-imported by CLAUDE.md
    <slug>.md                ← one ingestion: YAML frontmatter + summary
```

`--docs-dir` overrides `docs/sources`; `--project-root` (default cwd) is where
CLAUDE.md is looked for. The project root is the directory the user is working
in — **never** persist into `~/.claude/skills/` (commit-by-default repo).

## The ingestion file

`persist.py` wraps the summary in frontmatter:

```yaml
---
source: "<URL or path>"
type: youtube | webpage | pdf | image | document
title: "<title>"
ingested: YYYY-MM-DD
tier: <how content was obtained>
---
```

**Idempotent by source:** re-ingesting a URL/path that already has a file
*updates* that file in place (matched on frontmatter `source:`) and refreshes
its INDEX.md line — no duplicates. The JSON reports `action: created|updated`.

## INDEX.md

One line per ingestion:

```
- [Title](slug.md) — type · YYYY-MM-DD · <hook>
```

The hook is the retrieval cue ("when would a future task need this?") supplied
via `--hook`. `persist.py` creates INDEX.md with its header on first run and
upserts lines after that — never edit it by hand mid-run.

## The CLAUDE.md gate (spec A7 — all four parts)

`persist.py` only *reports* wiring status in its JSON (`claude_md.status`) and
emits the exact `claude_md.block` to insert. The edit itself is consent-gated:

- **(a) Trigger** — unambiguous: `status` is `absent` or `no-file` (marker
  `<!-- ingest-source:start -->` not found). `present` → say nothing, done.
- **(b) `--agent` bypass** — never edit CLAUDE.md unattended. Skip the edit,
  and include in the run report: the status, the block, and one line telling
  the user to re-run interactively or paste it themselves.
- **(c) Ask, don't degrade** — interactive: offer
  *Wire it up (insert the block) / I'll add it myself (print the block) /
  Skip*. On "wire it up": append `claude_md.block` to the end of CLAUDE.md
  (create the file containing only the block if `no-file`) using Edit/Write —
  scripts never touch CLAUDE.md.
- **(d) Graceful dead-end** — if the edit fails or is declined, the ingestion
  is still complete and said so; print the block for manual pasting. Never
  block, never retry silently.

Ask **once per project per run** — if the user declines, do not re-raise the
gate for subsequent ingestions in the same session; note it in the report.

The block (canonical copy lives in `persist.py:claude_md_block()`; always use
the JSON's `claude_md.block`, which has the correct relative path baked in):

```markdown
<!-- ingest-source:start -->
## Ingested sources

Captured source material (videos, articles, PDFs, images) lives in
`docs/sources/`, ingested by the ingest-source skill. The index below
is imported every session; read the underlying file when a listed source
is relevant to the task at hand.

@docs/sources/INDEX.md
<!-- ingest-source:end -->
```

Why `@`-import: CLAUDE.md `@path` imports inline the file at session start, so
the *index* (one line per source) is always in context while the ingestion
bodies load on demand — the same index-vs-body split as the typed-memory
system's MEMORY.md.

## NATIVE-mode persistence (no python3)

Replicate the contract by hand with Write/Edit: same frontmatter, same INDEX
line format, same gate. Check for an existing file with the same `source:`
before creating a new one.
