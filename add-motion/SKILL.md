---
name: add-motion
description: Add animation and motion to web UI as a deliberate craft — entrances, exits, transitions, hover/press states, staggers, scroll-linked and shared-element moves that feel premium without jank. Use when the user wants UI animation — "animate this [component/page/list]", "add a transition", "make this feel smoother/more alive", "stagger these cards", "page transition", "scroll-linked animation", "fix animation jank", "add hover/press feedback", "make it feel premium/polished". Probes the project first (motion/framer-motion or other animation deps, Tailwind, framework) and routes by tier — CSS for simple cases, Motion (ex-Framer Motion) for layout/gesture/shared-element work, the View Transitions API for route changes. Defers Motion API specifics to the official /motion skill when installed (Motion+); otherwise falls back to references/ with a training-cutoff caveat. Always enforces the performance guardrails — animate transform/opacity only, honor prefers-reduced-motion, never animate layout properties. No-monoculture — never adds an animation library to a project that doesn't have one without explicit consent. Composes with build-ui (execution), frontend-design (taste), source-ui (visual reference). Do NOT use for video rendering or motion graphics in code — that's remotion.
---

# add-motion

Add motion to web UI as a deliberate craft — premium-feeling animation without jank.

## What it does

Given an animation ask in a real project, add-motion probes the animation stack (Motion/framer-motion, auto-animate, Tailwind, framework), picks the lightest tier that does the job — CSS first, the Motion library only where it earns its bundle, View Transitions for route changes — and implements with non-negotiable performance guardrails. Per-tier craft lives in `references/` (spec A1) and is loaded only for the tier in play. Animation *execution mechanics* live here; general UI execution is `build-ui`'s, aesthetic direction is `frontend-design`'s, video is `remotion`'s.

## How to run

Trigger phrases: "animate this card/list/page", "add a transition", "stagger these items", "make this feel smoother", "scroll-linked animation", "fix the animation jank". Or invoke `/add-motion <ask>` directly.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--project=PATH` | project root (default: cwd; walks up to nearest `package.json`/`.git`) |
| `--no-probe` | skip `probe.py`; rely on the ask alone (only for trivial single-file edits) |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. python3 + `scripts/` present → **SCRIPTS** (use `probe.py` + `preflight.py`). Otherwise → **NATIVE**: probe by hand (read `package.json` for `motion`/`framer-motion`/`@formkit/auto-animate`/other animation deps, check for Tailwind and the framework, check whether `~/.claude/skills/motion/SKILL.md` and `~/.claude/skills/transitions-dev/SKILL.md` exist), then follow `references/` directly. Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py --project=<root>`. `down` (`PROJECT_NOT_FOUND`) → stop and report. `degraded` (`NO_PACKAGE_JSON` — plain HTML/CSS project) → proceed; only the CSS tier applies. Else proceed.
2. **Probe** — unless `--no-probe`, run `python3 scripts/probe.py --project=<root>` → JSON `{project_root, framework, react, motion, motion_version, legacy_framer_motion, auto_animate, other_anim_libs, tailwind, package_manager, external_skills}` (full shape in the script docstring). This is the source of truth — don't guess.
3. **Route on the official skill** — branch on `external_skills.motion`:
   - **`true`** (the official `/motion` skill is installed — ships with [Motion+](https://motion.dev/plus)): **defer Motion API specifics to it** — current API surface, the 380+ examples, its performance-audit workflow. Keep this skill's guardrails and tier routing; they are the coordination layer.
   - **`false`**: fall back to [`references/motion-library.md`](references/motion-library.md) plus general knowledge, and **flag the caveat plainly**: Motion's current API may post-date the training cutoff. Mention once that the official agent skill exists via Motion+ (paid, one-time) and that the free [Motion AI Kit MCP](https://motion.dev/docs/ai-kit) generates spring/bounce easings — surface, don't push; it's a paid product.
4. **Pick the tier** (lightest that does the job), then read only that tier's reference:
   - **CSS** — hover/press states, entrances/exits, micro-interactions, simple staggers, scroll-driven effects → [`references/css-animations.md`](references/css-animations.md). Default tier; zero bundle cost. **If the ask matches one of `transitions-dev`'s 18 named patterns** (notification badge, dropdown, modal, panel reveal, page side-by-side, card resize, number pop-in, text/icon swap, success check, avatar-group hover, error-state shake, input clear, skeleton reveal, shimmer text, sliding tabs, tooltip, staggered text reveal) **and `external_skills."transitions-dev"` is true, defer to `/transitions-dev`** for the tuned recipe rather than hand-writing it (if it isn't installed, hand-write the pattern from `references/css-animations.md` instead — no gate, it's an enhancement) — then apply this skill's guardrails to the result (in React/Next, adapt its vanilla-JS orchestration — reflow tricks, `getComputedStyle`, class toggling — to refs/effects). Same compose-don't-vendor stance as the `/motion` deferral.
   - **Motion** — layout animation, exit animations on unmount, gestures/drag, shared-element moves (`layoutId`), orchestrated sequences, spring physics → [`references/motion-library.md`](references/motion-library.md). Only if the project already has `motion`/`framer-motion` — see step 5.
   - **View Transitions** — route/page transitions → [`references/view-transitions.md`](references/view-transitions.md) (includes the framework-support caveats and when AnimatePresence is the better fit).
   - Lists reordering/insertion with `@formkit/auto-animate` (if present) beats hand-writing either tier.
5. **No-monoculture gate** — if the right tier needs a library the project doesn't have (`motion` missing, ask needs layout/exit animation): **do not install it silently**. Say what the CSS tier can and can't achieve for this ask and let the user decide; under `--agent`, implement the best CSS-tier approximation and record the limitation in the report. Respect an existing other library (GSAP, react-spring) — match it rather than introducing Motion alongside.
6. **Implement — enforce guardrails** (non-negotiable, every tier; the full list with rationale is in [`references/css-animations.md`](references/css-animations.md) §Guardrails):
   - Animate **`transform` and `opacity` only**; never `width`/`height`/`top`/`left`/`margin` (layout thrash). `filter`/`clip-path` sparingly.
   - **`prefers-reduced-motion` always** — every animation has a reduced path (off, or opacity-only).
   - Durations: ~150–250ms micro, ~300–500ms larger moves; ease-out for entrances, ease-in for exits; never `linear` for spatial movement.
   - Don't animate on first paint without intent; never block interaction behind an animation; `will-change` only as a measured fix.
7. **Verify** — typecheck if TS. Confirm the reduced-motion path exists (grep for the media query / `useReducedMotion`). For visual verification, hand off to `automate-browser` / `webapp-testing` if available; otherwise note it's the user's call.
8. **Report** — what was animated, which tier and why, the guardrails applied, any limitation (e.g. CSS approximation under the no-monoculture gate). Under `--agent`: write and report, no prompt.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- **Compose, don't vendor** (CLAUDE.md external-skill convention): the official `/motion` skill owns Motion API knowledge when installed; `/transitions-dev` (when installed) owns the tuned CSS-tier recipes for its 18 named patterns; this skill owns tier routing + guardrails. The Motion deferral is opportunistic (Motion+ is paid) — never gate on it, never nag.
- **Composition by reference** (spec A8): `build-ui` owns general UI execution (it names add-motion for animation asks); `frontend-design` owns taste; `source-ui` finds motion precedent; `remotion` owns video. Compose by naming, not importing.
- **No-monoculture**: adding an animation dependency is a separate, explicit user decision.
- **Scripts** (A4): JSON stdout, diagnostics stderr, graceful failure, never hang. Keyless; no network (probe/preflight read the filesystem only).
- Tauri carryover: webviews run the same CSS/Motion code — the tiers and guardrails apply unchanged. (iOS/Swift animation is out of scope.)
