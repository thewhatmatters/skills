---
name: build-ui
description: Implement, scaffold, or extend UI in a project — following its existing stack and conventions instead of imposing new ones. Use when the user wants frontend execution in a real codebase — "scaffold a [page/component/route]", "add a [feature] following our project conventions", "implement this design in our [Tailwind/shadcn/Next/etc.] setup", "build a settings page in this codebase", "add a data table using shadcn", "make a responsive [layout/section]", "wire up this form", "extend our component library", "add a route + UI for X". Probes the project first (package.json, tailwind.config.*, components.json, tsconfig paths, src/ shape) so it picks the right stack-specific patterns from references/ instead of guessing — Tailwind, shadcn/ui, vanilla CSS, accessibility, and JavaScript/TypeScript hygiene. Composes with frontend-design (for aesthetic direction), add-motion (for animation craft), and source-ui (for visual reference). This skill is about *execution* in a real project; aesthetic taste lives in frontend-design.
---

# build-ui

Implement UI in a real project, following its existing stack and conventions rather than inventing new ones.

## What it does

Given a UI ask in a real codebase, build-ui probes the project to learn its stack (framework, styling, components, motion, path aliases) and then implements following the matching patterns in `references/`. The probe is the key: it stops the skill from guessing "Tailwind?" or "shadcn?" — it knows. Bulky per-stack guidance lives in `references/` (A1 progressive disclosure) and is loaded only for the libraries the project actually uses.

This skill owns **execution mechanics**. Aesthetic *direction* (bold, distinctive, anti-AI-slop) is `frontend-design`'s territory; animation as a craft is `add-motion`'s. Compose by reference — don't reinvent.

## How to run

Trigger phrases the skill listens for: "scaffold a settings page", "add a data table in our shadcn setup", "implement this design following our project conventions", "build a responsive section using our Tailwind config", "wire up this form", "extend our component library". Or invoke `/build-ui <ask>` directly.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--project=PATH` | project root (default: cwd; walks up to nearest `package.json`/`.git`) |
| `--no-probe` | skip `probe.py` and rely on the ask alone (not recommended; only for trivial single-file edits) |
| `--stack=KEY` | force a stack hint when the probe is ambiguous (`tailwind`, `shadcn`, `vanilla-css`) |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. If python3 + `scripts/` are present → **SCRIPTS** (use `probe.py` + `preflight.py`). Otherwise → **NATIVE**: do the probe by hand (read `package.json`, look for `tailwind.config.*`, `components.json`, `tsconfig.json`, the `src/` shape), then follow `references/` directly. Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py --project=<root>`. `down` (e.g. `PROJECT_NOT_FOUND`) → stop and report; else proceed.
2. **Probe the project** — `python3 scripts/probe.py --project=<root>` → JSON `{framework, css, components, motion, aliases, dirs, tokens?}`. This is the source of truth for the rest of the flow; do not guess.
3. **Load only the references the project uses** — for each detected lib, read the matching `references/` file:
   - `css == "tailwind"` → [`references/tailwind.md`](references/tailwind.md)
   - `components == "shadcn"` → defer **execution** (add, preset, registry, `info --json`, current primitives, smart-merge) to the **official `shadcn` skill** (pinned in `skills-lock.json`; symlinked at `~/.claude/skills/shadcn`). Read [`references/shadcn.md`](references/shadcn.md) only for build-ui's coordination layer: the no-monoculture rule, how the probe and `info --json` are sequenced, and the routing table for when to invoke the shadcn skill vs. write JSX against installed primitives.
   - `css == "vanilla"` (no tailwind/CSS-in-JS) → [`references/vanilla-css.md`](references/vanilla-css.md)
   - Always read [`references/a11y.md`](references/a11y.md) — work its **Universal Pre-Flight** for every component, then the matching **component-specific** section (Modal Dialog, Tabs, Combobox, Forms & Inputs, Menu, Disclosure/Accordion, Live Regions, Tables, Cards, Carousels). On shadcn/Radix-using projects, most keyboard/ARIA mechanics are handled by the primitive — use the checklist to verify you didn't break them with custom markup and to cover what primitives can't solve (labels, alt, contrast, copy, errors, focus restoration). Accessibility is not opt-in.
   - Always read [`references/javascript-patterns.md`](references/javascript-patterns.md) — stack-agnostic JS/TS hygiene: async/effects cleanup, state derivation (vs. syncing), TypeScript narrowing at boundaries, DOM perf gotchas (layout thrash, observers), forms, and the anti-patterns to stop on sight. Match the project's lint + tsconfig + library choices over generic best-practice.
   If a stack key isn't covered in references, **say so** and fall back to the model's general knowledge; do not pretend coverage.
4. **Plan briefly, then implement** — restate the ask in one sentence, name the files you'll touch and the conventions you'll follow (from probe + references), then write the code. Use the project's existing path aliases (`@/components/...`), file naming, and component patterns. Match what's already in the repo over what's "best in general".
5. **Verify** — run typecheck (if TS) and any tests the criteria specify. For UI changes, if the user has `automate-browser` or `webapp-testing`, hand off the browser-verify step to them; otherwise note that visual verification is the user's call.
6. **Tell the user what you did + why** — files added/changed, the convention you matched, any deliberate deviations. Under `--agent`: write and report, no prompt.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- **Composition by reference, not import** (spec A8): `frontend-design` owns aesthetic direction; `add-motion` owns animation craft; `source-ui` finds visual precedent. build-ui does *execution*. Compose by naming, not by including their logic.
- **Project conventions beat global "best practice"** (A12 honesty): a probe-driven match to what the repo already does is more correct than what the model would write from scratch. Resist drift.
- **Scripts** (A4): JSON to stdout, diagnostics to stderr, graceful failure, never hang.
- **No assumptions about non-detected stacks** — if the project doesn't use shadcn, don't introduce it. Adding a dependency is a separate, explicit user decision.
- Keyless; no network.
