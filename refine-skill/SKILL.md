---
name: refine-skill
description: Improve an existing Claude skill by learning from one real session that used it. Use after a task leveraged a skill and you want to capture what worked, what didn't, and what to fix — "refine the X skill", "reflect on this session and improve X", "what should we improve in skill X", "self-improve X from this run", "post-mortem this skill usage", "tune X based on what just happened", "/refine-skill X". Reads the session transcript, extracts evidence-grounded friction (manual workarounds Claude wrote that the skill should have done, gates/degrades that fired, output that needed hand-fixing, errors), and classifies each finding — skill bug or incomplete logic (propose a code/doc diff), routing/description gap (defer to audit-skill's triggering check), or user/task preference (route to the memory system, never bake into the shared skill). Proposes a validated diff plus rationale for you to approve — never auto-commits. Validates a proposed code change by re-running on the captured failing input (kept as a regression fixture), compiling, and running audit-skill to confirm spec compliance. Guards against n=1 overfitting and bloating lean SKILL.md files. Composes with audit-skill, generate-skill, and the memory system.
---

# refine-skill

Improve a skill by learning from one real session that used it — propose an
evidence-grounded, validated diff for the user to approve.

## What it does

Turns a finished task into a targeted improvement to the skill it used. It reads
the session transcript, extracts concrete friction signals (one-off workarounds
Claude wrote, gates/degrades, output fixups, errors), and reasons about each as a
**classified, evidence-cited finding**. Skill bugs become a proposed diff;
user/task preferences are routed to **memory** (never baked into a shared skill);
routing/description gaps are handed to `audit-skill`. Every proposed code change
is *validated before it is shown* — re-run on the captured failing input, compiled,
and re-audited. It **proposes; it never auto-commits.** The taxonomy, evidence
signals, validation ladder, and the n=1 overfitting guard live in
[`references/reflection-model.md`](references/reflection-model.md) (spec A1) — read
it before classifying.

## How to run

Trigger with "refine the `<skill>` skill", "reflect on this session and improve
`<skill>`", "what should we improve in `<skill>`", or `/refine-skill <skill>`.
With no skill named, infer the most-recently-invoked skill from the transcript and
confirm. Output is a markdown findings report; pass it to `render-html` for a
branded page.

An opt-in **Stop hook** (`scripts/stop_hook.py`, registered in
`~/.claude/settings.json`) surfaces a one-line, once-per-session offer to run
`/refine-skill <skill>` when a session used a skill — it only offers; you decide.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9). Reports proposals; never edits or commits |
| `--out=PATH` | findings-report markdown location (default: `./<skill>-refine-<date>.md`, outside the skills repo) |
| `--transcript=PATH` | explicit session `.jsonl` (default: newest transcript for the current project) |
| `--skill=NAME` | target skill (default: inferred from the transcript's last Skill invocation) |
| `--apply` | after a finding is approved, write the validated diff with Edit (still never commits) |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. python3 + `scripts/` present → **SCRIPTS** (use the
scripts below). Otherwise → **NATIVE**: locate the transcript yourself (newest
`*.jsonl` under `~/.claude/projects/<cwd-with-/-and-.-as-dashes>/`), read it, and
extract the signals by hand. Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py [--transcript=PATH] [--agent]`.
   Read the JSON. `down` (`TRANSCRIPT_MISSING`) → stop and report. `degraded`
   (`AUDIT_SKILL_ABSENT`) → proceed but note that the spec-compliance check in
   Step 5 is unavailable.
2. **Resolve target + session** — pick the skill (`--skill`, else the transcript's
   last `Skill` invocation; confirm if inferred — under `--agent`, take the
   inferred skill without prompting) and the transcript (`--transcript`, else
   newest for the project). Confirm the target skill directory exists.
3. **Extract evidence** — `python3 scripts/extract_evidence.py --transcript=PATH
   [--skill=NAME]` → JSON `{skill_invocations, signals:[{i,kind,detail,path}],
   summary}`. Each signal carries a message index `i` for citation. The script
   only *extracts*; it does not judge.
4. **Classify (NATIVE reasoning)** — for each signal, decide **bug | routing/doc |
   preference**, cite the message index, and assign confidence. Apply the **n=1
   guard** (`references/reflection-model.md`): a single session is weak evidence —
   only propose a code edit when the fix is *general*; otherwise log an observation
   to memory and act when the pattern recurs.
5. **Propose & validate** —
   - **bug/doc** → draft the diff, then validate: capture the failing input as a
     fixture in the target skill's `tests/fixtures/`, re-run the affected script on
     it, `py_compile`, and run `audit-skill` on the modified skill. Surface only
     diffs that pass; show the validation result.
   - **preference** → propose a `memory/` entry (per the memory convention), not a
     skill edit.
   - **routing/description** → hand to `audit-skill`'s triggering check.
6. **Report** — markdown findings to `--out`, led by the **target skill, transcript
   filename, and date** (spec A10), then findings grouped by class, each with
   evidence (cited), proposed action, and validation result. The user approves; on
   approval (or `--apply`) write the diff with Edit. **This skill never runs git.**
   Offer the `render-html` step.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Composition by reference, not import — runs `audit-skill`'s documented entry
  point, routes preferences to the memory system, emits markdown for `render-html`;
  imports none of their code (spec A8).
- Proposes, never auto-commits; never edits a skill without approval; never runs
  git. The user owns every change (mirrors `generate-skill`'s no-git rule).
- Guards against n=1 overfitting and against bloating lean `SKILL.md` files — a
  finding that would add weight must clear a higher bar than one that removes it.
- Scripts: JSON stdout / diagnostics stderr / graceful failure / never hang
  (spec A4). Keyless — no secrets, no `_env.py`; reads only local transcripts and
  skill files.
