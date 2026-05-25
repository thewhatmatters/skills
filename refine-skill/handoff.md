# refine-skill — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-24  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
Improve a skill by learning from one real session that used it — propose an
evidence-grounded, validated diff for the user to approve.

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Notable:
- **A1 progressive disclosure** — the judgement layer (taxonomy, evidence signals,
  validation ladder, overfit guard) lives in `references/reflection-model.md`;
  SKILL.md stays lean and routes to it.
- **A3 dual-mode** — SCRIPTS (extractor + preflight) with a NATIVE fallback that
  reads the transcript by hand.
- **A8 composition by reference** — runs `audit-skill`'s entry point, routes
  preferences to the memory system, emits markdown for `render-html`; imports none.

## 3. Decision log
- 2026-05-24: scaffolded by generate-skill.
- 2026-05-24: **action mode = propose-only.** The skill proposes a diff + rationale;
  the human approves and commits. Rationale: skills are version-controlled, shared
  artifacts — auto-editing off one session is unsafe and overfit-prone. Mirrors
  generate-skill's no-git rule.
- 2026-05-24: **new skill, not part of audit-skill.** audit-skill is a-priori/
  structural (skill vs static spec); refine-skill is empirical/runtime (skill vs one
  real session). Different input and output; keeping them separate preserves
  audit-skill's single concern. They compose: refine-skill runs audit-skill to
  validate a proposed change.
- 2026-05-24: **n=1 overfitting guard is the core safeguard.** Bias toward logging a
  memory observation over editing the skill; edit only when the fix is provably
  general; act on weak/specific signals only when a pattern recurs (n ≥ 2). Prevents
  one-off tasks from bloating lean skills.
- 2026-05-24: **three-way classification** — bug (propose diff) / routing-doc (defer
  to audit-skill triggering check) / user-preference (route to memory, never bake in).
- 2026-05-24: **regression fixtures live in the target skill's `tests/fixtures/`.**
  The captured failing input is committed alongside the fix (a test asset, not a
  generated report) — seeding a regression suite for a repo that has none.
- 2026-05-24: **trigger = opt-in Stop hook (implemented).** `scripts/stop_hook.py`
  is registered as a Claude Code `Stop` hook. Contract: stdin JSON carries
  `transcript_path`/`session_id`/`stop_hook_active`; it exits 0 with
  `{"systemMessage": ...}` to surface a non-blocking offer — never `decision:block`
  / exit 2 (which would force continuation). Gated to **once per session** via a
  `/tmp/refine-skill-hook/<session_id>.seen` marker so it isn't noisy; only suggests
  skills that exist under `~/.claude/skills` (excludes refine-skill itself; silent if
  refine-skill was already used). Fails silent (always exit 0) so a trigger can never
  disrupt a session. Registered in `~/.claude/settings.json` (user scope, so it fires
  wherever skills are used); the handler script is versioned here, the wiring just
  points at its absolute path.
- 2026-05-24: **portability — `scripts/install_hook.py` owns the wiring.**
  `~/.claude/settings.json` is user-global and outside this repo, so it does NOT
  travel with a clone; the docs alone wouldn't reliably tell a fresh machine to wire
  the hook, and a hardcoded path would break under a different username. The
  idempotent installer computes the handler's absolute path from its own `__file__`
  (portable), merges into settings.json without clobbering other keys, backs up
  first, refuses to touch unparseable JSON, and supports `--remove`. `preflight.py`
  surfaces `HOOK_NOT_INSTALLED` so the gap is discoverable. Setup on a new machine:
  `python3 refine-skill/scripts/install_hook.py`.

## 4. Known limitations / environment caveats
- One session is weak evidence; the guard in §reflection-model is what keeps this
  honest. Generality must be argued, not just validated on one input.
- Transcript location is the Claude Code convention `~/.claude/projects/<cwd with
  '/' and '.' replaced by '-'>/`; if that layout changes, `extract_evidence.py`'s
  resolver needs updating (pass `--transcript=PATH` as the escape hatch).
- The Stop-hook trigger is not implemented yet — manual invocation only for now.
- Validation's spec-compliance step needs audit-skill present (preflight reports
  `AUDIT_SKILL_ABSENT` and degrades otherwise).

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.

## 6. Notes
Reference example baked into `references/reflection-model.md`: the `summarize-yt`
rolling-caption fix done by hand in the session that motivated this skill —
signal → classify (general bug) → propose diff → validate on captured input →
human commits.
