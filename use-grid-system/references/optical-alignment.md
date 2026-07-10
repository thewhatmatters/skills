# Optical alignment — put display INK on the line, not its box

**Box-on-grid ≠ ink-on-grid.** A 180px headline whose layout box is exactly on
column line 1 still *looks* indented vs body text, because the letterform's ink is
inset by its **left side-bearing**. The cure is a runtime nudge measuring the
actually-loaded font. (Canon: the headline whose box was on the grid but whose ink
wasn't — see the live "HOKKAIDO" example in the research report, where the H's ink
lands on the margin line once aligned.)

## Why not just use `text-box-trim`?
`text-box-trim` / `text-box-edge` (renamed from `leading-trim`) trims the
half-leading so text boxes sit true on the grid — but it is **NOT Baseline as of
Apr 2026**; it fails in widely used browsers. So:
- **Vertical** rhythm → tokens (`--spacing` + `--leading-*`) handle it cross-browser.
- **Horizontal** optical alignment of display type → the canvas JS below is the
  only cross-browser-correct path today.
- Add `text-box-trim` as **progressive enhancement** only:
  ```css
  @supports (text-box-trim: trim-both) {
    .display { text-box-trim: trim-both; text-box-edge: cap alphabetic; }
  }
  ```
  It *reduces* but does not replace the JS nudge. Re-evaluate when it reaches
  Baseline.

## The module (framework-agnostic; runs after fonts load + on resize)
```js
/* Nudge each display element so its visible INK-left lands on its column line.
   Measures the ACTUALLY-LOADED font via canvas, so it's correct in the user's
   browser. Point `sel` at your display elements only (mastheads, big numerals,
   section headlines) — never body/label text. */
(function () {
  var cvs = document.createElement('canvas'), ctx = cvs.getContext('2d');
  var sel = '.masthead, .numeral, .display, .page-title';   /* <-- your selectors */
  function align() {
    document.querySelectorAll(sel).forEach(function (el) {
      el.style.marginLeft = '0px';
      var cs = getComputedStyle(el), ch = (el.textContent || '').trim().charAt(0);
      if (!ch) return;
      if (cs.textTransform === 'uppercase') ch = ch.toUpperCase();
      ctx.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
      ctx.textAlign = 'left';
      var abl = ctx.measureText(ch).actualBoundingBoxLeft; /* +ve = ink overhangs left */
      if (isFinite(abl)) el.style.marginLeft = abl.toFixed(2) + 'px'; /* ink -> on the line */
    });
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(align);
  align();
  var t; window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(align, 120); });
})();
```
In React, run this in a `useEffect` keyed on the text + a `ResizeObserver`, or use
the `tailwindcss-react-grid-overlay` package for the column overlay and keep this
module separate (it does columns only, not optics).

## CRITICAL caveat — side-bearing is font-specific
Measure with the wrong font and you get the wrong nudge. We measured **−16px on a
fallback grotesque vs −7px on real Inter** for the same `H`. Implications:
- Production is correct because the JS measures the *loaded* webfont.
- **Offline/headless verification must embed the real webfont** (`@font-face`,
  local TTF) or it will report false ink offsets — headless Chrome usually lacks
  the webfont and silently falls back. See `verification.md`.
- Same trap if you ever rasterize art: a `Helvetica`/`Arial` CSS stack can fall
  back to Noto/Calibri-like faces. Wrong font in → wrong result out.

## What to apply it to
- **editorial profile:** mastheads, big numerals, section headlines, pull quotes.
- **app profile:** page titles and large metric numbers only — NOT body, labels,
  table cells, or buttons (their boxes are fine; nudging them is noise).
