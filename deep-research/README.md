# deep-research

**What it is:** a multi-pass research assistant. You ask "help me understand
X" — about a market, a product, a feature, a competitor, a regulation, an
opportunity — and you get back a structured, cited research report instead
of a vague summary.

## What you get

- `research-<slug>.md` — a structured markdown report. Sections vary by the
  research type the question landed in (e.g. for **market research**:
  market size, segmentation, growth drivers, key players, trends, risks; for
  **competitive analysis**: competitor table, positioning, pricing, recent
  moves). Every claim is cited inline.
- `research-<slug>.html` *(optional)* — a single self-contained HTML file
  (inline CSS) you can share or print.
- A brief summary on stdout: sources used, sections that came through
  cleanly, sections marked "not surfaced", and any open questions.

## How to run it

Just ask, e.g.:

- "research the pet insurance market in the US"
- "what are the options for serverless Postgres?"
- "dig into how Stripe handles SCA"
- "map out the AI inference startup landscape"
- "look into California's AB-2273 regulations"

You can also tune the run:

- `--depth=quick` — one broad sweep, ~5 sources, minutes.
- `--depth=standard` — broad sweep + focused follow-up, ~12–20 sources. (Default.)
- `--depth=exhaustive` — multi-pass, ~30+ sources, may take longer.
- `--type=<kind>` — force a specific research type (`market`, `competitive`,
  `feature`, `regulatory`, `product`, `problem`, `opportunity`, `landscape`).
  Default `auto` detects from your question.
- `--no-html` — markdown only.
- `--dry-run` — show the research plan without doing the search or writing
  any files. Useful to sanity-check angles before committing to an
  exhaustive run.

## What it needs

Optional but recommended:

- **`TAVILY_API_KEY`** and/or **`EXA_API_KEY`** in `~/.claude/skills/.env`.
  Either one unlocks SCRIPTS mode and higher-quality search.
- **`python3`** — same.

If neither key is present, the skill falls back to **NATIVE mode** using
Claude's built-in `WebSearch` / `WebFetch`. The artifact is the same; the
result quality may be lower because you lose Tavily's relevance ranking
and Exa's semantic search. The skill never blocks on missing keys.

## How it works (high level)

1. **Scope.** Classifies the question (research type + depth + recency
   axis). If it's secretly a single-fact lookup, the skill says so and gives
   you a one-line answer instead of a multi-pass research run. If it's
   secretly about *recent discussion*, it suggests `/scan-trends` instead.
2. **Plan.** Picks the section template for the research type and generates
   the right number of subquery angles for the chosen depth.
3. **Search.** Runs the subqueries through Tavily/Exa (SCRIPTS) or built-in
   WebSearch (NATIVE). When recency matters for one of the angles, it
   invokes `/scan-trends` instead of normal search — skill composition.
4. **Follow up** (standard/exhaustive depths). Finds gaps and chases them
   with targeted queries; fetches full content for the most cited sources.
5. **Synthesize.** Fills in the type template, citing every claim inline,
   labelling sections it couldn't source as "not surfaced" and pushing them
   into Open questions.
6. **Write.** Markdown always; HTML optionally via `scripts/report.py`.
   Never clobbers an existing file with the same slug.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `references/research-templates.md` — the 8 type templates (one section
  structure per research type).
- `references/synthesis-rules.md` — citation discipline and honesty rules.
- `handoff.md` — design decisions and the "why".
