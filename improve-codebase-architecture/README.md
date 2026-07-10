# improve-codebase-architecture

## What it is

A codebase health check that looks specifically for **shallow modules** —
clusters of small, tangled files that are hard for both humans and AI
coding agents to navigate and test — and proposes turning them into **deep
modules**: a small, clean interface hiding a lot of well-tested behaviour
behind it.

This is the skill Matt Pocock demoed in his AI Engineer workshop as his
single top recommendation ("if you take one thing away from today, just
try running this on your repo"). See the full capture at
`/claude/best-practices/matt-pocock-ai-coding-workflow.md` in the vault. In
his demo, running it on a browser-based video editor surfaced a way to wrap
the entire front-to-back flow as one testable module — which measurably
improved how well an agent could work in that code afterward.

## What you get

A single self-contained HTML report, written to your OS temp directory
(never your repo), with one card per candidate: which files are involved,
what's currently causing friction, what would change, a before/after
diagram, and a recommendation strength (`Strong` / `Worth exploring` /
`Speculative`). It ends with a top pick and why.

Nothing gets refactored automatically. Once you pick a candidate from the
report, the skill hands off to an interview (the `grilling` skill) to
actually design the fix with you — constraints, dependencies, what the new
interface looks like, what tests survive. You can also ask it to generate
several genuinely different interface designs in parallel and compare them
(via `codebase-design`'s design-it-twice pattern) before committing to one.

If your project has a `CONTEXT.md` domain glossary or `docs/adr/`
architecture decision records, the report speaks in your project's own
vocabulary instead of generic names, and respects decisions already on
record there — it won't re-litigate an ADR-backed choice without saying so
explicitly.

## How to run it

This skill is **user-invoked only** — say "improve the architecture of this
codebase," "find shallow modules," "deepen modules," or run it explicitly.
It won't fire on its own from a vaguer prompt, on purpose: a run explores
the whole codebase with a sub-agent and can propose a meaningfully large
refactor, so it shouldn't trigger without you asking for it. Pocock
recommends running it every few days as an ongoing habit, not just once.

## What it needs

Nothing external — no scripts, no secrets, no network access beyond the
Tailwind/Mermaid CDN links the generated HTML report loads in your browser.
It needs the Agent tool's `Explore` subagent type to walk the codebase, and
composes with two sibling skills: `codebase-design` (vocabulary) and
`grilling` (the post-selection interview).

## How it works

1. **Explore** — reads `CONTEXT.md`/`docs/adr/` if present, then an Explore
   subagent walks the codebase looking for friction, applying the deletion
   test from `codebase-design` to anything suspected shallow.
2. **Report** — writes the HTML file (scaffold and diagram patterns in
   `references/HTML-REPORT.md`), opens it, and stops — it deliberately does
   not propose an interface yet.
3. **Grill** — once you pick a candidate, hands off to `grilling` to design
   the fix with you, updating `CONTEXT.md` (`references/CONTEXT-FORMAT.md`)
   and offering an ADR (`references/ADR-FORMAT.md`) as decisions
   crystallize.

## Where this came from

Adapted from Matt Pocock's `improve-codebase-architecture` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT license) —
see `NOTICE.md` in this directory for the attribution and what changed.
