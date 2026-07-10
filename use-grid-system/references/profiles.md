# Two grid profiles — `editorial` and `app`

The canon was written for magazine spreads. Web-app UI keeps most of it but bends
a few rules. The skill ships **two profiles**; pick with `--profile=` (default
inferred from `probe.py` — `app` when the project looks like a web app).

## `editorial` — strict whole-field occupancy
The prior-skill regime, for magazine/report/longform/marketing pages.
- **Every element occupies whole fields** (column line → column line, row field →
  row field). Photos fill fields; captions sit in a constant field.
- **Strict baseline**: media heights = multiples of the leading; everything snaps.
- **Big display type** with runtime optical alignment (mastheads, numerals).
- Generous margins; asymmetric compositions held in tension by the grid.
- Verification target: `col ≈ 0px`, `baseline ≤ ½ baseline`, `ink ≈ 0px`.

Use when: "magazine/editorial layout", "report cover", "Müller-Brockmann spread",
landing/marketing pages with a strong typographic point of view.

## `app` — column-line alignment + baseline rhythm, relaxed rows
For dashboards, settings, forms, data tables, app shells. **What survives** from
the canon: columns + constant gutters, the baseline as the vertical quantum,
placement by column line, restraint, functional alignment. **What bends:**

- **App shell ≠ content fields.** Sidebars / nav rails / toolbars are *structure* —
  anchor them to column lines, but let content scroll within the field grid; the
  shell itself isn't a field.
- **Relax whole-row occupancy.** Cards, table rows, and form rows have variable
  heights; keep them on the **baseline** (heights/padding in baseline multiples)
  but drop "every block = a whole field."
- **Column rhythm for forms/tables.** Label / field / help align to column lines;
  the grid is the *alignment* unit, not necessarily the *sizing* unit.
- **Density.** App UI runs denser than spreads; expect 8/12-col with tighter
  gutters; container queries (not breakpoints) drive component reflow.
- Verification target: `col ≈ 0px` on aligned elements, `baseline ≤ ½ baseline`;
  the optical-ink check applies only to genuine display type (page titles, big
  metrics), not body/label text.

Use when: "put this dashboard on a grid", "align this settings page", "a 12-column
grid for our app", "grid system for our component library".

## Picking, in one line
- Content-led, typographic, few templates → **editorial**.
- Component-led, dense, many states, data → **app**.
- Mixed product (marketing + app) → **app** for the product surface, **editorial**
  for marketing routes; both read the *same* `@theme` tokens, so they stay coherent.

Both profiles share the source of truth, the overlay, and the optical-alignment
module; they differ only in **how strictly rows are treated** and **which
elements** the ink check covers.
