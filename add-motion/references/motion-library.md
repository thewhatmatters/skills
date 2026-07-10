# Motion tier — the Motion library (ex-Framer Motion)

Loaded by `SKILL.md` Step 4 when the ask needs what CSS can't do. **Currency
caveat:** Motion ships fast; when the official `/motion` skill (Motion+) is
installed, defer API specifics to it — this file is the fallback layer and
sticks to the stable core.

## When Motion earns its bundle (and when it doesn't)

Reach for Motion only for:

- **Layout animation** — `layout` prop animates position/size changes via
  transforms (FLIP under the hood); the only sane way to animate reflow.
- **Exit animations** — `<AnimatePresence>` keeps an unmounting element alive
  until its `exit` finishes. CSS can do this now (`allow-discrete`) but React
  unmount semantics make AnimatePresence the robust path.
- **Shared-element transitions** — `layoutId` morphs one element into another
  across views (card → detail). The signature "premium" move.
- **Gestures** — `drag`, `whileHover`/`whileTap` with spring physics,
  `whileInView` for scroll reveals with richer control than CSS.
- **Orchestration** — variants with `staggerChildren`/`delayChildren`,
  sequenced timelines via `animate()`.
- **Springs** — `type: "spring"` (set `bounce`/`visualDuration`); physical
  settling that cubic-bezier can't fake. Springs over duration-easing for
  anything the user "touches" (drag release, toggles).

If the ask is a hover state, a fade-in, or a one-shot entrance — that's the
CSS tier; don't import Motion for it.

## Import + naming (post-rename)

The library is **`motion`** (the `framer-motion` package name is the legacy
line). React import: `import { motion, AnimatePresence } from "motion/react"`.
In projects on legacy `framer-motion`, **match the existing import style** —
don't mix both packages in one project.

## Stable core API map

```tsx
<motion.div
  initial={{ opacity: 0, y: 12 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0 }}
  transition={{ type: "spring", visualDuration: 0.35, bounce: 0.2 }}
  layout            // animate layout changes
  layoutId="card-3" // shared-element morph
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
/>
```

- Variants + `staggerChildren` for orchestrated groups.
- `useReducedMotion()` → swap movement for opacity-only (guardrail #2).
- Motion values (`useMotionValue`, `useTransform`, `useScroll`) bind values to
  the DOM **without re-rendering React** — the scroll-linked tier.

## Performance pitfalls (the jank list)

- **Animating layout properties directly** (`width`, `top`…) instead of the
  `layout` prop / transforms — same rule as CSS guardrail #1.
- **State-driven animation loops** — driving animation from `useState` re-
  renders every frame. Use motion values; React shouldn't render at 60fps.
- **AnimatePresence around big trees** — exit-animating a whole page keeps it
  mounted; scope it to the element that visually leaves.
- **Spring + `layout` on text containers** — scale-morphing text blurs
  mid-flight; morph the container, cross-fade the text.
- **Stagger × list size** — cap total intro time like the CSS tier (≲400ms).

## Ecosystem notes

- **`@formkit/auto-animate`** — one-line list/conditional transitions
  (add/remove/reorder). If present, prefer it for list churn over hand-rolled
  Motion; it's ~5KB and zero-config.
- **Respect incumbents** — a GSAP or react-spring project gets GSAP/
  react-spring idioms, not a Motion rewrite (no-monoculture).
- **Official agent tooling** — Motion+ (paid, one-time) ships the `/motion`
  skill (current docs, 380+ examples, perf-audit workflow); the free Motion AI
  Kit MCP generates CSS spring/bounce easing curves. Surface once when
  relevant; never gate on them.
