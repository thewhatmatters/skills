# Stage 1 · Environment interview

You are the interviewer. The user has just launched a spec-first setup and
chosen the conan method — the house environment scaffolder. Your job in
this stage is a **light, one-pass interview about how they'll work**, not
what they're building. The deep what-and-why interview belongs to the
Karpathy method; if the user starts speccing the product at you, note it
for the Project section and gently steer back — the spec itself is a
deferred offer their new environment will make at the right time.

Keep the whole interview to roughly one screen's worth of exchanges. Light
and fast is the contract of this method.

## What you must gather

Five areas, in this order:

1. **What is this?** Two or three sentences in the user's own words: what
   the project is and the outcome that matters. This heads the CLAUDE.md.
   Do not excavate — one clarifying follow-up at most.
2. **Kind.** Web app / API or backend / CLI tool / research / content or
   writing / other. This is a *modifier*, never a fork: it tunes which
   skills get wired into the CLAUDE.md map and whether DESIGN.md is
   offered immediately (UI kinds only).
3. **Stack + commands.** Language, runtime, and the commands that will
   gate every commit (typecheck, test, build). "Not decided yet" is a
   valid answer — it gets recorded as an open decision, not forced.
4. **Rituals.** Two independent choices:
   - **Handoff at session boundaries** — convention only (the CLAUDE.md
     instructs sessions to run a handoff before ending/compacting), or
     enforced (the first working session offers to install the handoff
     hooks). Ask which they want.
   - **Knowledge wiring** — should the project be wired into their
     knowledge vault now, later, or not at all?
5. **Build style.** When a PRD eventually locks, does this project get the
   autonomous build-loop treatment (decompose into prd.json stories + a
   runner script), or will it be driven by hand? This decides whether the
   "When ready to build" section is a full playbook or a stub.

## How to interview

- **Prefer the AskUserQuestion tool whenever the question has enumerable
  answers** — kind, ritual choices, build style are all option picks (the
  user can always type into Other). Keep "what is this?" free-text; its
  whole point is unprompted recall.
- **Bundle related option questions** rather than asking five times.
- **Do not challenge or probe deeply.** This is the light method: accept
  the user's answers, reflect the summary once, and move on. Vague is
  acceptable here in a way it is not in a spec interview.

## Adapting to the detected project context

- **New / empty directory (`projectState: "new"`):** interview as above.
- **Existing codebase (`projectState: "existing"`):** first do a bounded
  read — manifest, README, obvious command scripts; a minute, not an
  audit — then *pre-fill* stack + commands and the likely kind from what
  you found, and confirm rather than ask. The interview shrinks to: what
  is this (unless a README already says), confirm kind/stack/commands,
  rituals, build style. Never propose reorganizing existing source files.

## Exit / resume contract

This stage is exit-able. If the user wants to stop after the interview,
write the gathered answers as a draft `CLAUDE.md` containing only a
`## Project` section and an HTML comment marker on the first line:

    <!-- conan-scaffold: interview-complete, scaffold-pending -->

followed by the five answers as a bullet list. Tell the user a later run
resumes at Stage 2 from that draft. When the user is ready, continue to
Stage 2 (scaffold the operating system).
