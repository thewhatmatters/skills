# extract-docs

**What it is:** Extract a documentation site into per-page markdown via an
acquisition ladder, landing in the project's `docs/sources/<vendor>/` — with
an optional single distilled vault article through curate-vault's gate.

## What you get

- One markdown file per docs page under `docs/sources/<vendor>/`, mirroring
  the site's URL structure — clean content, no nav/footer chrome.
- A dated `index.md` manifest (source URL, ladder tier used, per-page table)
  you can `@`-import from the project's CLAUDE.md so future sessions see the
  docs.
- Optionally, ONE distilled reference article in the knowledge vault —
  always through `/curate-vault`'s confirmation gate, never a wholesale dump.

## How to run

Say "extract the docs from https://…", "does X publish an llms.txt?", or run
`/extract-docs <url>`. Example: `/extract-docs https://www.onorca.dev/docs`.

## What it needs

Nothing — keyless, stdlib-only Python, network access to the target site.
JS-rendered pages retry through your automate-browser skill when installed;
otherwise they're listed as not captured.

## How it works (high level)

1. **Probe the ladder** — checks for machine-readable manifests before ever
   crawling: `llms-full.txt` (whole docs, one fetch), `llms.txt`, per-page
   `.md` variants, `sitemap.xml`, and only then a bounded crawl capped at
   `--max-pages` (default 200).
2. **Fetch + convert** — scripts download each page and convert the main
   content to markdown deterministically; the model never pages through the
   site burning tokens.
3. **Index** — writes the manifest index that doubles as the refresh anchor.
   Re-run any time for a full re-extract, or use `--refresh` to apply only
   the delta (added/changed/removed pages) and get a report of what the
   vendor changed — useful as a docs changelog.
4. **Distill (optional)** — if something genuinely durable surfaced, offers
   one vault article via curate-vault.

The captured tree is deliberately disposable: it's a regenerable mirror, so
it lives with the project (not the vault) and carries no grooming debt.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
