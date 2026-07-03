---
name: ingest-source
description: Ingest any source — a YouTube video, webpage/article, PDF, image, or local document — into a structured, cited markdown summary, then save it as project knowledge in docs/sources/ with an index that CLAUDE.md @-imports so future sessions are informed by it. Use when the user supplies a link or file and wants it summarized, transcribed, captured, or remembered for the project — "summarize this YouTube video", "tl;dr this video/article", "what does this video/page/PDF say", "key points with timestamps", "notes from this talk", "ingest this", "capture this source", "add this PDF/article to the project docs", "save this for the project", "remember this source". YouTube: watches audio + visuals via the Gemini API when a Google key is present (best for on-screen demos/text), else keyless timestamped captions via yt-dlp; public videos only for the watch tier. Webpages: fetched and distilled, with browser fallback for JS-heavy pages. PDFs and images: read natively. Adapts structure to the content (tutorial → steps; top-N → ranked items; review → pros/cons; talk/essay → key points; spec/paper → key facts + structure map). Persisting is the default; --no-save for a summary only. Asks whether to save to the project (docs/sources/), the personal OKF vault (routed through curate-knowledge — "ingest this into the vault"), or both. Replaces summarize-yt. Pairs with render-html for a branded page.
---

# ingest-source

Turn any source — YouTube video, webpage, PDF, image, document — into a
structured, cited markdown summary, and persist it as project knowledge the
project's CLAUDE.md can see.

## What it does

Given a URL or file path, it classifies the source, acquires its content
through the best available tier (degrading, never blocking — spec A3),
writes a summary shaped to the content type with real locators (`MM:SS`,
`p. N`, `§ Heading`), and saves it to `<project>/docs/sources/<slug>.md` with
YAML frontmatter. An `INDEX.md` line is upserted per ingestion, and — once,
with consent — a marker block is added to the project's CLAUDE.md that
`@`-imports the index, so every future session starts aware of what's been
ingested. Acquisition details live in `references/youtube.md` and
`references/web-docs.md`; summary shapes in `references/templates.md`; the
persistence contract and CLAUDE.md gate in `references/persistence.md` (A1).
Before persisting, a destination gate asks whether the summary belongs to the
project, the personal OKF vault (delegated to `curate-knowledge`), or both.

## How to run

Trigger with "summarize this video <url>", "ingest this article <url>",
"add this PDF to the project docs", or `/ingest-source <url-or-path>`.
Output pairs with `render-html` for a branded page.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | override the ingestion file location (default: `<docs-dir>/<slug>.md`) |
| `--docs-dir=PATH` | knowledge-base dir (default: `docs/sources` under the project root) |
| `--no-save` | summarize only; skip the destination gate and all persistence |
| `--dest=project\|vault\|both` | skip the destination question (default: infer from phrasing, else ask; `--agent` defaults to `project`) |
| `--watch` | YouTube: force the Gemini watch tier; gates if no key (under `--agent`, degrades) |
| `--transcript-only` | YouTube: force the keyless caption path; never call Gemini |
| `--lang=CODE` | YouTube: preferred caption language (default `en`) |
| `--install` | allow the gated `yt-dlp` install to run without prompting |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. python3 + `scripts/` present → **SCRIPTS**. Otherwise
→ **NATIVE**: WebFetch for pages, native Read for PDFs/images/documents,
yt-dlp by hand per `references/youtube.md`, persistence by hand per
`references/persistence.md`. Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py [--agent]`. Read the JSON.
   Offline is only `degraded` here (local files still ingest). `gated`
   (`YTDLP_MISSING`) → matters only for YouTube sources; offer the install
   from `references/youtube.md`, run it only on a yes or `--install`, else
   degrade. Other degrades → proceed and note which tier is off.
2. **Classify the source** — youtube / webpage / pdf / image / document, per
   the table in `references/web-docs.md`. Open the matching reference.
3. **Acquire content** —
   - youtube: tier ladder in `references/youtube.md`
     (`gemini_watch.py` → `fetch_transcript.py` → frames → metadata).
   - webpage: `scripts/fetch_url.py --url=<url>` → WebFetch →
     automate-browser (by reference), per `references/web-docs.md`.
   - remote pdf: `scripts/fetch_url.py --raw --out=/tmp/…` then native Read.
   - local pdf / image / document: native Read.
4. **Classify content & summarize (NATIVE reasoning)** — apply the matching
   template from `references/templates.md`. Every claim gets a real locator
   from the source — never invent one. Write for a future session that hasn't
   seen the source.
5. **Destination gate** (skip on `--no-save` or explicit `--dest=`) — decide
   where the knowledge lives. Infer from phrasing when unambiguous ("for the
   project" → project; "into the vault / knowledge base" → vault); otherwise
   ask once: *project / vault / both* (recommend `project` when working inside
   a repo the source clearly serves, `vault` for cross-project material).
   Under `--agent` with no `--dest`: default `project` and note it.
6. **Persist — project** (when dest includes `project`) — pipe the summary to
   `python3 scripts/persist.py --source=… --type=… --title=… --tier=…
   --hook=…` (idempotent: same source updates in place). Read the JSON. Then
   the **CLAUDE.md gate (spec A7)** — if `claude_md.status` is
   `absent`/`no-file`, run the consent gate in `references/persistence.md`:
   ask before inserting the `@`-import block (scripts never edit CLAUDE.md;
   under `--agent`, skip and report the block instead).
7. **Persist — vault** (when dest includes `vault`) — delegate to the
   `curate-knowledge` skill (by reference, spec A8): hand it the summary as a
   pre-drafted `type: Reference` candidate targeting a topic directory per
   the vault's layout (curate-knowledge's curation guide owns the path
   recommendation).
   Its own HITL gate, index/log wiring, and bundle verification apply — this
   skill never writes into the vault directly. Under `--agent`,
   curate-knowledge emits its proposals file instead of writing; report that
   honestly.
8. **Report** — file(s) written per destination, `created|updated`, index
   line, tier used, wiring status. Offer the `render-html` step.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure / time-bounded
  network (spec A4).
- Composition by reference, not import — delegates hostile pages to
  `automate-browser`, branded HTML to `render-html`, vault persistence to
  `curate-knowledge`; feeds `generate-prd` / `deep-research`; runs none of
  their code (spec A8).
- Layered binary resolution (spec A11): yt-dlp via `$YT_DLP_BIN → PATH → uvx →
  pipx → gated install → degrade`; web fetch via `requests → urllib → curl`.
- Secrets via the shared `scripts/_env.py` loader; `GOOGLE_API_KEY` /
  `GEMINI_API_KEY` in the `x-goog-api-key` header only, never in URLs/logs.
  Keyless tiers work with no key — the key is a gate, not a blocker (spec A7).
- Persists into the **user's project** and/or — only via `curate-knowledge`'s
  gate — the OKF vault; never into `~/.claude/skills/` (commit-by-default
  repo). Generated artifacts stay out of this repo.
