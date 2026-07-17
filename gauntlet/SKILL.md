---
name: gauntlet
description: Run code or an artifact through the gauntlet — a sustained builder→critic refinement loop where deterministic gates (typecheck/tests/lint) are the floor, an isolated cross-vendor critic (Grok CLI, headless) is the ceiling, and a fresh-context builder fixes each round until the critic returns VERDICT APPROVED, oscillation is detected, or the round cap hits (5 correctness / 10–40 quality). Use when the user wants output adversarially refined until it passes, not reviewed once — "run the gauntlet", "gauntlet this", "put this diff through the gauntlet", "refine until the critic approves", "loop builder and reviewer until clean", "keep iterating until review passes", "adversarial refine loop", "have another model critique and iterate". Two species — correctness (critic judges the diff against a spec rubric) and quality (critic judges the running artifact via screenshots against a quality rubric, Inkling-style). Critic flags, never fixes; builder fixes, never self-approves; findings are structured JSON filtered by confidence; close-out is one fresh final audit with a distinct verdict keyword. Degrades to an isolated Claude subagent critic when Grok is missing or unauthenticated. NOT for single-pass review (that is /code-review), skill audits (audit-skill), or interval scheduling (/loop).
---

# gauntlet

Adversarial builder→critic refinement loop: deterministic gates as the
**floor**, an isolated cross-vendor critic verdict as the **ceiling**,
fresh builder context every **round**, hard caps so it always terminates.

## Leading words

- **floor** — deterministic gates (typecheck/tests/lint) run first each round; a red floor skips the critic (cheap before expensive).
- **ceiling** — the critic's structured `VERDICT: APPROVED|REVISE`; prose is never inferred as approval.
- **isolation** — the critic sees ONLY the packet (diff/screenshots + rubric + tracked list), never the builder's conversation or reasoning.
- **flags-not-fixes** — critic flags, never fixes; builder fixes, never self-approves.
- **species** — `correctness` (diff vs spec rubric, cap 5) or `quality` (running artifact vs quality rubric, cap 10, max 40).
- **tracked** — low-confidence / out-of-scope findings are ledgered, not acted on; they never drive a round.

## How to run

"run the gauntlet", "gauntlet this diff/feature", "refine until the critic
approves", or `/gauntlet [--species=…] [--rounds=N] [--rubric=PATH]`.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | run-report location (default `./gauntlet-report-<date>.html`) |
| `--species=correctness\|quality` | loop species; default inferred (diff present → correctness) |
| `--rounds=N` | round cap override (correctness default 5; quality default 10, hard max 40) |
| `--rubric=PATH` | rubric file; default drafted from spec/PRD/conventions and confirmed |
| `--critic=CMD` | critic command override (default: `$GAUNTLET_CRITIC_CMD` → `grok` on PATH → `~/.local/bin/grok`); single binary path, no arguments |
| `--no-live` | preflight only: skip the live critic auth probe |

## Step 0 — Mode probe

Try `python3 --version` with `scripts/` present → **SCRIPTS**; else
**NATIVE** (assemble packets and call the critic CLI directly via Bash;
validate its JSON yourself). Session-only deps (A15b), probed model-side:

- **Agent tool** available → builder runs as a fresh subagent each round (full isolation). Absent → fix inline and disclose reduced builder isolation in the report.
- **automate-browser** (quality species, soft compose) → screenshots for the packet if available; else describe the artifact state textually and disclose.

## Step 1 — Preflight

`python3 scripts/preflight.py` (add `--no-live` to skip the live critic
probe; `--agent` for unattended). Gates:

| Gate | Trigger | Interactive (A7c) | `--agent` / Skip |
|------|---------|-------------------|------------------|
| `CRITIC_MISSING` | no critic binary resolves | Fix it for me (install hint) / I'll do it myself / Skip | degrade: isolated Claude subagent critic — isolation kept, vendor diversity lost; disclosed in report |
| `CRITIC_UNAUTHED` | live probe returns an auth error (unambiguous; timeouts are `degraded`, never gated) | suggest `! grok login` / I'll do it myself / Skip | same degrade as above |
| `NO_REPO` (degraded, not gated) | not a git repo | — | correctness species unavailable; quality still runs |

`down` → STOP. Never silently degrade a gate (A7).

## Step 2 — Species, scope, rubric

1. **species**: `--species` or infer — uncommitted/branch diff exists → `correctness`; "make it feel/look better" style ask → `quality`. Announce the choice and cap.
2. **scope**: the diff (correctness) or the artifact + how to run it (quality). Scope is diff + one hop — the critic is told to stay in scope.
3. **rubric**: `--rubric` file, else draft one from the spec/PRD/project conventions (quality: see `references/critic-protocol.md` for the rubric shapes). Interactive: confirm before looping. `--agent`: proceed with the draft, disclosed.

## Step 3 — The loop (per round, ≤ cap)

1. **floor** — run discovered gates (from preflight's `gates` check). Any fail → those failures ARE the round's findings; skip the critic; go to 4.
2. **packet** — assemble under isolation: rubric + diff (correctness) or screenshots/state (quality) + the tracked ledger. Template: `references/critic-protocol.md`.
3. **ceiling** — SCRIPTS: `python3 scripts/run_critic.py --packet=<file>`; NATIVE: call the critic CLI with the same prompt + JSON schema. Invalid output → one retry → fallback critic (disclosed). Filter findings: only `confidence ≥ high` AND in-scope drive the round; rest → **tracked**.
4. **build** — fresh builder context (Agent tool): give ONLY spec + rubric + current diff + this round's findings. Builder fixes; never argues with the critic in-packet.
5. **terminate?** — floor green AND `VERDICT: APPROVED` → Step 4. Same finding set two rounds running (compare `file:line+category`) → oscillation exit with diagnostic. Cap hit → exit, disclosed as unconverged.

## Step 4 — Close-out audit

One final audit in a fresh context (new subagent or fresh critic call)
with a WIDER scope — systemic/cross-cutting issues, not the round scope.
Distinct keyword so it cannot re-open the loop: `FINAL_AUDIT: CLEAR|CONCERNS`.
`CONCERNS` are reported to the user, never looped on.

## Step 5 — Report & handoff

SCRIPTS: pipe the run ledger JSON to `python3 scripts/report.py --out=<out>`
(self-contained HTML: request, date, rounds, verdicts, findings, tracked
ledger, disclosures). NATIVE: write the same ledger as markdown. Then print
a short summary: rounds used, converged or not, tracked count, report path.

The gauntlet produces **reviewed** code, not approved code — present the
final diff for human review; NEVER commit, push, or merge.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- Keyless — the critic CLI carries its own auth; this skill never handles or logs credentials.
