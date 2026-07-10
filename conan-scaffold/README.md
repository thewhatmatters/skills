# conan-scaffold

## What it is

A Claude Code skill that runs the conan method: a light, one-pass
interview about *how you'll work* — not what you're building — that
scaffolds a `CLAUDE.md` operating system for the project. The CLAUDE.md
it writes is behavioral: its sections encode deferred offers that future
sessions act on at the right moments (the spec interview when you're
ready, DESIGN.md when UI work starts, handoffs at session boundaries,
knowledge-vault wiring, a decompose→build-loop playbook).

It is the environment half of **conan-cli**'s two-method split: the deep
what-and-why spec belongs to `karpathy-spec`, which the scaffolded
CLAUDE.md offers when speccing time comes.

## What you get

One lean `CLAUDE.md` in your project directory — project summary, docs
hub with state, command gates, session rituals, knowledge wiring, build
playbook, and a kind-tuned skills map — plus a starter `DESIGN.md` if
your project has UI and you opt in immediately. Nothing else is written:
no project files, no folders, no dependencies, no hooks, no scripts. The
docs instruct; the sessions that follow do the installing.

## How to run it

Normally you don't invoke it directly — conan-cli launches a `claude`
session primed to run it after you pick the conan method from its menu.
To run it by hand, start `claude` in your project directory and ask:
"run the conan-scaffold skill" or "set up how we'll work here".

It works in two modes, detected automatically:

- **New / empty directory** — the full (still light) interview.
- **Existing codebase** — stack, commands, and kind are pre-filled from a
  bounded read and confirmed rather than asked.

Both stages are exit-able: stop after the interview and a marked draft
CLAUDE.md lets a later run resume straight into the scaffold.

## What it needs

- Claude Code, with this skill visible to the session.
- The stage prompt files: in a conan-cli-installed copy they live in
  `stages/` inside this skill directory (the installer makes the skill
  self-contained); in the conan-cli repo they live beside the skill in
  `methods/conan/stages/`.
- No API keys, no network beyond Claude itself, no other skills installed.

## How it works

`SKILL.md` is a thin orchestrator: it establishes project context (new vs
existing), locates the two canonical stage prompts, and runs them in
order — 1 environment interview, 2 scaffold the operating system. The
stage files in `methods/conan/stages/` are the single source of truth for
the method, so the method can evolve by editing markdown, not the skill.
