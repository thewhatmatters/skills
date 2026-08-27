# scaffold-studio

**What it is:** A Cursor skill that puts Motion (the Cursor plugin, including Motion+ MCP) on this machine and CSS Studio into the current web project, without shipping the editor to production.

## What you get

- The Motion plugin under `~/.cursor/plugins/local/motion` if it is not already there (available in every local repo after a Cursor restart).
- CSS Studio as a **dev-only** app dependency, wired at the app entry, plus the `/studio` skill and project MCP from `npx cssstudio install`.
- A short markdown run report (default `/tmp/scaffold-studio-report.md`).

## How to run

In the target repo, ask: "add Motion and CSS Studio" or invoke `/scaffold-studio`.

Example: `/scaffold-studio --css-studio-only` on an existing Next app.

## What it needs

- Git (to clone the Motion plugin).
- Node/npm (for CSS Studio).
- A web app with an entry point (Next `layout`, Vite `main`, or `index.html`). This skill does not create an app unless you ask for that separately.
- After a first-time Motion install: fully quit and reopen Cursor, then enable **Motion** in Settings → Plugins.
- After CSS Studio: restart the agent, then `/studio`. Motion+ audits need a Motion+ login when Cursor prompts.

## How it works (high level)

1. Checks git, npm, and that Cursor's local plugin folder is writable.
2. Copies the Motion plugin from GitHub into Cursor's local plugins directory (skips if already named `motion`).
3. Detects how the app loads JS, installs `cssstudio` as a dev dependency, and starts it only in development.
4. Runs the CSS Studio installer for the skill + MCP.
5. Writes a report and tells you what to restart.

## Where to look next

- `SKILL.md` — operating instructions the agent follows.
- `WHY.md` — design decisions and the "why".
- `references/` — Motion clone steps and per-framework CSS Studio wiring.
