# Critic protocol

Loaded at Step 3 (packet assembly) and Step 4 (close-out). Holds the bulky
templates so SKILL.md stays lean (spec A1).

## Findings JSON schema (the ceiling contract)

Passed to the critic CLI as `--json-schema`; `run_critic.py` embeds it.

```json
{
  "type": "object",
  "properties": {
    "verdict": { "type": "string", "enum": ["APPROVED", "REVISE"] },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "severity": { "type": "string", "enum": ["critical", "important", "minor"] },
          "category": { "type": "string" },
          "confidence": { "type": "string", "enum": ["high", "medium", "low"] },
          "location": { "type": "string" },
          "issue": { "type": "string" },
          "evidence": { "type": "string" },
          "suggested_test": { "type": "string" }
        },
        "required": ["severity", "category", "confidence", "location", "issue"]
      }
    },
    "summary": { "type": "string" }
  },
  "required": ["verdict", "findings"]
}
```

Verdict rules (state them in every packet):

- `APPROVED` only when zero `critical`/`important` findings remain in scope.
- `REVISE` otherwise. Prose is never a verdict; only the `verdict` field counts.
- The critic FLAGS — it must not propose full alternative implementations
  (`suggested_test` and a one-line remediation direction are the maximum).

## Packet template — correctness species

```
You are an adversarial code critic. You did not write this code and have no
stake in it. Judge ONLY what is in this packet. Stay in scope: the diff plus
at most one hop into directly-touched interfaces. Flag issues; do not fix
them or rewrite the code.

== RUBRIC (the spec this diff must satisfy) ==
<rubric text>

== DIFF ==
<unified diff>

== PREVIOUSLY TRACKED (context only — do NOT re-flag unless newly severe) ==
<tracked ledger, one line each; "(none)" on round 1>

Return findings per the JSON schema. APPROVED only if no critical/important
in-scope findings remain.
```

## Packet template — quality species (Inkling-style)

```
You are a demanding product/design critic judging a RUNNING artifact against
a quality rubric. You see only what is in this packet. Flag concrete,
actionable shortfalls — "what is wrong and where", never "here is my
rewrite". Prioritize: the 3–5 highest-impact issues per round, not an
exhaustive list.

== QUALITY RUBRIC ==
<rubric: dimensions + what "good" looks like per dimension>

== ARTIFACT STATE ==
<screenshots (attached) and/or textual state description; how it was exercised>

== PREVIOUSLY TRACKED ==
<ledger or "(none)">

Return findings per the JSON schema. APPROVED means: shipping this today
would not embarrass the rubric.
```

Quality rubric shapes (drafting guide, Step 2): 4–7 dimensions, each with a
one-line bar. E.g. for a game: feel/responsiveness, visual coherence,
feedback/juice, difficulty curve, edge-case robustness. For a UI: hierarchy,
spacing rhythm, state coverage (empty/loading/error), copy tone, a11y basics.

## Close-out audit packet (Step 4)

Fresh context, wider lens, distinct keyword — it cannot re-open the loop:

```
You are performing a FINAL SYSTEMIC AUDIT after an iterative refinement loop
converged. Do not re-review round-level details. Look ONLY for systemic or
cross-cutting issues the round scope would have missed: architectural drift,
duplicated logic across rounds of fixes, security posture, missing tests for
the loop's fix pattern, spec sections silently dropped.

<final diff or artifact state + original rubric>

Respond with `FINAL_AUDIT: CLEAR` or `FINAL_AUDIT: CONCERNS` followed by at
most 5 concerns. Never use the word VERDICT.
```

## Oscillation detection (Step 3.5)

Fingerprint each round's driving findings as sorted
`location|category` pairs. If round N's fingerprint set equals round N-1's,
the loop is oscillating (builder and critic disagree or the fix regresses) —
exit with both rounds' findings and the diff of attempted fixes as the
diagnostic. Do not spend a third round on the same set.

## Fallback critic (degrade path)

When Grok is missing/unauthenticated/persistently invalid: run the critic as
an isolated subagent (Agent tool, fresh context, same packet, same
JSON contract enforced by prompt). Isolation is preserved; vendor diversity
is lost — say so in the report's disclosures. Never run the critic inline in
the builder's own conversation; that forfeits isolation, the load-bearing
property.
