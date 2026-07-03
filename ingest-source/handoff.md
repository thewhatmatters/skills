# ingest-source — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-06-11  ·  Generator: generate-skill @ CC 2.1.145  ·  Absorbs: summarize-yt (2026-05-24)

## 1. Purpose
Ingest any source (YouTube video, webpage, PDF, image, document) into a
structured, cited markdown summary, and persist it as project knowledge in
`docs/sources/` with an INDEX.md that the project's CLAUDE.md `@`-imports.

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Notable points:
- **A1:** four reference files, each loaded at a distinct step — acquisition
  split per source type (`youtube.md`, `web-docs.md`) so a PDF ingestion never
  loads the YouTube ladder.
- **A3:** SCRIPTS vs NATIVE, plus per-type capability ladders (YouTube 5-tier;
  webpage fetch → WebFetch → automate-browser; remote PDF download → Read).
- **A4:** `preflight.py`, `fetch_transcript.py`, `gemini_watch.py` (absorbed),
  `fetch_url.py`, `persist.py` (new) — one concern each, JSON stdout.
- **A7:** three gates — yt-dlp install (absorbed), Gemini key (degrade), and
  the new **CLAUDE.md wiring gate** (consent before editing the user's file).
- **A8:** composes by reference with automate-browser, render-html,
  generate-prd, deep-research.
- **A11:** yt-dlp ladder (absorbed) + the audit-ui fetch-transport ladder
  (requests → urllib → curl) for webpages.

## 3. Decision log
- 2026-07-02: vault targets are **topic directories** (e.g. `claude/…`), not
  `<vault>/reference/` — the vault went topic-first the same day; the path
  recommendation is owned by curate-knowledge's curation guide.
- 2026-07-02: **Added the destination gate (step 5) — project / vault / both.**
  Vault persistence is delegated by reference to `curate-knowledge` (its HITL
  gate, OKF wiring, and verification apply); this skill never writes the vault
  directly. `--dest=` skips the question; phrasing is inferred when
  unambiguous; `--agent` defaults to `project`. `--no-save` still bypasses
  everything. Rationale: one acquisition/distillation pipeline, two knowledge
  scopes — project-local (docs/sources/ + CLAUDE.md import) vs cross-project
  (OKF vault).
- 2026-06-11: **Absorb-and-replace summarize-yt** (user's explicit choice over
  a router that delegates). `_env.py`/`_tools.py` copied verbatim;
  `fetch_transcript.py`/`gemini_watch.py` verbatim except diagnostics labels;
  `references/tiers.md` split into `youtube.md` (ladder) + `templates.md`
  (shapes, generalized to all source types). summarize-yt's decision log
  (2026-05-24) remains valid for the YouTube path — key points repeated below
  so this file stands alone.
- 2026-06-11: **Persistence is the point; summarizing is the means.** The new
  capability vs summarize-yt is `docs/sources/` + INDEX.md + the CLAUDE.md
  `@`-import. CLAUDE.md cannot "watch a folder" — `@docs/sources/INDEX.md`
  inlines the index each session start while bodies load on demand; same
  index-vs-body split as the typed-memory system. Persisting is the default
  (`--no-save` opts out) because an unsaved ingestion is just a chat answer.
- 2026-06-11: **Scripts never edit CLAUDE.md.** `persist.py` only reports
  wiring status + emits the canonical block; the edit is performed natively by
  Claude behind a consent gate (interactive ask; `--agent` skips + prints the
  block). Editing a user's CLAUDE.md from a subprocess would bypass the
  permission system and the "confirm before modifying user files" rule.
- 2026-06-11: **Idempotency keyed on frontmatter `source:`**, not slug —
  re-ingesting a URL updates its file in place (`action: updated`), so the
  knowledge base can't accumulate duplicates of the same source as titles
  drift.
- 2026-06-11: **Offline ≠ down.** summarize-yt's preflight returned `down` on
  no network; here local PDF/image/document ingestion needs no network, so
  offline is `degraded` (`NETWORK_OFFLINE`) and nothing in preflight is ever
  `down`.
- 2026-06-11: **Webpage extraction is stdlib `html.parser`**, not readability/
  trafilatura (stdlib-first rule). Good enough because Claude re-reads the
  extracted text anyway; hostile/JS pages route to automate-browser by
  reference. Transport ladder requests → urllib → curl carried from audit-ui's
  macOS CA-bundle lesson.
- 2026-06-11: Self-audit found 2 findings, both fixed same-session: `--out`
  was documented but unimplemented (now real in `persist.py`: explicit path;
  outside `--docs-dir` the index is skipped and said so), and the shared
  `.env.example` "Used by:" note still named summarize-yt (updated).
- Carried from summarize-yt (2026-05-24): Claude can't watch video natively →
  visual understanding delegated to Gemini (URL as `fileData`, ~1 fps,
  `x-goog-api-key` header only, public videos only); Gemini key is optional
  (gate, not requirement); never globally install yt-dlp without consent
  (`$YT_DLP_BIN → PATH → uvx → pipx → gated install → degrade`); summarization
  stays NATIVE reasoning (scripts deterministic, judgment in the model); no
  DESIGN.md (plain markdown; render-html owns visual identity).

## 4. Known limitations / environment caveats
- All summarize-yt caveats carry over: pure-visual + no-captions + no-key
  videos remain the gap; YouTube IP-blocks scrapers; watch tier is
  public-videos-only with a free-tier daily cap.
- `fetch_url.py` extraction is heuristic — SPAs and consent-walled pages
  return shells; the ladder's answer is automate-browser, not a heavier
  parser.
- The CLAUDE.md `@`-import inlines INDEX.md into every session of the target
  project; at one line per source this is cheap, but a project with hundreds
  of ingestions should prune or shard its index (note in INDEX.md header).
- `--out` overrides the file path but persistence still expects to manage
  INDEX.md in `--docs-dir`; pointing `--out` outside the docs dir effectively
  means `--no-save` semantics for the index.

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.
Secrets row applies (optional Gemini key via shared `_env.py`). Gate /
preflight / binary-resolution rows all apply; the CLAUDE.md gate is the
novel A7 instance (all four parts documented in `references/persistence.md`).

## 6. Notes
Deps: optional `yt-dlp` (resolved, never required-installed), optional
`ffmpeg`, optional Gemini key, optional `requests`/`curl` (transport ladder).
Downstream: `render-html`; upstream source capture for `generate-prd` /
`deep-research`. The retired summarize-yt's history lives in git
(`summarize-yt/` up to 2026-06-11) — its handoff was the basis for §3's
carried-over entries.
