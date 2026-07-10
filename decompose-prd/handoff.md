# decompose-prd — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-24  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
Turn a PRD into iteration-sized, dependency-ordered, skill-aware user stories as
`prd.json` — the decomposition front-end to an autonomous agent loop: a
fresh-context agent looped over a task list until every story passes.

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Notable points:
- **A1 progressive disclosure:** the conversion craft (schema, sizing/ordering
  rules, splitting, worked example) lives in `references/conversion-rules.md`,
  loaded only at Step 3; SKILL.md stays lean.
- **A3 dual-mode:** SCRIPTS (python3 + the three scripts) vs NATIVE (list skill
  dirs + decompose + hand-check by hand). The decomposition itself is always
  NATIVE reasoning — sizing/ordering is judgment, not deterministic.
- **A4 scripts:** `list_skills.py` (inventory), `validate.py` (structure check),
  `preflight.py` (input/output) — JSON stdout, diagnostics stderr, graceful.
- **A8 composition by reference:** consumes generate-prd's PRD upstream; names
  automate-browser for the verify step; imports neither.

## 3. Decision log
- 2026-05-24: scaffolded by generate-skill.
- 2026-05-24: **Global, not project-only.** Generalized from the user's
  original project-level loop skill. The decomposition rules are general
  agent-loop conventions, not project-specific, so they belong at global scope.
- 2026-05-24: **Skill-aware via discovery, not hard-coding.** The original skill
  hard-coded "dev-browser skill". Instead `list_skills.py` scans global +
  project skills and the model embeds only skills that actually exist — so the
  prd.json works wherever the loop runs it. Project shadows global on name clash.
- 2026-05-24: **Schema stays runner-compatible.** Skill references go in existing
  fields (`acceptanceCriteria`, `notes` "Suggested skills:"). The only added
  top-level keys are inert metadata a runner ignores: `generatedAt` + `sourcePrd`
  (see next entry). No other top-level keys.
- 2026-05-24: **A10 self-containment (post-audit fix).** Added `generatedAt`
  (ISO date) + `sourcePrd` so the prd.json records what it was built from and
  when — closing the lone 🟡 from the self-audit. They are runner-ignored
  metadata, so runner compatibility holds; `validate.py` warns (not errors) if
  they're absent, keeping externally-authored prd.json valid.
- 2026-05-24: **Offer a runner (`assets/run-tasks.sh`).** After writing
  prd.json, if the project root has no `run-tasks.sh`, the skill *offers* to
  create one (Step 6). Named `run-tasks.sh` — descriptive, not brand-tied.
  Bundled as an `assets/` template: a fresh-agent loop over the
  stories, `AGENT_CMD` defaulting to `claude -p` (overridable, e.g. `amp` or
  with `--permission-mode`), validates prd.json each iteration via the skill's
  own `validate.py` (degrades if not found), archives on branchName change,
  caps at `MAX_ITER`. **Never overwrites an existing runner; never executes it**
  — creating a file is safe, running an autonomous loop is the user's call.
  Interactive asks; `--agent` skips unless `--runner` is passed. This is a
  deliberate, bounded scope step: decompose-prd makes its output runnable, but
  execution stays runner-side (the template is clearly editable/owned by the user).
- 2026-05-24: **Generalized couplings.** "fresh Amp instance" → "fresh agent
  instance"; the runner script / `archive/` documented as *runner-side*
  conventions, not things this skill executes.
- 2026-05-24: **Validator is mechanical only.** `validate.py` checks structure
  (fields, "Typecheck passes", priority ordering, UI-needs-verify warning). Story
  *quality* (true sizing, real dependency order) stays model/human judgment — a
  script can't reliably judge "completable in one iteration".
- 2026-05-24: **Dropped the "Ralph" branding.** Earlier drafts called the target
  the "Ralph technique" (Geoffrey Huntley's name for looping a fresh-context
  agent over a spec) and the schema "Ralph-compatible". The first was apt but
  niche jargon; the second was inflated — the `prd.json` schema is ours, with no
  external "Ralph" spec to be compatible with. Now described neutrally as an
  "autonomous agent loop / build loop". The `branchName` prefix moved `ralph/` →
  `loop/` (and `validate.py`'s warning with it); the runner is `run-tasks.sh`,
  which was never brand-tied. Functionally a no-op — the runner reads `branchName`
  verbatim and never enforced a prefix.

## 4. Known limitations / environment caveats
- "One iteration" sizing is a judgment call the script can't enforce; the
  validator only catches mechanical issues.
- `list_skills.py` reports skills present *now* in the named project; if the
  loop later runs in a different checkout, re-generate so references match.
- Plugin-namespaced skills (`plugin:skill`) are not scanned — only global
  `~/.claude/skills` and `<root>/.claude/skills`.

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.
Secrets/gate rows are N/A (keyless, no network, no external binaries).

## 6. Notes
Front-end to an autonomous build loop (a fresh-context agent looped over the
task list until done). Upstream: generate-prd.
Downstream: a runner consumes prd.json — the skill can emit a default one
(`assets/run-tasks.sh` → project root) on request. The executing agent uses
whatever skills `list_skills.py` surfaced (commonly automate-browser for UI
verification).
