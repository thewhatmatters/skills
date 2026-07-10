---
name: remotion
description: Make real videos programmatically with Remotion (remotion.dev) — author React-based motion graphics from a script, preview them in Studio, and render them to MP4. Use when the user wants to create, generate, animate, or render a video/motion-graphics with Remotion, or turn a script/text into video scenes in code — "make a Remotion video", "animate this with Remotion", "turn this script into video scenes", "render this composition to MP4", "build motion graphics in React", "create an intro/explainer/promo video in code", "add a scene to my Remotion project", "export my Remotion video at 1080p/4K", "set up Remotion in this project". Orchestrates the end-to-end workflow — probe/scaffold → script-to-scenes → preview → render/export → optional transparency, image insertion, audio, cloud render. Composes with (and defers Remotion API knowledge to) Remotion's official `remotion-best-practices` skill when installed; surfaces the install command and falls back to general knowledge otherwise. Enforces deterministic-render guardrails (no Math.random/Date.now, useCurrentFrame-driven, no CSS/Tailwind animations). Honors a no-monoculture rule — won't impose Remotion on a non-Remotion project without consent.
---

# remotion

Make real videos programmatically with Remotion — author React motion-graphics from a script, preview in Studio, and render to MP4.

## What it does

Given a request to make a video, `remotion` runs the **workflow** the framework is built for: it probes for a Remotion project + Node, scaffolds one if asked, turns a script into scenes/compositions, previews them in Studio or the Player, and renders/exports to an `out/` folder — then optionally handles transparency/green-screen, image insertion, audio, and cloud render. It owns the **workflow**, not Remotion's API: domain knowledge (animation, timing, audio, captions, 3d, transitions, …) is **deferred to Remotion's official `remotion-best-practices` skill** when installed, and falls back to a thin local reference + general knowledge (with a training-cutoff caveat) otherwise. Bulky detail lives in `references/` (spec A1) and is loaded only when the step needs it.

## How to run

Trigger phrases: "make a Remotion video", "turn this script into video scenes", "animate this in Remotion", "render my composition to MP4", "export at 4K", "set up Remotion here", "add a scene". Or invoke `/remotion <ask>` directly.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--project=PATH` | project root (default: cwd; walks up to nearest `package.json`/`.git`) |
| `--out=PATH` | render output dir (default: `<project>/out`) |
| `--no-probe` | skip `probe.py`; rely on the ask alone (only for trivial single-file edits) |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. python3 + `scripts/` present → **SCRIPTS** (use `probe.py` + `preflight.py`). Otherwise → **NATIVE**: do the probe by hand (read `package.json` for a `remotion` dep, look for `remotion.config.ts`, `src/Root.tsx`/`src/index.ts`, check `node`/`npx`, and whether `~/.claude/skills/remotion-best-practices/SKILL.md` exists), then follow `references/` directly. Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py --project=<root>`. `down` → stop and report. `gated` (`NODE_MISSING`) → you can still author code; surface that rendering/Studio need Node and offer the install path; under `--agent` proceed in author-only mode. Else proceed.
2. **Probe** — unless `--no-probe`, run `python3 scripts/probe.py --project=<root>` → JSON `{project_root, is_remotion, remotion_version, has_config, root_file, node, npx, package_manager, tailwind, external_skills}` (full shape in the script docstring). This is the source of truth — don't guess.
3. **Route on the official skill** — branch on `external_skills["remotion-best-practices"]`:
   - **`true`** (installed at `~/.claude/skills/remotion-best-practices`): **defer all Remotion API/domain knowledge to it** — animation, timing, sequencing, transitions, audio, audio-visualization, captions, 3d, gifs, fonts, lottie, maps, voiceover, Zod parameters, etc. Read [`references/compose.md`](references/compose.md) for the coordination layer (routing table + what `remotion` still owns). Do **not** re-derive what that skill knows.
   - **`false`** (not installed — fresh machine): degraded path. Surface the install command before doing the work: `npx skills add remotion-dev/skills` (open-source at `remotion-dev/remotion/packages/skills`; agent variant `npx -y skills@latest add remotion-dev/skills -g -y`). Until installed, fall back to general knowledge for the task and **flag the caveat plainly**: Remotion's current API/components and best-practice rules may post-date the training cutoff. Still read [`references/guardrails.md`](references/guardrails.md) — the determinism rules and core concepts there are load-bearing and stable.
4. **Decide project state (no-monoculture)** — from the probe:
   - `is_remotion == true` → work in place.
   - empty dir / greenfield → scaffold with `npx create-video@latest --yes --blank my-video` (offer "Hello World" or a template if the user wants a starting point); see [`references/workflow.md`](references/workflow.md).
   - **a JS/TS project that is *not* Remotion** → **do not add Remotion silently.** Adding a dependency is a separate, explicit user decision (spec: no-monoculture). Ask first; under `--agent`, state the assumption and stop short of mutating `package.json` unless the ask clearly authorizes it.
5. **Script → scenes** — read the user's script/text and draft scenes/compositions (one `<Composition>` per scene or a `<Series>`/`<Sequence>` timeline). Translate the *meaning* of the script into visuals, not verbatim text. See [`references/workflow.md`](references/workflow.md).
6. **Build scenes — enforce guardrails** — write components deferring animation/timing patterns to the official skill, but **always enforce** the determinism rules in [`references/guardrails.md`](references/guardrails.md): all animation driven by `useCurrentFrame()`; **no `Math.random()`** (use `random(seed)` from `remotion`); **no `Date.now()`/wall-clock**; **CSS transitions/animations and Tailwind animation classes are FORBIDDEN** (they flicker); prefer `<OffthreadVideo>` over `<Video>` in renders; assets in `public/` via `staticFile()`; true randomness/async only in `calculateMetadata()`. These are non-negotiable regardless of which skill writes the animation.
7. **Preview** — start Studio with `npm run dev` / `npx remotion studio`, or embed the Player (`@remotion/player`, no server needed) for runtime playback. See [`references/guardrails.md`](references/guardrails.md) for the four composition props and the Player shape.
8. **Render / export** — read [`references/render-and-export.md`](references/render-and-export.md). CLI: `npx remotion render <id> <out/file.mp4>` with `--props`/`--codec`/`--frames`/`--scale`; or programmatic `@remotion/renderer` (`bundle()` → `selectComposition()` → `renderMedia()`). Write to `--out` (default `<project>/out`), 1080p or 4K. Never overwrite an existing render without saying so.
9. **Optional advanced** — transparency/green-screen, image insertion from a `public/` (or `PNGs/`) folder, audio/voiceover, and Remotion **Lambda** cloud render are documented in [`references/workflow.md`](references/workflow.md) and (for API specifics) the official skill. Note Lambda has its own cost/licensing.
10. **Report** — what you built/changed, which skill supplied the API patterns, the render output path, and any guardrail you had to enforce. Under `--agent`: write and report, no prompt.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- **Compose, don't vendor** (CLAUDE.md 5-step external-skill convention; spec A3/A7/A8): defer Remotion API knowledge to `remotion-best-practices`; probe-gate it; keep local references thin so they don't drift each release. `remotion` owns the *workflow*; the official skill owns the *API*.
- **No-monoculture**: never introduce Remotion into a project that doesn't use it without explicit consent.
- **Determinism guardrails are non-negotiable** — they're cheap, stable, and exactly what agents get wrong (spec A12 honesty).
- **Scripts** (A4): JSON to stdout, diagnostics to stderr, graceful failure, never hang. Keyless; no network (probe/preflight read the filesystem only).
- **Licensing honesty**: Remotion is free for individuals, ≤3-employee for-profits, and non-profits; larger companies need a paid company license via remotion.pro. Surface this; don't assert prices.
- The video's third-party "anti-gravity" token-efficiency skill is **not** a Remotion product — mention it only as an optional external add-on, never bake it in.
