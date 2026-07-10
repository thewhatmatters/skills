# audit-skill — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12). Backfilled 2026-05-21 (the skill predates the
handoff convention; renamed from `skill-auditor` → `audit-skill`).

## 1. Purpose
Audit a target skill against the canonical spec at
`~/.claude/skills/skill-architecture.md` and report severity-grouped findings
with file:line evidence. Report only — never fix unless the user picks a scope.

## 2. Reusable patterns (link to spec A1..A14)
Follows `~/.claude/skills/skill-architecture.md` A1–A14. Notable points:
- **A1 / single source of truth:** the rubric is **not** duplicated here — it
  lives once in the spec (§A patterns, §B rubric, §C severity). Editing the spec
  changes both this auditor and `generate-skill`. This is why audit-skill is
  intentionally **script-less**: it reads the spec and reasons, rather than
  encoding rubric logic in code that could drift from the spec.
- **A12 honesty:** distinguish PASS / FAIL / N/A with real evidence; never invent
  findings to look thorough; say plainly when a skill is solid.

## 3. Decision log
- (pre-2026-05-19): created as `skill-auditor`.
- 2026-05-19: renamed `skill-auditor` → `audit-skill` (verb-noun convention).
- 2026-05-21: **No scripts, by design.** The audit is model-driven against the
  spec; adding a `preflight.py`/rubric-checker would duplicate the spec (A1
  violation) and risk drift. The skill reads `skill-architecture.md` fresh each
  run — explicitly "do not audit from memory."
- 2026-05-21: **Offer, don't act.** Step 5 stops after the report and offers
  fix-all / critical-only / leave; edits happen only on an explicit scope.
  `--agent` mode reports and stops (no interactive offer, no edits).
- 2026-05-21: handoff.md backfilled (this file) to close the lone gap found in
  the repo-wide audit — audit-skill had no decision record.
- 2026-05-24: **Suite-sweep mode** — "audit all skills" fans out one agent per
  ~3 skills (each runs the structural audit against the spec) and aggregates.
  Agents are pointed at the spec, not given a copy of the rubric (keeps A1).
- 2026-05-24: **`--triggers` mode + first scripts.** Added `scripts/trigger_eval.py`
  (all-skills triggering bake-off) and `scripts/preflight.py` (gates on the
  `claude` CLI). This refines — does not reverse — the "script-less by design"
  call: the structural audit stays script-free (the rubric still lives only in
  the spec; encoding it in code would risk A1 drift). The triggering harness is
  a *measurement tool*, not the rubric, so it carries no drift risk. **Why not
  skill-creator's run_eval:** it only detects an ad-hoc command name, so it reads
  a false 0/3 for already-installed skills; the bake-off presents all real skills
  and records which fires (see references/triggering-eval.md). Gated + opt-in
  because it costs real `claude -p` calls — run on description changes only.

## 4. Known limitations / environment caveats
- If `skill-architecture.md` is missing, the audit STOPs — there is no spec to
  check against, and auditing from memory is disallowed.
- Findings are as good as the spec: audit-skill enforces the rubric, it does not
  invent new criteria beyond §A/§B.

## 5. Audit rubric coverage
See `skill-architecture.md` §B. The structural audit is keyless and largely
script-free, so most secret/artifact rows are N/A. The `--triggers` scripts now
make the Reliability rows apply: `trigger_eval.py` and `preflight.py` follow A4
(JSON stdout / diagnostics stderr / graceful — never hang), and `preflight.py`
is a real A6 4-state check with the `CLAUDE_CLI_MISSING` gate (A7: recoverable,
offers a fallback, never blocks the structural audit). Secrets rows stay N/A
(keyless — `claude -p` carries its own auth).

## 6. Notes
Counterpart to `generate-skill` (which scaffolds *to* the spec and then invokes
this skill to self-audit). Keyless; the structural audit needs no network or
scripts. The opt-in `--triggers` mode shells out to the `claude` CLI (its only
external dependency) and is gated accordingly. Description *optimization* (vs the
measurement here) is `example-skills:skill-creator`'s job — hand off to it.
