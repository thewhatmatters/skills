# extract-docs — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-07-17  ·  Generator: generate-skill @ CC 2.1.181

## 1. Purpose

Extract a documentation site into per-page markdown via an acquisition
ladder, landing in the project's `docs/sources/<vendor>/` — with an optional
single distilled vault article through curate-vault's gate.

## 2. Reusable patterns (link to spec A1..A15)

This skill follows `~/.claude/skills/skill-architecture.md` patterns A1–A15;
note here any deliberate deviations.

- **A10 deviation (deliberate):** the "self-contained artifact" is the
  `<dest>/index.md` manifest, not a single HTML file — the run's product IS
  a file tree, and the index records request, date, tier, and results. No
  `report.py`.
- **A15:** all composes are soft (automate-browser, curate-vault,
  ingest-source) with documented "if available" fallbacks — no hard deps,
  hence no `preflight-deps.py` wiring.

## 3. Decision log
- 2026-07-18: Added `--refresh` (scripts/refresh.py) — delta refresh for existing mirrors: added/changed/removed classification by source-comment URL + normalized-body hash (frontmatter and extracted-date excluded so re-runs converge); changed pages keep local OKF frontmatter verbatim; full manifest still fetched (the win is write-churn + the delta report as vendor changelog). Also to_markdown now backticks bare HTML/JSX tags left in prose (Obsidian render safety; unit-tested, idempotent) — motivated by 49 hazard candidates in the first Next.js mirror.


- 2026-07-17: scaffolded by generate-skill; self-audit (skill-auditor) found
  0 HIGH / 1 MEDIUM — probe.py pre-truncated manifests to `--max-pages`,
  making SKILL.md's scope gate unreachable (a silent cap the 54-page live
  test couldn't expose). Fixed same run: probe now emits the FULL manifest
  + true count; enforcement lives with the model's gate decision and
  fetch.py's `--max-pages`. Also fixed: fetch.py hard-crashed on a bad
  manifest (now `{"error": ...}` + exit 1), stale `--discover` docstring,
  misleading sitemap note under forced `--tier`.
- 2026-07-17 — **Project docs, never the vault, as the bulk destination.**
  The original idea was "extract a docs site into the vault"; assessed and
  redirected before building: a wholesale dump conflicts with the vault's
  per-article gate (200 confirmations or a bypass), the derivability rule
  (vendor docs are canonical elsewhere), groom-by-verification economics
  (mirrors rot fast), and index blurb economy. The vault gets at most ONE
  distilled article, through curate-vault. Rationale article:
  `/claude/best-practices/vault-ops/groom-by-verification-not-age.md` (vault).
- 2026-07-17 — **Manifest-first ladder over crawling.** Live probe of
  onorca.dev during design: no llms.txt at any location, no per-page `.md`
  variants, but sitemap.xml enumerated all 54 docs pages — validating that
  most sites resolve at a manifest tier and the crawl tier is a genuine
  last resort. Scripts do all fetching/conversion; the model never pages
  through a site.
- 2026-07-17 — **Stdlib-only HTML→md converter** (html.parser), per the
  house dependency discipline — no html2text/bs4 requirement for the core
  path. Good-enough conversion (headings, paragraphs, lists, code, links,
  tables) beats a dependency; automate-browser covers the JS-rendered tail.

- 2026-07-17 — **Converter v2 after the first full-site test run** (54-page
  onorca.dev extraction + an agent-driven quality review): the root page
  maps to `home.md` (the manifest owns `index.md` — collision lost a page
  in run 1); `<head><title>` no longer leaks into the body and is promoted
  to an H1 when the page has none; tables get their `| --- |` separator
  row; `<p>` close emits a real paragraph break; images become
  `*[image: alt]*` placeholders (assets aren't mirrored); same-site docs
  links are rewritten to relative local `.md` paths so the mirror is
  navigable offline. All verified in a clean re-run: 54/54 fetched, tables
  render, cross-directory `../` links resolve, zero unrewritten
  same-site links.

## 4. Known limitations / environment caveats

- The stdlib converter is pragmatic, not perfect: complex tables, tabbed
  code groups, and MDX components degrade to plain text. Acceptable for a
  regenerable mirror.
- `robots.txt` is honored at the crawl tier only; manifest tiers (llms.txt,
  sitemap) are published for machine consumption.
- Sites that soft-404 (SPA returning 200 with empty shells) surface as
  `empty` pages → automate-browser retry tier.

## 5. Audit rubric coverage

See `skill-architecture.md` §B; this skill targets every PASS that applies.

## 6. Notes

Composes with automate-browser (JS-heavy fallback), ingest-source
(single-URL cousin; shares the docs/sources/ destination convention),
curate-vault (owns the only vault write path). Soft deps per A15c.
