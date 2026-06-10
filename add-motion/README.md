# add-motion

**What it is:** Adds motion to web UI as a deliberate craft — premium-feeling animation without jank.

## What you get

- Animation implemented directly in your project (CSS, the Motion library, or the View Transitions API — whichever lightest tier fits), following your existing stack.
- Performance guardrails applied on every change: compositor-only properties, `prefers-reduced-motion` support, disciplined durations and easing.
- An honest report of which tier was used, why, and any limitation (e.g. when the right tool would need a library your project doesn't have).

## How to run

Say things like "animate this card grid", "add a page transition", "stagger these list items", "make this modal feel smoother", "fix the animation jank" — or invoke `/add-motion <ask>` directly.

```
/add-motion stagger the dashboard cards on first load
```

## What it needs

Nothing — no keys, no network. Python 3 makes the project probe automatic; without it the skill probes by hand. If you own [Motion+](https://motion.dev/plus), its official `/motion` skill is detected and deferred to for current Motion API detail; without it the skill uses its bundled references and tells you when something may post-date its knowledge.

## How it works (high level)

1. Probes your project: which animation libraries exist (Motion, framer-motion, auto-animate, GSAP…), Tailwind, framework.
2. Picks the lightest tier that does the job — CSS first, Motion for layout/gesture/shared-element work, View Transitions for route changes.
3. Never adds an animation library without asking — if the ideal tool is missing, it says what CSS can and can't do and lets you decide.
4. Implements with the guardrails (transform/opacity only, reduced-motion always, tight durations), then verifies the reduced-motion path exists.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/` — per-tier craft: `css-animations.md`, `motion-library.md`, `view-transitions.md`.
