# Stage 2 · Draft the spec

You now hold a confirmed goal summary from Stage 1 (goal, audience,
definition of done, out-of-scope). Your job in this stage is to draft a
small, compartmentalized spec into `PRD.md` in the target directory — and
nothing else.

The canonical instruction for this stage, verbatim from Karpathy's method:

> **"bias towards smaller and more compartmentalized specs"**

## Be agile, not waterfall

Do not dump everything the project could ever be into the spec. The loop
this spec feeds is: tight scope → clear checkpoint → review → adjust →
repeat. A spec that tries to be complete is a spec nobody reviews — the
documented failure mode of heavyweight spec-driven tooling is exactly that
markdown wall. Concretely:

- Scope the spec to the **smallest version that meets the definition of
  done** from Stage 1. Everything else goes in the Roadmap section as a
  later phase, or in Open questions.
- Prefer cutting a section's content over padding it. A three-line section
  that is true beats a page that is filler.
- When you catch yourself speculating ("we may eventually need…"), move it
  to Roadmap or Open questions and shrink the core.
- One compact `PRD.md`. Not a folder of planning documents.

## The PRD template (embedded — this is the house layout)

Write `PRD.md` with exactly these sections, in this order:

```markdown
# <Project name> — <one-line description>

## Problem
Who hurts, how, today. The goal from Stage 1 belongs here, stated in the
user's confirmed words.

## Solution
What we're building and the core approach — small and concrete. State the
definition of done. List what is explicitly out of scope (from Stage 1).

## UX flow
How a user moves through it, end to end. Plain steps or a short annotated
sketch — enough that someone could storyboard it.

## Technical architecture
The moving parts and how they connect: language/runtime, key libraries,
process boundaries, integration points. Only decisions this version needs.

## Data model
The core entities/shapes and where they live (files, tables, messages).
Schemas verbatim where they're already decided.

## Roadmap
Phases: what this version ships, then the deliberately deferred phases.
The deferred list is where "smaller and more compartmentalized" lives.

## Risks
What could sink or stall this, and the mitigation or early-warning for
each.

## Open questions
Every decision NOT made yet, as questions. An empty list is a red flag —
it usually means assumptions went unstated instead of unmade.
```

Notes on filling it in:

- Ground every section in the Stage 1 interview. Where the interview didn't
  cover something, ask now — one question at a time — rather than inventing
  an answer. Silent assumptions are the enemy; anything you had to assume
  goes on the list for Stage 3.
- Write for the next agent as much as the user: the spec will prime a
  build session, so precise nouns (file names, commands, shapes) beat
  adjectives.
- **Docs-only:** this stage writes `PRD.md` and nothing else — no project
  files, folders, or dependencies. The build session that follows creates
  the structure *from* the doc.
- **Never overwrite an existing artifact.** If a `PRD.md` already exists,
  offer to extend it or write the new spec under a distinct name
  (e.g. `PRD-<change>.md`) — the user picks.
- If the `generate-prd` skill is available in this session, you may use it
  to produce the draft — it follows this same house layout. If it is not
  available, the template above is self-contained; write the file directly.
  Never treat any external skill as required.

## Exit / resume contract

This stage is exit-able: the user can stop once `PRD.md` is drafted and
still hold a usable artifact — a reviewable spec. If the user pauses
mid-draft, save what exists (a partial `PRD.md` with remaining sections
stubbed as `TBD`) so a later session can resume by filling the stubs
instead of starting over. When the draft is complete, continue to Stage 3
(verify decisions) — the spec is not final until it survives that review.
