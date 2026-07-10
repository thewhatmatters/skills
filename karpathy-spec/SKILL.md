---
name: karpathy-spec
description: >-
  Run the Karpathy spec-first method: a deep multi-round interview that
  excavates the real goal behind the task, drafts a small compartmentalized
  spec into PRD.md, walks the user through explicit item-by-item
  verification of every decision before the spec locks, then authors a
  CLAUDE.md distilled from the locked spec. Use when a conan-cli handoff
  names this skill, or when the user says "interview me to identify the
  goal of this project", "run the karpathy method", "spec-first setup",
  "help me write a spec/PRD before I build", "spec this project out with an
  interview", or, in an existing codebase, "spec the next change". Docs-only:
  writes PRD.md and CLAUDE.md, nothing else.
---

# karpathy-spec — goal interview → small spec → verified PRD.md → primed CLAUDE.md

Run four exit-able stages, strictly in order. The deliverable is one
reviewed, locked `PRD.md` in the current directory, plus a `CLAUDE.md`
authored from it (Stage 4 — standard, but the user may decline it; the
locked `PRD.md` alone is a valid outcome). This is Layer 1 of Karpathy's
3-layer method (spec → verifier → environment); this skill ends at the
spec and its primed workspace — later layers are out of scope.

The full instructions for each stage live in four canonical stage files
shipped with this skill (see Step 0). **Read each stage file in full when
you reach that stage and follow it** — this document only sequences them.

## Hard invariants (hold in every stage)

- **Docs-only.** Write `PRD.md` and `CLAUDE.md`, nothing else — never
  project files, folders, or dependencies. The build session that follows
  creates the structure *from* the docs.
- **Never overwrite an existing artifact.** If `PRD.md` already exists and
  is not a resumable draft of this method, offer to extend it or to write
  under a distinct name (e.g. `PRD-<change>.md`) — the user picks. If
  `CLAUDE.md` already exists, Stage 4 proposes additions and applies only
  what the user explicitly confirms — never a rewrite.
- **Never propose reorganizing existing source files.** Permanently out of
  scope, in every mode.
- **No required external skills.** This skill is self-contained. Other
  skills (e.g. `generate-prd`, `craft-claude`, `decompose-prd`) may be
  *mentioned* as optional enhancements, guarded by "if available" — never
  required, never assumed installed.

## Step 0 — Context intake

Do all three checks before Stage 1. They take seconds; do not narrate them
at length to the user.

1. **Detection context.** The invoking prompt (from conan-cli) may carry
   `{projectState: "new" | "existing", cwd, sourceFileCount}`. Use it if
   present. If absent, derive it yourself: list the current directory —
   source files present (code extensions; dotfiles, README, and docs don't
   count) means `existing`, otherwise `new`. This value adapts Stage 1:
   `new` interviews about the project; `existing` interviews about the next
   unit of work (details in the stage file).

2. **Locate the stage files.** Resolve the first of these that exists:
   1. a `methods/karpathy/stages/` path given explicitly in the invoking
      prompt;
   2. `stages/` directly beside this SKILL.md (the deployed layout —
      conan-cli's installer copies the stage files into the skill
      directory so the installed skill is fully self-contained);
   3. `../../methods/karpathy/stages/` relative to this SKILL.md (the
      repo layout — skill and method travel together);
   4. `methods/karpathy/stages/` under the current working directory.

   The directory must contain `1-goal.md`, `2-spec.md`, `3-verify.md`,
   `4-environment.md`. If none of the four locations resolve, say the
   conan-cli install looks incomplete, ask the user where conan-cli lives,
   and try `<that path>/methods/karpathy/stages/`. Do not improvise the
   stages from memory — the files are the method.

3. **Resume check.** A prior run may have exited early (every stage is
   exit-able). If `PRD.md` already exists, look for its resumable shapes:
   only a draft goal-summary header block → resume at Stage 2; sections
   stubbed `TBD` → resume Stage 2 by filling stubs; a `## Verification`
   heading with per-item status → resume Stage 3 at the first unconfirmed
   item; a complete, locked PRD with no `CLAUDE.md` beside it → offer to
   resume at Stage 4. Confirm the resume point with the user in one line
   before continuing. If `PRD.md` exists but matches none of these, it's a
   pre-existing artifact — the no-overwrite invariant applies.

## The four stages

| # | Stage | File | Artifact on exit |
|---|-------|------|------------------|
| 1 | Excavate the goal | `1-goal.md` | Confirmed goal summary (goal, audience, definition of done, out-of-scope) |
| 2 | Draft the spec | `2-spec.md` | Drafted `PRD.md` (house template embedded in the stage file) |
| 3 | Verify decisions | `3-verify.md` | Reviewed, locked `PRD.md` |
| 4 | CLAUDE.md from the locked PRD | `4-environment.md` | `CLAUDE.md` distilled from the locked spec (declinable — the locked `PRD.md` alone stands) |

For each stage: read its file in full, follow it, and honor its
exit/resume contract — the user may stop after any stage and still hold
the listed artifact. If the user exits early, write the artifact exactly
as the stage file specifies, tell them how to resume (re-run the method;
Step 0's resume check picks up from the artifact), and stop cleanly.

## Finish

When Stage 4 completes (or the user declines it after the Stage-3 lock),
state plainly what the workspace now holds — a reviewed, locked `PRD.md`,
plus a `CLAUDE.md` authored from it if Stage 4 ran — and name the natural
next step: decomposing the PRD into small, dependency-ordered tasks for a
build loop (the `decompose-prd` skill does this, if available) — **without
running it**. The method ends here.
