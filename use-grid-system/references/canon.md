# The canon — Müller-Brockmann's modular grid (the discipline)

Source: Josef Müller-Brockmann, *Grid Systems in Graphic Design / Raster systeme
für die visuelle Gestaltung* (Niggli, 1981). Locators are the book's **printed
page numbers** (`p. N`). Distilled from the 162-page scan of the book; the design
rationale that builds on it is in `research-rationale.md` (same dir).

> **"The grid system is an aid, not a guarantee. It permits a number of possible
> uses and each designer can look for a solution appropriate to his personal
> style. But one must learn how to use the grid; it is an art that requires
> practice."** (p. 174)

## The thesis (pp. 10–13)
The grid is **constructive thought** and a professional ethic — the system, not
the ego, organises the page. It **"divides a two-dimensional plane into smaller
fields"** (p. 11); fields are separated by an **intermediate space** (the gutter);
a field's size = the size of a text block; elements occupy **whole fields**.
Purpose (p. 13): legibility, credibility, objectivity, economy, coherent identity.

## The construction method (pp. 49–67) — the load-bearing part
1. **Determine the type area from the content** (text + illustrations), via
   small-scale 1:1 sketches; divide it into **1 / 2 / 3 / 4 / 8 columns** (3→6,
   4→8/16) — more columns = narrower columns = smaller type (pp. 49–56).
2. **Build the field grid by dividing the column DEPTH into horizontal fields.**
   Worked example (pp. 57–59): a column **57 lines** deep wanting **4 fields** has
   **3 blank "Leerzeile" rows** between them → `57 − 3 = 54`, `54 ÷ 4 = 13.5`. No
   half-lines exist, so correct to a **55-line** column = **4 fields of 13 lines,
   1 blank line between** (depth ≈ 54 ciceros / 24.7 cm).
3. **The field is the atomic unit** — text, photos, captions all snap to whole
   fields or whole multiples of field + gutter (p. 58). Field grids scale: **8**
   (p. 72) → halve → **16**; also **20** (p. 80) and **32** (p. 97).
4. **Two gutters, both constant:** a **column gutter** (vertical) and a **row
   gutter = the blank line / Leerzeile** (horizontal). This row gutter is the
   single most-missed construction detail.

## Type, rhythm, margins
- **Column width (pp. 30–33):** target **7–10 words per line**; too narrow or too
  wide both tire the eye. Width, type size, and leading are **interdependent**.
- **Leading (pp. 34–38):** vertical rhythm is sacred; sans-serif and large type
  need more leading; leading sets the lines-per-column, hence the field math.
- **Display type sizing (p. 59):** chosen by **divisibility against the baseline**
  (e.g. 30 pt on 4 pt lead = 24 pt = two 12 pt lines) so headings land on the
  body baseline.
- **Margins (pp. 39–41):** the type area sits in a margin zone; well-proportioned
  margins enhance reading; book/picture margins are generous. **Folios** placed
  **functionally**, in a constant grid position (p. 42).

## Craft defaults (pp. 16, 19, 81)
- **Type:** a **grotesque sans** (Akzidenz-Grotesk / Helvetica / Univers; on the
  web Inter / Helvetica Now / Archivo). **Flush-left, ragged-right.** Few sizes,
  large scale jumps for hierarchy; objective, not expressive. Big numerals/data.
- **Palette:** white paper, near-black ink, **one accent — red is canonical**
  (`#e4002b`). Avoid warm-cream; never blue/purple gradients.
- **Reach:** one grid governs **corporate identity** across every touchpoint
  (p. 133); it organises **3-D / exhibition** space (pp. 141–157); the same
  ordering impulse runs from **Miletus (479 BC)** to **Le Corbusier's Plan Voisin
  (1924)** (pp. 158–173).

## What translates to the web (and where it bends → `profiles.md`)
| Canon | Web translation |
|---|---|
| Field = atomic unit (p. 57) | subgrid **bands**; place by **column line** |
| Row gutter = Leerzeile (pp. 57–59) | baseline-multiple `row-gap`; **8px baseline / 24px leading** |
| One measuring system, whole multiples (pp. 17, 59) | one `@theme` source of truth (`--spacing` + grid namespace) |
| Margin zone + type area (p. 39) | content + overlay share the **same content box** |
| Grotesque + restraint + red (pp. 16, 19) | Inter/Helvetica + Swiss red; no cream, no blue/purple |
| "Learn it; prove it" (p. 174) | the `g`-key overlay + automated adherence checks |

## Creed
A grid you can't toggle on and measure is a mood board, not a system. Build it
from one source of truth, place by the line, lock the baseline, align the **ink**,
and prove it at ~0px.
