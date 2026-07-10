# CSS tier — animation craft + the universal guardrails

Loaded by `SKILL.md` Step 4 when the CSS tier is in play (and §Guardrails by
every tier at Step 6). CSS is the default tier: zero bundle cost, runs off the
main thread when compositor-only, and covers most "make it feel alive" asks.

## Guardrails (every tier — non-negotiable)

1. **Compositor-only properties.** Animate `transform` and `opacity`. Never
   `width`, `height`, `top`, `left`, `margin`, `padding`, `font-size` — each
   frame forces layout + paint. To "grow" something, `transform: scale()` or
   animate a clip; to "move" it, `translate`. `filter`/`backdrop-filter` and
   `clip-path` are paint-but-not-layout — acceptable sparingly, test on a
   low-end device.
2. **`prefers-reduced-motion` always.** Every animation ships a reduced path:

   ```css
   @media (prefers-reduced-motion: reduce) {
     .animated { animation: none; transition: none; }
   }
   ```

   Pattern to prefer: gate the *motion* (translate/scale), keep a plain opacity
   fade — full stillness is rarely required, vestibular-safe usually is.
   In React with Motion: `useReducedMotion()`.
3. **Duration discipline.** ~150–250ms for micro-interactions (hover, press,
   toggles), ~300–500ms for larger moves (panels, page elements). Past ~600ms
   UI feels sluggish; reserve it for hero/onboarding moments.
4. **Easing carries the premium feel.** `ease-out` for entrances (fast start,
   settle), `ease-in` for exits, `ease-in-out` for moves within the view.
   Never `linear` for spatial movement (only for marquees/spinners/progress).
   Defaults read as default — a custom curve like
   `cubic-bezier(0.22, 1, 0.36, 1)` (decisive start, soft landing) or the
   newer `linear()` spring approximations set the tone. Pick one or two curves
   and reuse them everywhere — consistency *is* the luxury signal.
5. **Don't block, don't surprise.** Never make the user wait on an animation to
   interact; entrances shouldn't replay on every re-render; nothing moves on
   first paint without intent.
6. **`will-change` is a measured fix,** not a sprinkle. Adding it everywhere
   costs memory and can hurt. Add only after observing jank, remove if it
   doesn't help.

## Transitions vs keyframes

- `transition` — state A→B tied to a class/pseudo-class change. Hover, press,
  open/close, theme switches. Your default.
- `@keyframes` — multi-step or autonomous motion (pulse, shimmer, attention
  nudge), entrances that play once on mount (`animation-fill-mode: both`).

## Entry/exit without JS (2026 baseline)

Two newer primitives cover what used to need a library:

- **`@starting-style`** — define the *from* state for an element entering the
  DOM (or going `display: none` → visible), so a plain `transition` animates
  the entrance.
- **`transition-behavior: allow-discrete`** — lets `display`/`overlay`
  participate in transitions, so exits can animate before the element leaves.

Both are baseline in evergreen browsers; if the project supports older
targets, fall back to a mounted class toggle. Verify support if the project's
browserslist looks conservative.

## Staggers

`animation-delay`/`transition-delay` stepped per item: inline
`style="--i: ${index}"` + `transition-delay: calc(var(--i) * 40ms)`.
30–60ms steps; cap total stagger ≲ 400ms regardless of list length
(`min(var(--i) * 40ms, 400ms)`) so long lists don't crawl.

## Scroll-driven animations

CSS `animation-timeline: scroll()` / `view()` runs scroll-linked effects off
the main thread — parallax, reveal-on-scroll, progress bars — with no observer
code. **Support caveat:** verify current browser coverage before relying on it
(it post-dated some engines); the fallback is an `IntersectionObserver` adding
a class (one-shot reveal), which is also the reduced-motion-friendlier shape.

## Tailwind notes

- Arbitrary keyframes/values work inline; define reusable animation tokens in
  the theme (`--animate-*` under `@theme` in v4) rather than repeating
  arbitrary strings.
- `transition` utility animates a sane property set; add `duration-*` and
  `ease-[cubic-bezier(...)]` explicitly — the defaults read as default.
- `motion-safe:`/`motion-reduce:` variants are the reduced-motion gate; use
  `motion-safe:animate-...` so the animation is opt-in by preference.
