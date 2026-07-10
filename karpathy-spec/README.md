# karpathy-spec

## What it is

A Claude Code skill that runs the Karpathy spec-first method: instead of
you prompting an agent to build something, the agent interviews *you* —
deeply, one question at a time — until the real goal is explicit, then
drafts a small spec and makes you confirm every decision in it before
anything gets built.

It is the method half of **conan-cli**: the CLI shows the menu and hands
off to Claude; this skill is what runs inside that Claude session.

## What you get

A reviewed, locked `PRD.md` in your project directory, covering problem,
solution, UX flow, technical architecture, data model, roadmap, risks, and
open questions — sized deliberately small ("agile, not waterfall") — plus
a `CLAUDE.md` distilled from that locked spec (Stage 4; declinable), so
every future Claude session in the directory starts primed. Nothing else
is written: no project files, no folders, no dependencies.

## How to run it

Normally you don't invoke it directly — conan-cli launches a `claude`
session primed to run it after you pick the Karpathy method from its menu.
To run it by hand, start `claude` in your project directory and ask for it:
"run the karpathy-spec skill" or "interview me to identify the goal of
this project".

It works in two modes, detected automatically:

- **New / empty directory** — the interview is about the project itself.
- **Existing codebase** — the interview is about the *next change* (a
  feature, refactor, or fix), after a quick read of the codebase.

Every stage is exit-able: stop after any stage and you still hold a usable
artifact; re-running the method resumes where you left off.

## What it needs

- Claude Code, with this skill visible to the session.
- The stage prompt files: in a conan-cli-installed copy they live in
  `stages/` inside this skill directory (the installer makes the skill
  self-contained); in the conan-cli repo they live beside the skill in
  `methods/karpathy/stages/`.
- No API keys, no network beyond Claude itself, no other skills installed.

## How it works

`SKILL.md` is a thin orchestrator: it establishes project context (new vs
existing), locates the four canonical stage prompts, and runs them in
order — 1 excavate the goal, 2 draft the spec, 3 verify decisions,
4 author `CLAUDE.md` from the locked spec. The
stage files in `methods/karpathy/stages/` are the single source of truth
for the method (they carry Karpathy's canonical prompts verbatim), so the
method can evolve by editing markdown, not the skill.
