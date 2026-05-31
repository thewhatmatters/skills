# shadcn — the build-ui complement to the official skill

Loaded when `probe.components == "shadcn"`. The **official `shadcn` skill**
(pinned in `skills-lock.json`, symlinked at `~/.claude/skills/shadcn`) owns the
execution surface: `add`, presets, registry search, `npx shadcn@latest info
--json`, current primitives, smart-merge. **Defer to it.** This file is kept
intentionally small so it doesn't drift from upstream.

## What build-ui owns here

- **No-monoculture rule.** Refuse to introduce shadcn into a project that
  doesn't already have `components.json` — adding it writes config, copies
  sources, and changes the project's posture. That's a separate, explicit user
  decision; flag it, don't sneak it in. (`probe.components` will say `none`
  when it's not already adopted.)
- **Probe + `info --json` are not redundant — they're sequenced.** The probe
  (`scripts/probe.py`) gives you a deterministic planning snapshot read straight
  from the configs on disk. The shadcn skill's `info --json` gives live state at
  execution. **Plan with probe; execute with `info`.** If they disagree, trust
  `info` (it sees what the CLI sees).

## Routing — when build-ui defers vs. acts directly

| Need | Where |
|---|---|
| Add / update / preview a component | **shadcn skill** (`add`, `--diff`, `--dry-run`) |
| Apply / switch / inspect a preset | **shadcn skill** (`preset` / `apply`) |
| Component docs and examples | **shadcn skill** (`docs <name>`) |
| Use an *installed* primitive correctly (`FieldGroup`, `data-icon`, `size-*`, …) | **shadcn skill rules** (`rules/*.md`) |
| Compose a custom component from installed primitives | **build-ui** (this skill) |
| Project conventions (aliases, dir layout, `cn()` location, file naming) | **build-ui + the probe** |

## Composition stance

`frontend-design` (taste) → `build-ui` (project conventions, no-monoculture) →
**shadcn skill** (execution mechanics). When you're writing JSX against
*already-installed* primitives, that's everyday build-ui work — don't invoke
the shadcn skill for every line that imports a primitive. Invoke it for actions
that touch the component layer (add, update, switch preset, fetch docs).
