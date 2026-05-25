---
name: summarize-yt
description: Summarize a YouTube video into structured, timestamped, human- and agent-readable markdown. Use when the user supplies a YouTube link and wants it watched, summarized, transcribed, or turned into notes — "summarize this YouTube video", "tl;dr this video", "what does this video say", "key points with timestamps", "notes from this talk", "recap this tutorial", "what are the steps in this video", "break down this top-10 video". Adapts structure to the content: tutorials → ordered steps with commands and timestamps; ranked/top-N lists → per-item entries; reviews → pros/cons; talks → key points. Watches both audio and visuals via the Gemini API when a Google key is present (best for on-screen text and demos), otherwise reads the video's timestamped captions keyless via yt-dlp. Public videos only for the watch tier. Outputs markdown that pairs with render-html for a branded page.
---

# summarize-yt

Turn a YouTube URL into a structured, timestamped markdown summary — watching the
video when a key is present, reading its captions otherwise.

## What it does

Given a YouTube link, it produces a markdown summary with `MM:SS` timestamps,
shaped to the video's type (tutorial, ranked list, review, talk). It runs a
**degraded capability ladder** (spec A3): best fidelity is the Gemini API
*watching* audio **and** visuals; without a key it falls back to keyless caption
transcripts via `yt-dlp`, then to frame sampling, then to metadata only — it
never hard-blocks. The exact tier mechanics, the per-content-type summary
templates, and the binary-resolution ladder live in
[`references/tiers.md`](references/tiers.md) (spec A1) — read it before summarizing.

## How to run

Trigger with "summarize this YouTube video <url>", "tl;dr this video", "notes
with timestamps from <url>", or `/summarize-yt <url>`. Output is markdown; pass it
to `render-html` for a branded page, or use it upstream of `generate-prd` /
`deep-research` as a source-capture step.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | where to write the summary markdown (default: `./<video-id>-summary.md`) |
| `--watch` | force the Gemini watch tier; gates if no key (under `--agent`, degrades) |
| `--transcript-only` | force the keyless caption path; never call Gemini |
| `--lang=CODE` | preferred caption language (default: `en`, falls back to any available) |
| `--install` | allow the gated `yt-dlp` install to run without prompting |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. python3 + `scripts/` present → **SCRIPTS** (use the
scripts below). Otherwise → **NATIVE**: resolve `yt-dlp` yourself (see the ladder
in `references/tiers.md`), fetch captions, and summarize by hand. Announce the
mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py [--agent]`. Read the JSON.
   `down` (e.g. `NETWORK_DOWN`) → stop and report. `gated` (`YTDLP_MISSING`) →
   offer the install command in `references/tiers.md`; run it only on a yes or
   `--install`, else degrade. `degraded` (`GEMINI_KEY_ABSENT`, `FFMPEG_MISSING`)
   → proceed and note which tier is unavailable.
2. **Pick the tier** — honor `--watch` / `--transcript-only`; otherwise take the
   highest tier preflight reports as available. Watch tier needs a key **and** a
   public video.
3. **Acquire content** —
   - Watch tier: `python3 scripts/gemini_watch.py --url=<url> [--format=auto]` →
     timestamped notes straight from the model (it sees the screen).
   - Transcript tiers: `python3 scripts/fetch_transcript.py --url=<url>
     [--lang=en]` → JSON `{video, captions:[{t,text}], chapters, source}`.
   - Frame/metadata fallbacks: see `references/tiers.md`.
4. **Detect content type & summarize (NATIVE reasoning)** — classify the video
   (tutorial / ranked-list / review / talk / other) and apply the matching
   template from `references/tiers.md`. Every claim gets an `MM:SS` timestamp
   sourced from the captions or Gemini output — never invent times.
5. **Write the summary** — markdown to `--out` (default `./<video-id>-summary.md`).
   Lead with title, channel, duration, source-tier line (so the reader knows
   whether it was watched or transcribed). Offer the `render-html` step.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Composition by reference, not import — emits markdown for `render-html`; feeds
  `generate-prd` / `deep-research`; runs none of their code (spec A8).
- Layered binary resolution (spec A11): `$YT_DLP_BIN → yt-dlp on PATH → uvx yt-dlp
  → pipx run yt-dlp → gated install → degrade`. Never installs globally without
  consent; under `--agent` degrades instead of mutating the system.
- Scripts: JSON stdout / diagnostics stderr / graceful failure / time-bounded
  network (spec A4).
- Secrets via the shared `scripts/_env.py` loader; `GOOGLE_API_KEY` /
  `GEMINI_API_KEY` sent in the `x-goog-api-key` header only, never in URLs/logs.
  Keyless tiers work with no key — the key is a gate, not a blocker (spec A7).
