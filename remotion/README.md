# remotion

**What it is:** Make real videos programmatically with Remotion — author React motion-graphics from a script, preview them in Studio, and render them to MP4.

## What you get

- An end-to-end path from a script/idea to rendered video scenes: probe/scaffold → script-to-scenes → preview → render to an `out/` folder.
- Deterministic-render guardrails enforced for you (the rules that make Remotion renders not flicker).
- Clean deferral to Remotion's official `remotion-best-practices` skill for all API detail — so the knowledge stays current instead of going stale here.

## How to run

Say something like "make a Remotion video from this script", "animate this in Remotion", "render my composition to MP4 at 1080p", or "set up Remotion here" — or invoke `/remotion <ask>` directly.

## What it needs

- **Node 18+** for previewing (Studio) and rendering. You can author components without it; you can't render without it.
- Recommended: Remotion's official skill, `npx skills add remotion-dev/skills`. If it's missing, this skill surfaces the install command and falls back to general knowledge with a "may be out of date" caveat.
- No API keys, no network for the skill's own scripts (they read the filesystem only).

## How it works (high level)

1. **Probe** the project — is this a Remotion project? Is Node here? Is the official skill installed?
2. **Route** — defer Remotion API questions to the official skill (or surface its install command).
3. **Scaffold or locate** — make a new Remotion project, or work in the existing one. It won't add Remotion to a project that doesn't use it without asking.
4. **Script → scenes → render** — draft scenes from the script, preview them, render to MP4, with the determinism guardrails always enforced.
5. **Optional** — transparency/green-screen, image insertion, audio/voiceover, cloud render.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/compose.md` — how it coordinates with the official Remotion skill (+ no-monoculture).
- `references/guardrails.md` — core concepts + the non-negotiable deterministic-render rules.
- `references/workflow.md` — the script → scenes → render → composite pipeline.
- `references/render-and-export.md` — CLI + `@remotion/renderer` rendering.
