# render-and-export — getting an MP4 out

Two ways to render: the **CLI** (quick, one-off) and the **`@remotion/renderer` Node
API** (programmatic, for pipelines / batch / data-driven runs). For flags/options that
may have changed, confirm against `npx remotion render --help` and
[remotion.dev/docs](https://www.remotion.dev/docs) — defer to the live tool over this
static note.

## CLI

```bash
# render a composition by id to an output file
npx remotion render <composition-id> out/video.mp4

# no id → interactive picker
npx remotion render

# list composition ids
npx remotion compositions

# single still frame → PNG/JPEG
npx remotion still <composition-id> out/frame.png --frame=30
```

Key `render` flags _(snapshot — Remotion v4, 2026-06; flags can change between
releases, so treat `npx remotion render --help` and the official skill as
authoritative if they differ)_:

| Flag | Purpose |
|---|---|
| `--props='{"k":"v"}'` or `--props=path.json` | input props (override `defaultProps`) |
| `--codec=h264\|h265\|vp8\|vp9\|prores\|gif` | output codec (default `h264`) |
| `--frames=0-99` | render a frame range only |
| `--scale=2` | upscale (e.g. 1080p comp → 4K) |
| `--concurrency=N` | parallelism (render speed vs. CPU/RAM) |
| `--image-format=jpeg\|png` | per-frame format (png needed for alpha) |
| `--crf=N` / `--jpeg-quality=N` | quality knobs |
| `--sequence` | emit an image sequence instead of a video |

Config can also live in **`remotion.config.ts`** (applies to CLI renders). For 4K,
either set the composition's `width`/`height` to 3840×2160 or render a 1080p comp with
`--scale=2`.

## Programmatic (`@remotion/renderer`, Node)

Three functions: `bundle()` → `selectComposition()` → `renderMedia()`.

```ts
import { bundle, selectComposition, renderMedia } from "@remotion/renderer";

// 1. Bundle the project (returns a local serveUrl path; or host it)
const serveUrl = await bundle({ entryPoint: "./src/index.ts" });

// 2. Pick the composition (resolves calculateMetadata + input props)
const composition = await selectComposition({
  serveUrl,
  id: "MyVideo",
  inputProps: { titleText: "Hello" },
});

// 3. Render
await renderMedia({
  composition,
  serveUrl,
  codec: "h264",
  outputLocation: "./out/video.mp4",   // omit → in-memory buffer
  inputProps: { titleText: "Hello" },
  onProgress: ({ progress }) => console.log(`${Math.round(progress * 100)}%`),
});
```

- `serveUrl` is either the local path from `bundle()` or a hosted bundle URL.
- This is the path for **data-driven / batch** rendering: loop over a dataset, pass
  each row as `inputProps`, render one file each.

## Cloud (Remotion Lambda)

`@remotion/lambda` parallelizes rendering on AWS Lambda for speed/scale:
`npx remotion lambda render <serve-url> <comp-id>`. Requires AWS setup + deploy and
has its own cost model and licensing — advanced opt-in, not the default. See the
official docs/skill for setup specifics.

## House rules for this skill

- Default output dir is `--out` (default `<project>/out`); create it if missing.
- **No clobber**: if the target file exists, write a numbered sibling
  (`video-2.mp4`) or tell the user — never silently overwrite a render.
- Report the exact output path(s) and the codec/resolution used.
