# Building a `use-grid-system` skill — a Müller-Brockmann modular grid for all our web/app projects, on TailwindCSS

> **Deep-research report** · type: feature/landscape · depth: standard→exhaustive ·
> mode: **NATIVE** (built-in WebSearch/WebFetch; no Tavily/Exa key) · date: 2026-06-13 ·
> sources: 14 (WebSearch ×12, WebFetch ×2) + 1 live-browser validation (Playwright)
> Companion to [`canon.md`](canon.md) (the ingested book, distilled). The original
> scratch ingest (full summary + the prior `müller-brockmann.json` skill export +
> the 162-pp scan) was reference-only and has been removed; recoverable from git
> history @ commit 3515745.

---

## Executive recommendation

Build `use-grid-system` as a **dual-mode, Tailwind-first skill that treats the grid as
tokens, not CSS** — because in Tailwind v4 the grid genuinely *is* tokens. Four findings
collapse most of the prior skill's bespoke machinery into the framework:

1. **Tailwind v4's spacing scale is already an 8px baseline engine.** Every spacing
   utility is `calc(var(--spacing) * n)` off a single `--spacing` base (default 0.25rem /
   4px).[^spacing] Set `--spacing` and a leading token in `@theme`, and baseline-multiple
   spacing/leading falls out of `p-*`, `gap-*`, `mt-*`, `leading-*` for free — the prior
   skill's hand-rolled `--bl/--lh` source of truth becomes **one `@theme` block**.[^theme]
2. **Subgrid is now Baseline (Mar 15 2026).**[^subgrid] "Place by column LINE" — the prior
   skill's `.band` trick — is now production-safe via `grid-cols-subgrid` + `col-start/
   col-end`, with a trivial `@supports` fallback. The bespoke subgrid CSS shrinks to a
   couple of `@utility` definitions.[^subgrid]
3. **Optical alignment still needs the runtime JS.** `text-box-trim`/`text-box-edge`
   (the renamed `leading-trim`) is **NOT Baseline as of Apr 2026** — it fails in widely
   used browsers.[^textbox] So the prior skill's canvas `actualBoundingBoxLeft` nudge
   stays as the cross-browser path; `text-box-trim` is a progressive-enhancement layer,
   not a replacement.
4. **The overlay is a compose, not a build.** `tailwindcss-react-grid-overlay` already
   ships a `g`-key-toggled column overlay for React/Tailwind[^overlay] — same gesture our
   prior skill uses. We extend it (it does columns only, dev-only, "not an all-encompassing
   grid system") with a baseline-line layer rather than reinventing it.

**Net:** the skill is ~70% **tokens + a thin reference layer + composition**, and ~30%
genuinely novel code (the baseline overlay layer, the optical-alignment module, and the
verification glue into our existing Playwright skills). It must honor **no-monoculture** —
in non-Tailwind projects it degrades to a vanilla-CSS variable scaffold (the prior skill's
proven approach), never imposing Tailwind.

---

## Findings (the seven questions)

### 1. Encoding the grid as ONE source of truth in Tailwind v4

Tailwind v4 (Jan 2025) replaced `tailwind.config.js` with **CSS-first `@theme`**.[^v4]
Theme variables are special: they emit both a `:root` CSS variable *and* the corresponding
utility classes.[^theme] Namespaces drive utility generation — `--spacing-*` → spacing
utilities, `--breakpoint-*` → responsive variants, `--text-*` → font-size utilities, custom
`--<ns>-*` → custom utilities.[^theme]

The load-bearing detail for us: **all spacing/sizing is `calc(var(--spacing) * n)`** off a
single base (default `0.25rem`).[^spacing] So:

```css
@import "tailwindcss";
@theme {
  --spacing: 0.5rem;            /* 8px baseline unit → the WHOLE grid's vertical quantum */
  --leading-base: 1.5rem;       /* 24px = 3 × baseline (the book's leading=3×bl, p.59) */
  --grid-cols-page: 12;         /* column count */
  --grid-gutter: 1.5rem;        /* 24px column gutter, a baseline multiple */
  --grid-margin: 4.5rem;        /* 72px page margin */
  --grid-maxw: 81rem;           /* 1296px content max-width */
  --color-paper: #fff;
  --color-ink: #111315;
  --color-accent: #e4002b;      /* Swiss red (book p.16/81) */
}
```

This single block replaces the prior skill's `:root{--cols/--gutter/--bl/--lh/--margin/
--maxw}` — and unlike raw `:root`, it *also* makes `gap-[--grid-gutter]`, `leading-base`,
etc. real utilities.[^theme] Column-line placement and subgrid bands are best expressed as
**`@utility`** definitions (the v4 replacement for the v3 plugin system)[^v4] plus arbitrary
values — so yes, a thin slice of bespoke CSS remains, but it's `@utility .band { … }` and
`@utility .guides { … }`, not a parallel token system.

> ⚠️ **Caveat (inference):** a literal `--spacing: 0.5rem` doubles every default Tailwind
> spacing utility (`p-1` becomes 8px, not 4px), which can surprise an existing project.
> Safer for app projects: keep `--spacing: 0.25rem` (4px base — *even* multiples already
> land on the 8px baseline) and add an explicit `--leading-*`/grid-namespace on top. The
> skill should detect which and not silently re-scale a live project (no-monoculture).

### 2. Subgrid + "place by column line" in Tailwind

CSS subgrid is **Baseline Widely Available since Mar 15 2026** — Chrome/Edge 117+,
Firefox 71+, Safari 16+, ~97% global.[^subgrid] A nested grid with `grid-template-columns:
subgrid` reuses the parent's tracks, so children align to the *same* lines as everything
else — exactly the book's "elements occupy whole fields" (summary p.57).[^subgrid]

In Tailwind: `grid grid-cols-subgrid` on the band, then `col-start-1 col-end-6` /
`col-start-6 col-end-13` on children. Fallback via `@supports not (grid-template-columns:
subgrid)` re-declaring `repeat(var(--grid-cols-page),1fr)` — the prior skill already
carries this exact guard.[^subgrid] **Recommendation:** ship a `.band` `@utility` that
encapsulates the subgrid + gutter + `@supports` fallback so authors write one class, not
the raw declaration.

### 3. Baseline rhythm + the optical-alignment decision

The 8-point baseline is the standard: line-height 24px = 3×8, all spacing in multiples of
8.[^8pt] The community consensus is blunt: a true baseline grid on the web is **"not
easy — for every font family and size you have to measure where the letters sit and shift
to the nearest gridline, then adjust margins/paddings."**[^8pt][^alistapart] That is
precisely the problem the prior skill's runtime canvas measurement solves.

`text-box-trim`/`text-box-edge` (renamed from `leading-trim`) is designed to remove the
half-leading above cap-height / below baseline so text boxes sit *true* on the grid — but
it is **not Baseline (Apr 2026)** and fails in widely used browsers.[^textbox] **Decision:**

- **Vertical rhythm** → tokens (`--spacing` + `--leading-*`); Tailwind utilities keep
  margins/paddings/leading on the baseline automatically.[^spacing] This eliminates most
  of the prior skill's manual baseline bookkeeping.
- **Horizontal optical alignment of large display type** (ink-left vs box-left side-bearing,
  summary's "box-on-grid ≠ ink-on-grid") → **keep the runtime canvas JS.** It's the only
  cross-browser-correct path today, and it measures the *actually loaded* font.[^textbox]
- **`text-box-trim`** → add as a progressive-enhancement utility (`@supports (text-box-trim:
  trim-both)`) that *reduces* but does not replace the JS nudge.

### 4. Fluid type + container queries vs breakpoints

Tailwind v4 ships **native container queries** — `@container` + `@sm:/@md:` variants, no
plugin.[^container] This is the right primitive for "the grid holds from dashboard card to
marketing hero": a card queries *its own* width, so a 12-field grid can collapse to 6/4/2
fields based on the **container**, not the viewport[^container] — directly mirroring the
book's 12→6→3 / 8→4 column subdivisions (summary p.51–56).

Pair with `clamp()` for fluid type, but **clamp the type so its line-height stays a baseline
multiple** at every size (the prior skill re-runs optical alignment on resize for this
reason). **Recommendation:** breakpoints for the page shell / margins; container queries for
components (cards, panels, data tables); `clamp()` for display type, baseline-quantized.

### 5. Generalizing editorial → web-app UI

The modular grid transfers to apps well-documented: dashboards apply it so "each card
follows the same size and spacing," and modular row×column grids are called "perfect for
dashboards, galleries, and complex data layouts."[^dash][^uxpin] Material's responsive
layout grid is the 12-column reference.[^dash] **What survives** from Müller-Brockmann:
columns + fields, constant gutters, baseline rhythm, whole-field occupancy, restraint,
functional alignment. **What bends:**

- **App shell ≠ page.** Sidebars / nav rails / toolbars are *structure*, not content fields
  — anchor them to column lines but let content scroll within the field grid.
- **Data tables / forms** want the **column rhythm** (label/field/help on column lines) but
  loosen strict *row*-field occupancy (variable row heights) — keep the baseline as the
  vertical quantum, drop "every block = whole field."
- **Density.** App UIs run denser than magazine spreads; the field becomes the *alignment*
  unit, not necessarily the *sizing* unit.

So the skill should offer **two grid profiles**: `editorial` (strict fields, the prior
skill's regime) and `app` (column-line alignment + baseline spacing, relaxed row fields).

### 6. Overlay & verification tooling

- **Overlay:** `tailwindcss-react-grid-overlay` gives a `<Grid>` component, per-breakpoint
  column configs, and a **`g`-key toggle** — but **dev-only, columns-only, explicitly "not
  an all-encompassing Grid System."**[^overlay] Framer's MasterGrid shows baseline+column
  toggles exists as prior art.[^overlay2] **Recommendation:** compose the columns overlay,
  add a thin **baseline-line + margin-line layer** (the prior skill's `.guides .rows`
  gradient, ported to a token-driven component), keep the `g` gesture.
- **Verification:** do **not** ship a bespoke Puppeteer harness. The prior skill's four
  checks (column adherence both-edges, overlay-matches-content, baseline modulo, optical
  ink-on-its-own-line) are sound — but they should run **through our existing `audit-ui` /
  `automate-browser` Playwright engine** as a new "grid-adherence" dimension, not a parallel
  Chrome driver. This is house-spec composition-by-reference (the platform-foreign Puppeteer
  flags in the JSON export are a liability we drop on the way in).

### 7. No-monoculture + composition

The skill must **probe the project first** (the `build-ui` pattern: `package.json`,
`tailwind.config.*` / `@import "tailwindcss"`, `components.json`) and branch:

| Project stack | Behavior |
|---|---|
| **Tailwind v4** | Inject `@theme` grid tokens + `@utility` bands/overlay; primary path. |
| **Tailwind v3** | Fall back to `theme.extend` + plugin (note the v4 upgrade benefit). |
| **Vanilla / CSS Modules / styled** | Degrade to the prior skill's `:root` variable scaffold — proven, framework-free. |
| **No CSS framework / consent declined** | Emit the scaffold to a file; never mutate the project's styling system. |

Composition (by reference, never import — house spec A8):
- **`design-md`** owns the token *spec* (`## Grid` section in DESIGN.md) → `use-grid-system`
  *consumes* it as the source of truth, rather than inventing tokens.
- **`build-ui`** *executes* the grid in the real codebase (this skill supplies the
  patterns/tokens; build-ui writes the components).
- **`frontend-design`** owns *taste* (when a strict grid is right vs. expressive).
- **`audit-ui`** *verifies* adherence (hosts the grid-adherence check + the overlay).
- **`source-ui`** supplies *reference* layouts (Mobbin/Refero) to ground a grid in precedent.

`use-grid-system` is therefore a **thin spine**: the canon + the Tailwind token/utility
layer + the overlay/optical module + verification glue. It does not duplicate execution,
taste, tokens, or the browser engine — it routes to the skills that own each.

---

## Validated against a working example

Drove a real browser (Playwright, 1440px) to a live Müller-Brockmann spread the user
supplied — *"Hokkaido — The Island Issue"*
([hyperagent.com/s/koRV0F0BWOD12os3U2L74w](https://hyperagent.com/s/koRV0F0BWOD12os3U2L74w))
— and toggled its grid overlay on. Observations that **corroborate the architecture**:

- **The overlay is exactly the proposed engineering.** Toggling on revealed **numbered
  translucent column fields (1…n) with red edge lines**, **red margin lines** bounding the
  content, and a **cyan baseline grid** (major line per leading-step, faint minor per
  baseline unit) running continuously through kicker, masthead, and lede — i.e. one source
  of truth driving columns + margins + baseline in the *same* content box.
- **Optical alignment is real and visible.** The huge "HOKKAIDO" masthead lands its **ink**
  (the H's left stem) precisely on the column-1 / left-margin line, while the body lede sits
  flush on the same line and each text line drops to a baseline — the canvas
  `actualBoundingBoxLeft` nudge (Finding 3) doing its job. **Box-on-grid *and* ink-on-grid**,
  confirmed empirically.
- **The toggle is `Show grid[G]`** — the `g`-key gesture converges with both the prior export
  and `tailwindcss-react-grid-overlay` (Finding 6). Standardize `use-grid-system` on it.
- **The artifact runs in a sandboxed `pub.hyperagent.com` iframe** (the top page is just a
  Next.js shell). This matches the export's documented "can't-auth/broken-image" trap and
  reinforces a design rule: **the overlay must be fully self-contained — reading only
  `@theme` CSS variables, making no external calls** — so it works identically in-iframe,
  in-app, and under headless verification.

Bottom line: the live reference is a clean proof that the column/baseline/optical-alignment
stack the proposal inherits *works as drawn* — the open work is the **Tailwind translation +
generalization to app UI**, not the core grid engineering.

---

## Proposed architecture for `use-grid-system`

**Dual-mode (spec A3):**
- **SCRIPTS** — `python3` present + scripts: a deterministic **token+scaffold generator**
  (the prior `grid_tokens.py`, refactored to emit *Tailwind `@theme` + `@utility`* by
  default, and *vanilla `:root`* under `--vanilla`).
- **NATIVE** — no python: emit the same scaffold by hand from `references/`.

**Step 0 — probe** (compose build-ui's probe): detect Tailwind v4/v3/none, React/Vue/none,
existing DESIGN.md `## Grid`, baseline of current `--spacing`.

**`references/` split (progressive disclosure, A1):**
- `references/canon.md` ← the ingested book's method + page locators (done).
- `references/tailwind.md` — the `@theme` token block, `@utility .band/.guides`, subgrid +
  `@supports` fallback, container-query profiles, the `--spacing` caveat.
- `references/profiles.md` — `editorial` vs `app` grid profiles (Finding 5).
- `references/optical-alignment.md` — the canvas `actualBoundingBoxLeft` module + the
  `text-box-trim` progressive-enhancement note + the font-measurement caveat.
- `references/verification.md` — the four checks, expressed as an `audit-ui` dimension.
- `references/non-tailwind.md` — the degraded vanilla-CSS scaffold.

**`scripts/`:**
- `grid_tokens.py` — emit `@theme`+`@utility` (default) or `:root` (`--vanilla`); flags
  `--cols/--baseline/--gutter/--margin/--maxw/--accent/--profile=editorial|app`; warn when
  gutter/margin aren't baseline multiples (carry the prior warning). JSON/stderr discipline.
- `probe.py` — stack detection (Tailwind version, framework, DESIGN.md grid) → JSON gate.
- *(no bespoke verifier)* — verification composes audit-ui/automate-browser.

**The overlay/optical module** — a small framework-agnostic JS (ported from the export):
columns + baseline + margin lines reading the `@theme` CSS variables, `g`-key toggle,
runtime optical alignment. Shipped as a copy-in dev component (compose
`tailwindcss-react-grid-overlay` where React is present).

**Naming:** `use-grid-system` is verb-ish/usable — consistent with the house verb-noun
convention; the canon stays branded internally as "Müller-Brockmann."

---

## Phased build plan

1. **Phase 0 — fold the canon.** Move `grid-system-summary.md` → `references/canon.md`;
   scaffold the skill with `/generate-skill --name=use-grid-system` (self-audits to spec).
2. **Phase 1 — Tailwind token layer.** `grid_tokens.py` emits the `@theme`+`@utility` block;
   `references/tailwind.md`. Verify on a throwaway Tailwind v4 app: subgrid bands + baseline
   spacing hold at 3 widths.
3. **Phase 2 — overlay + optical module.** Port `.guides` (add baseline layer) + the canvas
   alignment JS; wire the `g` toggle; compose the React overlay lib where present.
4. **Phase 3 — profiles + responsive.** `editorial` vs `app`; container-query component
   profiles; `clamp()` baseline-quantized type.
5. **Phase 4 — verification.** Add the grid-adherence dimension to `audit-ui` (or a documented
   automate-browser recipe); retire the Puppeteer dependency.
6. **Phase 5 — degrade + compose.** `references/non-tailwind.md` vanilla path; probe-gated
   routing to build-ui/design-md/frontend-design; `/audit-skill use-grid-system`.

---

## Risks & trade-offs

- **`--spacing` re-scaling a live project** (Finding 1 caveat) — biggest footgun. Mitigate:
  default to keeping 4px base + additive grid namespace; never silently re-scale.
- **`text-box-trim` not Baseline** — tempting to drop the JS too early; don't. Keep canvas
  measurement until `text-box-trim` reaches Baseline (re-evaluate then).[^textbox]
- **Optical alignment is font-specific & headless-fragile** — the export's hard-won lesson
  (−16px fallback vs −7px real Inter): verification must embed the real webfont or measure
  in-browser, else false readings. Carry this caveat verbatim.
- **App-profile dilution** — relaxing row-field occupancy risks "grid in name only." Keep the
  overlay + adherence check mandatory so the grid stays *measurable*, per the book's creed
  (summary p.174).
- **Subgrid fallback drift** — the `@supports` path must be tested at widths above and below
  `--grid-maxw` (the centered-container bug the export documents).
- **Composition seams** — design-md/build-ui/audit-ui boundaries must be sharp or the skill
  re-implements them. Enforce by reference-only (A8).

## Open questions

1. Does the user want `editorial` and `app` profiles in v1, or ship `app` first (their stated
   need: "all our web app/design projects")? *(scope decision)*
2. Should the grid token spec live in **DESIGN.md `## Grid`** (design-md owns it) or in the
   skill? Leaning design-md-owns, skill-consumes — confirm.
3. Is there a house **default column/baseline** (12 / 8px / 24px) to bake in, or per-project?
4. React-first overlay (compose the lib) vs framework-agnostic vanilla overlay as the
   primary — which is our modal project? *(probe data would settle this)*
5. `text-box-trim` Baseline ETA — set a revisit trigger to simplify the optical module.

---

## Sources

[^v4]: Tailwind CSS v4.0 announcement — CSS-first config. https://tailwindcss.com/blog/tailwindcss-v4
[^theme]: Theme variables / `@theme` directive (utility generation, namespaces, `inline`, CSS-var output). https://tailwindcss.com/docs/theme
[^spacing]: Tailwind v4 dynamic spacing — `calc(var(--spacing) * n)`, 0.25rem base. https://blog.logrocket.com/getting-ready-tailwind-v4/ · https://github.com/tailwindlabs/tailwindcss/discussions/16666
[^subgrid]: CSS Subgrid — Baseline Widely Available Mar 15 2026; support + `@supports` fallback. https://zenn.dev/tonkotsuboy_com/articles/css-subgrid-all-browsers?locale=en · https://caniuse.com/css-subgrid · https://web.dev/articles/css-subgrid
[^textbox]: `text-box-trim`/`text-box-edge` (renamed from `leading-trim`) — NOT Baseline as of Apr 2026. https://developer.mozilla.org/en-US/docs/Web/CSS/text-box-trim · https://caniuse.com/css-text-box-trim · https://css-tricks.com/leading-trim-the-future-of-digital-typesetting/
[^container]: Tailwind v4 native container queries (`@container`, `@md:`). https://www.sitepoint.com/tailwind-css-v4-container-queries-modern-layouts/ · https://github.com/tailwindlabs/tailwindcss-container-queries
[^8pt]: 8-point grid & vertical rhythm (line-height 24px = 3×8; "not easy" on web). https://medium.com/built-to-adapt/8-point-grid-vertical-rhythm-90d05ad95032 · https://plane.com/blog/implementing-baseline-rhythm-in-css
[^alistapart]: Setting type to a baseline grid — measure & shift per font/size. https://alistapart.com/article/settingtypeontheweb/
[^overlay]: `tailwindcss-react-grid-overlay` — `g`-key toggle, per-breakpoint columns, dev-only, "not an all-encompassing Grid System." https://github.com/SimeonGriggs/tailwindcss-react-grid-overlay
[^overlay2]: MasterGrid (Framer) — baseline/column/thirds/safe-area toggles (prior art). https://www.framer.com/marketplace/components/mastergrid/
[^dash]: Modular grids for dashboards; Material 12-col responsive layout grid. https://medium.com/@glorynwokocha99/mastering-dashboard-design-grid-systems-a-comprehensive-guide-f0b280cea56e · https://m2.material.io/design/layout/responsive-layout-grid.html
[^uxpin]: UI grids guide — modular row×column grids for data layouts. https://www.uxpin.com/studio/blog/ui-grids-how-to-guide/
