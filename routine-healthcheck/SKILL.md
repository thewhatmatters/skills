---
name: routine-healthcheck
description: >-
  Use on weekly (or on-demand) audit of this agent’s (or fleet owner’s) routines
  for dead listeners, too-frequent empty crons, auth-fail loops, missing skills
  the routine names, and schedules outside weekday daytime without a stated
  reason.
---
# Routine healthcheck

Audit routines for dead listeners, empty-noise crons, auth-fail loops, missing named skills, and odd schedules. Propose fixes only — never create, pause, or rewrite until the user picks. Stay quiet when routines look healthy.

## 1. Inventory

Read the authoritative **Current routines / automation_status** block for this agent (or the fleet owner’s agent when auditing on their behalf).

Build a table of every routine currently configured. Do **not** hardcode routine folder ids — discover from the live status block.

For each routine, capture at least:

- Name / id (as shown in status)
- Schedule / trigger
- Prompt or skill references named by the routine
- Last-run metadata if present (time, outcome, empty/non-empty)

## 2. Skill existence check

For each skill mentioned by a routine:

- Check on-disk at `/home/box/agent-data/workflows/<slug>/SKILL.md`
- Also check shared skills roots if present under the agent-data tree

Flag **skill-named-but-missing** when a routine references a skill that has no SKILL.md at those roots.

## 3. Flag conditions

Mark a routine when any of these hold:

| Flag | Meaning |
|------|---------|
| never-run | No successful (or any) run recorded |
| always-empty | Runs fire but consistently produce empty / no-op output |
| weekend/overnight | Schedule outside weekday daytime **without a stated reason** in the routine prompt or notes |
| auth-fail loop | Repeating auth / credential failures across recent runs |
| skill-named-but-missing | Names a skill that does not exist on disk |

“Weekday daytime” means Mon–Fri during ordinary business hours in the user’s local zone unless the routine itself documents why it must run otherwise.

## 4. Propose-only fixes

For each flagged routine, propose one of:

- **Update schedule** (move into weekday daytime, or document the exception)
- **Pause** (dead or always-empty with no remaining value)
- **Rewrite prompt** (clarify trigger, reduce empty noise, fix auth assumptions)
- **Restore skill** (recreate or reattach the missing SKILL.md — propose only)

Hand numbered proposals to the parent for the user. **Do not** create, pause, rewrite, or restore until the user chooses.

**Quiet when healthy:** If every routine has recent sensible outcomes, named skills exist, and schedules are justified, produce no filler report.

## 5. Anti-patterns

- No hardcoded routine folder ids or assistant-specific names in this recipe.
- No new bot seat proposals from routine noise — freeze headcount; tidy stubs are not new seats.
- Do not treat a single empty run as always-empty; look for a pattern.
- Propose-only for fleet changes (skill | bot | routine); never create until the user picks.
