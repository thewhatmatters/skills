# guardrails — core concepts + the deterministic-render rules

The thin, **stable** core. This is the one reference safe to rely on even when the
official `remotion-best-practices` skill isn't installed — these rules rarely change
and are exactly what agents get wrong. For anything beyond this (specific animation/
audio/caption/3d patterns), defer to the official skill (see [`compose.md`](compose.md)).

## The mental model

Remotion renders a **video as a function of frames**: it gives your React component
a frame number and a blank canvas; the component renders differently per frame;
Remotion encodes the frames into a real video (MP4 etc.). Animation = a value that
changes with the current frame.

## The four composition properties

Every video/composition is defined by four numbers:

- `width` (px), `height` (px)
- `durationInFrames` (total frames)
- `fps` (frames per second)

**Duration in seconds = `durationInFrames / fps`.** Frames are 0-indexed: the first
frame is `0`, the last is `durationInFrames - 1`. (1080p = 1920×1080; 4K = 3840×2160;
common fps = 30 or 60.)

## Project shape

- `src/index.ts` → `registerRoot(RemotionRoot)`.
- `src/Root.tsx` → returns one or more `<Composition>` elements (wrap multiple in a
  React Fragment). Each `<Composition>` carries: `id` (unique; how the CLI/renderer
  selects it), `component`, `durationInFrames`, `fps`, `width`, `height`,
  `defaultProps`, and optionally `calculateMetadata`.

## Key hooks & primitives (from `remotion`)

- `useCurrentFrame()` → current frame number. **Drives all animation.**
- `useVideoConfig()` → `{ width, height, durationInFrames, fps }`.
- `interpolate(frame, [inFrom, inTo], [outFrom, outTo], opts)` → map a frame to a
  value. Common opts: `extrapolateLeft`/`extrapolateRight` (`"clamp"`), `easing`.
- `spring({ fps, frame, config })` → physics animation; default slightly overshoots
  (bounce); tune `config: { damping, mass, stiffness }`.
- `Easing` → bezier/ease helpers for `interpolate`.
- `<AbsoluteFill>` → full-screen absolutely-positioned wrapper; the standard scene container.
- `<Sequence from={N} durationInFrames={M}>` → time-shift children so their local
  `useCurrentFrame()` starts at 0 at frame `N`. The core timing primitive.
- `<Series>` → plays children back-to-back without manual `from` math.
- `<Img>`, `<OffthreadVideo>` / `<Video>`, `<Audio>`, `staticFile()`.

## Assets

Put files in the project's **`public/`** folder and reference them with
**`staticFile("name.ext")`** — never hardcode a path. Example:
`<Img src={staticFile("logo.png")} />`.

## Data-driven video

- `defaultProps` on the `<Composition>` are the defaults.
- **Input props** override them at render time (CLI `--props`, renderer `inputProps`).
- `calculateMetadata({ props })` computes `durationInFrames`/`fps`/dimensions (or
  fetches data) **once** before render — e.g. set duration from an audio file's length.
  It is the *only* place true randomness / async / wall-clock is safe.
- A **Zod schema** for props enables visual editing in Studio + validation (defer
  the schema specifics to the official skill's `parameters` rule).

## ⛔ Determinism guardrails (NON-NEGOTIABLE)

Renders run **many frames in parallel across processes**. Anything non-deterministic
diverges between frames → flicker/garbage. Enforce these no matter who writes the code:

1. **No `Math.random()` in render code.** Use `random(seed)` from `remotion` — same
   seed ⇒ same value across all render threads:
   ```tsx
   import { random } from "remotion";
   const x = random(`x-${i}`);     // seed is a string or number
   // intentionally-true randomness (suppresses the ESLint warning): random(null)
   ```
2. **No `Date.now()` / `new Date()` / wall-clock** in render code (same divergence).
3. **All animation must be driven by `useCurrentFrame()`.** A value that animates by
   any other clock won't be frame-accurate.
4. **CSS transitions/animations and Tailwind animation classes are FORBIDDEN.** They
   don't render correctly and cause flickering. Animate by computing inline styles
   from the current frame instead. (Tailwind for *static* styling is fine; only its
   `animate-*` / `transition-*` motion utilities are banned.)
5. **Prefer `<OffthreadVideo>` over `<Video>`** for frame-accurate embedded video in renders.
6. **True randomness / async / network only inside `calculateMetadata()`** (runs once).

## Licensing (state honestly; don't quote prices)

Remotion is **free** for individuals, for-profit companies with **≤3 employees**, and
non-profits. Larger companies need a **paid company license** via
[remotion.pro](https://www.remotion.pro). Remotion **Lambda** (cloud render) has its
own cost/licensing. When a user's context implies a bigger company, surface the
license requirement rather than asserting a specific price.
