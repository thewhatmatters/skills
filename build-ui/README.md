# build-ui

**What it is:** implements UI in your project — following the stack and conventions you already use, not whatever the model would invent from scratch.

## What you get

- Code that matches your existing project: Tailwind utilities (not random CSS), your shadcn config and `cn()` helper, your path aliases, your file naming.
- A short plan up front — what files will change and which convention is being matched — before any code is written.
- Accessibility built in (semantic HTML, focus, contrast, reduced-motion) — not an afterthought.

## How to run

Say what you want built and where: "scaffold a settings page", "add a data table using our shadcn setup", "implement this section following our Tailwind config", "wire up this form". Or invoke `/build-ui <ask>` directly.

## What it needs

Nothing to set up — Python standard library only. It reads your project's `package.json` / `tailwind.config.*` / `components.json` / `tsconfig.json` to learn the stack. Pass `--project=PATH` if you're not in the project root.

## How it works (high level)

1. Walks up to find your project root.
2. Reads `package.json` + a few configs to detect the stack (framework, styling, components, motion, path aliases).
3. Loads only the references that match (Tailwind / shadcn / vanilla-CSS / a11y) — nothing irrelevant.
4. Plans briefly, then writes the code following the conventions it found.
5. Runs typecheck if applicable, and points at `automate-browser` or `webapp-testing` for browser verification.

## Where it fits

- **`frontend-design`** (the example skill) — *taste/direction* (bold, distinctive, anti-AI-slop). build-ui doesn't override its aesthetic judgement; if you want a striking look, that skill drives.
- **`add-motion`** — animation craft as its own thing (planned).
- **`source-ui`** — finds Mobbin/Refero precedent if you need visual reference before building.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/` — per-stack guidance (Tailwind / shadcn / vanilla-CSS / a11y), loaded only when your project actually uses each.
