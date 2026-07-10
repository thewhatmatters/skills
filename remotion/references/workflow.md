# workflow — script → scenes → render → composite

The end-to-end pipeline this skill orchestrates, distilled from Remotion's docs and
the tutorial workflow that seeded the skill. The *API* for each step lives in the
official `remotion-best-practices` skill (see [`compose.md`](compose.md)); this is the
*spine* that connects them.

## 1. Locate or scaffold the project

- **Existing Remotion project** (`probe.is_remotion == true`): work in place. Use
  `probe.root_file` and `probe.package_manager`.
- **Greenfield / empty dir**: scaffold.
  ```bash
  npx create-video@latest                          # interactive wizard
  npx create-video@latest --yes --blank my-video   # all defaults, blank template
  ```
  Wizard prompts: **template** (Hello World is a good beginner base; Blank; React
  Three Fiber/3D; others), **TailwindCSS** (yes/no), **Agent Skills** (say **yes** —
  installs `remotion-best-practices`). Min toolchain: **Node 18+** (docs floor Node
  16 / Bun 1.0.3). Start Studio with `npm run dev`.
- **Existing *non-Remotion* JS app**: STOP — see the no-monoculture rule in
  [`compose.md`](compose.md). Get consent before adding Remotion.

## 2. Script → scenes

Read the user's script/text and **draft scenes** — one `<Composition>` per scene, or
a single timeline using `<Series>` / `<Sequence>`. Translate the **meaning** of each
script line into a visual, not the literal words. Sketch the scene list first
(beat → visual idea → rough duration), confirm with the user, then build. Setting a
**creative direction** up front (a one-line style brief, e.g. "editorial
investigation: The New Yorker meets a forensic autopsy") keeps a batch of scenes
coherent; re-state/lock a new direction when you intentionally change styles.

## 3. Build scenes

Write each scene as a React component under `src/`. Defer animation/timing/transition
**patterns** to the official skill, but **always enforce** the determinism guardrails
in [`guardrails.md`](guardrails.md). Register each in `src/Root.tsx` with its four
props (`durationInFrames`, `fps`, `width`, `height`) + `defaultProps`.

## 4. Preview

- **Studio**: `npm run dev` or `npx remotion studio` — scrub, inspect, edit props live.
- **Player** (`@remotion/player`): embed `<Player component={…} durationInFrames={…}
  fps={…} compositionWidth={…} compositionHeight={…} controls />` in any React app for
  runtime playback — **no server/render needed**. Good for in-app preview or letting a
  user tweak `inputProps`.

## 5. Render / export

See [`render-and-export.md`](render-and-export.md) for the full CLI + programmatic API.
Short version: `npx remotion render <id> out/<name>.mp4 --props=…` or the
`@remotion/renderer` `bundle → selectComposition → renderMedia` chain, writing to an
`out/` folder at 1080p (or 4K via `--scale`/dimensions). Don't overwrite an existing
render silently.

## 6. Optional advanced

These are real parts of the workflow but lean on the official skill / docs for the
exact API:

- **Transparency / green-screen** — render with an alpha-channel codec (e.g.
  `--codec=prores` with a transparency-capable profile) for a truly transparent video,
  *or* generate a green-screen-friendly scene (elements in solid, far-from-green colors
  for clean keying) and key it out in your NLE (DaVinci Resolve "3D Keyer" / Premiere
  Ultra Key). Official skill: `transparent-videos` rule.
- **Image insertion** — drop images into `public/` (the tutorial used a `PNGs/` folder)
  and reference them via `staticFile()` inside the relevant scene; prompt the build to
  place a specific image per scene/slide. Official skill: `images` rule.
- **Audio / voiceover / SFX** — `<Audio src={staticFile("music.mp3")} volume={…}>`;
  use `calculateMetadata()` to set `durationInFrames` from the audio length; audio
  analysis via `@remotion/media-utils`. Official skill: `audio`, `voiceover`, `sfx`,
  `audio-visualization` rules.
- **Cloud render (Remotion Lambda)** — `@remotion/lambda` renders frames in parallel on
  AWS for speed/scale (`npx remotion lambda render …`). Has its own setup + cost +
  licensing; treat as an advanced opt-in, not the default path.

## NLE composite (when the user finishes in a video editor)

Rendered scenes are normal MP4s — they drop into DaVinci Resolve / Premiere like any
clip. The typical finishing pass: mark each scene's in-point on the timeline, drop the
matching render, close gaps, add short transitions (e.g. "push in") + whoosh SFX +
background music, then export. This is NLE work, not Remotion — keep it on the user
unless they ask for step-by-step editor guidance.
