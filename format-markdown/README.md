# format-markdown

**What it is:** Formats and audits markdown documents against the house style
spec — Google's docguide distilled plus house overlays (tables for structured
data, tight bullets, a TOC threshold).

## What you get

- **AUDIT mode:** a severity-grouped findings report (`file:line` + the spec
  rule violated + a concrete fix) — nothing is changed.
- **FORMAT mode:** the file rewritten to spec, meaning-preserving —
  structure changes only, never rewording.
- **A shared rulebook:** `references/markdown-style.md`, which the
  document-writing skills (curate-knowledge, ingest-source, handoff,
  deep-research, generate-prd) follow when they author markdown.

## How to run

Say "format this markdown", "clean up this doc", "audit this README's
formatting", or `/format-markdown path/to/doc.md`. Example:

```text
/format-markdown docs/architecture.md --mode=audit
```

## What it needs

Nothing mandatory. If `markdownlint` is available (or `npx` can fetch it),
a mechanical lint pass runs first; without it the skill still works on the
judgment pass alone. No keys, no configuration.

## How it works (high level)

1. Checks readiness (style spec present; is markdownlint resolvable).
2. Loads the house style spec — the only rulebook it applies.
3. Skips files other skills own (OKF index/log files, CLAUDE.md, SKILL.md)
   and routes you there instead.
4. Runs markdownlint for the mechanical rules (when available), then a
   judgment pass for what a linter can't see: table-vs-list-vs-prose
   choice, TOC threshold, link-text quality.
5. Reports findings (AUDIT) or applies the restructuring (FORMAT) and
   honestly lists what was and wasn't covered.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/markdown-style.md` — the house style spec itself.
