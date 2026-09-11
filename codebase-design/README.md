# codebase-design

## What it is

Vocabulary and principles for **deep modules** (John Ousterhout): a small
interface hiding a lot of behaviour, easier to test and easier for an
agent to navigate. Default mode is that language. `--improve` is the
repo-wide scan Matt Pocock demoed as "run this on your repo" (vault:
`/claude/best-practices/matt-pocock-ai-coding-workflow.md`).

## What you get

**Default:** consistent terms — **module**, **interface**,
**implementation**, **depth**, **seam**, **adapter**, **leverage**,
**locality** — plus the deletion test and dependency categorization
(`references/DEEPENING.md`). Nothing is written to the project.

**`--improve`:** a markdown report in the conversation (or `--html` to
`$TMPDIR`, never the repo): one candidate per section, before/after,
recommendation strength, a top pick. Nothing is refactored until you
pick one; then a one-question-at-a-time interview designs the fix with
you. `CONTEXT.md` and
`docs/adr/` are respected when present.

## How to run it

- Design one module: "design this module's interface," "is this too
  shallow," "where should the seam go."
- Scan the repo: `/codebase-design --improve`, `/improve-codebase-architecture`,
  "find shallow modules." The scan is **not** auto-fired from a vague
  prompt. Habit: every few days, not once.

## What it needs

Default: nothing. `--improve` prefers an Explore subagent (inline fallback).
After you pick a candidate, a one-question-at-a-time interview.

## How it works

SKILL.md is the always-loaded glossary. `references/DEEPENING.md` and
`DESIGN-IT-TWICE.md` load on those branches. `--improve` loads
`references/improve.md` (explore → report → interview).

## Where this came from

Adapted from Matt Pocock's `codebase-design` and
`improve-codebase-architecture` skills in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT) — see
`NOTICE.md`.
