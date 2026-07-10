# Webpage / PDF / image / document acquisition

Loaded by `SKILL.md` Step 3 when the source is not a YouTube URL (progressive
disclosure, spec A1). Each source type has its own short ladder; every rung
degrades rather than blocks (spec A3).

## Classifying the source (Step 2 recap)

| Looks like | Type | Acquire via |
|---|---|---|
| `youtube.com/watch`, `youtu.be/…`, `/shorts/…` | `youtube` | `references/youtube.md` |
| any other `http(s)://` URL ending `.pdf` (or serving `application/pdf`) | `pdf` | download → native Read |
| any other `http(s)://` URL | `webpage` | fetch ladder below |
| local `.pdf` | `pdf` | native Read |
| local `.png/.jpg/.jpeg/.gif/.webp` | `image` | native Read |
| local `.md/.txt/.docx/.html` or other text file | `document` | native Read (docx → the example-skills:docx skill if available, else `textutil -convert txt` on macOS) |

Ambiguous → ask (interactive) or best-guess by content-type header (`--agent`).

## Webpage ladder

1. **SCRIPTS:** `python3 scripts/fetch_url.py --url=<url>` → JSON
   `{title, text, transport, …}`. Transport ladder inside the script:
   requests → urllib → curl (macOS stdlib Python often lacks a CA bundle;
   the script reports which transport worked).
2. **NATIVE fallback:** WebFetch the URL. Note in the tier line that content
   passed through a summarizing fetch (lossier than raw extraction).
3. **JS-heavy / login-walled pages** (fetch returns a shell, a consent wall,
   or near-empty text): compose with **automate-browser** by reference — ask
   it to open the page and extract the readable content. Never import its
   scripts (spec A8).
4. **Total failure:** persist nothing; report which rungs failed.

Tier labels: `text (fetched)` · `text (WebFetch)` · `text (browser)`.

## Remote PDF

`python3 scripts/fetch_url.py --url=<url> --raw --out=/tmp/ingest-<slug>.pdf`
then Read the downloaded file (native PDF reading; use the `pages` parameter
on long documents — read ALL pages before summarizing, in ≤20-page chunks).
Tier label: `native read (pdf)`.

## Local PDF / image / document

No scripts — Claude's Read tool handles PDFs and images natively; plain-text
documents are just files. For an image, describe what it shows *and* transcribe
any text in it (that text is usually why it's being ingested). Tier labels:
`native read (pdf)` · `native read (image)` · `native read (document)`.

## Rules

- **Quote sparingly, cite always.** The ingestion is a distillation with
  pointers (section names, page numbers, timestamps, headings) — not a mirror
  of the source. Never persist a full article body wholesale.
- **Anchor every claim** to its locator: `[p. 12]` for PDFs, `[§ Heading]` for
  pages/documents, `[MM:SS]` for video. Locators must come from the source —
  never invent one (same rule as YouTube timestamps).
- **Record the tier honestly** — `text (WebFetch)` is not `text (fetched)`;
  a metadata-only capture must say the source was not actually read.
- Paywalled/login-walled content: capture only what was legitimately
  reachable; say so in the summary.
