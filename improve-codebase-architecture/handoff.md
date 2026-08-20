# Handoff — improve-codebase-architecture

_Created 2026-07-10_

## What this is

The primary deliverable of a session that ingested Matt Pocock's AI
Engineer workshop talk into the vault
(`/claude/best-practices/matt-pocock-ai-coding-workflow.md`), then went
looking for his actual `improve-codebase-architecture` skill instead of
reinventing it from the talk's verbal description alone. Found it public
and MIT-licensed at `github.com/mattpocock/skills` — considerably more
mature than the talk implied (deletion test, four-way dependency
classification, HTML report with before/after diagrams, deferred interface
design, design-it-twice). Vendored and adapted rather than rebuilt from
scratch. Sibling skills from the same pass: `codebase-design`, `grilling`.

## Decisions

- **Hard-dep preflight via the shared helper (2026-07-16).** Step 0 now runs
  `~/.cursor/skills/scripts/preflight-deps.py --skills=codebase-design,grilling`
  (spec A15): both siblings are hard deps — vocabulary source and the Step-3
  loop — gated with an A7c fix offer and documented degrades (inline
  vocabulary + drift flag; plain interview). Step 1 gained the
  Agent-tool-unavailable inline-exploration fallback, and `--agent --html`
  no longer auto-opens a browser (headless has none).
- **Markdown report by default, `--html` opt-in (2026-07-15).** The source
  skill always writes an HTML file; the user asked that report-emitting
  skills default to markdown in-conversation with HTML as an option. The
  HTML path (and `references/HTML-REPORT.md`) is unchanged when opted into;
  markdown mode renders one section per candidate with mermaid fenced
  blocks or before/after tables, and writes no file.
- **Vendor + adapt**, chosen by the user over a from-scratch simplified
  version or a full 4-skill port (see the three-option `AskUserQuestion` in
  this session). Rationale in `codebase-design/handoff.md`.
- **`disable-model-invocation: true`, kept from the source.** This is a
  deliberate first real use of that field in this skill suite — as of this
  session, every other skill here is model-invoked (confirmed via grep: no
  skill in `~/.cursor/skills/*/SKILL.md` sets this field before now). The
  reasoning: this skill spawns an Explore subagent over the whole codebase
  and can spawn 3+ more via design-it-twice, writes a file, and opens it in
  the browser — a real-token-cost, real-side-effect operation that
  shouldn't fire from an ambiguous prompt. This also matches Matt's own
  choice in the source and the generator's own A14 heuristic
  ("side-effectful / outward / timing-sensitive... → user-invoked"). Note:
  this doesn't resolve the open trigger-mode decision noted in a prior
  session's handoff for `announce-conan-release` / `wire-vault` /
  `automate-browser` — those are separate, still-open decisions.
- **`domain-modeling` not ported as a full skill** — see
  `codebase-design/handoff.md` and this skill's `NOTICE.md`. Only the two
  format references it needs (`CONTEXT-FORMAT.md`, `ADR-FORMAT.md`) were
  copied in.
- **Cross-skill references use plain names** ("the `codebase-design`
  skill"), not the source's slash-command style — matches how this suite's
  other skills reference each other (e.g. wire-vault ↔ curate-knowledge).

## Self-audit (2026-07-10, same session)

Ran a `skill-auditor` fan-out over all three new skills right after writing
them. `grilling` came back clean. `codebase-design` and this skill each had
findings — all fixed in this session:

- **codebase-design**: LATENT — frontmatter description had an unquoted
  `: ` mid-line that fails strict `yaml.safe_load` (lenient harness parse
  still recovered it, per the vault gotcha
  `/claude/best-practices/lenient-frontmatter-hides-invalid-yaml.md`) —
  fixed by folding with `>-`. LOW — "Boundary" avoid-note was duplicated
  verbatim in both the glossary and Rejected framings — fixed by keeping it
  only in the glossary entry.
- **improve-codebase-architecture** (this skill): MEDIUM — the `--agent`
  behavior at the Step 2→3 boundary (report generation vs. the interactive
  selection prompt + grilling handoff) was undocumented — fixed, Step 2 now
  states `--agent` stops after writing/opening the report. MEDIUM — the
  `CONTEXT.md` inline-write bullets sat next to the ADR offer-first bullet
  with no stated reason for the different consent treatment — fixed by
  adding an explicit rationale (CONTEXT.md edits happen inside a live,
  user-steered `grilling` conversation; an ADR is a new file the user
  hasn't been asked about). LOW/polish — the frontmatter `description` used
  the suite's trigger-rich style (quoted example phrases) despite being
  user-invoked, where per spec A14 the description never reaches the model
  and should read as plain human-facing text instead — trimmed. Two minor
  polish items also picked up: an `Explore`-subagent-unavailable fallback
  note, and the HTML report header now records the run's scope.

Not re-run after fixes — the fixes are small, mechanical, and each traces
directly to one auditor finding; re-running the fan-out for confirmation
would be reasonable before treating this as fully closed, per the vault's
`/claude/best-practices/verify-fanout-findings.md` discipline, but wasn't
done in this session.

## Not done / next steps

- **No live run yet.** This skill has not been exercised end-to-end against
  a real codebase — everything here is adapted from source text and cross-
  checked for internal consistency (link paths, skill-name references), but
  not verified by actually invoking it. Recommend running it on a real
  project before trusting the HTML report output blindly.
- ~~Self-audit not yet run~~ — done 2026-07-16: a `skill-auditor` pass
  found no HIGHs; its MEDIUMs (stale README, gate missing the A7c offer)
  were fixed the same day.
- ~~Not yet added to the vault's skill-catalog~~ — done (catalog row
  updated 2026-07-15 for the markdown-default report).
- ~~Not yet committed~~ — committed and pushed (7abd99e onward; repo is
  `github.com/thewhatmatters/claude`, skills live under `skills/`).
