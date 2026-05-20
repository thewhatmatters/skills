---
name: audit-skill
description: Audit a Claude skill against the canonical skill-architecture spec. Use when the user wants to QA, review, audit, or health-check a skill's structure, reliability, secret hygiene, gates, preflight, or conventions — "audit this skill", "qa the X skill", "review skill X", "is this skill well-built", "check skill X against our architecture", "find issues in this skill". Produces a severity-grouped findings report with file:line evidence and concrete fixes.
---

# audit-skill

Audit a target skill against the canonical spec at
`~/.claude/skills/skill-architecture.md`. Report only — never fix unless asked.

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

## `--agent` mode

Output the full report and stop. No interactive offer, no edits.

## Conventions this skill itself follows

The rubric is NOT duplicated here — it lives once in
`~/.claude/skills/skill-architecture.md` (spec A1: progressive disclosure /
single source of truth). Editing the spec changes both this auditor and any
future generator.
