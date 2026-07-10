---
name: conan-scaffold
description: >-
  Run the conan method: a light, one-pass environment interview (what is
  this, project kind, stack + command gates, session rituals, build style)
  that scaffolds a CLAUDE.md operating system — a behavioral hub whose
  sections encode deferred offers future sessions act on (spec via
  karpathy-spec/generate-prd when ready, DESIGN.md at first UI work,
  handoff at session boundaries, vault wiring, a decompose→build-loop
  playbook) — plus a starter DESIGN.md when a UI kind opts in now. Use
  when a conan-cli handoff names this skill, or when the user says "set up
  how we'll work here", "run the conan method", "scaffold my environment /
  CLAUDE.md for this project", "set up my house setup", or "light project
  setup without the deep spec". Docs-only: writes CLAUDE.md (and DESIGN.md
  on opt-in), nothing else.
---

# conan-scaffold — environment interview → CLAUDE.md as the operating system

Run two exit-able stages, strictly in order. The deliverable is one lean
`CLAUDE.md` in the current directory — the project's *operating system*:
how we work here, with deferred offers that fire in future sessions —
plus a starter `DESIGN.md` when a UI kind opts in immediately. This is
the environment half of the two-method split: the deep what-and-why spec
belongs to the `karpathy-spec` skill, which the scaffolded CLAUDE.md
offers at the right moment.

The full instructions for each stage live in two canonical stage files
shipped with this skill (see Step 0). **Read each stage file in full when
you reach that stage and follow it** — this document only sequences them.

## Hard invariants (hold in every stage)

- **Docs-only, via "docs instruct, session installs".** Write `CLAUDE.md`
  (and `DESIGN.md` on opt-in), never project files, folders, dependencies,
  hooks, or runner scripts. The CLAUDE.md's instructions cause *later
  sessions* to install hooks, create docs, and write runners at the moment
  of need.
- **Never overwrite an existing artifact.** An existing `CLAUDE.md` that
  is not this method's resumable draft gets proposed additions, applied
  only on explicit confirmation — never a rewrite. Same for `DESIGN.md`.
- **Never propose reorganizing existing source files.** Permanently out of
  scope, in every mode.
- **No required external skills.** This skill is self-contained. Skills
  named in the template (`karpathy-spec`, `generate-prd`, `design-md`,
  `handoff`, `wire-vault`, `decompose-prd`, …) are optional enhancements
  guarded by "if available" — never required, never assumed installed.

## Step 0 — Context intake

Do all three checks before Stage 1. They take seconds; do not narrate them
at length to the user.

1. **Detection context.** The invoking prompt (from conan-cli) may carry
   `{projectState: "new" | "existing", cwd, sourceFileCount}`. Use it if
   present. If absent, derive it yourself: list the current directory —
   source files present (code extensions; dotfiles, README, and docs don't
   count) means `existing`, otherwise `new`. This value adapts Stage 1:
   `existing` pre-fills stack/commands/kind from a bounded read and
   confirms instead of asking.

2. **Locate the stage files.** Resolve the first of these that exists:
   1. a `methods/conan/stages/` path given explicitly in the invoking
      prompt;
   2. `stages/` directly beside this SKILL.md (the deployed layout —
      conan-cli's installer copies the stage files into the skill
      directory so the installed skill is fully self-contained);
   3. `../../methods/conan/stages/` relative to this SKILL.md (the repo
      layout — skill and method travel together);
   4. `methods/conan/stages/` under the current working directory.

   The directory must contain `1-interview.md` and `2-scaffold.md`. If
   none of the four locations resolve, say the conan-cli install looks
   incomplete, ask the user where conan-cli lives, and try
   `<that path>/methods/conan/stages/`. Do not improvise the stages from
   memory — the files are the method.

3. **Resume check.** A prior run may have exited after the interview. If
   `CLAUDE.md` exists and its first line is the marker comment
   `<!-- conan-scaffold: interview-complete, scaffold-pending -->`, offer
   to resume at Stage 2 using the draft's recorded answers (confirm in one
   line). If `CLAUDE.md` exists without the marker, it is a pre-existing
   artifact — the no-overwrite invariant applies (Stage 2 proposes
   additions only).

## The two stages

| # | Stage | File | Artifact on exit |
|---|-------|------|------------------|
| 1 | Environment interview | `1-interview.md` | Confirmed answers (what/kind/stack+gates/rituals/build style); on early exit, a marked draft `CLAUDE.md` |
| 2 | Scaffold the operating system | `2-scaffold.md` | `CLAUDE.md`-as-OS (+ starter `DESIGN.md` on UI opt-in) |

For each stage: read its file in full, follow it, and honor its
exit/resume contract. If the user exits early, write the artifact exactly
as the stage file specifies, tell them how to resume (re-run the method;
Step 0's resume check picks up from the draft), and stop cleanly.

## Finish

When Stage 2 completes, state plainly what the workspace now holds — a
`CLAUDE.md` operating system (and `DESIGN.md`, if opted in) — and what it
will do on its own: offer the spec interview when the user is ready, offer
DESIGN.md at first UI work, keep session boundaries handed off, and carry
the build playbook. Name the natural next step — running `karpathy-spec`
when they want to spec the product — **without running it**. The method
ends here.
