# Skill Architecture — Canonical Spec

The single source of truth for how a "research/automation" skill in this family
is built. **`skill-auditor` checks against this; a future `skill-generator`
scaffolds to this.** Edit here once; both tools follow.

Reference implementation: `trendscan`. Last updated: 2026-05-18.

---

## A. Architecture patterns

A conforming skill SHOULD embody these. Not every skill needs every pattern, but
deviations should be deliberate, not accidental.

1. **Lean SKILL.md + progressive disclosure.** SKILL.md (loaded every run) holds
   only core flow. Bulky/occasional detail (output templates, long tables) lives
   in `references/` and is pulled in only when relevant.
2. **YAML frontmatter.** `name` matches the directory; `description` is
   trigger-rich (verbs + example phrases the model will see) and accurate to
   current capability.
3. **Mode probe + degraded path.** A Step 0 probe picks an execution mode; every
   capability has a functional fallback path when the preferred one is absent.
4. **One concern per script.** Each script does one thing, has a docstring
   stating its I/O contract, writes its payload to **stdout as JSON** and
   diagnostics to **stderr**, and fails gracefully (never hangs the run).
5. **Shared key loader.** Secrets via a single loader with precedence
   `real env → ~/.claude/.env → ~/.claude/skills/.env`; empty values skipped so
   a placeholder never shadows a real key; keys sent in **headers only**, never
   in URLs or logs; no heavyweight dependency. `.env` is `chmod 600` and
   gitignored; `.env.example` is committed with a "Used by:" note per key.
6. **Preflight readiness check.** Before any expensive run, a `preflight.py`
   probes every dependency and emits a human board (stderr) + machine JSON
   (stdout) with `status ∈ {ready, degraded, gated, down}` and a `gate` id.
   Unreliable things (auth/session) are verified for real, not by file-presence
   heuristics.
7. **Recoverable Setup Gates.** A one-time setup gap (missing key, not logged
   in) is NOT a transient error and MUST NOT silently degrade. Each gate has
   four parts: (a) **unambiguous trigger** distinct from transient failures;
   (b) **`--agent` bypass** — never prompt unattended; (c) **ask, don't
   degrade** — interactive: offer *Fix it for me / I'll do it myself / Skip*;
   (d) **graceful dead-end** — if the fix fails, fall back anyway; never block.
8. **User scope control.** Interactive runs let the user choose what runs
   (multi-select annotated with live preflight status). Selecting a not-ready
   item fires its gate; deselecting skips it silently. Bypass with `--agent`,
   explicit `--<scope>=`, or `--all`.
9. **Consistent flags.** `--agent` (non-interactive, no prompts/pauses),
   `--out=PATH` (artifact location), plus domain flags (e.g. `--days=N`). Any
   documented flag is implemented or explicitly marked "reserved".
10. **Self-contained artifact.** Produces one dependency-free output file
    (inline assets, escaped) recording the original request, the date, and the
    results. Generated in every mode including `--agent`.
11. **No unguarded environment assumptions.** Binary/path resolution is
    layered: explicit override → known sandbox path → bundled/default. No hard
    failure when the optimistic path is absent.
12. **Honesty & memory discipline.** Distinguish code-verified vs live-verified;
    disclose partial/degraded runs; never write secret values to memory/logs;
    record non-obvious decisions so they are not re-litigated.

## B. Audit rubric

Each item is PASS / FAIL / N/A with file:line evidence.

**Structure**
- [ ] SKILL.md has valid frontmatter; `name` == dir; description trigger-rich.
- [ ] SKILL.md is lean; bulky detail is in `references/`.
- [ ] Scripts: one concern each, docstring I/O contract, JSON-stdout /
      stderr-diagnostics, graceful failure.

**Environment & secrets**
- [ ] Mode probe + a working degraded/NATIVE path.
- [ ] Secrets only via the shared `_env` convention; header-only; never logged.
- [ ] `.env` `chmod 600` + gitignored; `.env.example` committed w/ "Used by:".
- [ ] Binary/path resolution layered with fallback (no unguarded hard-coded path).

**Reliability**
- [ ] Preflight covers every external dependency; 4-state status + gate id;
      unreliable deps verified for real.
- [ ] Recoverable gaps use the Setup Gate pattern (all 4 parts present).
- [ ] Transient errors do NOT trigger gates (trigger is unambiguous).
- [ ] `--agent` bypasses every prompt/pause.
- [ ] Fallbacks are honest; partial runs disclosed in output.

**UX & output**
- [ ] Standard flags present, consistent, and implemented (or marked reserved).
- [ ] Self-contained artifact records request + date + results; works in `--agent`.
- [ ] User can scope what runs (or it's deliberately all-in with rationale).

**Hygiene**
- [ ] No secret values in code, logs, memory, or committed files.
- [ ] Non-obvious decisions recorded (decision log / memory).
- [ ] Docs match reality (no stale references to removed features/sources).

## C. Severity guide (for findings)

- **🔴 Critical** — breaks at runtime, leaks/credential exposure, silent
  degradation of a recoverable gap, or docs that will cause wrong behavior.
- **🟠 Important** — reliability/consistency gaps: missing `--agent` bypass,
  gate triggers on transient errors, unguarded env path, missing preflight
  coverage, dishonest fallback.
- **🟡 Nice** — polish: stale comment/docstring, deprecation warnings, optional
  consistency.

Report findings grouped by severity, each with file:line evidence and a concrete
fix. Triage before fixing; never silently expand scope.
