# craft-claude — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-06-16  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
Author, audit, and maintain a project's CLAUDE.md and its memory/rules
ecosystem against verified Claude Code mechanics.

## 2. Reusable patterns (link to spec A1..A13)
This skill follows `~/.claude/skills/skill-architecture.md` patterns A1–A13.
Mirrors the repo's **spec-bound** pattern: just as `skill-architecture.md` is
the canon for `audit-skill`/`generate-skill`, `references/claude-md-spec.md` is
the canon both AUTHOR and AUDIT modes reference (do not duplicate its rubric in
SKILL.md — A1). Deliberate notes:
- Dual-mode + degraded ladder (A3): SCRIPTS (probe.py) vs NATIVE (hand-probe).
  Never `down` — it's a local file transform.
- A7 consent gate on every CLAUDE.md write, same posture as `ingest-source`;
  scripts never edit CLAUDE.md (they report + emit the proposed block).

## 3. Decision log
- 2026-06-16: scaffolded by generate-skill.
- 2026-06-16: name `craft-claude` (user's explicit choice over the suggested
  `tend-claude-md`/`craft-claude-md`). Verb-noun; "craft" reads for both
  set-up and refine, the two moments the user cares about most.
- 2026-06-16: spec must be grounded in the **official Claude Code memory docs**,
  NOT the AllyHub "CLAUDE.md — The Complete Guide" infographic, which is shipped
  as a reference artifact only. The infographic's known soft-spots to NOT
  encode as law: it overstates "under 300 lines, always" (docs target ~200, and
  it's soft, not enforced); it contradicts itself on negative framing (its model
  Global example has a `# Never Do` block while its mistakes panel bans negative
  framing); and it omits the `.claude/rules/` **load-on-read-not-write** caveat
  and the managed/enterprise policy layer.
- 2026-06-16: differentiate from built-in `/init` — AUTHOR layers *above* it
  (adds scope/rules/memory structure), does not duplicate a generic scaffold.

## 4. Known limitations / environment caveats
- Verified-mechanics baseline is CC 2.1.145 (docs cache). Re-verify the
  rules/import/memory mechanics when the Claude Code memory docs change.
- `.claude/rules/` path-scoped rules load when Claude **reads** a matching file,
  not when it Writes a new one — the spec/audit must flag this so users don't
  over-rely on them for generation-time guidance.

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.

## 6. Notes
Scaffolded with `needs_scripts=true` (probe/preflight/report), `needs_secrets`
=false (keyless), `needs_design`=false.

Authored this session (beyond the generate-skill scaffold):
- `references/claude-md-spec.md` — the canon: §1 verified mechanics, §2 author
  target, §3 audit rubric, §6 folklore-vs-docs.
- `references/templates.md` — CLAUDE.md / CLAUDE.local.md / `.claude/rules/` /
  `@`-import skeletons.
- `references/allyhub-claude-md-guide.png` — the cited infographic (artifact,
  not law; soft-spots catalogued in spec §6).
- `scripts/probe.py` — real project probe (scopes, line counts, rules, imports,
  suggested mode); `scripts/preflight.py` — real checks (spec/target/render-html).

Deliberately **not** created: a separate `references/scopes-and-rules.md` — its
content folded into `claude-md-spec.md` §1–2 to keep one canon.

Open follow-ons (n=1 evidence, not pre-built): first real AUTHOR/AUDIT run →
`/refine-skill craft-claude`; consider an `INDEX`-style report.py that stamps
the original request/path into the HTML artifact (A10 polish).
