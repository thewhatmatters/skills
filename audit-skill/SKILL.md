---
name: audit-skill
description: Audit a Claude skill against the canonical skill-architecture spec. Use when the user wants to QA, review, audit, or health-check a skill's structure, reliability, secret hygiene, gates, preflight, or conventions — "audit this skill", "qa the X skill", "review skill X", "is this skill well-built", "check skill X against our architecture", "find issues in this skill". Also sweeps the whole suite ("audit all skills") and offers an opt-in triggering check that measures whether a skill's description routes real prompts correctly and whether overlapping skills cross-trigger ("check triggering for X", "is my description firing", "test skill triggering"). Produces a severity-grouped findings report with file:line evidence and concrete fixes.
---

# audit-skill

Audit a target skill against the canonical spec at
`~/.claude/skills/skill-architecture.md`. Report only — never fix unless asked.

## Modes

- **Single skill** (default) — the structural audit in Steps 0–5 below.
- **Suite sweep** ("audit all skills" / `--all`) — see "Suite sweep" after Step 5.
- **Triggering check** (`--triggers`) — opt-in, gated, *costs money*; measures
  whether descriptions route real prompts correctly. See "Triggering check".

The structural audit (Steps 0–5) needs no scripts — it reads the spec + files
with built-in tools. Only `--triggers` uses `scripts/`.

## Step 0: Resolve the target skill

Determine the skill directory:
- Explicit path/name in the request → use it (`~/.claude/skills/<name>`,
  following symlinks).
- A `SKILL.md` in the current working directory → that.
- Otherwise list `~/.claude/skills/*/SKILL.md` and ask which to audit.

Resolve symlinks to the real source dir before reading. State the target.

## Step 1: Load the rubric (source of truth)

Read `~/.claude/skills/skill-architecture.md` in full — sections A (patterns),
B (rubric), C (severity). If it is missing, STOP and say so: the audit has no
spec to check against. Do not audit from memory.

## Step 2: Inventory the target

Enumerate and read: `SKILL.md` (frontmatter, length, whether bulky detail is
offloaded to `references/`), every file in `scripts/`, `references/`, and any
`.env.example`. Note what each script does from its docstring + code. Gather
real evidence — open files; do not assume.

## Step 3: Evaluate every rubric item

For each checkbox in spec §B, decide **PASS / FAIL / N/A** with concrete
`file:line` evidence. Be specific and skeptical:
- A gate that triggers on a transient error = FAIL (spec A7a).
- A documented flag that isn't implemented and isn't marked reserved = FAIL.
- A secret value found in code/logs/committed files = FAIL (Critical).
- Docs referencing removed features/sources = FAIL (Hygiene).
- Steering text that fails the **deletion test** — a paragraph whose removal
  would not change agent behavior — = FAIL (Hygiene). Agent-written skills
  are the usual source; judge each instruction block by what would actually
  differ without it.
- Reference material inline in SKILL.md that only one branch of the skill
  consults = FAIL (spec A1 branch test).
N/A is valid (e.g. no external deps → preflight items N/A) — say why.

## Step 4: Report findings

Lead with a one-line verdict and counts. Then group findings by spec §C
severity. Each finding: **what** (with `file:line`), **why it violates the
spec** (cite the rubric item), **concrete fix**.

```
{SKILL} audit — {N} 🔴 critical · {N} 🟠 important · {N} 🟡 nice · {N} PASS

🔴 Critical
- [spec B/<area>] <finding> — `file:line`. Fix: <concrete fix>.

🟠 Important
- ...

🟡 Nice
- ...

✅ Notable passes: <1-line>
```

Be honest: if it's solid, say so plainly. Don't invent findings to look thorough.

## Step 5: Offer, don't act

Stop after the report. Offer: fix all / critical-only / leave as-is. Make no
edits unless the user chooses a fix scope. Triage before fixing; never silently
expand scope.

## Suite sweep (audit all skills)

When asked to audit the whole suite ("audit all skills", `--all`): enumerate
`~/.claude/skills/*/SKILL.md`, then **fan out** — spawn one agent per ~3 skills
(or per skill), each running Steps 0–5 against the spec and returning a compact
severity-grouped report. Aggregate into a single table (per skill: 🔴/🟠/🟡
counts + the Name & Description verdict), then list the findings worth acting on.
Fan-out keeps each skill's evidence in isolated context; you keep the conclusions.
Do not re-implement the rubric in the agents — point them at the spec.

The sweep table also reports **context load**: each skill's `description`
length (chars) and trigger mode. Every model-invoked description rides in
every session's context — flag the heaviest ones and any side-effectful
skills that look like `disable-model-invocation` candidates (spec A14).

## Triggering check (`--triggers`, opt-in, gated)

Measures whether descriptions actually route real prompts to the right skill, and
whether overlapping skills cross-trigger. **This is the only mode that costs
money/time** (it fires `claude -p` per query) — run it on description *changes*,
not routinely. Skills with `disable-model-invocation: true` are excluded from
the eval set: their descriptions never enter the model's context, so there is
no routing to measure and they cannot cross-trigger (spec A14). Full method, the run_eval gotcha, and eval-set design are in
[`references/triggering-eval.md`](references/triggering-eval.md). Flow:

1. **Preflight** — `python3 scripts/preflight.py`. Gate `CLAUDE_CLI_MISSING` →
   triggering unavailable; say so and fall back to the structural audit (never
   block). Surface the cost note before proceeding.
2. **Build the eval set** — per `references/triggering-eval.md`: should-trigger
   queries + cross-seeded sibling negatives + pure negatives, each labeled with
   the `expected` skill. Confirm with the user before spending.
3. **Run** — `python3 scripts/trigger_eval.py --eval-set <set.json>
   --model <session-model> --out <path>` (all real skills present; records which
   fires per query, kills on detection so nothing executes).
4. **Report** — routing match + the cross-triggering verdict; if wording needs
   work, hand off to `example-skills:skill-creator` (it owns description
   optimization). `--agent`: run only if an eval set is supplied; never prompt.

## `--agent` mode

Output the full report and stop. No interactive offer, no edits.

## Conventions this skill itself follows

The rubric is NOT duplicated here — it lives once in
`~/.claude/skills/skill-architecture.md` (spec A1: progressive disclosure /
single source of truth). Editing the spec changes both this auditor and any
future generator.

`scripts/` exists only for the opt-in `--triggers` mode (a measurement harness,
not the rubric): `trigger_eval.py` (all-skills bake-off; JSON stdout, diagnostics
stderr, never hangs — spec A4) and `preflight.py` (gates on the `claude` CLI —
spec A6/A7). The structural audit stays script-free by design.
