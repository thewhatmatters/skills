# gauntlet — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-07-16  ·  Generator: generate-skill @ CC 2.1.181

## 1. Purpose

Sustained builder→critic refinement loop: deterministic gates floor +
isolated cross-vendor critic (Grok) verdict ceiling, fresh builder context
per round, hard caps and oscillation detection so it always terminates.

## 2. Reusable patterns (link to spec A1..A15)

Follows `~/.cursor/skills/skill-architecture.md` A1–A15. Deliberate notes:
- A5 (shared key loader): N/A — keyless by design; the Grok CLI carries its
  own auth (`~/.grok/auth.json`), this skill never touches credentials.
- A15b: Agent tool (fresh builder subagent) and automate-browser (quality
  screenshots) are session-only/soft — probed model-side, degrades disclosed.

## 3. Decision log

- 2026-07-16: scaffolded by generate-skill.
- 2026-07-16: **Named `gauntlet`** (was working title `refine-loop`) — both
  words of the old name cross-triggered with existing skills (`refine-skill`,
  `/loop`).
- 2026-07-16: **Critic = Grok CLI, not Gemini** — user lost Gemini access;
  Grok 0.2.102 installed + authenticated. Smoke-tested headless structured
  output: `grok -p … --output-format json --json-schema …` returns a
  `structuredOutput` object honoring the schema (it even returned
  REVISE/"no artifact provided" on an empty probe — good critic instincts).
- 2026-07-16: **Isolation by construction** — the critic gets a packet file
  via `--prompt-file` and needs no repo/tool access; research says context
  isolation (not vendor diversity) is the load-bearing property, so the
  fallback critic is an isolated subagent, and inline critique is
  forbidden.
- 2026-07-16: **Design source**: vault articles
  `/research/synthesis/agent-reviewer-refinement-loops.md` and
  `/research/synthesis/agent-reviewer-loops-coding-agents.md` (Inkling
  trigger). Key imports: role asymmetry (flags-not-fixes), two species with
  different budgets (correctness 5 / quality 10–40), explicit VERDICT
  keyword, distinct close-out keyword (`FINAL_AUDIT`) so the final pass
  cannot re-open the loop, oscillation exit on repeated finding fingerprints.
- 2026-07-16: Generated against live CC 2.1.181 with generate-skill baseline
  at 2.1.144 (drift = upstream added `disallowed-tools` frontmatter field;
  additive, not used here).

## 4. Known limitations / environment caveats

- Grok CLI flags are as of 0.2.102; `--json-schema` implies
  `--output-format json`. If the envelope key `structuredOutput` renames,
  `run_critic.py` exits 2 and the loop falls back to the subagent critic.
- Auth detection in preflight is marker-string based (AUTH_MARKERS); an
  auth failure with novel wording lands as `degraded` (safe: never a false
  gate, per A7a).
- Quality species without automate-browser degrades to textual artifact
  description — weaker critique, disclosed.
- The live auth probe spends one tiny Grok turn; use `--no-live` to skip.
- `GAUNTLET_CRITIC_CMD` / `--critic` must be a single binary path — values
  with arguments would fail (`subprocess.run` list form, no shell).

## 5. Audit rubric coverage

See `skill-architecture.md` §B; this skill targets every PASS that applies
(secrets items are N/A — keyless).

## 6. Notes

Hard dep: none beyond python3 (NATIVE path documented). Soft: Grok CLI
(degrades to subagent critic), Agent tool, automate-browser. Testbed per
research: the geo project for a quality-species run.
