# grilling

## What it is

A very small skill with one job: interview you, one question at a time,
about whatever plan or design you're about to build, until you and the
agent are genuinely on the same page. It exists because agents in plan mode
tend to rush toward producing *a* plan the moment they think they have
enough — this skill deliberately slows that down.

This is the technique Matt Pocock demoed in his AI Engineer workshop as
"grill me" (see the vault article at
`/claude/best-practices/matt-pocock-ai-coding-workflow.md`, Phase 1) — the
goal isn't a document, it's what Frederick Brooks called a shared "design
concept": you and the agent holding the same mental model before any code
gets written.

## What you get

A conversation, not a file. By the end you'll have surfaced the decisions a
brief or idea glossed over — each posed as a question with the agent's own
recommended answer, so you're confirming or overriding rather than
inventing from scratch. That conversation history is itself the useful
artifact: feed it into a PRD-writing step, or just proceed straight to
implementation with both of you aligned.

Sessions can be short (a handful of questions) or long — Pocock reports
sessions running 20–100+ questions for a genuinely underspecified feature.
It stops when you say it's stopped, not on a fixed count.

## How to run it

Say "grill me about this," "grill this plan," or hand it a brief directly:
"grill me on this Slack message from [client]." It can also be invoked by
another skill — `improve-codebase-architecture` uses it after you pick
which architectural candidate to pursue, to walk through the design tree
for that specific change.

Works equally well fed a written brief or a meeting transcript — anything
with unstated assumptions worth surfacing.

## What it needs

Nothing — no scripts, no secrets, no network access. It's a single prompt.

## How it works

One instruction set, always active: ask one question at a time, offer a
recommendation with each, look up anything answerable from the codebase
instead of asking, and never proceed to implementation until you've
explicitly confirmed alignment.

## Where this came from

Adapted from Matt Pocock's `grilling` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT license) —
see `NOTICE.md` in this directory for the attribution and what changed
(effectively nothing but the frontmatter and this README; the source was
already this small).
