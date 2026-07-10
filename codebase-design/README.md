# codebase-design

## What it is

A shared vocabulary and a handful of principles for designing code so it's
easy to test and easy for an agent (or a human) to navigate. It's not a
tool that does anything by itself — it's the language other skills (chiefly
`improve-codebase-architecture`) borrow so their suggestions read as one
consistent design philosophy instead of ad-hoc opinions.

The core idea, from John Ousterhout's *A Philosophy of Software Design*:
prefer **deep modules** (a small interface hiding a lot of behaviour) over
**shallow modules** (an interface that's nearly as complicated as what's
behind it). Deep modules are easier to test — you wrap one test boundary
around the interface — and easier for an agent to reason about, because it
doesn't have to trace a tangle of small files to understand one concept.

## What you get

Nothing is written to your project by this skill directly. What you get is
consistent terminology in whatever conversation invokes it: **module**,
**interface**, **implementation**, **depth**, **seam**, **adapter**,
**leverage**, **locality** — each with a precise meaning, and an explicit
list of near-synonyms to avoid ("component," "service," "boundary," "API")
so suggestions don't drift into vaguer language mid-conversation.

It also carries two techniques:

- **The deletion test** — a fast way to tell whether a module is earning
  its keep: imagine deleting it; if the complexity it held reappears at
  every caller, it was doing real work; if it just vanishes, it was a
  pass-through.
- **Dependency categorization** (`references/DEEPENING.md`) — a four-way
  classification (in-process, local-substitutable, remote-but-owned,
  true-external) that determines how a deepened module should be tested.

## How to run it

Ask directly — "design this module's interface," "is this too shallow,"
"where should the seam go" — or let another skill (like
`improve-codebase-architecture`) pull it in automatically when it needs the
vocabulary. It's a reference skill, not a workflow: there's no multi-step
process to walk through, just a glossary and a couple of design patterns to
apply.

For the deeper techniques:
- `references/DEEPENING.md` — how to classify a candidate's dependencies
  before deepening it, and how to test the result.
- `references/DESIGN-IT-TWICE.md` — a parallel-subagent pattern for
  generating several genuinely different interface designs for the same
  module and comparing them, instead of committing to the first idea.

## What it needs

Nothing — no scripts, no secrets, no network access. It's pure prompt
guidance.

## How it works

SKILL.md is the always-loaded glossary and principles. The two reference
files are pulled in only on the branches that need them (classifying
dependencies, or running the parallel-design exploration) — most
conversations that use this skill only ever need SKILL.md itself.

## Where this came from

Adapted from Matt Pocock's `codebase-design` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT license) —
see `NOTICE.md` in this directory for the attribution and what changed.
