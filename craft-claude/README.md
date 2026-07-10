# craft-claude

**What it is:** Author, audit, and maintain a project's CLAUDE.md and its
memory/rules ecosystem against verified Claude Code mechanics.

## What you get

- A healthy, opinionated **CLAUDE.md** when a project doesn't have one — with
  the scope/rules/memory layering that built-in `/init` doesn't set up.
- A **severity-grouped audit** of an existing CLAUDE.md (line bloat, soft rules,
  inlined examples, stale rules, missed `.claude/rules/` splits) — report-only,
  with concrete fixes and `file:line` evidence.
- A **prune pass** that trims dead rules and proposes splits as the file grows.

## How to run

Say "set up CLAUDE.md for this project", "review our CLAUDE.md", "our CLAUDE.md
is too long / being ignored", or run `/craft-claude [author|audit|maintain]`.
The mode auto-selects from a probe of the project; force it with `--mode=`.

## What it needs

Nothing — keyless, no network by default. It reads the project's CLAUDE.md
family and the canonical spec; it only writes to a project's CLAUDE.md behind a
one-time consent prompt (never under `--agent`).

## How it works (high level)

1. Probe the project — which CLAUDE.md scopes exist, line counts, and a
   suggested mode.
2. Read the canonical CLAUDE.md spec (grounded in the official Claude Code
   memory docs, not folklore).
3. Run the chosen mode — author a new file, audit an existing one, or prune.
4. Author/maintain edits go behind a consent gate; audit is always report-only.
5. Optionally render the audit as a branded HTML page via `render-html`.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/claude-md-spec.md` — the canonical CLAUDE.md spec + audit rubric
  (verified mechanics, author target, scoped-rules recipes).
- `references/templates.md` — CLAUDE.md and `.claude/rules/` skeletons.
