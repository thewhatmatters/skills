# use-grid-system

**What it is:** A skill that brings a genuine Josef Müller-Brockmann modular grid
(the Swiss / International Typographic Style) into web app and design projects —
TailwindCSS-first — and makes the grid real, visible, and verifiable rather than
decorative.

## What you get

- A **single source of truth** for the grid: one Tailwind `@theme` block (or a
  vanilla `:root` block off-Tailwind) holding columns, gutter, margin, max-width,
  an 8px baseline unit, and the leading — every spacing/leading utility derives
  from it.
- **Subgrid "band"** patterns that place every element by **column line**, a
  toggleable **column + baseline overlay** (press `g`), and a runtime
  **optical-alignment** module so big display type lands its *ink* on the line.
- A **verification path** (four adherence checks) run through your existing
  `audit-ui` / `automate-browser` skills — so a finished page proves it sits on
  its grid at multiple widths.

## How to run

Say "put this on a grid", "set up our grid system", "add a column + baseline
grid", "Müller-Brockmann / Swiss layout", or run
`/use-grid-system [path] --profile=app`. Example:
`/use-grid-system src/app --profile=app --cols=12`.

## What it needs

Nothing required — it is keyless and works with no setup. For the full Tailwind
path it expects a Tailwind v4 project (it detects this); otherwise it degrades to
a framework-free `:root` scaffold. The optional React overlay composes the
`tailwindcss-react-grid-overlay` package when React is present.

## How it works (high level)

1. **Probe** the project — Tailwind v4 / v3 / none, framework, an existing
   `DESIGN.md` grid spec, the current spacing base.
2. **Pick a profile** — `editorial` (strict whole-field layout, magazine spreads)
   or `app` (column-line alignment + baseline rhythm, relaxed rows for dashboards,
   forms, and tables).
3. **Emit the source of truth** — the `@theme` (or `:root`) tokens + the band /
   overlay utilities, consuming a project `DESIGN.md ## Grid` block if one exists.
4. **Build on it** — place elements by column line as subgrid bands; lock spacing
   and leading to the 8px baseline; add the overlay + optical-alignment.
5. **Verify** — measure column / overlay / baseline / ink adherence via audit-ui
   at widths above and below the content max-width; hand fixes to build-ui.

This skill is the *grid spine*: execution lives in `build-ui`, aesthetic taste in
`frontend-design`, the token spec in `design-md`, reference layouts in
`source-ui`. It composes with them by reference and runs none of their code.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/` — the canon (`canon.md`), the Tailwind token/utility layer
  (`tailwind.md`), the two profiles (`profiles.md`), optical alignment
  (`optical-alignment.md`), verification (`verification.md`), the non-Tailwind
  fallback (`non-tailwind.md`), and the design rationale / build proposal
  (`research-rationale.md`).
