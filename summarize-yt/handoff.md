# summarize-yt — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-24  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
Turn a YouTube URL into a structured, timestamped markdown summary — watching the
video via the Gemini API when a key is present, reading its captions keyless via
yt-dlp otherwise. Adapts the summary shape to the content type.

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Notable points:
- **A1 progressive disclosure:** the capability ladder, exact per-tier commands,
  and per-content-type summary templates live in `references/tiers.md`, loaded
  only at Steps 2–4; SKILL.md stays lean.
- **A3 dual-mode + degraded ladder:** SCRIPTS vs NATIVE; and a 5-rung capability
  ladder (Gemini watch → yt-dlp captions → youtube-transcript-api → frame
  sampling → metadata) that degrades rather than blocks.
- **A4 scripts:** `preflight.py` (readiness), `fetch_transcript.py` (keyless
  captions/metadata), `gemini_watch.py` (watch tier) — JSON stdout, diagnostics
  stderr, graceful, time-bounded network. `_tools.py` is an internal helper
  (binary resolution), `_env.py` the shared key loader.
- **A7 gate:** missing yt-dlp is a *gate* (offer install) not a silent global
  install; a missing Gemini key *degrades* to keyless, never blocks.
- **A8 composition by reference:** emits markdown for `render-html`; feeds
  `generate-prd` / `deep-research`; imports none of them.
- **A11 layered binary resolution:** `$YT_DLP_BIN → yt-dlp → uvx yt-dlp → pipx
  run yt-dlp → gated install → degrade`.

## 3. Decision log
- 2026-05-24: scaffolded by generate-skill.
- 2026-05-24: **Claude can't watch video natively — so the ladder splits "watch"
  from "read".** Web research (Jan 2026) confirmed the Claude model has no native
  video/YouTube-URL input; it reads text and images. So genuine *visual*
  understanding (on-screen text, demos, top-N lists shown not spoken) is
  delegated to the Gemini API, which [accepts a YouTube URL directly and
  processes audio + visual at 1fps with MM:SS
  timestamps](https://ai.google.dev/gemini-api/docs/video-understanding). Speech-
  carried content is handled keyless from captions. This split is the whole
  reason for the tiering.
- 2026-05-24: **Gemini key is optional (gate, not requirement).** Keyless caption
  tiers cover most videos, so the skill must work with no key. The key only
  unlocks the visual tier. `GOOGLE_API_KEY` or `GEMINI_API_KEY`, in the
  `x-goog-api-key` header (never the URL). YouTube ingestion is currently a free
  Gemini preview (pricing "likely to change"); public videos only.
- 2026-05-24: **Never globally install yt-dlp without consent (user choice).**
  Asked the user explicitly; they chose gated + ephemeral over auto-install.
  Resolution ladder is `$YT_DLP_BIN → on-PATH → uvx yt-dlp → pipx run yt-dlp →
  gated install → degrade`. The ephemeral runners mean the keyless path works
  with **zero** global install on most modern machines (this dev box has `uvx`
  but not `yt-dlp`). Install runs only on a yes or `--install`; under `--agent`
  it degrades. Matches A7 (recoverable gap = gate) and the "confirm
  system-modifying actions" rule.
- 2026-05-24: **Summarization stays NATIVE reasoning.** Scripts do the
  deterministic part (resolve binaries, fetch captions/metadata, call Gemini).
  Detecting content type and writing the structured summary is Claude's
  judgment, applying templates from `references/tiers.md` — same division of
  labor as decompose-prd (scripts validate; the model decomposes).
- 2026-05-24: **No DESIGN.md.** Emits plain markdown; `render-html` owns the
  visual identity (same call as draw-diagram → render-html).

## 4. Known limitations / environment caveats
- **Pure-visual + no-captions + no-key videos** are the genuine gap — only the
  frame-sampling tier (needs `ffmpeg`) partially fills it, coarsely.
- YouTube actively blocks scraping IPs: `youtube-transcript-api` gets
  [IP-blocked](https://github.com/jdepoix/youtube-transcript-api/issues/511)
  (esp. datacenter IPs), and `yt-dlp` needs periodic updates. Gemini sidesteps
  this (Google fetching its own platform).
- Gemini watch tier: **public videos only** (no private/unlisted), one URL per
  request, free-tier daily cap ~8h of video.
- Timestamps are only as accurate as the caption track / Gemini output; never
  fabricate a time the source didn't provide.

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.
Secrets row applies (Gemini key, optional). Gate/preflight/binary-resolution
rows all apply.

## 6. Notes
Deps: `yt-dlp` (resolved, not required-installed), optional `ffmpeg` (frame
tier), optional Gemini API key (watch tier), optional `youtube-transcript-api`
(lighter keyless fallback). Downstream: `render-html` for branded HTML; upstream
source-capture for `generate-prd` / `deep-research`.
