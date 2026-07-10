# deep-research — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-19  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
A multi-pass research engine that scopes a question, sweeps and follows up
across the web (with Tavily/Exa keys or Claude's built-in search), and
synthesizes a cited markdown report — optionally with a self-contained HTML
companion.

## 2. Reusable patterns (link to spec A1..A13)
This skill follows `~/.claude/skills/skill-architecture.md` patterns A1–A13;
note here any deliberate deviations.

Notable choices:

- **Composes with `/scan-trends`, doesn't import it.** When the research
  question has a recency angle ("what are people saying lately about X"),
  the skill's Step 4 invokes `/scan-trends` via standard skill composition for
  that subquery — no cross-skill Python imports. Each skill stays
  self-contained. SKILL.md "Conventions" makes this explicit.
- **Dual-mode is real, not aspirational.** SCRIPTS mode uses Tavily/Exa for
  quality; NATIVE mode uses Claude's built-in `WebSearch` + `WebFetch` and
  produces **the same artifact**. NATIVE is a real fallback, not a
  degraded-by-design path (spec A3 + A7d).
- **`KEYS_MISSING` is a Recoverable Setup Gate but NEVER blocks.** The gate
  offers *Set keys / Proceed in NATIVE / Cancel*. Even if the user cancels
  the key prompt, the graceful-dead-end is automatic — NATIVE still works.
  This contrasts with scan-trends's tighter coupling to specific providers.
- **Anti-overtrigger guard at Step 1.** The description is intentionally
  aggressive on triggering (per the user's spec). Step 1 acts as the
  countermeasure: a quick scope assessment that gracefully exits for single-
  fact lookups and suggests `/scan-trends` when the real question is about
  recent discussion.
- **8 research-type templates, loaded on demand.** Section structures for
  market / competitive / feature / regulatory / product-eval / problem-
  solving / opportunity / landscape live in `references/research-
  templates.md` (spec A1 progressive disclosure).
- **Synthesis rules separated** into `references/synthesis-rules.md` —
  citation discipline, honesty rules, gap-flagging conventions live in one
  place so they apply uniformly across all 8 templates.
- **No clobber on output filenames.** Re-running on the same slug writes
  `research-<slug>-2.md`, `-3.md`, … (spec A11 layered fallback applied to
  filenames, same convention as `generate-prd`).
- **Fan-out sweep (2026-07-03) — parallel gathering, serial synthesis.** At
  `exhaustive` depth (opt-in at `standard` via `--parallel`) Step 4 fans the
  sweep out to parallel general-purpose subagents, one per angle, governed by
  `references/agent-fanout.md` (brief template + findings JSON contract).
  Why: wall-clock (angles run concurrently) and — the bigger win — context
  isolation: agents burn their own context reading pages and return only
  distilled cited findings, keeping the main context fresh for synthesis.
  Hard boundaries: gap analysis and synthesis never delegate; recency angles
  stay in the main session (`/scan-trends` gates are interactive); degrades
  to the serial sweep whenever the `Agent` tool is unavailable (spec A3).
  Rejected: Workflow-tool orchestration (heavier dependency than the task
  needs) and fan-out at `quick` (overhead exceeds the win). "Specialists"
  are prompt-made — each agent's brief embeds its angle + the template
  sections it feeds; there are no per-domain agent definitions to maintain.
- **No DDG fallback inside `search.py`.** When neither Tavily nor Exa is
  available, the skill drops to NATIVE mode and uses Claude's
  `WebSearch` — *not* a third Python provider tier. This keeps `search.py`
  focused and avoids the bot-block fragility scan-trends's handoff §6
  documents on the dev machine's DDG endpoint.

## 3. Decision log
- 2026-05-19: scaffolded by generate-skill (formal `/generate-skill`
  invocation).
- 2026-05-19: Tavily/Exa keys both present in `~/.claude/skills/.env`
  (verified at scaffold time via `_env.load()` + `os.environ` presence
  check — no values printed). Both will be available in SCRIPTS mode.
- 2026-05-19: self-audited via audit-skill (--agent): 0 critical, 1
  important, 2 nice — all fixed before commit:
  - 🟠 `--transcript` had no resolution path → added one at Step 1.
  - 🟡 SKILL.md preflight table duplicated the script docstring → collapsed
    to a compact list.
  - 🟡 shared `.env.example` "Used by:" notes were stale → updated to list
    `scan-trends, deep-research` for TAVILY/EXA (done; see §6).

- 2026-07-03: added the parallel fan-out sweep — SKILL.md Steps 4–6 +
  `--parallel`/`--no-parallel` flags + new `references/agent-fanout.md`;
  README updated. No script changes (fan-out is model-orchestrated via the
  Agent tool). Not yet exercised on a real run — `/refine-skill
  deep-research` after the first parallel run.

## 4. Known limitations / environment caveats
- NATIVE mode (no python3 or no keys) produces the same artifact but search
  quality may differ — Tavily's ranking and Exa's semantic match are
  generally better than `WebSearch` for research-grade queries.
- Search.py uses `requests` (already in the environment via scan-trends); no
  new dependency added.
- Trendscan handoff §6 documents a DDG 202-challenge on this dev machine —
  not relevant to deep-research, since we don't include a DDG path here.
- Tavily/Exa rate limits apply to SCRIPTS mode; the skill doesn't enforce
  caching/dedupe across runs (each invocation makes fresh calls).
- Fan-out multiplies token spend roughly with agent count, and agents in a
  round can't see each other's results — cross-angle awareness only lands
  at the central barrier (agent-fanout.md §3). Mitigated by the Step-5
  follow-up round; accepted as the price of parallelism.

## 5. Audit rubric coverage
See `skill-architecture.md` §B. Items expected to be N/A or special for
this skill:

- **A8 user scope control** — implemented via `--type`, `--depth`,
  `--no-html`, `--transcript`. No multi-source picker because both Tavily
  and Exa hit broadly the same web; the meaningful scope axes are type and
  depth.
- **Setup Gate (A7)** — `KEYS_MISSING` is a real gate, but spec A7d
  graceful-dead-end is automatic via NATIVE mode. No "fix it for me" auto-
  install option for keys (the user must add them to `~/.claude/skills/.env`
  themselves; the skill prints a paste-ready block).

## 6. Notes
Composes with `/scan-trends` for recency; uses Tavily/Exa via the shared
`~/.claude/skills/.env`; NATIVE fallback via built-in `WebSearch` keeps the
skill working keyless.

The shared `.env.example`'s `TAVILY_API_KEY` / `EXA_API_KEY` "Used by:"
notes now read `scan-trends, deep-research` (updated 2026-05-19 as part of the
post-audit cleanup). The skill itself never edits the shared file — this was
a manual maintainer touch.
