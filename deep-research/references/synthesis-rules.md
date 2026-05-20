# Synthesis rules

Loaded by `SKILL.md` Step 6. Citation discipline + honesty rules that apply
uniformly across all 8 research-type templates (spec A12).

The single most important rule: **every claim in the report must trace to a
source the search actually surfaced.** If you can't link to it, don't write
it.

---

## 1. Citation discipline

### What needs a citation

- Numerical claims (market sizes, growth rates, prices, dates, counts).
- Named entities (companies, products, regulations, people) when stated as
  fact.
- Direct quotes (always).
- Claims about what a product does, a regulation requires, or a company
  has announced.
- Comparative claims ("X is bigger than Y", "X grew faster than Y").

### What does NOT need a citation

- Restating the user's question.
- Section headers and structural language.
- Synthesis statements that are clearly summarizing **multiple cited
  claims** in the same section (the citations for the underlying claims
  are enough; don't double-cite).
- Tautologies and definitions of common terms.

### How to cite

Two acceptable styles — pick whichever fits the section's density:

**Inline markdown link** — preferred for sparse citations:
> AT&T launched UnlimitedFiber Pro [in March 2026](https://example.com/news).

**Numbered footnotes** — preferred for dense paragraphs with multiple
claims:
> The market is estimated at $4.2B in 2026 [1], with three players
> controlling ~70% of new policy volume [2][3].

Footnotes map to the Sources list at the bottom of the report. Numbered
citations make denser paragraphs readable; inline links work better when
each claim has its own source.

### Citation atomicity

One claim, one citation. Don't pile three citations after a multi-claim
sentence — split it:

❌ "X has 200 employees, raised $50M, and shipped iOS support [1][2][3]."
✅ "X has 200 employees [1], raised $50M in 2025 [2], and shipped iOS
    support [3]."

---

## 2. Honesty rules

### Stay grounded

If a fact came from a source's summary, write it as the source said.
Don't extrapolate beyond the source. If you find yourself writing
*"this suggests..."* or *"it follows that..."* — stop. Either that
inference IS in the source (cite it) or it's yours (mark it explicitly
as **inferred**).

### Distinguish inference from fact

When you DO need to synthesize beyond what any single source says,
**mark it**:

```
*(inferred: combining [3] and [5], it appears that …)*
```

Or use a dedicated subsection like "Implications" inside a section.
Never present your synthesis as if it were a direct claim from a
source.

### Flag gaps; never invent

When the broad sweep + follow-up didn't surface anything substantive
for a section, write **exactly**:

```
(not surfaced in sources — see open questions)
```

Then add a corresponding entry to `open_questions`:

```
- <Section> couldn't be sourced from the current search; consider
  follow-up: "<a specific query that might fill it>".
```

This is more useful than a vague "couldn't find much". The reader
gets a query they can actually re-run.

### Disagreeing sources

When two cited sources disagree, surface the disagreement explicitly:

> Market size estimates vary: $4.2B per [Statista][1], $5.8B per
> [GrandViewResearch][2]. The discrepancy likely reflects different
> segment definitions — [1] excludes pet wellness plans, [2] includes
> them.

Don't pick one and pretend the other doesn't exist.

### Recency labels

When a fact has a date (e.g. "as of Q2 2026"), say so inline. When a
source is from 2023 or earlier, note it — research from 3+ years ago in a
fast-moving space should be flagged as such:

> Per a [2023 McKinsey report][4] *(note: dated)*, the market was $3.1B...

---

## 3. Source quality

Not all sources are equal. Skew the synthesis toward higher-tier sources
when they're available, and label tiers where it matters:

| Tier | Examples |
|---|---|
| **Primary / authoritative** | Company SEC filings, official gov docs, regulator publications, peer-reviewed papers, named-source press releases |
| **Secondary / reputable** | Industry analyst firms (Gartner, Forrester, Statista), major financial press (FT, Bloomberg, WSJ, Reuters), top-tier trade publications |
| **Community / observational** | Reddit, Hacker News, Product Hunt, GitHub discussions — useful for "what do practitioners say" but not for hard facts |
| **Unreliable** | Content farms, AI-generated summary sites, SEO listicles without bylines — **do not cite** unless they're the original source of a verbatim quote |

If a community-tier source is the only thing surfaced for a "fact", treat
it as anecdotal:

> Reddit threads suggest that X loses customers around the $50/mo tier
> ([r/foo discussion][7]) — anecdotal, not confirmed by company data.

---

## 4. Sourcing the report's "Sources" section

Render every source the report actually cites — no orphans, no unused
entries. Each entry includes:

- A descriptive title (not just the bare URL).
- The provider that surfaced it (`tavily`, `exa`, `websearch`,
  `webfetch`, or `trendscan`). This is honesty about HOW the source
  reached the report.
- The access date.

When a source was fetched in full (via `WebFetch`), note `WebFetch (full
page)` — the reader knows that citation pulls a heavier extract than a
search snippet would.

---

## 5. Citations vs. snippets

When you cite from a search snippet, you have a one- or two-sentence
extract. Don't quote more than was in the snippet. If the section needs
a fuller treatment of one specific source, **fetch the full page** in
Step 5 (focused follow-up) and re-cite from the full text.

A claim that says "according to X, the Y is Z" with no clear language
mapping to the snippet is over-extrapolating. Either match the snippet
or fetch the full page.

---

## 6. The "open questions" section

Open questions exist for three reasons:

1. **Surface gaps** that the search couldn't fill. Each is paired with
   a proposed follow-up query the user could re-run.
2. **Note ambiguities** in the sources (e.g. conflicting market sizes
   that aren't resolvable without primary research).
3. **Flag the limits of the run** — depth=quick deliberately under-
   covers some core sections; surface those in Open questions so the
   reader knows what to do next.

Each open question is one bullet. Be specific:

❌ "More research on pricing needed."
✅ "Public pricing tiers for enterprise plans weren't surfaced — try a
    follow-up at `site:example.com pricing` or contact-sales scraping."

---

## 7. Trendscan-sourced content

When a subquery was routed through `/trendscan` because of a recency
angle (Step 4), the items it returns get `"provider": "trendscan"` in
the sources JSON. The report should label these clearly — e.g. in a
"Community signals" subsection of `trends` or `gaps` — so the reader
understands they're discussion-derived, not authoritative.

---

## 8. The TL;DR

The TL;DR at the top of the report is the only place where you may
synthesize across sections without inline citations on every sentence
(the underlying section citations cover them). It must:

- Be ≤ 3 sentences for `--depth=quick`, ≤ 5 for `standard`, ≤ 8 for
  `exhaustive`.
- Restate the question's core answer first, then the most important
  qualifications.
- Mention any major gap ("note: pricing for enterprise tiers was not
  surfaced") so the reader knows up front what's missing.

A good TL;DR lets a reader who reads ONLY that paragraph leave with the
right mental model — including knowing what's NOT covered.
