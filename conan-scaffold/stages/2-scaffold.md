# Stage 2 · Scaffold the operating system

Turn the interview answers into the workspace's `CLAUDE.md` — and, on UI
opt-in, a starter `DESIGN.md`. Nothing else. The CLAUDE.md you write here
is **not a static description: it is behavioral**. Its sections encode
*deferred offers* — instructions that make future sessions create docs,
install hooks, and set up build loops at the moment each is actually
needed, with the user present. The environment scaffolds itself lazily;
your job is to write the instructions well.

## Hard rules

- **Docs-only.** Write `CLAUDE.md` (and `DESIGN.md` on opt-in), never
  project files, folders, dependencies, hooks, or scripts. "Docs instruct,
  session installs": the sections below cause *later sessions* to do the
  installing.
- **Never overwrite an existing CLAUDE.md.** If one exists (and is not
  this method's resumable draft), propose additions section by section and
  apply only what the user explicitly confirms.
- **No required external skills.** Skills named in the template are
  enhancements guarded by "if available" — never dependencies. Keep those
  guards in the text you write.

## The CLAUDE.md template

Write the following sections, filled from the interview. Keep the whole
file lean — aim under ~120 lines; an operating system is a card, not a
manual. Omit a section only when the interview explicitly ruled it out,
and say so in one line rather than leaving silence.

### `# <project name> — CLAUDE.md`

### `## Project`
The 2–3 interview sentences: what this is and the outcome that matters.

### `## Docs (with state)`
A short table or list tracking the context docs. Each entry is either a
live pointer or a deferred offer:

- `PRD.md` — *not yet written.* When it's time to define what we're
  building: run the `karpathy-spec` skill for a deep spec interview, or
  `generate-prd` to distill a discussion (each if available; otherwise
  interview + draft by hand).
- `DESIGN.md` — live pointer if created below; otherwise, for UI kinds:
  *not yet written — when UI work starts, offer to create it* (the
  `design-md` skill helps, if available). Non-UI kinds: omit.
- **Self-maintenance rule (include it verbatim in the section):** "After
  creating any doc listed here, update its entry from 'not yet written'
  to a live pointer."

### `## Commands`
The gates from the interview: dev/build/typecheck/test commands, and the
rule that every change passes them before commit. If the stack is
undecided, write the open decision here instead of inventing one.

### `## Session rituals`
- End-of-session, pre-compact, and before `/clear`: write a checkpoint
  (the `checkpoint` skill, if available; otherwise a project-memory note
  capturing state, decisions, and next steps).
- If the user chose **enforced** in the interview: add — "If checkpoint
  enforcement hooks are not installed, offer to install
  them (the checkpoint skill's setup documents them) in the first working
  session."

### `## Knowledge`
Per the interview choice: a pointer to the project's knowledge-vault layer
(wire now → tell the session to run `wire-vault`, if available); or "wire
later — offer when the first durable insight lands"; or omit if declined.

### `## When ready to build`
If the build style is the loop: the playbook — once a PRD is locked, run
`decompose-prd` (if available) to produce dependency-ordered `prd.json`
stories, then create a runner script that executes them one per fresh
session; each story must pass the Commands gates. If driven by hand:
one line saying builds are manual and the PRD is still the source of
truth.

### `## Skills map`
The kind-tuned list, every entry guarded "if available":

| Kind | Wire in |
|---|---|
| Web app | design-md, build-ui, audit-ui |
| API / backend | (no skill wiring — gates + conventions carry it) |
| CLI tool | (prose note: test in a real pty; guard non-TTY paths) |
| Research | deep-research, scan-trends, ingest-source |
| Content / writing | polish-copy, format-markdown, render-html |
| Other / blank | only what the interview named |

List only the chosen kind's row, plus anything the user added.

## DESIGN.md (UI kinds, opt-in now)

If the kind has UI and the user opted in during the interview, also write
a starter `DESIGN.md`: sections for visual direction, typography, color,
spacing/layout system, and component conventions — filled with whatever
the user volunteered, stubbed `TBD` otherwise. The `design-md` skill can
deepen it later (if available). If the user deferred, the Docs section's
offer covers it — write nothing.

## Exit / finish contract

If resuming from a Stage-1 draft (the `conan-scaffold:` marker comment),
replace the draft with the full file — that is the one permitted
"overwrite", and only with the user's one-line confirmation.

When the docs are written: remove any marker comment, show the user the
file list in one line, and state what the environment will now do on its
own — offer the spec when they're ready, offer DESIGN.md at first UI work,
remind about handoffs, and carry the build playbook. Name the natural next
step — "when you want to spec what we're building, run karpathy-spec" —
**without running it**. The method ends here.
