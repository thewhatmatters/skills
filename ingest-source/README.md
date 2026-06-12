# ingest-source

**What it is:** turns any source — a YouTube video, webpage, PDF, image, or document — into a structured, cited markdown summary, and saves it as project knowledge your CLAUDE.md can see. (Replaces `summarize-yt`.)

## What you get

- A markdown summary shaped to the content (tutorial → steps; top-N → ranked items; review → pros/cons; talk/essay → key points; spec/paper → key facts + a structure map), every point carrying a real locator — `MM:SS` for video, `p. N` for PDFs, `§ Heading` for pages.
- The summary saved to your project's `docs/sources/<slug>.md` with frontmatter (source, type, date, how it was obtained), plus a one-line entry in `docs/sources/INDEX.md`. Re-ingesting the same source updates the file instead of duplicating it.
- One-time, with your OK: a small block in your project's CLAUDE.md that `@`-imports the index — so every future Claude session starts knowing what sources the project has captured, and reads the full files only when relevant.

## How to run

"Summarize this YouTube video <url>", "ingest this article <url>", "add this PDF to the project docs", or `/ingest-source <url-or-path>`. Add `--no-save` for a summary without saving anything.

## What it needs

- **Nothing for local files** — PDFs, images, and documents are read directly, even offline.
- **Webpages** work out of the box (built-in fetch with fallbacks; JS-heavy pages hand off to the `automate-browser` skill).
- **YouTube keyless path** only needs `yt-dlp`, resolved without installing globally (an existing binary, else ephemeral `uvx`/`pipx run`). If none are reachable it *offers* an install and runs it only with your OK (or `--install`).
- **Optional:** a Google API key (`GOOGLE_API_KEY` or `GEMINI_API_KEY`) in the shared `~/.claude/.env` unlocks the YouTube **watch** tier — Gemini sees the screen, not just the soundtrack, which matters for on-screen text and demos. No key → captions, never blocked.

## How it works (high level)

1. Probes what's available (network, fetch transports, yt-dlp, Gemini key) and classifies the source by URL/extension.
2. Acquires content through the best available tier — Gemini watch or captions for YouTube, text extraction for pages, native reading for PDFs/images — degrading gracefully, never blocking.
3. Writes a summary in the structure matching the content type, citing real timestamps/pages/headings only.
4. Saves it into `docs/sources/` and updates the index; the summary header and frontmatter always say *how* the content was obtained (watched vs transcribed vs metadata-only).
5. Asks once per project whether to wire the index into CLAUDE.md; you can also paste the printed block yourself.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why" (including what carried over from summarize-yt).
- `references/` — the YouTube tier ladder, web/PDF/image acquisition, summary templates, and the persistence contract.
