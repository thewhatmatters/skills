---
name: scaffold-studio
description: >-
  Scaffold a web project with the Motion Cursor plugin (Motion+) and CSS Studio.
  Use when the user asks to bootstrap, set up, or include Motion, Motion+, CSS
  Studio, or cssstudio on a new or existing repo — "add CSS Studio and Motion
  to this project", "scaffold a Next app with motion and css studio", "install
  the Motion plugin and CSS Studio", "/scaffold-studio". Installs the local
  Motion plugin if missing, wires cssstudio as a dev-only client import, and
  runs npx cssstudio install. Does not create an app from scratch unless asked.
---

# scaffold-studio

Install **Motion** (machine-wide Cursor plugin + Motion+ MCP) and **CSS Studio**
(per-project, **dev-only**) so new web work can use `/motion` and `/studio`.

Leading words: **machine-wide**, **per-project**, **dev-only**.

## How to run

Say "add Motion and CSS Studio to this project", "scaffold studio tooling", or
`/scaffold-studio` from the target repo.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | run-report markdown path (default: `/tmp/scaffold-studio-report.md`) |
| `--project=PATH` | target repo (default: cwd) |
| `--motion-only` | skip CSS Studio |
| `--css-studio-only` | skip the Motion plugin |
| `--all` | both layers (default when no scope flag) |

`--motion-only` / `--css-studio-only` / `--all` / `--agent` satisfy spec A8.

## Step 0 — Mode probe

Try `python3 --version`. If python3 works, mode = **SCRIPTS**. Otherwise
**NATIVE** (run the same git/npm/file steps with the agent's Shell).

Then:

```bash
python3 ~/.cursor/skills/scaffold-studio/scripts/preflight.py --project=<path>
```

`down` → STOP and show the ⛔ check. `gated` → Step 1. `degraded` → proceed and
disclose. NATIVE: check `git`, `npm` (if CSS Studio is in scope), and that
`~/.cursor/plugins/local` is writable.

Hard deps (A15a): none. Session-only MCP is **not** required for install.

## Step 1 — Setup gates (A7)

| Gate | Trigger | Interactive | `--agent` |
|------|---------|-------------|-----------|
| `GIT_MISSING` | `git` not on PATH | *Install Git / I'll do it / Skip Motion* | skip Motion, disclose |
| `NPM_MISSING` | `npm` missing and CSS Studio in scope | *Install Node / I'll do it / Skip CSS Studio* | skip CSS Studio, disclose |
| `PLUGIN_DIR_UNWRITABLE` | cannot create `~/.cursor/plugins/local` | *Fix perms / I'll do it / Skip Motion* | skip Motion, disclose |
| `PROJECT_MISSING` | `--project` path does not exist | *Pick another path / I'll do it / Cancel CSS Studio* | skip CSS Studio, disclose |

Graceful dead-end: skip that layer; never block the other.

## Step 2 — Scope

Default **both**. Honor `--motion-only` / `--css-studio-only`. Interactive (not
`--agent`): confirm if the cwd is not a JS/TS app and CSS Studio is in scope.

Do **not** `create-next-app` unless the user asked for a new app.

## Step 3 — Motion plugin (machine-wide)

If Motion is in scope, run:

```bash
python3 ~/.cursor/skills/scaffold-studio/scripts/install_motion_plugin.py
```

NATIVE: follow [`references/motion-plugin.md`](references/motion-plugin.md).

Idempotent: if `plugin.json` already `"name": "motion"`, skip the clone.
**Do not** edit `~/.cursor/mcp.json` (the plugin ships Motion and Motion+ MCP).
**Do not** touch other entries under `~/.cursor/plugins/local`.

Motion+ extras (audits, example source) need a Motion+ account; sign-in is
Cursor-prompted later — this skill does not paste tokens.

After a **new** plugin copy, tell the user to **fully restart Cursor** and
enable **Motion** under Settings → Plugins.

## Step 4 — CSS Studio (per-project, dev-only)

If CSS Studio is in scope:

1. Detect ESM vs script-tag using [`references/css-studio-entry.md`](references/css-studio-entry.md). Unsure → ask once (`--agent`: ESM + `package.json` if present, else stop CSS Studio and disclose).
2. `npm install -D cssstudio` (or yarn/pnpm equivalent). Never a production dependency.
3. Wire `startStudio()` **dev-only** per that recipe (Next client + `NODE_ENV`, Vite `import.meta.env.DEV`, or localhost script tag). Never ship the GUI.
4. `mkdir -p .cursor` then `npx cssstudio install` from the project root so the Cursor skill lands.
5. Add a `cssstudio` module declaration if TypeScript complains (recipe has the stub).

Do not rewrite unrelated product UI.

## Step 5 — Report

Pipe a JSON object (`date`, `project`, `motion`, `cssStudio`, `notes`) into:

```bash
python3 ~/.cursor/skills/scaffold-studio/scripts/report.py --out=<path>
```

NATIVE: write the same markdown yourself.

Tell the user:

1. Restart Cursor if the Motion plugin was newly copied; enable it in Plugins.
2. **Restart the agent**, then run **`/studio`** to edit CSS.

## Conventions this skill follows

- Spec is `~/.cursor/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- **`WHY.md`:** read before changing this skill's design. After a run that locks a non-obvious choice (went unusually well or badly, reason not already in SKILL.md), append a dated line. Skip routine runs. Cross-project lessons go to `/curate-vault`.
