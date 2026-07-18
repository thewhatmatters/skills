# build-ui

**What it is:** the front door for building web UI in your project — a tiered production contract that briefs the work, builds it following the stack and conventions you already use, gates showcase work on an approved first frame, and verifies with screenshots before claiming done.

## What you get

- **A process sized to the ask.** A hover state goes straight to code. A page gets a one-minute brief. A landing hero gets a real interview, a committed brief file, and a hard checkpoint before the full build.
- Code that matches your existing project: Tailwind utilities (not random CSS), your shadcn config and `cn()` helper, your path aliases, your file naming.
- **The art-direction gate:** for showcase work you approve ONE rendered frame before the full experience is built — taste gets checked when changing course is cheap.
- Verification you can see: screenshots of the affected states/checkpoints across viewports, reduced-motion checks, console clean — not just "typecheck passed".
- Accessibility built in (semantic HTML, focus, contrast, reduced-motion) — not an afterthought.

## How to run

Say what you want built and where: "scaffold a settings page", "add a data table using our shadcn setup", "wire up this form" — or contract-level: "brief this screen before building", "ship this feature end-to-end", "build the landing hero sequence". Or invoke `/build-ui <ask>` directly. Useful flags: `--tier=micro|product|showcase` (override the classification), `--quick` (one-form brief instead of the interview), `--brief=PATH` (reuse a brief).

## What it needs

Nothing to set up — Python standard library only. It reads your project's `package.json` / `tailwind.config.*` / `components.json` / `tsconfig.json` to learn the stack. Pass `--project=PATH` if you're not in the project root. Browser verification uses `automate-browser` or `webapp-testing` when available.

## How it works (high level)

1. Walks up to find your project root and probes the stack (framework, styling, components, motion, path aliases).
2. Classifies the ask: **micro** (state/affordance) / **product** (page, form, table) / **showcase** (hero, landing sequence, scroll experience).
3. Briefs proportionally — showcase runs a `grilling`-style interview into `docs/briefs/<slug>.md`; the imagery-source question is asked first because it decides the quality ceiling.
4. Loads only the references the probe found relevant (Tailwind / shadcn / Next / vanilla-CSS / project DESIGN.md) plus always-on accessibility and JS/TS hygiene.
5. Showcase only: builds ONE representative frame and stops for your approval before the full build.
6. Implements following the conventions it found, then verifies per tier — up to full checkpoint QA (both scroll directions, two viewports, reduced motion, console, interaction integrity).

## Where it fits

- **`grilling`** — owns the one-question-at-a-time interview loop the showcase brief uses.
- **`frontend-design`** — taste/direction (bold, distinctive, anti-AI-slop). build-ui doesn't override its aesthetic judgement.
- **`add-motion`** — animation craft; executes motion inside this skill's contract on showcase work.
- **`source-ui`** — finds Mobbin/Refero precedent when the brief lacks visual reference.
- **`use-grid-system`** — grid discipline when a Müller-Brockmann grid is named.

## Where to look next

- `SKILL.md` — the operating contract Claude follows.
- `references/brief-template.md` — the showcase brief the interview fills.
- `handoff.md` — design decisions and the "why".
- `references/` — per-stack guidance, loaded only when your project actually uses each.
