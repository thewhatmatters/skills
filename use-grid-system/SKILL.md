---
name: use-grid-system
description: Bring a GENUINE Josef Müller-Brockmann modular grid (International Typographic Style) into web app and design projects — TailwindCSS-first. Use when the user wants a real, load-bearing grid: "put this on a grid", "Müller-Brockmann / Swiss / International Typographic Style layout", "add a column + baseline grid", "grid overlay toggle", "align everything to the grid / to the baseline", "make this editorial/magazine layout", "set up our grid system", "a 12-column modular grid for this dashboard/app". Encodes the discipline (columns + row fields/modules on constant gutters, an 8px baseline rhythm, grotesque type, flush-left, restrained black/white/red) AND the front-end engineering to make the grid real, visible, and verified: one Tailwind @theme source of truth, subgrid bands that place by column LINE, a toggleable column+baseline overlay (the g key), runtime optical alignment so display ink (not its box) lands on the line, and verification composed via audit-ui/automate-browser. Two profiles: editorial (strict fields) and app (column-line + baseline, relaxed rows). Probes the project first and never imposes Tailwind on a non-Tailwind codebase. Composes with build-ui (execution), frontend-design (taste), design-md (owns the token spec), source-ui (reference). Do NOT use to audit a skill (audit-skill) or for general UI work without a grid mandate (build-ui).
---

# use-grid-system

Make a real Müller-Brockmann modular grid load-bearing in a web project — one
`@theme` source of truth, subgrid bands placed by column line, an 8px baseline,
a toggleable overlay, and runtime optical alignment — then prove it adheres.

## What it does

Encodes the *discipline* (the canon — `references/canon.md`) and the *engineering*
that makes a grid genuinely real on the web, not decorative. In Tailwind v4 the
grid **is tokens**: a single `@theme` block (cols/gutter/margin/maxw + an 8px
`--spacing`/leading) drives everything, `@utility` bands place children by column
LINE via `grid-cols-subgrid`, a `g`-key overlay shows the columns + baseline in
the *same* content box, and a small runtime JS nudges display type so its **ink**
(not its box) lands on the line. It runs in two **profiles** — `editorial`
(strict whole-field occupancy) and `app` (column-line + baseline, relaxed row
heights for dashboards/forms/tables). It **probes the project first** and degrades
to a vanilla `:root` scaffold rather than impose Tailwind (no-monoculture, spec A8).

## How to run

Trigger with "put this on a grid", "set up our grid system", "add a column +
baseline grid", "Müller-Brockmann / Swiss layout", "grid overlay toggle", or
`/use-grid-system [path] [--profile=app|editorial]`. Hand the emitted tokens +
patterns to **build-ui** for execution; verify with **audit-ui**.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | where to write the emitted scaffold (default: stdout / project CSS) |
| `--profile=app\|editorial` | grid profile (default: inferred from probe; `app` for web-app UI) |
| `--cols=N` | column count (default 12) |
| `--baseline=PX` | baseline unit in px (default 8; leading = 3×) |
| `--gutter=PX` `--margin=PX` `--maxw=PX` | grid geometry (baseline multiples) |
| `--accent=HEX` | accent color (default Swiss red `#e4002b`) |
| `--vanilla` | emit a framework-free `:root` scaffold instead of Tailwind `@theme` |
| `--design-md` | emit a `## Grid` block for a project DESIGN.md (design-md owns the spec) |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. python3 + `scripts/` → **SCRIPTS** (run
`grid_tokens.py` / `probe.py`). Otherwise → **NATIVE**: emit the same scaffold by
hand from `references/tailwind.md` (or `references/non-tailwind.md`). Announce the
mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py [--agent]`. Read the JSON; only
   `down` stops a run (nothing here is network-bound).
2. **Probe the project** — `python3 scripts/probe.py [path]` → JSON: Tailwind
   v4/v3/none, framework (React/Vue/none), existing `DESIGN.md ## Grid`, current
   `--spacing` base. This picks the path and prevents silently re-scaling a live
   project (the `--spacing` caveat in `references/tailwind.md`).
3. **Pick the profile** — `app` vs `editorial` (`references/profiles.md`).
4. **Emit the source of truth** — `python3 scripts/grid_tokens.py --profile=…
   [--vanilla] [geometry flags]`: Tailwind `@theme` + `@utility` band/overlay by
   default; `:root` vanilla under `--vanilla`. Warns if gutter/margin aren't
   baseline multiples. **DESIGN.md is the source of truth:** if `probe.py`
   reported `design_md_grid:true`, READ that `## Grid` section yourself (a NATIVE
   step — no script parses it) and pass its values as `grid_tokens.py` flags. If
   there's no `## Grid` yet, offer to seed one with `grid_tokens.py --design-md`
   (design-md owns it; this skill consumes it).
5. **Place by column LINE** — build layout as subgrid bands; lock spacing /
   leading / media heights to the baseline (`references/tailwind.md`).
6. **Overlay + optical alignment** — wire the `g`-key column+baseline+margin
   overlay (same content box) and the runtime ink-alignment JS
   (`references/optical-alignment.md`); compose `tailwindcss-react-grid-overlay`
   where React is present rather than rebuild.
7. **Verify** — don't trust, measure. Run the four adherence checks
   (`references/verification.md`) through **audit-ui / automate-browser**, at
   widths above and below `--maxw`. Report `col / overlay / baseline / ink` deltas.
8. **Hand off** — give the tokens + patterns to **build-ui** to implement;
   **frontend-design** for taste; **source-ui** for reference layouts.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- Dual-mode + degraded ladder (A3); probe-gated, no-monoculture (A7/A8): never
  impose Tailwind, never silently re-scale a project's `--spacing`.
- Composition by reference, not import (A8): build-ui (execution), frontend-design
  (taste), audit-ui/automate-browser (verification), design-md (token spec),
  source-ui (reference). Runs none of their code.
- The canon stays branded **Müller-Brockmann** internally (`references/canon.md`),
  citing *Grid Systems in Graphic Design* (Niggli, 1981) by printed page.
- Keyless; no secrets; writes only the scaffold the user asks for.
