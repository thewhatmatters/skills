---
name: build-ui
description: 'Front door for building web UI in a real project — a tiered production
  contract that briefs, builds, gates, and verifies. Use for frontend execution
  in a real codebase — "scaffold a [page/component/route]", "build a settings
  page", "add a data table using shadcn", "implement this design in our [Tailwind/shadcn/Next]
  setup", "wire up this form", "extend our component library", "make a responsive
  [layout/section]" — AND for contract-level asks: "brief this screen before building",
  "interview me about this UI", "ship this feature end-to-end", "build the hero/landing/scroll
  sequence", "run the UI contract". Tiered process — micro asks (hover state,
  badge) go straight to execution; product asks (pages, tables, forms) get a quick
  brief; showcase work (heroes, landing/cinematic sequences) gets a grilling interview
  into a committed brief file, a HARD art-direction gate (one approved frame before
  any full build), and checkpoint QA (screenshots across viewports + states, reduced
  motion, console, interaction integrity). Probes the project first (package.json,
  tailwind.config.*, components.json, src/ shape) and follows the repo''s own
  conventions — Tailwind, shadcn/ui, vanilla CSS, a11y, JS/TS hygiene via references/.
  Composes with grilling (interview loop), frontend-design (taste), add-motion
  (animation craft), source-ui (visual reference), use-grid-system (grid discipline).
  Execution + process contract live here; aesthetics and animation stay with their
  skills.'
---

# build-ui

Implement UI in a real project under a tiered production contract: probe → brief → build → gate → verify — following the project's existing stack and conventions rather than inventing new ones.

## What it does

Given a UI ask in a real codebase, build-ui probes the project to learn its stack (framework, styling, components, motion, path aliases), classifies the ask into a **tier** (micro / product / showcase), collects a brief proportional to that tier, then implements following the matching patterns in `references/`. Showcase work cannot proceed to a full build until ONE representative frame has been approved (the art-direction gate), and no tier ships without its verification step. Bulky per-stack guidance lives in `references/` (A1) and is loaded only for the libraries the project actually uses.

This skill owns **execution mechanics and the production process**. Aesthetic *direction* is `frontend-design`'s territory; animation craft is `add-motion`'s; the deep-interview loop is `grilling`'s. Compose by reference — don't reinvent.

## How to run

Trigger phrases: "scaffold a settings page", "add a data table in our shadcn setup", "implement this design following our project conventions", "wire up this form", "brief this screen before building", "ship this feature end-to-end", "build the landing hero sequence". Or invoke `/build-ui <ask>` directly.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) — see per-step degrades |
| `--project=PATH` | project root (default: cwd; walks up to nearest `package.json`/`.git`) |
| `--no-probe` | skip `probe.py` and rely on the ask alone (only for trivial single-file edits) |
| `--stack=KEY` | force a stack hint when the probe is ambiguous (`tailwind`, `shadcn`, `vanilla-css`) |
| `--tier=X` | override tier classification (`micro`, `product`, `showcase`) |
| `--quick` | showcase interview collapses to one pre-filled form instead of the grilling loop |
| `--brief=PATH` | reuse an existing brief file; skips the interview |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. If python3 + `scripts/` are present → **SCRIPTS** (use `probe.py` + `preflight.py`). Otherwise → **NATIVE**: do the probe by hand (read `package.json`, look for `tailwind.config.*`, `components.json`, `tsconfig.json`, the `src/` shape), then follow `references/` directly. Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py --project=<root>`. `down` (e.g. `PROJECT_NOT_FOUND`) → stop and report; else proceed.
2. **Probe the project** — unless `--no-probe` is set, run `python3 scripts/probe.py --project=<root>` → JSON `{project_root, framework, css, components, motion, aliases, dirs, package_manager, tailwind, shadcn, design_md, external_skills}` (full shape in `scripts/probe.py` docstring). This is the source of truth for the rest of the flow; do not guess. With `--no-probe`, you have only the user's ask — proceed only for trivial single-file edits and flag the limitation in the plan.
3. **Classify the tier** (or take `--tier=X`) and announce it with one line of rationale:
   - **micro** — a state or affordance on an existing element (hover/press, badge, spinner, single transition). No brief, no gate; execute.
   - **product** — a page, route, form, table, or component with real content and layout decisions. Quick brief, no art gate.
   - **showcase** — work whose *point* is visual impact: heroes, landing/marketing sequences, scroll-driven or cinematic experiences, brand moments. Full contract: interview → brief file → art gate → checkpoint QA.
   When in doubt between product and showcase, say so and ask (interactive) or take product and record the doubt (`--agent`).
4. **Brief** (tier-scaled; skip entirely for micro, or when `--brief=PATH` provides one):
   - **product** → one round of questions (goal, target users/context, content source, done-criteria), each with a pre-filled recommended answer. Keep it under a minute of the user's time; record answers in the plan, no file required.
   - **showcase** → run the `grilling` skill's interview loop (if installed; otherwise run the interview yourself — the template's "Interview conduct" section is a self-contained fallback) over the template in [`references/brief-template.md`](references/brief-template.md) — one question at a time, each with a recommended answer, until every required field is filled and the user confirms the brief is locked (`--quick`: collapse to a single pre-filled form round instead). Write the locked brief to `docs/briefs/<slug>.md` in the project and treat it as the contract for everything downstream. If the brief needs visual precedent the user can't supply, route to `source-ui` (if available) before locking.
   - `--agent`: never interview — take the ask as the brief, write the assumed brief to `docs/briefs/<slug>.md` with an `UNCONFIRMED` marker listing the unfilled fields as assumptions, and proceed (A7d: degrade, never block).
5. **Load only the references the project uses** — first, if `--stack=KEY` was passed, override the matching probe field before routing: `--stack=tailwind` → `css=tailwind`; `--stack=vanilla-css` → `css=vanilla`; `--stack=shadcn` → `components=shadcn`. Then for each detected lib, read the matching `references/` file:
   - `css == "tailwind"` → [`references/tailwind.md`](references/tailwind.md)
   - `framework == "next"` or `components == "shadcn"` → the **external-skill deferral gate** (CLAUDE.md 5-step convention). Branch on `external_skills[<name>]` from the probe:
     - **installed** → defer the row's domain knowledge to the official skill; read our coordination layer (always — it holds the no-monoculture rule, probe↔`info --json` sequencing, and the routing table for when to invoke the skill vs. write code directly).
     - **missing** (fresh-clone case) → surface the row's install command (skills.sh; pinned in `skills-lock.json`), then fall back to general knowledge for this task and **flag the cutoff caveat plainly**. Still read the coordination layer for routing intent.

     | Probe condition | Official skill / defers | Coordination layer | Install | Cutoff caveat to flag |
     |---|---|---|---|---|
     | `framework == "next"` | `next-best-practices` — file conventions, RSC boundaries, async APIs (15+), directives, navigation hooks, error files, data patterns, route handlers, metadata/`next/og`, `next/image`, `next/font`, bundling | [`references/next-best-practices.md`](references/next-best-practices.md) | `npx skills add https://github.com/vercel-labs/next-skills --skill next-best-practices` | async params/`cookies()`/`headers()`, v16 `middleware`→`proxy` rename, current canary conventions |
     | `components == "shadcn"` | `shadcn` — add, preset, registry, `info --json`, current primitives, smart-merge | [`references/shadcn.md`](references/shadcn.md) | `npx skills add https://github.com/shadcn/ui --skill shadcn` | live `info --json`, presets, recent primitives (`FieldGroup`, `InputGroup`, `ToggleGroup`, …) |
   - The ask is animation-heavy (or `motion` is detected and the work is motion craft) → hand off to the sibling `add-motion` skill if installed (composition by reference — build-ui doesn't own animation craft); if missing, implement the motion here with general knowledge, honoring transform/opacity-only + reduced-motion, and flag the gap. For showcase tiers, `add-motion` executes the motion inside THIS skill's contract: the brief, gate, and checkpoint QA still apply.
   - The ask names a **grid system** / Müller-Brockmann / Swiss / column+baseline layout (e.g. "build the blog on a grid system") → **establish the grid spine first with the sibling `use-grid-system` skill** if installed (it emits the `@theme`/`:root` grid source of truth + the band/overlay patterns and owns the profile choice + adherence verification), then execute here **placing elements by column line** on those tokens; if missing, say so and apply general grid knowledge with the limitation flagged. build-ui doesn't own grid discipline — compose, don't reinvent.
   - `css == "vanilla"` (no tailwind/CSS-in-JS) → [`references/vanilla-css.md`](references/vanilla-css.md)
   - Always read [`references/a11y.md`](references/a11y.md) — work its **Universal Pre-Flight** for every component, then the matching **component-specific** section (Modal Dialog, Tabs, Combobox, Forms & Inputs, Menu, Disclosure/Accordion, Live Regions, Tables, Cards, Carousels). On shadcn/Radix-using projects, most keyboard/ARIA mechanics are handled by the primitive — use the checklist to verify you didn't break them with custom markup and to cover what primitives can't solve (labels, alt, contrast, copy, errors, focus restoration). Accessibility is not opt-in.
   - Always read [`references/javascript-patterns.md`](references/javascript-patterns.md) — stack-agnostic JS/TS hygiene: async/effects cleanup, state derivation (vs. syncing), TypeScript narrowing at boundaries, DOM perf gotchas (layout thrash, observers), forms, and the anti-patterns to stop on sight. Match the project's lint + tsconfig + library choices over generic best-practice.
   - If `design_md` is set in the probe (a `DESIGN.md` at the project root) → read [`references/design-md.md`](references/design-md.md), then **read the project's `DESIGN.md` itself** and treat it as the override for visual language (color tokens + semantic names, geometry/shape, atmosphere, component stylings). Project-checked-in DESIGN.md beats generic taste. Format-agnostic: handle both the [google-labs `design.md`](https://github.com/google-labs-code/design.md) YAML-token flavor and the Stitch natural-language-with-hex flavor. If `design_md` is `null` and the user has Stitch designs that need a DESIGN.md, point them at the sibling `/design-md` skill (composition by reference — build-ui doesn't generate it).
   If a stack key isn't covered in references, **say so** and fall back to the model's general knowledge; do not pretend coverage.
6. **Art-direction gate** (showcase tier only — HARD gate): before any full build, produce ONE representative frame — the hero composition or the single most characteristic component — as real code in the project (static or minimally animated), screenshot it via `automate-browser` / `example-skills:webapp-testing`, and present it for approval. Aesthetic direction comes from `example-skills:frontend-design` if available (otherwise apply the brief's visual-direction field directly; `source-ui` for precedent). **Do not continue until the user approves, redirects, or kills it** — the frame is cheap, the full build is not. On redirect: revise the frame, re-present. `--agent`: build the frame first anyway, include its screenshot in the report, flag `ART_GATE_UNREVIEWED`, and continue (A7d).
7. **Plan briefly, then implement** — restate the ask (and brief, if any) in one sentence, name the files you'll touch and the conventions you'll follow (from probe + references), then write the code. Use the project's existing path aliases (`@/components/...`), file naming, and component patterns. Match what's already in the repo over what's "best in general".
8. **Verify** (tier-scaled; never skip):
   - **all tiers** — typecheck (if TS) and any tests the criteria specify.
   - **micro** — drive or screenshot the affected element's states (default/hover/focus/disabled as applicable).
   - **product** — drive the affected flow end-to-end via `automate-browser` / `example-skills:webapp-testing`: screenshot key states at desktop + mobile widths, exercise every new control, check console for errors, run the matching a11y checklist section.
   - **showcase** — full checkpoint QA: define the experience's checkpoints up front (scroll positions / sequence beats / interaction states), screenshot each at ≥2 viewports, forward AND reverse for scroll-driven work; verify reduced-motion has a genuine alternative; console clean; zero horizontal overflow; interaction integrity (every visible control acts, no dead anchors). Fix defects and re-verify — screenshots are the evidence, not the code.
   If no browser tooling is available, say so plainly and list which checks were skipped (A12) — do not claim visual verification.
9. **Tell the user what you did + why** — files added/changed, the tier and why, the convention you matched, brief path (showcase), gate outcome, verification evidence (screenshot paths / checkpoint results), any deliberate deviations. Under `--agent`: write and report, no prompt.

## Conventions this skill follows

- Spec is `~/.cursor/skills/skill-architecture.md`.
- **Stable contract, per-project brief.** This SKILL.md is the reusable production contract (the role a versioned PROMPT.txt plays in prompt-kit workflows); everything project-specific lives in the run's brief (`docs/briefs/<slug>.md` for showcase). Change the contract deliberately, never per-project.
- **Composition by reference, not import** (spec A8): `frontend-design` owns aesthetic direction; `add-motion` owns animation craft; `grilling` owns the interview loop; `source-ui` finds visual precedent; `use-grid-system` owns Müller-Brockmann grid discipline. build-ui owns *execution and process*. Compose by naming, not by including their logic.
- **The art gate exists because verified-but-ugly ships without it.** A technically clean build the user hates is a failed build; taste is checked on one cheap frame before the spend, not after.
- **Project conventions beat global "best practice"** (A12 honesty): a probe-driven match to what the repo already does is more correct than what the model would write from scratch. Resist drift.
- **Scripts** (A4): JSON to stdout, diagnostics to stderr, graceful failure, never hang.
- **No assumptions about non-detected stacks** — if the project doesn't use shadcn, don't introduce it. Adding a dependency is a separate, explicit user decision.
- Keyless; no network.
