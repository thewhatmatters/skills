# gauntlet

**What it is:** an adversarial refinement loop — Claude builds, an isolated
cross-vendor critic (Grok) reviews with a structured verdict, and the loop
runs until the work passes or a hard cap stops it.

## What you get

- Code (or a UI/artifact) iteratively refined until deterministic gates pass
  AND an independent critic returns `VERDICT: APPROVED`.
- A self-contained HTML run report: every round, every verdict, what drove
  each fix, what was tracked-but-deferred, and any degraded-mode disclosures.
- A final systemic audit from a fresh context before handoff — the result is
  reviewed code for you to merge, never auto-committed.

## How to run

Say "run the gauntlet on this diff", "gauntlet this", or "refine this until
the critic approves". Example: after building a feature, "put this through
the gauntlet against the PRD".

## What it needs

- The Grok CLI (`grok`) installed and logged in (`grok login`) — it is the
  cross-vendor critic. If it's missing, the skill still works using an
  isolated Claude subagent as critic (and tells you so).
- A git repo for diff-based (correctness) runs; quality runs on a live
  artifact work anywhere.

## How it works (high level)

1. Preflight checks the critic, its auth (live probe), the repo, and which
   test/lint/typecheck gates the project has.
2. Each round: gates run first (the floor); if green, the critic gets an
   isolated packet — just the diff/screenshots plus a rubric, none of the
   builder's context — and returns structured findings plus a verdict (the
   ceiling).
3. A fresh-context builder fixes only the high-confidence, in-scope
   findings; low-confidence ones are tracked, not chased.
4. The loop ends on APPROVED + green gates, on oscillation (same findings
   twice), or at the round cap (5 for correctness, 10–40 for quality).
5. A final fresh-context audit looks for systemic issues, then the report is
   written and the diff is handed to you.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/critic-protocol.md` — packet templates, findings schema, rubric shapes.
