# Capability ladder, commands & summary templates

Loaded by `SKILL.md` Steps 2–4 (progressive disclosure, spec A1). This is the
craft of the skill: which tier to use, the exact commands, and how to shape the
summary to the content type.

## The capability ladder (best → worst)

| # | Tier | Needs | Sees | When |
|---|------|-------|------|------|
| 1 | **Gemini watch** | Google API key + public video | audio **+ visuals** | best fidelity; required for on-screen-only content (demos, slides, text overlays, some top-N lists) |
| 2 | **yt-dlp captions** | yt-dlp (resolved, see below) | spoken words | default keyless path; great for talks/tutorials/reviews |
| 3 | **youtube-transcript-api** | the pip lib importable | spoken words | lighter keyless fallback; flakier (IP blocks) |
| 4 | **frame sampling** | yt-dlp + ffmpeg | visuals only (sampled) | partial visual recovery when no key |
| 5 | **metadata only** | yt-dlp `-J` or WebFetch | title/desc/chapters | last resort; clearly labelled as not-watched |

Pick the highest available tier unless `--watch` / `--transcript-only` forces
one. Always record the tier used in the summary header so the reader knows
whether the video was *watched* or *transcribed*.

## Binary resolution (spec A11)

`yt-dlp` is resolved by `scripts/_tools.py:resolve_ytdlp()` in this order, first
hit wins:

1. `$YT_DLP_BIN` (explicit override)
2. `yt-dlp` on `PATH`
3. `uvx yt-dlp` (ephemeral, no global install)
4. `pipx run yt-dlp` (ephemeral, no global install)
5. **gate** — none reachable: print the install hint below and stop unless the
   user says yes or passed `--install`; under `--agent`, degrade (skip yt-dlp
   tiers). **Never** install globally without consent.

Install hint (only offered, never auto-run without a yes / `--install`):
```
pipx install yt-dlp      # isolated, recommended
# or: uv tool install yt-dlp
# or: brew install yt-dlp
```

`ffmpeg` (frame tier only) resolves `$FFMPEG_BIN → ffmpeg on PATH → skip tier`.

## Tier 1 — Gemini watch

`python3 scripts/gemini_watch.py --url=<url> [--format=auto|tutorial|list|review|talk]`

Sends the YouTube URL to the Gemini API as a `file_data.file_uri` part alongside
a prompt that asks for timestamped notes in the chosen shape. The model samples
~1 frame/sec and can answer with `MM:SS` timestamps. Key goes in the
`x-goog-api-key` header (never the URL). Public videos only. Returns the model's
markdown notes on stdout (JSON-wrapped: `{tier, model, text}`).

If the call fails (no key, private video, quota), the script exits non-zero with
a stderr reason and the caller drops to Tier 2.

## Tiers 2–3 — captions

`python3 scripts/fetch_transcript.py --url=<url> [--lang=en]`

Resolves yt-dlp, downloads auto + manual subs as SRT, parses to JSON:
```json
{"video": {"id","title","channel","duration","url"},
 "chapters": [{"t":"MM:SS","title":""}],
 "captions": [{"t":"MM:SS","text":""}],
 "source": "yt-dlp|youtube-transcript-api"}
```
The equivalent raw yt-dlp call (for NATIVE mode):
```
<yt-dlp> --skip-download --write-auto-sub --write-sub --sub-lang <lang> \
         --convert-subs srt --output '%(id)s' <url>
```
If yt-dlp yields nothing and `youtube-transcript-api` is importable, the script
falls back to it automatically.

## Tier 4 — frame sampling

When there is no key and the video is visual, sample frames at chapter marks (or
every ~30s) and read them as images:
```
<yt-dlp> -f 'bestvideo[height<=480]' -o frames-src.%(ext)s <url>
<ffmpeg> -i frames-src.* -vf fps=1/30 frames/%04d.jpg
```
Feed the frames to Claude as images; pair each with its timestamp. Coarse —
label the summary accordingly.

## Tier 5 — metadata only

`<yt-dlp> -J --skip-download <url>` (or WebFetch the watch page) → use title,
description, and chapter list. State plainly that the video was **not watched**.

## Content-type templates (Step 4)

Classify the video, then apply the matching shape. Every bullet carries a real
`MM:SS` from the source. Lead every summary with this header — it records the
request (URL), the date, and how the content was obtained (spec A10, A12):

```
# <Title>
**Source:** <video URL> · **Channel:** <name> · **Length:** <H:MM:SS>
**Summarized:** <YYYY-MM-DD> via <tier — "watched (Gemini)" | "transcript (yt-dlp)" | "transcript (youtube-transcript-api)" | "metadata only — NOT watched">
[one-sentence tl;dr]
```

**Tutorial / how-to** — ordered, reproducible:
```
## Steps
1. **[00:42] <action>** — <detail>; `command if shown`
2. **[02:15] <action>** — …
## Gotchas / notes
- [05:30] <caveat the presenter called out>
```

**Ranked / top-N list:**
```
## The list
- **#1 — <item> [01:10]** — <why; one line>
- **#2 — <item> [02:45]** — …
[honor the video's own ordering; note if it counts down]
```

**Review / comparison — pros/cons:**
```
## Verdict — [tl;dr + the timestamp it's stated]
| Pros | Cons |
|------|------|
| <point> [03:10] | <point> [06:20] |
## Notable moments
- [08:05] <benchmark / demo / price>
```

**Talk / interview / explainer — key points:**
```
## Key points
- **[00:30] <claim/idea>** — <supporting detail>
- **[04:10] <claim/idea>** — …
## Quotable
> "<short quote>" — [12:40]
```

**Unknown / mixed:** default to the talk template (timestamped key points) and
note the type was ambiguous.

## Rules

- Never invent a timestamp; only use times present in captions / Gemini output.
- Keep the source-tier line honest — if you transcribed, don't imply you watched.
- Long videos: summarize section-by-section using chapter marks as anchors.
- Offer the `render-html <out>` step after writing, for a branded page.
