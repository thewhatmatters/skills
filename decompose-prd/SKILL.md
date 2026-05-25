---
name: decompose-prd
description: Decompose a Product Requirements Document into small, actionable, dependency-ordered user stories as prd.json — each story sized to finish in a single autonomous-agent iteration (one fresh context). Use when the user wants to turn a PRD or spec into executable tasks for an autonomous build loop — "convert this PRD to prd.json", "turn this PRD into agent-loop tasks", "decompose this PRD into stories", "break this spec into agent tasks", "taskify this PRD", "create prd.json from this", "split this into one-iteration stories". Discovers the available global + project skills and embeds the right one into each story's acceptance criteria (e.g. verify UI with automate-browser) so the executing agent knows which skill to reach for. Pairs with generate-prd as its upstream PRD source. Stories are dependency-ordered (schema → backend → UI) with verifiable criteria, always including "Typecheck passes".
---

# decompose-prd

Turn a PRD into iteration-sized, dependency-ordered, **skill-aware** user stories as `prd.json` for an autonomous build loop.

## What it does

Reads a PRD (markdown file or text) and emits `prd.json` — a list of small user stories each completable in one fresh-context agent iteration, ordered so no story depends on a later one, with verifiable acceptance criteria. It first **discovers the skills available in the execution environment** (global + project) and embeds the relevant one into each story, so the agent that later runs the story knows which skill to use. The schema, sizing/ordering rules, splitting heuristics, and a worked example live in [`references/conversion-rules.md`](references/conversion-rules.md) (spec A1) — read it before converting.

## How to run

Trigger with "convert this PRD to prd.json", "decompose this PRD into agent-loop tasks", "taskify this spec", or `/decompose-prd <prd-file>`. Consumes the markdown PRD that `generate-prd` produces.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | where to write `prd.json` (default: `./prd.json`) |
| `--project=PATH` | project root to scan for project-level skills and resolve the output dir (default: cwd) |
| `--no-validate` | skip the `validate.py` structure check (not recommended) |
| `--runner` | under `--agent`, create `run-tasks.sh` without prompting (interactive runs always ask) |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. If python3 + `scripts/` are present → **SCRIPTS** (use the scripts below). Otherwise → **NATIVE**: do skill discovery by listing `~/.claude/skills/*/SKILL.md` and `<project>/.claude/skills/*/SKILL.md` yourself, decompose by hand per `references/conversion-rules.md`, and hand-check the JSON. Announce the mode in one line.

## Steps

1. **Preflight** — `python3 scripts/preflight.py --in=<prd> --out=<dest>`. `down` (e.g. `INPUT_MISSING`, `OUT_UNWRITABLE`) → stop and report; else proceed.
2. **Inventory skills** — `python3 scripts/list_skills.py --project=<root>` → JSON `[{name, scope, description}]` for every global + project skill the executor will have. This is the source of truth for the next step.
3. **Decompose (NATIVE reasoning)** — apply `references/conversion-rules.md`: split into one-iteration stories, order by dependency (schema → backend → UI), write verifiable criteria. For each story, **match its intent against the inventory** and embed the right skill: name it in the verify criterion (e.g. a UI story → "Verify in browser using automate-browser skill" *iff* that skill is present) and list candidates in `notes` ("Suggested skills: …"). Always append `"Typecheck passes"`; add a browser-verify criterion to UI stories. Skill references go in existing fields only — keep the schema runner-compatible. Set the `generatedAt` (today, ISO) and `sourcePrd` metadata keys so the artifact records what it was built from and when (spec A10).
4. **Validate** — `python3 scripts/validate.py <out>` (unless `--no-validate`). Fix every reported error before finalizing.
5. **Archive check** — if `--out` already holds a `prd.json` for a *different* `branchName` with real progress, follow the archive convention in `references/conversion-rules.md` before overwriting.
6. **Offer a runner** — after `prd.json` is written, check the project root for an existing runner (`run-tasks.sh`). If none exists, **ask** whether to create one from [`assets/run-tasks.sh`](assets/run-tasks.sh): copy it to the project root and `chmod +x`. It loops a fresh agent (`$AGENT_CMD`, default `claude -p`) over the stories until all pass. **Never overwrite an existing runner, and never execute it** — creating the file is safe; running an autonomous loop is the user's call. Under `--agent`: skip the prompt and create it only if `--runner` was passed.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Composition by reference, not import — consumes `generate-prd`'s PRD; names `automate-browser` for browser verification; runs neither's code (spec A8 family convention).
- Skill references are **discovered, not hard-coded** — never assume a project skill exists; embed only what `list_skills.py` actually found.
- Keyless; stdlib scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
