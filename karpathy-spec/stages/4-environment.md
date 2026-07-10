# Stage 4 · CLAUDE.md from the locked PRD

The spec is reviewed and locked as of Stage 3. Your job in this stage is
to author a `CLAUDE.md` in the target directory *distilled from that
locked `PRD.md`* — so every future Claude session in this workspace starts
primed with the verified what-and-why instead of a cold directory.

This stage is standard, but the user can decline it: a locked `PRD.md`
alone is a valid outcome of the method. Offer the stage in one line
("author a CLAUDE.md from the locked spec now?") and respect a no.

## Why this stage exists

A `CLAUDE.md` is the workspace's persistent memory — Claude Code auto-loads
it in every session. One authored *from a just-verified spec* beats one
written from a cold interview: every line in it traces to a decision the
user explicitly confirmed in Stage 3, so the primed workspace and the spec
cannot drift apart on day one. The PRD answers *what and why*; this file
makes every future session start already knowing it.

## What to do

1. **Re-read the locked `PRD.md`.** It is the sole source for this stage —
   do not re-interview the user or introduce content the spec doesn't
   support. Distill, don't invent:
   - **Overview** ← Problem + Solution (what this is, who it's for, the
     definition of done in one breath).
   - **Stack + commands** ← Technical architecture (language/runtime, key
     libraries, and the build/test/run commands the spec names — mark
     commands the build hasn't created yet as planned).
   - **Hard rules and boundaries** ← Risks (each mitigation the user
     confirmed becomes a rule), the spec's stated invariants, and the
     Roadmap's deferred phases (each becomes an explicit "not now"
     boundary so sessions don't creep scope).
   - **Point at the spec.** State explicitly that `PRD.md` is the build
     source of truth and later sessions should read it before nontrivial
     work.
2. **Draft into the house skeleton** (embedded below). Keep it lean —
   ~200 lines is the soft ceiling; a CLAUDE.md is an operating condensation,
   not a second PRD. Prefer pointing at `PRD.md` sections over restating
   them.
3. **Show the draft and confirm.** Present the drafted file (or the
   proposed changes — see the no-overwrite rule below) and get an explicit
   go-ahead before writing. Prefer the AskUserQuestion tool for the
   confirm/adjust choice when it is available.
4. **Write the file**, then tell the user what every future `claude`
   session in this directory now starts knowing.

## The CLAUDE.md skeleton (embedded — this is the house layout)

Write `CLAUDE.md` with these sections, in this order, dropping any that
would be empty:

```markdown
# <Project name> — CLAUDE.md

## Project overview
What this is, who it's for, and the definition of done — from the PRD's
Problem and Solution sections. One short paragraph, not a pitch.

## Source of truth
`PRD.md` is the reviewed, locked spec this workspace builds from. Read it
before nontrivial work; if the plan changes, update it first.

## Stack
Language/runtime and the key libraries the PRD's Technical architecture
commits to — only what is decided, nothing speculative.

## Architecture
The moving parts and how they connect, condensed from the PRD. Pointers
to PRD sections beat restated detail.

## Commands
The build/test/run invocations the spec names. If the build loop hasn't
created them yet, list them as planned and update once real.

## Hard rules
Non-negotiables distilled from the PRD's Risks (confirmed mitigations),
invariants, and scope decisions. Imperative, one line each.

## Boundaries (not now)
The Roadmap's deferred phases and the spec's explicit out-of-scope list —
what sessions must not creep into.

## Gotchas
Sharp edges the spec surfaced (from Risks or Open questions) that a fresh
session would otherwise rediscover the hard way.
```

Notes on filling it in:

- Every line must trace to the locked PRD. If you catch yourself writing
  something the spec doesn't say, it either belongs in `PRD.md` (ask the
  user, update the spec first) or it doesn't belong at all.
- Write imperatives for rules ("never X", "always Y before Z") — soft
  prose gets ignored; the Risks section's confirmed mitigations are
  already decisions, so state them as law.
- **Never overwrite an existing `CLAUDE.md`.** If one exists, read it,
  propose specific additions/updates derived from the locked PRD (as a
  short list of concrete edits), and apply only what the user explicitly
  confirms — item by item, not as a blanket rewrite. Prefer the
  AskUserQuestion tool to walk the proposed edits.
- **Docs-only:** this stage writes `CLAUDE.md` and nothing else — no
  project files, folders, or dependencies. The build session that follows
  creates the structure *from* the docs.
- If the `craft-claude` skill is available in this session, you may use
  it to author or audit the file — it follows this same house layout. If
  it is not available, the skeleton above is self-contained; write the
  file directly. Never treat any external skill as required.

## Exit / resume contract

This stage is exit-able: the user can decline or stop at any point and
still hold a usable artifact — the locked `PRD.md` from Stage 3 stands on
its own as a valid method outcome. If the user pauses after the draft was
shown but before it was written, nothing is on disk and nothing needs
cleanup; a later session resumes by re-running this stage against the
locked `PRD.md` (the distillation is deterministic enough to regenerate).
When this stage completes, the method is done: the workspace holds a
reviewed `PRD.md` and a `CLAUDE.md` authored from it.
