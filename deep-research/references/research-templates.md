# Research-type templates

Loaded by `SKILL.md` Step 3 / Step 6. Progressive disclosure (spec A1) — the
type templates and the internal JSON shape stay here so the main SKILL.md
keeps the lean orchestration path.

---

## 1. Internal JSON shape

Step 6 synthesis fills in this structure (held by the model; same JSON gets
piped into `scripts/report.py` for the HTML render).

```
{
  "title":  "<short label for the research question>",
  "slug":   "<kebab — used in filenames>",
  "date":   "<YYYY-MM-DD>",
  "type":   "market | competitive | feature | regulatory | product | problem | opportunity | landscape",
  "depth":  "quick | standard | exhaustive",
  "question": "<the question the user asked, verbatim>",
  "summary": "<one-paragraph TL;DR>",
  "sources": [
    {"id": 1, "url": "...", "title": "...", "provider": "tavily|exa|websearch|webfetch|scan-trends",
     "accessed": "<YYYY-MM-DD>"},
    ...
  ],
  "sections": {
    "<section_key_1>": "<markdown body with inline [n] or [link](url) citations>",
    "<section_key_2>": "...",
    ...
  },
  "open_questions": ["...", "..."]
}
```

Section keys depend on the research type (see §2 below). Bodies are
markdown, free-form within the section's purpose, but every claim carries
an inline citation. Sections with no signal from the search are written
verbatim as `"(not surfaced in sources — see open questions)"`.

---

## 2. Type templates

One section structure per research type. Pick by `--type` (or auto-detect at
Step 1). Sections marked **(core)** are required by spec — if there's no
signal for a core section, emit the "not surfaced" placeholder and push the
gap into `open_questions`. Sections marked *(optional)* are emitted only if
the search produced meaningful content.

### 2.1 `market` — Market research

Use when the user asks about a market category, segment, or industry.

| Section key | Title | Purpose |
|---|---|---|
| `market_size` *(core)* | Market size | TAM / SAM / SOM where defensible, year, source |
| `segmentation` *(core)* | Segmentation | Who the customers are, sliced by 1–3 useful axes |
| `growth_drivers` *(core)* | Growth drivers | What's pushing the market up or down |
| `key_players` *(core)* | Key players | 3–10 main companies, brief positioning |
| `customer_needs` | Customer needs | Recurring pains the market is forming around |
| `trends` | Trends | Directional shifts (12–24 month horizon) |
| `risks` | Risks | Headwinds: regulatory, structural, technology |

**Starter subquery angles for the broad sweep:** "<topic> market size",
"<topic> market segmentation", "<topic> growth drivers", "<topic> key
players", "<topic> trends 2026", "<topic> market risks".

### 2.2 `competitive` — Competitive analysis

Use when the user wants to map who's playing in a space and how.

| Section key | Title | Purpose |
|---|---|---|
| `competitor_table` *(core)* | Competitor table | One row per competitor: name, positioning, pricing, recent moves |
| `positioning_map` *(core)* | Positioning map | How the players differentiate (in prose; an axes-diagram is overkill in markdown) |
| `pricing` *(core)* | Pricing | Public pricing tiers, free tier policies, enterprise notes |
| `strengths_weaknesses` *(core)* | Strengths & weaknesses | Per-competitor or per-cohort |
| `recent_moves` | Recent moves | Funding rounds, launches, M&A, leadership changes |
| `gaps` | Market gaps | Where coverage is thin / underserved |

**Starter subquery angles:** "<topic> competitors", "<topic> pricing",
"<topic> alternatives", "<topic> vs X", "<topic> recent funding", "<topic>
market gaps", site:product-hunt.com|crunchbase.com|github.com angles.

### 2.3 `feature` — Feature exploration

Use when the user asks "what are the options for X" — exploring an
implementation/feature space.

| Section key | Title | Purpose |
|---|---|---|
| `state_of_the_art` *(core)* | State of the art | What the dominant approaches are today |
| `options` *(core)* | Options | 3–7 approaches with one-line summary each |
| `build_vs_buy` *(core)* | Build vs. buy | Honest assessment per option |
| `gotchas` *(core)* | Gotchas | Common failure modes, hidden costs |
| `recommendation` *(optional)* | Recommendation | Only if the question implies a decision is wanted |

**Starter subquery angles:** "<feature> approaches", "<feature> open
source", "<feature> SaaS", "<feature> vendor comparison", "<feature> common
pitfalls", "<feature> implementation guide".

### 2.4 `regulatory` — Regulatory deep-dive

Use for compliance, legal, policy research.

| Section key | Title | Purpose |
|---|---|---|
| `applicable_laws` *(core)* | Applicable laws / regulations | Full names, jurisdictions, effective dates |
| `key_bodies` *(core)* | Key bodies | Who enforces, who issues guidance |
| `compliance_requirements` *(core)* | Compliance requirements | What an actor must do, concretely |
| `penalties` *(core)* | Penalties for non-compliance | Fines, criminal, civil |
| `recent_changes` | Recent changes | Last 12 months: amendments, new guidance |
| `gray_areas` | Gray areas | Where reasonable people disagree |

**Always cite the regulation by its statutory name** and link to the
official source (gov, EU/EEA, national gazette). Synthesis rules apply
extra strictly here.

**Starter subquery angles:** "<topic> regulation <jurisdiction>", "<topic>
compliance requirements", "<topic> enforcement actions", "<topic> recent
amendments", "<topic> guidance document".

### 2.5 `product` — Product evaluation

Use when the user is evaluating ONE product (vs. competitive's many).

| Section key | Title | Purpose |
|---|---|---|
| `capabilities` *(core)* | Capabilities | What it does, by category |
| `pricing` *(core)* | Pricing | Tiers, free policies, enterprise |
| `integrations` | Integrations | Important ones; mark "supported" vs "via Zapier" etc |
| `fit_assessment` *(core)* | Fit assessment | When this product is the right answer; when it isn't |
| `gotchas` *(core)* | Gotchas | Real user complaints from forums, churn signals, scaling cliffs |
| `alternatives` | Alternatives | 2–4 substitutes worth knowing |

**Starter subquery angles:** "<product> features", "<product> pricing",
"<product> review", "<product> vs", "<product> limitations", "<product>
complaints" (Reddit, HN — consider `/scan-trends` for this angle).

### 2.6 `problem` — Problem-solving research

Use when the user has a problem and wants to map the option space.

| Section key | Title | Purpose |
|---|---|---|
| `framing` *(core)* | Problem framing | Restate the problem in concrete terms; surface hidden assumptions |
| `options` *(core)* | Options | 3–6 approaches with tradeoffs |
| `tradeoffs` *(core)* | Tradeoffs | Comparison table or prose; cost / time / risk / fit |
| `recommendation` *(core)* | Recommendation | A defensible call with caveats |
| `precedents` | Precedents | "Companies who did X / how it went" |

**Starter subquery angles:** "how do companies solve <problem>", "<problem>
playbook", "<problem> postmortem", "<problem> best practice", "<problem>
case study".

### 2.7 `opportunity` — Opportunity assessment

Use for "is there a business here?" / "should we build X?" framings.

| Section key | Title | Purpose |
|---|---|---|
| `market_size` *(core)* | TAM / SAM / SOM | Honest, sourced; admit when fuzzy |
| `customer_pain` *(core)* | Customer pain | Evidence the pain exists and is severe enough to act on |
| `competitive_landscape` *(core)* | Competitive landscape | Who's in this space; where's the white space |
| `barriers_to_entry` *(core)* | Barriers to entry | Capital, regulatory, network effects, distribution |
| `recommended_angle` | Recommended angle | If/where to enter, and why |
| `timing` | Timing | Is now the right moment? What signals say yes/no? |

**Starter subquery angles:** "<topic> market size", "<topic> customer
pain", "<topic> competitive landscape", "<topic> barriers", "why now
<topic>", "<topic> startup landscape".

### 2.8 `landscape` — Landscape mapping

Use when the user wants the full picture of who's doing what in a space.

| Section key | Title | Purpose |
|---|---|---|
| `categories` *(core)* | Categories | Natural groupings of players (3–6 buckets) |
| `players_by_category` *(core)* | Players by category | One subsection per category, with 2–8 players each |
| `white_space` *(core)* | White space | Where coverage is thin or missing |
| `notable_recent_entrants` | Notable recent entrants | New companies in the last 12–24 months |
| `key_questions` | Key questions | The questions a buyer or builder should answer next |

**Starter subquery angles:** "<topic> landscape", "<topic> market map",
"<topic> categories", "<topic> startup landscape", "<topic> ecosystem".

---

## 3. Auto-detect heuristics for `--type=auto`

When `--type` is not specified, infer from the question's phrasing. Tie-
breakers default to the LEFT column.

| Keywords / patterns in the question | → type |
|---|---|
| "market", "industry", "TAM", "market size", "category" | `market` |
| "competitors", "competitive", "vs", "alternatives to", "who else does" | `competitive` |
| "options for", "approaches to", "how do people do X", "best way to" | `feature` |
| "regulation", "compliance", "law", "GDPR/HIPAA/SOC2/etc.", "policy" | `regulatory` |
| "evaluate <ProductName>", "is <ProductName> good", "<ProductName> review" | `product` |
| "how should we", "what should we do about", "problem with", "stuck on" | `problem` |
| "opportunity", "should we build", "is there a business in", "is X worth doing" | `opportunity` |
| "landscape", "map of", "ecosystem", "who's doing X" | `landscape` |

If nothing matches confidently, default to `landscape` — it's the broadest
shape and most forgiving when the question is fuzzy.

---

## 4. Output markdown layout (Step 7)

Write `<out>/research-<slug>.md` with this layout. Section keys/titles come
from the chosen type template in §2.

```
# <title>

> **<type> research · depth: <depth> · <date>** — <one-line summary>

**Question.** <verbatim question>

**TL;DR.** <one-paragraph summary>

## <Section Title 1>
<markdown body with inline [1](url) citations>

## <Section Title 2>
...

## Open questions
- ...
- ...

---

## Sources
1. [<title>](<url>) — <provider>, accessed <date>
2. ...
```

Citation style: inline markdown links `[descriptive text](url)` for short
attributions, or numbered footnotes `[1]` that map to the Sources list at
the bottom for denser sections. Either is acceptable; the renderer treats
both as links.

---

## 5. HTML render — input/output contract (Step 8)

`scripts/report.py` reads the §1 JSON on stdin and produces one
self-contained HTML file (inline CSS, escaped content, light/dark friendly)
rendering title, question, TL;DR, all sections, open questions, and the
sources list with clickable links.

Required JSON keys: `title`, `date`, `type`, `summary`, `sections`,
`sources`. The script validates these and exits with a clear FATAL message
if any are missing.

User-derived strings are HTML-escaped only. Literal `{...}` in research
content (pseudocode, JSON examples, regex) is safe because `.format()`
substitutes replacement values verbatim and never re-parses them — values
must not be brace-doubled, or `{{...}}` leaks into the rendered page.
Same contract as generate-prd's report.py.

---

## 6. Provider-meta in the sources list

Every source carries a `provider` field. Render the provider as a small
muted tag next to each source. The full set:

| `provider` value | Render label |
|---|---|
| `tavily` | Tavily |
| `exa` | Exa |
| `websearch` | WebSearch |
| `webfetch` | WebFetch (full page) |
| `scan-trends` | via /scan-trends |

This is honesty discipline (spec A12): the reader sees where each citation
came from, including the difference between a search-snippet citation and
a full-page WebFetch.

---

## 7. Section selection by depth

| Depth | Sections written |
|---|---|
| `quick` | Only the **(core)** sections of the type template, plus Open questions |
| `standard` | All sections of the type template that have content; "not surfaced" placeholder for empty core sections |
| `exhaustive` | All sections, all core gaps surfaced as Open questions with proposed follow-up queries |

---

## 8. Anti-overtrigger fallback shapes

Step 1's bail paths emit one of three short outputs (no file written):

**Single-fact lookup:**
```
this looks like a quick fact, not deep research.
answer: <one sentence with a citation>
(if you want a deeper dive, say so explicitly.)
```

**Recency-focused → /scan-trends:**
```
this question is fundamentally about recent discussion of <topic>.
/scan-trends is a better fit. invoke it with:
  /scan-trends <topic> --days=<N>
(re-run /deep-research if you want an evergreen treatment instead.)
```

**Out-of-scope:**
```
deep-research is for evergreen + structured research on topics, markets,
products, etc. this question doesn't seem to fit. answering directly:
<one-paragraph response>
```

Step 9 (Emit) does NOT print for these bail paths — they replace the full
flow.

---

## 9. Dry-run summary shape (Step 3)

When `--dry-run` is set, Step 3 prints something like this and stops:

```
DRY RUN — no search, no files written

question:  "research the pet insurance market in the US"
type:      market   (auto-detected)
depth:     standard
out:       /Users/you/research-pet-insurance-us.md  (+.html)

research plan (8 subquery angles):
  1. pet insurance market size US 2026
  2. pet insurance market segmentation US
  3. pet insurance growth drivers US
  4. pet insurance key players US
  5. pet insurance customer needs US
  6. pet insurance trends US 2026
  7. pet insurance risks US
  8. pet insurance regulatory US

after broad sweep, follow-up phase will issue 3–5 targeted queries
to fill gaps. re-run without --dry-run to execute.
```
