---
name: extract-docs
description: Extract an entire documentation site into clean per-page markdown — systematically, via an acquisition ladder that prefers machine-readable manifests (llms.txt / llms-full.txt → docs-scoped llms.txt → per-page .md variants → sitemap.xml → bounded same-prefix crawl) over brute crawling. Use when the user wants a docs site captured wholesale — "extract the docs from <url>", "pull this documentation site", "mirror these docs locally as markdown", "capture the whole docs site", "check if X has an llms.txt", "make these vendor docs available to the project". Pages land in the project's docs/sources/<vendor>/ (regenerable and disposable — never the vault wholesale); optionally distills ONE gated vault article through curate-vault. Scripts fetch and convert HTML→markdown deterministically; falls back to automate-browser for JS-rendered pages. NOT for a single page/article/PDF (that's ingest-source) and NOT for open-ended research (that's deep-research).
---

# extract-docs

Extract a documentation site into per-page markdown via an acquisition
ladder, landing in the project's `docs/sources/<vendor>/` — with an optional
single distilled vault article through curate-vault's gate.

## What it does

Probes the site for the cheapest complete **manifest** (llms.txt tiers →
sitemap → bounded crawl), then **fetch-converts** every in-scope page to
markdown deterministically (scripts, not model tokens), writes a dated
manifest index, and offers exactly one gated vault distillate. The captured
tree is *regenerable* — re-run to refresh; nothing here is curated memory.

## How to run

"extract the docs from https://…", "pull this documentation site",
"does X publish an llms.txt?", or `/extract-docs <url>`.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | destination dir (default: `<project>/docs/sources/<vendor>/`) |
| `--vendor=<slug>` | override the vendor slug (default: derived from the domain, e.g. `onorca-dev` → `orca`… ask if ambiguous) |
| `--max-pages=N` | scope cap (default 200); manifests larger than N gate for scope confirmation |
| `--tier=<t>` | force a ladder tier: `llms-full`, `llms`, `page-md`, `sitemap`, `crawl` |
| `--refresh` | update an existing mirror in place: probe again, then `scripts/refresh.py` applies only the **delta** (added / changed / removed pages) and reports it — see "Refreshing a mirror" |
| `--dry-run` | probe the ladder, print the plan (tier, page count, destination), write nothing. With `--refresh`: compute and report the delta without writing |

## Step 0 — Mode probe

`python3 --version` + `scripts/` present → **SCRIPTS**. Otherwise **NATIVE**:
probe the ladder with WebFetch by hand (try `<root>/llms.txt`,
`<root>/llms-full.txt`, `<docs-base>/llms.txt`, one `<page>.md` variant,
`<root>/sitemap.xml` in that order) and fetch pages one at a time — slower,
same artifact. Announce the mode in one line.

## Step 1 — Preflight

`python3 scripts/preflight.py --url=<base-url> [--out=<dest>]` — checks the
site is reachable and the destination is writable. Act on `overall`:
`ready`/`degraded` → proceed (note degraded items); `down` → STOP.

## Step 2 — Probe the ladder

`python3 scripts/probe.py --url=<docs-url>` → JSON: the winning `tier`, the
`manifest` (list of page URLs), and `count`. The ladder prefers manifests
over crawling:

1. `llms-full.txt` at the site root — the full docs in one file; done after
   a single fetch.
2. `llms.txt` (root, then docs-scoped) — a curated URL manifest.
3. Per-page `.md` variants (Mintlify/Fumadocs-style) — probe one page.
4. `sitemap.xml`, filtered to the docs path prefix.
5. Bounded same-prefix crawl from the docs index (last resort; obeys
   `--max-pages`, never leaves the docs path).

Announce tier + count. `count > --max-pages` → **scope gate**: interactive,
ask *Extract first N / Raise the cap / Cancel*; `--agent` takes the first N
and records the truncation (no silent caps — spec A12).

`--dry-run` stops here with the plan.

## Step 3 — Resolve the destination

`--out` verbatim if given. Otherwise `<project>/docs/sources/<vendor>/`
(create it; same convention as ingest-source). Not in a project (no repo/
CLAUDE.md upward)? → ask; `--agent` uses the cwd. The extraction NEVER
writes into the vault — the only vault path is the Step-6 distillate via
curate-vault.

## Step 4 — Fetch + convert

`python3 scripts/fetch.py --manifest=<probe-json> --out=<dest>` — fetches
every manifest URL, converts HTML→markdown (prefers `<main>`/`<article>`
content; strips nav/footer), writes one `.md` per page mirroring the URL
path, and reports JSON: `fetched`, `failed`, `empty`. Pages that come back
**empty** are JS-rendered: retry them through automate-browser (if
available — spec A15c), else list them honestly in the summary as
not captured.

## Step 5 — Write the manifest index

Write `<dest>/index.md`: the extraction date, source URL, tier used, and a
table of every page (title, local path, source URL). This is the run's
artifact (spec A10) and the refresh anchor — re-running the skill re-fetches
against it. Suggest (don't apply) a CLAUDE.md `@docs/sources/<vendor>/index.md`
import so future sessions see the docs.

## Refreshing a mirror (`--refresh`)

For a destination that already holds a mirror: run the Step-2 probe as
usual, then `python3 scripts/refresh.py --manifest=<probe-json> --out=<dest>
[--dry-run]` instead of `fetch.py`. It classifies every page — **added**
(fetched + written), **changed** (body replaced, any existing OKF
frontmatter preserved verbatim), **removed** (deleted), unchanged (left
alone) — and emits the delta JSON. Honest cost: the full manifest is still
fetched for comparison; the win is write-churn and the **delta report**,
which doubles as a vendor changelog (surface it to the user — renames and
new pages are exactly the signal that invalidates existing project
knowledge). After a non-empty delta: re-run whatever conformance/index
pass the original extraction used (vault mirrors: frontmatter for added
pages, index regeneration, a log entry naming the delta, verify). A
version-scoped manifest (e.g. Next.js llms.txt) makes the delta a
version-bump detector — note the new version in the mirror's root index.

## Step 6 — Offer the vault distillate (interactive only)

If the run surfaced genuinely durable, cross-project knowledge (a platform
gotcha, an architectural fact worth keeping beyond this project), offer ONCE:
*"Want a single distilled reference article in the vault? I'll route it
through `/curate-vault`."* Run curate-vault only on yes — its per-article
gate owns the write. Never wholesale-copy pages into the vault; if
curate-vault is absent, skip the offer (spec A15c). Under `--agent`: skip.

## Step 7 — Emit

Print: pages fetched / failed / empty (with the automate-browser retry
outcome), the destination tree root, the index path, and the one-line
refresh command.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- **Ladder** and **manifest** are the leading words: always announce which
  ladder tier won and how many pages the manifest holds.
- Keyless; network only to the target site. Respects `robots.txt` disallow
  rules at the crawl tier (manifest tiers are published for consumption).
- Soft composes (spec A15c): automate-browser (JS retries), curate-vault
  (the distillate), ingest-source (single-URL cousin — route single pages
  there). All "if available"; no hard deps, so no preflight-deps wiring.
- Writes only inside `<dest>`; the vault is reachable exclusively through
  curate-vault's gate.
