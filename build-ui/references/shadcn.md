# shadcn — the build-ui complement to the official skill

Loaded by `SKILL.md` Step 3 when `probe.components == "shadcn"`.

## Defer execution to the official `shadcn` skill

If a project has `components.json`, the **official `shadcn` skill** (from
shadcn-ui, version-pinned in our `skills-lock.json`) auto-triggers and owns the
*execution* surface: `add`, `--diff`/`--dry-run` smart-merge, presets
(`apply`/`decode`/`resolve`), registry search (incl. community: `@magicui`,
`@tailark`, etc.), live project context via `npx shadcn@latest info --json`
(returns `aliases`, `isRSC`, `tailwindVersion`, `tailwindCssFile`, `style`,
`base`, `iconLibrary`, `preset`, `packageManager`, `framework`,
`resolvedPaths`), and the current primitive set (which evolves — `Field` /
`FieldGroup` / `InputGroup` / `ToggleGroup` are recent and your training cutoff
may not have them).

**Don't replicate any of that here.** When you need a component added,
documented, or updated, run the shadcn CLI through that skill. This file is the
*complement* — what build-ui adds on top.

## What build-ui's perspective adds

- **No-monoculture rule.** Refuse to introduce shadcn into a project that
  doesn't already use it. Adding it writes a `components.json`, copies sources,
  and changes the project's posture — a separate, explicit user decision.
- **Project-probe alignment.** `scripts/probe.py` reports the shadcn
  `style` / `baseColor` / `rsc` / `components_alias` / `ui_alias` from
  `components.json` *before* any work — use it directly, don't ask the model
  to guess. (The official skill also runs `info --json` for live state; the
  probe gives you a deterministic snapshot to plan with.)
- **Compose, don't fork.** When building a `StatCard`, `PricingTable`,
  `EmptyDashboard` etc., compose the existing shadcn primitives — don't copy
  them and rename. The shadcn skill's "Compose, don't reinvent" is the same
  rule we apply at the project layer.
- **The shadcn skill's Critical Rules pair with our `a11y.md` and
  `javascript-patterns.md`.** Its `styling.md` / `forms.md` / `composition.md`
  / `icons.md` / `base-vs-radix.md` cover shadcn-specific rules
  (`size-*` over `w-* h-*`, `gap-*` over `space-y-*`, `data-icon`, `FieldGroup`
  + `Field` validation patterns). Our references cover the project-agnostic
  layer (a11y patterns, async/effects, state derivation).

## When NOT to invoke the shadcn skill from a build-ui task

- The task is **inside a project that already uses shadcn** and is purely about
  writing *code that uses installed components* — that's normal build-ui work.
  Read the relevant primitives' files (`components/ui/<name>.tsx`) and use them.
  The shadcn skill is for *adding / updating / inspecting* components, not for
  every line of JSX that references one.
- The task explicitly opts out (e.g. "build this WITHOUT adding new shadcn
  components — work with what's installed").

## Composition with frontend-design

`frontend-design` may push toward distinctive typography, dramatic color, or a
maximalist treatment. Implement that by:
1. Editing the CSS variables in the project's `tailwindCssFile` (palette,
   radius) — never override per-component.
2. Adjusting the `cva` `variants` on the affected primitive (sizes, intents).
3. Keep the *structure* (Radix/base primitives, slots, ARIA) — only the
   surface changes.

The shadcn skill knows how to surface live `tailwindCssFile` for you.

## TL;DR routing

| Need | Where |
|---|---|
| Add a component (`Button`, `Dialog`, `Empty`, …) | **shadcn skill** (CLI: `add`) |
| Update / smart-merge existing components | **shadcn skill** (`--diff` / `--dry-run`) |
| Switch / apply a preset | **shadcn skill** (`apply` / `init --preset`) |
| Component docs and examples | **shadcn skill** (`docs <name>`) |
| Use an *installed* primitive correctly (`FieldGroup`/`Field`, `data-icon`, `size-*`, etc.) | **shadcn skill rules** (`rules/*.md`) |
| Compose a custom component from installed primitives | build-ui (this skill) |
| Project conventions (aliases, dir layout, `cn()` location) | build-ui + the probe |
| Accessibility checklist (Universal + per-pattern) | [`a11y.md`](a11y.md) |
| JS/TS hygiene (async, state, types) | [`javascript-patterns.md`](javascript-patterns.md) |
