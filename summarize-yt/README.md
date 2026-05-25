# summarize-yt

**What it is:** turns a YouTube link into a structured, timestamped markdown summary — watching the video when a key is present, reading its captions otherwise.

## What you get

- A markdown summary with `MM:SS` timestamps, shaped to the video type (tutorial → steps + commands; top-N list → per-item entries; review → pros/cons; talk → key points).
- A header that names the **source tier** — so you know whether the video was actually *watched* (audio + visuals) or *transcribed* from captions.
- Markdown that pairs with `render-html` for a branded page, or feeds `generate-prd` / `deep-research` as captured source material.

## How to run

"Summarize this YouTube video <url>", "give me timestamped notes from <url>", or `/summarize-yt <url>`.

## What it needs

- **Keyless path works out of the box** — it only needs `yt-dlp`, which it resolves without installing globally: an existing `yt-dlp`, else an ephemeral `uvx yt-dlp` / `pipx run yt-dlp`. If none are reachable it *offers* an install command and runs it only with your OK (or `--install`).
- **Optional:** a Google API key (`GOOGLE_API_KEY` or `GEMINI_API_KEY`) in the shared `~/.claude/.env` unlocks the **watch** tier — Gemini sees the screen, not just the soundtrack, which matters for on-screen text and visual demos. No key → it degrades to captions, never blocks.
- `ffmpeg` is only needed for the visual frame-sampling fallback; absent → that one tier is skipped.

## How it works (high level)

1. Probes what's available (yt-dlp, Gemini key, ffmpeg, network) and picks the best tier.
2. **Watch tier (key present):** hands the YouTube URL to the Gemini API, which processes audio + visuals and returns timestamped notes. Public videos only.
3. **Transcript tier (keyless):** pulls the video's timestamped captions with `yt-dlp` (or `youtube-transcript-api` as a lighter fallback).
4. Detects the content type and writes the matching summary structure, attaching a real timestamp to every point.
5. Saves the markdown; offers to render a branded HTML version.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/tiers.md` — the capability ladder, exact commands, and per-content-type summary templates.
