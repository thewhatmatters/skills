# The Tailwind layer — the grid as tokens

In **Tailwind v4** the grid genuinely *is* tokens. v4's spacing scale is
`calc(var(--spacing) * n)` off a single base, and `@theme` variables both emit
`:root` CSS variables **and** generate utilities. So the prior skill's hand-rolled
`:root{--cols/--gutter/--bl/--lh}` source of truth collapses into one `@theme`
block. `grid_tokens.py` emits this; the rules below are why.

## 1. One source of truth — the `@theme` block

```css
@import "tailwindcss";

@theme {
  /* --- the vertical quantum --- */
  /* Default Tailwind base is 0.25rem (4px). EVEN multiples already land on an
     8px baseline, so the SAFE default keeps 4px and adds an explicit leading.
     Only set --spacing: 0.5rem on a GREENFIELD project (it doubles every
     default spacing utility — see the caveat below). */
  --leading-base: 1.5rem;          /* 24px = 3 × 8px baseline (canon p.59) */

  /* --- grid geometry (one namespace) --- */
  --grid-cols: 12;                 /* column count */
  --grid-gutter: 1.5rem;           /* 24px column gutter (baseline multiple) */
  --grid-margin: 4.5rem;           /* 72px page margin */
  --grid-maxw: 81rem;              /* 1296px content max-width */

  /* --- restrained Swiss palette (canon) --- */
  --color-paper: #ffffff;
  --color-ink: #111315;
  --color-ink-soft: #5b6066;
  --color-accent: #e4002b;         /* Swiss red */
}
```

`--grid-*` is a custom namespace → reference the values anywhere as
`var(--grid-gutter)` and in arbitrary utilities (`gap-[var(--grid-gutter)]`,
`max-w-[var(--grid-maxw)]`). Keep `--leading-*` so `leading-base` is a real utility.

> ⚠️ **The `--spacing` re-scale caveat (read before touching a live project).**
> Setting `--spacing: 0.5rem` makes `p-1` = 8px (not 4px) and shifts *every*
> spacing utility in the codebase. On an existing project, **do not** re-scale —
> keep the 4px base (even multiples = 8px baseline) and add the grid namespace on
> top. `probe.py` reports the current base so we never re-scale silently
> (no-monoculture, spec A8). `--spacing: 0.5rem` is only for greenfield.

If a project `DESIGN.md` has a `## Grid` block, **its tokens win** — design-md owns
the spec, this skill consumes it.

## 2. Place by column LINE — subgrid bands as `@utility`

CSS subgrid is **Baseline Widely Available (Mar 15 2026)** — Chrome/Edge 117+,
Firefox 71+, Safari 16+ (~97%). A band spans all columns and re-exposes them so
children align to the **same** lines as everything else:

```css
@utility grid-page {
  display: grid;
  grid-template-columns: repeat(var(--grid-cols), 1fr);
  column-gap: var(--grid-gutter);
  row-gap: var(--leading-base);
  max-width: var(--grid-maxw);
  margin-inline: auto;
  padding-inline: var(--grid-margin);
}
@utility band {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: subgrid;
  column-gap: var(--grid-gutter);
  align-items: start;
}
/* fallback for the <3% without subgrid (and the centered-container case) */
@supports not (grid-template-columns: subgrid) {
  @utility band { grid-template-columns: repeat(var(--grid-cols), 1fr); }
}
```

Author markup places children by line — in Tailwind classes or arbitrary props:

```html
<div class="grid-page">
  <div class="band">
    <h2 class="col-start-1 col-end-6">…</h2>
    <figure class="col-start-6 col-end-13">…</figure>  <!-- height = ×leading -->
  </div>
</div>
```

`col-start-*` / `col-end-*` are stock Tailwind. Reach for `grid-cols-subgrid` (v4
ships it) on the band; the `@utility band` above just packages it + the gutter +
the `@supports` guard so authors write one class.

## 3. Lock vertical rhythm to the baseline
- Leading = `leading-base` (24px). For display type set line-height in **px
  multiples** of the baseline, never unitless (unitless drifts the box off-grid).
- Every margin/padding/gap a spacing-scale step (which is baseline-multiple).
- **Media heights = multiples of the leading** (e.g. `h-[15rem]` = 240px = 10×24)
  so a photo's top AND bottom land on lines.

## 4. Responsive — container queries for components, breakpoints for the shell
Tailwind v4 ships **native container queries** (no plugin): mark a wrapper
`@container`, then use `@sm:` / `@md:` variants on children so a component reacts to
*its own* width, not the viewport. This is how the grid holds from dashboard card
to marketing hero — the canon's 12→6→3 / 8→4 column subdivision becomes
container-driven:

```html
<section class="@container">
  <div class="grid grid-cols-4 @md:grid-cols-8 @xl:grid-cols-12">…</div>
</section>
```

Use **breakpoints** (`md:`, `lg:`) for the page shell / margins; **container
queries** (`@md:`) for cards, panels, tables; **`clamp()`** for fluid display type
— clamped so its line-height stays a baseline multiple at every size (re-run
optical alignment on resize — see `optical-alignment.md`).

## 5. Tailwind v3 / non-Tailwind
- **v3:** no `@theme`; put the same tokens in `theme.extend` (config JS) + a small
  plugin for the band utility. Note the v4 upgrade benefit to the user.
- **No Tailwind:** degrade to the framework-free `:root` scaffold in
  `references/non-tailwind.md`. Never add Tailwind to a project that doesn't use it.
