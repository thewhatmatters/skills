# OKF authoring conventions (operational condensation)

Loaded by SKILL.md Step 7. Source of truth: the mirrored spec in the vault at
`reference/okf-spec-v0.1.md`. If this file and the mirror disagree, the
mirror wins.

## Concept document shape

```markdown
---
type: <Type>                        # REQUIRED, non-empty
title: <Display name>
description: <One sentence — reused verbatim in index entries>
tags: [tag, tag]
timestamp: <ISO 8601, e.g. 2026-07-02T00:00:00Z>
---

Body: structural markdown (headings, lists, tables) over prose.
Cross-link with absolute form: [text](/path/to/concept.md).
Conventional headings when applicable: # Schema, # Examples, # Citations.
```

- Body structure/formatting follows the house markdown style spec:
  `~/.claude/skills/format-markdown/references/markdown-style.md`. Where it
  and OKF overlap (frontmatter, absolute links, reserved `index.md`/`log.md`),
  OKF — this file — wins; the style spec's own deference table agrees.
- `resource:` only when the concept describes one canonical asset (URI).
- Citations: numbered list under `# Citations`; targets may be URLs,
  vault-absolute paths, or mirrors under `/reference/`.

## Tool files (producer deviation)

`CLAUDE.md` and `HANDOFF.md` at the vault root are Claude Code infrastructure
with externally-defined formats — treated like reserved files (no OKF
frontmatter required, never concepts, excluded from the knowledge inventory).
Their links are still verified. A strict external OKF consumer may flag them;
accepted trade-off for a personal vault, recorded in the handoff decision log.

## Reserved files

- `index.md` — never a concept. No frontmatter (EXCEPT the bundle root, which
  MAY carry only `okf_version`). Format per directory:

  ```markdown
  # Section Heading

  * [Title](relative-path.md) - description from the concept's frontmatter
  * [Subdirectory](subdir/) - short description
  ```

- `log.md` — dated groups, **newest first**, ISO `YYYY-MM-DD` headings:

  ```markdown
  ## 2026-07-02
  * **Creation**: Added [Title](/path/concept.md).
  * **Update**: Revised [Title](/path/concept.md) — <what changed>.
  ```

## Wiring checklist (per approved article)

1. Write the concept file (frontmatter first, `type` mandatory).
2. Add/update its line in the containing directory's `index.md` (create the
   index if the directory is new; reuse the concept's `description`).
3. If a new top-level directory was created: add it to the root `/index.md`.
4. Append the log entry under today's date in `/log.md` (create today's
   heading if absent; keep newest-first ordering).
5. Run `scripts/verify_bundle.py` and fix anything this run introduced.

## Conformance floor (must never be violated by a write)

1. Every non-reserved `.md` has a parseable frontmatter block.
2. Every frontmatter has non-empty `type`.
3. `index.md`/`log.md` follow the shapes above.

Broken links to not-yet-written concepts are LEGAL (they mark future work) —
verify_bundle reports every broken link as `info`, never as an error; do not
"fix" them by deletion without asking.
