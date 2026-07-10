# View Transitions tier — route and page transitions

Loaded by `SKILL.md` Step 4 for route-change / page-level transition asks.

## What it is

The View Transitions API snapshots old DOM, swaps state, then animates between
snapshots — the browser-native way to do page/route transitions and
cross-view morphs without keeping both views mounted.

- **Same-document** (SPA): `document.startViewTransition(() => updateDOM())`.
  Customize via `::view-transition-old(root)` / `::view-transition-new(root)`
  keyframes; give an element `view-transition-name: hero` to morph it across
  the change (the CSS-native `layoutId`).
- **Cross-document** (MPA): opt in with `@view-transition { navigation: auto; }`
  on both pages — full page transitions with zero JS.

## Framework reality check (verify, don't assume)

- **Next.js App Router**: support has been experimental/in-flux — check the
  project's Next version and current docs before promising it; the
  `next-best-practices` skill (if installed) knows the current state. The
  robust fallback for App Router is Motion's `AnimatePresence` around route
  content or template-level CSS entrances.
- **React SPA**: `flushSync` inside `startViewTransition` is the integration
  point; React's experimental `<ViewTransition>` component may exist in the
  project's React version — match what's there.
- **Plain/MPA/Astro-style sites**: cross-document VT is the lightest-weight
  premium move available — prefer it.

## Choosing VT vs Motion for transitions

| Ask | Pick |
|---|---|
| Full-page route transition, MPA or VT-supported framework | View Transitions |
| Shared-element morph across a route change | VT `view-transition-name` (if routing supports it), else Motion `layoutId` |
| Exit animation on a component (not a route) | Motion `AnimatePresence` (or CSS `allow-discrete`) |
| Route transitions in a framework where VT is shaky | Motion / CSS entrances |

## Guardrails applied here

- Reduced motion: wrap the VT trigger —
  `matchMedia('(prefers-reduced-motion: reduce)')` → skip
  `startViewTransition`, just update; or set the transition CSS to a fade.
- Keep route transitions **fast** (200–350ms): users navigate constantly; a
  slow page wipe gets old by the third click.
- Don't name dozens of elements (`view-transition-name` must be unique per
  view; each named element costs a snapshot layer). One hero morph + a root
  cross-fade is usually the whole premium effect.
- Feature-detect: `if (!document.startViewTransition) { update(); return; }` —
  the no-VT path must be a clean instant swap, never an error.
