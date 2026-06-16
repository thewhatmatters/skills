---
name: craft-claude
description: Author, audit, and maintain a project's CLAUDE.md and its memory ecosystem — nested CLAUDE.md, CLAUDE.local.md, .claude/rules/ path-scoped rules, and @-imports — against verified Claude Code mechanics, not folklore. Use when the user wants to set up, write, review, lint, tighten, or prune CLAUDE.md — "set up CLAUDE.md for this project", "write/scaffold a CLAUDE.md", "review/audit our CLAUDE.md", "is our CLAUDE.md any good", "trim/prune CLAUDE.md", "our CLAUDE.md is too long / being ignored", "add coding rules", "split rules into .claude/rules", "scope rules to a subdirectory", "convert soft rules to hard rules", "make Claude follow our conventions". Three modes off a project probe — AUTHOR (scaffold an opinionated CLAUDE.md, layered above built-in /init), AUDIT (report-only, severity-grouped: line bloat vs the ~200-line soft target, soft rules where hard belong, inlined examples that should be file:line refs, stale rules, missed scoped-rules splits), MAINTAIN (prune/staleness). Spec-bound to references/claude-md-spec.md. Never edits a project's CLAUDE.md without a consent gate. Operates on the USER's project — not on skills (that's audit-skill) and not on settings.json/hooks (that's update-config).
---

# craft-claude

Author, audit, and maintain a project's CLAUDE.md and its memory/rules
ecosystem against verified Claude Code mechanics.

## What it does

Given a project, it picks one of three modes — **author** a healthy CLAUDE.md
when one is missing, **audit** an existing one (report-only, severity-grouped),
or **maintain** (prune/staleness) — judging every file against the canonical
`references/claude-md-spec.md` (grounded in the official Claude Code memory
docs, A1). The spec encodes the real mechanics most guides get wrong: the
scope/load order, `.claude/rules/` `paths:` globs (which load on **read**, not
write), `@`-import depth, the ~200-line **soft** target, and `/memory`. It
operates on the **user's project** and never edits a CLAUDE.md without a
consent gate (A7), the same posture as `ingest-source`.

## How to run

Trigger with "set up CLAUDE.md for this project", "review our CLAUDE.md",
"our CLAUDE.md is too long / being ignored", "split these rules into
`.claude/rules`", or `/craft-claude [mode] [path]`. Mode auto-selects from the
probe; pass `--mode=` to force it. Output pairs with `render-html` for a
branded audit page.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses, never edits CLAUDE.md (spec A7b/A9) |
| `--out=PATH` | audit-report location (default: stdout / project root) |
| `--mode=author\|audit\|maintain` | force a mode; default = inferred from the probe |
| `--path=PATH` | target project root (default: cwd) |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. python3 + `scripts/` present → **SCRIPTS**. Otherwise
→ **NATIVE**: probe the project with your built-in file tools per
`references/claude-md-spec.md`, lint by hand against the same spec, write
CLAUDE.md content yourself. Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py [--agent]`. Read the JSON.
   The only hard requirement is a readable spec + a target project dir;
   everything else degrades (it is a local file transform — never `down`).
2. **Probe the project** — `python3 scripts/probe.py --path=<root>`. Reports
   which scopes exist (root/nested CLAUDE.md, CLAUDE.local.md, `.claude/rules/`,
   `@`-imports), line counts, and a suggested **mode** (author if no CLAUDE.md;
   audit/maintain if one exists). Read the JSON; honor `--mode=` if forced.
3. **Open the spec** — read `references/claude-md-spec.md` (the canon for every
   mode): §1 verified mechanics, §2 author target, §3 audit rubric.
4. **Run the chosen mode (NATIVE reasoning):**
   - **author** — draft a CLAUDE.md to the spec's structure, *layered above*
     `/init` (add the scope/rules/memory layering `/init` omits); recommend a
     `.claude/rules/<area>.md` split for any large subsystem. Templates in
     `references/templates.md`.
   - **audit** — lint against the spec's rubric (`references/claude-md-spec.md`
     §Rubric): bloat vs the ~200-line soft target, soft rules where hard
     belong, inlined examples that should be `file:line` refs, stale rules,
     missed scoped-rules splits. Emit severity-grouped findings with evidence
     + concrete fixes; **report only**.
   - **maintain** — a focused prune/staleness pass (dead rules, drift,
     overgrown root → propose splits).
5. **Write / report (spec A7 gate)** — author/maintain edits to a project's
   CLAUDE.md go behind a one-time consent gate (ask before writing; `--agent`
   skips the edit and prints the proposed block instead — scripts never edit
   CLAUDE.md). Audit is always report-only. Use `scripts/report.py` for the
   HTML artifact.
6. **Report** — mode run, files touched/proposed, severity tally, and the
   `render-html` offer.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`; the **CLAUDE.md** canon is
  `references/claude-md-spec.md` (do not duplicate its rubric in this file —
  reference it, A1).
- Scripts: JSON stdout / diagnostics stderr / graceful failure / time-bounded
  (spec A4). Keyless — no secrets, no network by default.
- Composition by reference, not import (spec A8): defers hooks/settings.json to
  `update-config`, the auto-memory system to its own loader, branded reports to
  `render-html`; runs none of their code.
- Operates on the **user's project**, never persists into `~/.claude/skills/`
  (commit-by-default repo). Never edits a CLAUDE.md without a consent gate.
