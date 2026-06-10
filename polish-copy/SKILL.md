---
name: polish-copy
description: Review and elevate product microcopy to a luxury-grade bar — buttons, errors, empty states, placeholders, tooltips, onboarding, settings — in two layers, a universal craft floor (vague CTAs, robotic errors, inconsistent casing/tense, leaked jargon) plus the project's voice spec (the "## Voice" section in DESIGN.md, or a standalone VOICE.md). Use when the user wants a copy pass — "polish the copy", "review the microcopy", "make this copy feel premium", "fix these error messages", "UX-writing pass on this page/diff", "do these labels sound right", "copy audit before ship". Sweeps a named surface, route, or path set; proposes before→after rewrites, each tagged to the rule it serves — never mass-rewrites; --apply writes only approved rewrites. No voice spec → runs the floor and offers to bootstrap a draft "## Voice" section from your existing copy. Works on web JSX/TSX/HTML, Tauri webviews, and iOS String Catalogs (.xcstrings / .strings). Do NOT use for long-form marketing or docs authoring, or to generate copy from scratch — it reviews and refines what exists.
---

# polish-copy

Review product microcopy in two layers — the universal craft floor, then the project's voice — and propose before→after rewrites. Proposes; the user decides.

The layers live in `references/` (spec A1), loaded at the review step:

- [`references/floor.md`](references/floor.md) — the voice-independent floor: CTAs, errors, empty states, placeholders, consistency, jargon. Runs on every pass.
- [`references/voice-pass.md`](references/voice-pass.md) — the voice attribute set, how to audit against a spec, the bootstrap method, and the luxury-baseline seed template.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts; floor-only when no voice spec exists (never bootstraps unattended) (spec A7b/A9) |
| `--project=PATH` | project root (default: cwd; walks up to nearest `package.json`/`.git`/`.xcodeproj`) |
| `--path=GLOB` | scope the sweep to specific files/dirs (repeatable; default: the project's UI source) |
| `--out=PATH` | findings-report markdown location (default: `./copy-review-<date>.md`, outside the skills repo) |
| `--apply` | after the user approves findings, write the approved rewrites with Edit (never commits) |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. python3 + `scripts/` present → **SCRIPTS** (use the scripts below). Otherwise → **NATIVE**: locate the voice spec and read the scoped source files yourself, extracting user-facing strings by eye. Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py --project=<root>`. `down` (`PROJECT_NOT_FOUND`) → stop. Note `voice_spec` (`design_md_voice` / `voice_md` / `none`) and `copy_sources` (which file kinds were detected).
2. **Resolve the voice spec** (the per-project layer — never baked into this skill):
   - `## Voice` section in the project's `DESIGN.md` → use it (the default convention: brand is visual *and* verbal identity, one file).
   - else a standalone `VOICE.md` at the project root → use it (the override for copy-heavy products).
   - else **bootstrap**: offer to derive a draft — read the project's best existing surfaces, extract the de-facto attributes per `references/voice-pass.md` §Bootstrap, seed gaps from the luxury baseline, and **propose** a `## Voice` section for the user to approve and commit (never write it unasked). Under `--agent`: skip the offer, run floor-only, and say so in the report.
3. **Extract the copy** — `python3 scripts/extract_copy.py --project=<root> [--path=…]` → JSON strings with `{file, line, kind, text}` across JSX/TSX/HTML text + UI attributes, `.xcstrings`, and `.strings`. Heuristic and capped (disclosed via `truncated`); it *extracts*, it does not judge. Spot-check anything it likely missed (copy built from variables/i18n keys) and say what wasn't covered.
4. **Review — two layers** (NATIVE reasoning):
   - **Floor** (always): work `references/floor.md` over every extracted string.
   - **Voice** (when a spec resolved): audit against each attribute in the spec per `references/voice-pass.md`.
   Every finding: the current text with `file:line`, the rule it violates (floor item or voice attribute), and **one proposed rewrite** — not three options. Severity: 🔴 misleading/blocking copy (a label that lies, an error that misdirects, a destructive action with a vague confirm), 🟠 floor violations, 🟡 voice polish.
5. **Report** — markdown to `--out`, led by the project, date, scope, voice-spec source (or "floor-only — no spec"), then findings grouped by severity as before→after pairs, then a short ✅ list of surfaces that already hit the bar (spec A10/A12). Offer the `render-html` step.
6. **Apply only what's approved** — stop after the report. The user picks findings (all / by severity / by item); with approval (or `--apply` after an interactive yes) write exactly those rewrites with Edit. **Never mass-rewrite, never commit.** Under `--agent`: report only.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- **The skill is machinery; taste is the project's.** Voice lives in the checked-in spec (DESIGN.md `## Voice` / VOICE.md), exactly like visual tokens live in DESIGN.md — never hard-coded here (the refine-skill principle: preferences don't get baked into shared skills).
- **Reviews, never authors.** Per the research record: premium copy needs human tone-ownership; this skill audits and refines, the bootstrap drafts a *spec* (not copy) and even that is propose-only.
- **Composition by reference (A8)**: `design-md` produces the DESIGN.md this reads; `audit-ui` covers a11y aspects of copy (label presence) — polish-copy covers *quality*; `build-ui`/`generate-prd` surfaces feed it; `render-html` brands the report.
- **Scripts (A4)**: one concern each, JSON stdout / stderr diagnostics, graceful failure, capped output disclosed. Keyless; no network; never runs git.
- iOS carryover is first-class: `.xcstrings`/`.strings` extraction makes the same pass work on Swift projects.
