# Verification — don't trust, measure (composed, not bespoke)

The canon's demand is to *learn and prove* the grid (p. 174). We **do not** ship a
bespoke Puppeteer harness (the prior export's was platform-foreign). Instead the
four adherence checks run as a **grid-adherence dimension through `audit-ui`**
(which already hosts the Playwright engine) or via an `automate-browser` recipe —
composition by reference (spec A8).

Render the page and assert at **several widths including above and below
`--grid-maxw`** (e.g. 1440 / 1180 / 900) to catch centered-container drift.

## The four checks
1. **Column adherence** — every placed `.band > *` left edge snaps to a column
   START line and its right edge to a column END line (~0px). **Build BOTH the
   start set and the end set** of x-coordinates: an item spanning "to line N" ends
   at the *far* side of the gutter, so single-edge math falsely reports a
   one-gutter error. **Exclude optically-aligned display elements** (their box is
   intentionally side-bearing-offset; check 4 validates them).
2. **Overlay match** — each overlay `.col` rect equals the computed column rect
   (~0px): the overlay really is the content grid, not a look-alike.
3. **Baseline** — text-element tops modulo the baseline ≈ 0 (tolerance ≈ ½ a
   baseline; the box-top is a proxy — the leading does the real work).
4. **Optical ink** — each display element's ink-left (`box − actualBoundingBoxLeft`,
   measured with the **real** font) equals **its own** column line (the nearest
   column-start to its box), not always line 1.

A clean run reads: `col=0px overlay=0px baseline≤4px ink=0px → PASS`.

## How to run it (audit-ui dimension)
- Hand audit-ui the running dev-server URL and ask for the **grid-adherence**
  pass; it drives Playwright, evaluates the four checks in-page, and screenshots a
  **top-left zoom crop** (masthead vs body vs column line) for the fastest human
  eyeball.
- Or drive `automate-browser` directly: `goto` the URL at each width, `evaluate`
  the check functions, print the deltas, and read back the crop with the
  image-capable Read tool.

## The measurement gotchas (carry verbatim)
- **Embed the real webfont for offline/headless runs** or the ink check is wrong
  (headless Chrome falls back to a different grotesque — −16px vs −7px for the same
  `H`; see `optical-alignment.md`). In production the runtime JS is correct.
- **Both column edges** (start AND end sets) — see check 1.
- **Test above and below `--grid-maxw`** — the centered content box and a
  full-width overlay drift apart past the max-width if the overlay isn't in the
  same content box.
- Baseline tolerance is half a baseline unit; don't tighten it past the leading.

## app vs editorial
- **editorial:** all four checks, tight (`col≈0`, `ink≈0`).
- **app:** checks 1–3 on aligned elements; the **ink** check covers only genuine
  display type (page titles, big metrics), not body/labels/cells/buttons.

The point of keeping verification mandatory: in the `app` profile, relaxing
whole-row occupancy risks "grid in name only" — the overlay + adherence check keep
the grid *measurable*, honoring the creed.
