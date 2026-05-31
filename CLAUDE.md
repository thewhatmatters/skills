# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal collection of Claude Code **skills**, version-controlled. Each top-level
directory (except dotfiles) is one skill Claude can invoke. There is no app to build
or deploy — the "product" is the skills themselves. `README.md` is the user-facing
index of the fourteen skills; `skill-architecture.md` is the canonical spec they're all
built to.

## Single source of truth

`skill-architecture.md` defines how every skill in this family is built:
**§A** 13 architecture patterns (A1–A13), **§B** the audit rubric, **§C** the severity
guide. Two skills are bound to it:

- **`generate-skill`** scaffolds new skills *to* the spec (then self-audits).
- **`audit-skill`** checks existing skills *against* the spec.

Edit `skill-architecture.md` once and both follow. Do not duplicate the rubric
elsewhere; reference it.

## Anatomy of a skill

- **`SKILL.md`** — loaded on every invocation, so keep it **lean**. YAML frontmatter is
  `name` (must equal the directory) + a trigger-rich `description`. Conservative
  frontmatter is `name` + `description` only; never invent a frontmatter field —
  `generate-skill` validates against the live Claude-docs field list (`scripts/docs.py`,
  `scripts/reconcile.py`).
- **`references/`** — progressive disclosure (A1): bulky detail (templates, long tables,
  syntax guides) lives here and is pulled in *only when SKILL.md routes Claude to it*. A
  reference file the skill never points to is dead weight.
- **`scripts/`** — stdlib-first Python. Each script: one concern, a docstring stating its
  I/O contract, **JSON to stdout / diagnostics to stderr**, graceful failure, never hangs.
  `audit-skill` has no scripts (it reads the spec and reports).
- **`README.md`** (plain-language, A13) and **`handoff.md`** (decision log + rubric
  coverage — the "why").
- **`DESIGN.md`** — *only* for skills that emit **styled visual output** (e.g.
  `render-html`). Uses the [google-labs design.md](https://github.com/google-labs-code/design.md)
  format (YAML design tokens + rationale). Most skills have none. NB: a skill's own
  architecture-decisions doc may *also* be named `DESIGN.md` (e.g. `generate-skill/DESIGN.md`)
  — that is a different artifact from a visual-identity DESIGN.md.

## Cross-cutting patterns (read these in the spec before editing a skill)

- **Dual-mode + degraded ladder (A3).** A Step-0 mode probe picks SCRIPTS (full,
  usually needs keys/Node) vs NATIVE (built-in fallback). Every capability degrades
  rather than blocks — e.g. `deep-research` falls back to built-in WebSearch;
  `draw-diagram` falls back fenced-block → mmdc → Kroki → fenced-block;
  `automate-browser` falls back to read-only WebFetch.
- **Preflight (A6).** `scripts/preflight.py` emits a 4-state status
  (`ready | degraded | gated | down`) with a gate id on stdout (JSON) + a human board on
  stderr. Only `down` stops a run.
- **Setup gates (A7).** A recoverable gap (missing key, not logged in) is a *gate*, never
  a silent degrade; it always offers a fallback and never blocks under `--agent`.
- **Layered binary resolution (A11).** Resolve external tools as `$OVERRIDE → on-PATH →
  bundled/npx/default` (see `draw-diagram` `$MMDC_BIN → mmdc → npx`).
- **Composition by reference, not import.** Skills mention each other and run each
  other's documented entry points; they do not import across skill dirs. E.g.
  `deep-research` composes with `scan-trends`; `deep-research`/`generate-prd` reference
  `render-html` as an opt-in branded-HTML step; `draw-diagram` diagrams flow into
  `render-html`/`generate-prd`.

## Secrets

Shared loader `scripts/_env.py` (copied verbatim into skills that need keys). Precedence
**real env → `~/.claude/.env` → `~/.claude/skills/.env`**; empty values skipped; keys go
in **headers only**, never URLs/logs. The shared `.env` is `chmod 600` + gitignored;
**`.env.example` is committed** with a "Used by:" note per key. Do not create per-skill
`.env.example` files.

## House conventions

- **Naming is verb-noun** for action skills (`audit-skill`, `generate-skill`,
  `generate-prd`, `render-html`, `draw-diagram`, `scan-trends`); a brandable **noun** is
  reserved for named engines/tools (`deep-research`). Match this when adding skills.
- **Commit-by-default.** `.gitignore` tracks everything under the repo *except* secrets
  and generated junk (`.env`, `**/settings.local.json`, `**/.cache/`, `__pycache__/`,
  `node_modules/`, `results.html`, `.DS_Store`). Drop a skill in the folder and it's
  tracked.
- **Never commit `node_modules`.** Node tools run via `npx` on demand; if a pinned
  install is ever needed, commit a `package.json` and keep `node_modules` gitignored.
- **Generated artifacts stay out of the repo.** Skills write reports / rendered HTML to
  the user's home dir or `/tmp`, never into `~/.claude/skills/` (it's commit-by-default).

## Commands

- **Invoke a skill:** `/<name>` (e.g. `/render-html report.md`) or let it trigger on its
  description. Pass `--agent` for non-interactive (no prompts), `--out=PATH`, etc.
- **Run a script directly:** `python3 <skill>/scripts/<name>.py …` — preflight first,
  e.g. `python3 deep-research/scripts/preflight.py --out=<dir>`.
- **Check scripts compile (the de-facto test — there is no suite or CI):**
  `python3 -m py_compile <skill>/scripts/*.py`.
- **New skill:** `/generate-skill --name=<kebab> …` → scaffolds against the spec and runs
  `audit-skill` on the result.
- **Audit a skill:** `/audit-skill <path-or-name>`.

## Git workflow

Commit only when asked. The repo is maintained off `main` with fast-forward merges:
branch → commit → `git merge --ff-only <branch>` → `git push origin main` → delete the
branch. Commits end with a `Co-Authored-By:` trailer. This repo never commits generated
output, and skills themselves never run git.
