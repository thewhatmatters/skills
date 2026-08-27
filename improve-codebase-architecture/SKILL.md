---
name: improve-codebase-architecture
description: Scans your codebase for shallow modules (per John Ousterhout's deep-module principle) and proposes deepening refactors as a markdown report (pass --html for a visual HTML version), then walks you through implementing whichever one you pick. User-invoked only — run it explicitly (e.g. "run improve-codebase-architecture" or "/improve-codebase-architecture"). Worth running every few days as an ongoing habit, not just once.
disable-model-invocation: true
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** —
refactors that turn shallow modules into deep ones. The aim is testability
and AI-navigability.

Adapted from Matt Pocock's `improve-codebase-architecture` skill
([mattpocock/skills](https://github.com/mattpocock/skills), MIT) — see
`NOTICE.md` in this directory. Demoed live in the AI Engineer workshop
captured at `/claude/best-practices/matt-pocock-ai-coding-workflow.md` in
the vault ("if you take one thing away from today, just try running this
skill on your repo").

This command is *informed* by the project's domain model and built on a
shared design vocabulary:

- Run the `codebase-design` skill for the architecture vocabulary
  (**module**, **interface**, **depth**, **seam**, **adapter**,
  **leverage**, **locality**) and its principles (the deletion test, "the
  interface is the test surface," "one adapter = hypothetical seam, two =
  real"). Use these terms exactly in every suggestion — don't drift into
  "component," "service," "API," or "boundary."
- The domain language in `CONTEXT.md` gives names to good seams (format:
  `references/CONTEXT-FORMAT.md`); ADRs in `docs/adr/` record decisions
  this command should not re-litigate (format: `references/ADR-FORMAT.md`).

## Process

### 0. Preflight dependencies

```bash
python3 ~/.cursor/skills/scripts/preflight-deps.py --skills=codebase-design,grilling
```

Both siblings are hard dependencies (the vocabulary source; the Step-3
interview loop). If the helper itself is missing, treat both deps as
`gated` and continue with the degrades below (spec A11). On `gated`,
interactive runs offer *Fix it for me (git pull in ~/Development/skills) / I'll do it
myself / Skip* (spec A7c); on Skip or fix failure — and always under
`--agent` — degrade rather than block (spec A7d): missing
`codebase-design` → use the vocabulary summary inlined above (the intro's
term list) and flag the drift risk in the report header; missing
`grilling` → produce the report, and at Step 3 fall back to a plain
one-question-at-a-time conversation with the same intent.

### 1. Explore

Read the project's domain glossary (`CONTEXT.md`) and any ADRs in
`docs/adr/` covering the area you're touching first, if they exist.

Then use the Agent tool with `subagent_type=Explore` to walk the codebase
(fall back to `general-purpose` if `Explore` isn't available in the current
harness; if the Agent tool itself is unavailable — e.g. this skill is
already running inside a subagent — explore inline in the main session:
degrade, never block). Don't follow rigid heuristics — explore organically and note
where you experience friction:

- Where does understanding one concept require bouncing between many small
  modules?
- Where are modules **shallow** — interface nearly as complex as the
  implementation?
- Where have pure functions been extracted just for testability, but the
  real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their
  current interface?

Apply the **deletion test** to anything you suspect is shallow: would
deleting it concentrate complexity, or just move it? A "yes, concentrates"
is the signal you want.

### 2. Present candidates as a report

Default output is **markdown, presented directly in the conversation**;
pass `--html` for the visual HTML report instead.

**Markdown (default).** One `##` section per candidate carrying the fields
below. Before/after structure goes in fenced ` ```mermaid ` blocks when the
relationships are graph-shaped (call graphs, dependencies, sequences), else
a compact before/after table or indented tree — never pad with decoration
markdown can't carry. No file is written; the report is the chat output.

**HTML (`--html`).** Write a self-contained HTML file to the OS temp
directory so nothing lands in the repo. Resolve the temp dir from
`$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to
`<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh
file. Open it for the user — `xdg-open <path>` on Linux, `open <path>` on
macOS, `start <path>` on Windows — and tell them the absolute path. The
report uses **Tailwind via CDN** for layout and styling, and **Mermaid via
CDN** for diagrams where a graph/flow/sequence reliably communicates the
structure. Mix Mermaid with hand-crafted CSS/SVG visuals — Mermaid for
graph-shaped relationships, hand-built divs/SVG for editorial visuals
(mass diagrams, cross-sections, collapse animations). Each candidate gets
a **before/after visualisation**. Be visual. See
[references/HTML-REPORT.md](references/HTML-REPORT.md) for the full HTML
scaffold, diagram patterns, and styling guidance.

For each candidate, render a section (markdown) or card (HTML) with:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and how
  tests would improve
- **Before / After diagram** — illustrating the shallowness and the
  deepening (side-by-side custom-drawn in HTML; mermaid/table in markdown)
- **Recommendation strength** — one of `Strong`, `Worth exploring`,
  `Speculative` (a badge in HTML, bold inline in markdown)

End the report with a **Top recommendation** section: which candidate
you'd tackle first and why.

**Use `CONTEXT.md` vocabulary for the domain, and the `codebase-design`
vocabulary for the architecture.** If `CONTEXT.md` defines "Order," talk
about "the Order intake module" — not "the FooBarHandler," and not "the
Order service."

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface
it when the friction is real enough to warrant revisiting the ADR. Mark it
clearly in the card (e.g. a warning callout: *"contradicts ADR-0007 — but
worth reopening because…"*). Don't list every theoretical refactor an ADR
forbids.

Do NOT propose interfaces yet. After the report is presented, ask the
user: "Which of these would you like to explore?"

Under `--agent`: produce the report as normal (under `--html`, write the
file and report its absolute path — skip the auto-open; a headless run has
no browser to open into), then stop — skip the selection prompt and the
rest of this process (Step 3 requires a live human pick and a live
`grilling` conversation; neither has a non-interactive form).

### 3. Grilling loop

Once the user picks a candidate, run the `grilling` skill to walk the
design tree with them — constraints, dependencies, the shape of the
deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize. `CONTEXT.md` edits and
ADR offers are both writes to real repo files, but they're gated
differently on purpose: `CONTEXT.md` edits happen silently, inline, because
they occur *inside* the live `grilling` conversation the user is actively
steering — the user sees and can redirect every naming choice as it's typed,
the same way they'd catch a typo in the agent's own chat message. An ADR is
different: it's a new file the user hasn't been asked about yet, so it gets
an explicit offer before it's written.

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add
  the term to `CONTEXT.md`, following
  [references/CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md). Create the
  file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md`
  right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR,
  framed as: *"Want me to record this as an ADR so future architecture
  reviews don't re-suggest it?"* Only offer when the reason would actually
  be needed by a future explorer to avoid re-suggesting the same thing —
  skip ephemeral reasons ("not worth it right now") and self-evident ones.
  Format and the three-part offering test are in
  [references/ADR-FORMAT.md](references/ADR-FORMAT.md).
- **Want to explore alternative interfaces for the deepened module?** Run
  the `codebase-design` skill and use its design-it-twice parallel
  sub-agent pattern (`references/DESIGN-IT-TWICE.md` there).

## Conventions this skill follows

- Spec is `~/.cursor/skills/skill-architecture.md`.
- **`WHY.md`:** read before changing this skill's design. After a run that locks a non-obvious choice (went unusually well or badly, reason not already in SKILL.md), append a dated line. Skip routine runs. Cross-project lessons go to `/curate-vault`.
