# generate-skill — Design (for review; no code yet)

Status: **proposal**, awaiting sign-off. Last updated 2026-05-18.
Decisions locked with the user are marked ✅. Open items in §9.

This is the not-yet-built counterpart named in `scan-trends/handoff.md` §intro:
*"a rubric usable by a future generate-skill and audit-skill."* `audit-skill`
exists; this completes the pair.

---

## 1. Purpose & the loop it closes

Scaffold a new Claude Code skill that satisfies our house conventions, using
**two inputs reconciled**:

- **In-house truth:** `~/.claude/skills/skill-architecture.md` — the same spec
  `audit-skill` checks against. Generator *emits* against it; auditor *checks*
  against it. One spec, both directions.
- **Upstream truth:** the official Claude docs (✅ *Official Claude docs*),
  pinned and cached locally, used to keep our frontmatter/format current and to
  **flag drift** when Anthropic changes the SKILL.md contract.

Closing step: the generator runs `audit-skill` on its own output. A skill it
produces must pass the auditor, or the generator reports the findings instead of
claiming success. generator → auditor → shared spec is a closed loop.

**Non-goals (explicit):** it does NOT `git`-commit or publish (you do the
`.gitignore` opt-in by hand, per repo convention); it does NOT auto-rewrite
`skill-architecture.md` from upstream (drift is surfaced, you decide); it does
NOT continuously poll docs (✅ *on-demand + preflight*, not a background poller).

## 2. Authoritative docs (✅ Official Claude docs)

Pinned canonical URLs (verified; served as clean `.md`):

| Slug | URL | Used for |
|------|-----|----------|
| `skills` | `https://code.claude.com/docs/en/skills.md` | SKILL.md format + frontmatter field list (the field set we validate against) |
| `changelog` | `https://code.claude.com/docs/en/changelog.md` | cheap version signal (e.g. `2.1.144`) + "skill"-mentioning entries |
| `plugins-reference` | `https://code.claude.com/docs/en/plugins-reference.md` | skill-in-plugin specs |
| `claude-directory` | `https://code.claude.com/docs/en/claude-directory.md` | skill discovery locations |
| `agent-sdk-skills` | `https://code.claude.com/docs/en/agent-sdk/skills.md` | SDK skill usage (reference only) |

Honest constraint (verified with the docs guide): there is **no JSON schema**
for SKILL.md, frontmatter is a prose markdown table, and no ETag/Last-Modified is
guaranteed. So freshness is best-effort by design (see §4), and `docs.py` must
tolerate the `.md` convention itself changing (fall back to bundled snapshot).

## 3. File layout

```
generate-skill/
  SKILL.md                       # lean core; YAML frontmatter; trigger-rich description
  README.md                      # plain-language "what this is / how it works" (house convention)
  DESIGN.md                      # this file (living design record, like scan-trends/handoff.md)
  references/
    generation-recipe.md         # the step-by-step scaffold the model follows (progressive disclosure)
    claude-docs-snapshot/        # committed offline fallback copy of the §2 docs (NATIVE path)
  scripts/
    _env.py                      # shared key loader — copied verbatim from scan-trends convention
    docs.py                      # fetch/cache/diff canonical docs; emit drift report
    preflight.py                 # connectivity + docs-cache freshness + target writability
    reconcile.py                 # diff live frontmatter field set vs skill-architecture.md assumptions
  .cache/docs/                   # runtime cache (gitignored; never committed)
```

`.cache/` is added to the repo's always-ignore block so it can never be
committed even after `generate-skill/` is opted in.

## 4. `docs.py` contract (✅ on-demand + preflight)

- **I/O:** `python3 scripts/docs.py [--refresh] [--agent]`. stdout = JSON
  manifest; stderr = human diagnostics. (scan-trends convention: JSON-stdout /
  diagnostics-stderr, single concern, graceful failure, never hangs.)
- **Fetch mechanism (✅ locked):** SCRIPTS mode uses Python **stdlib
  `urllib.request`** — keyless, zero added dependency (consistent with the
  handoff's "no python-dotenv" minimalism). NATIVE mode uses the harness
  `WebFetch`. The `.env` Tavily/Exa keys are NOT used here.
  - **SSL trust (found in build/testing):** macOS python.org Python builds
    don't trust certs via the system keychain, so stdlib `urllib` hits
    `CERTIFICATE_VERIFY_FAILED` while `curl` succeeds. `docs.py` builds its SSL
    context from `certifi` when importable (it ships with `requests`, already
    used by scan-trends → still zero *added* dependency) and falls back to the
    default context otherwise. Layered, no unguarded assumption — spec A11.
- **Resolution order (dual-mode, mirrors scan-trends SCRIPTS vs NATIVE):**
  1. live fetch of the pinned URLs (SCRIPTS: `urllib`; NATIVE: `WebFetch`),
  2. local `.cache/docs/` if fetch fails, or if cache is fresh and no `--refresh`,
  3. committed `references/claude-docs-snapshot/` if offline (NATIVE fallback).
- **Cache entry:** `{slug, url, sha256, fetched_at, http_status,
  claude_code_version}` in `.cache/docs/manifest.json`.
- **Version signal:** tolerant regex for the first version token in
  `changelog.md` (e.g. `2.1.144`). Cheap, reliable-enough staleness trigger.
- **Freshness rule:** stale if cache age > 30d **or** changelog version moved
  **or** `--refresh`. Stale ⇒ preflight reports `status=degraded`,
  `gate=DOCS_STALE` with a one-line human action; `--agent` bypasses (uses
  cache/snapshot, prints a single notice — never prompts). This is the handoff's
  Recoverable-Setup-Gate philosophy applied to docs.
- **The `.env`/Tavily-Exa keys:** *secondary discovery only* — used if we ever
  need to *search* for new guidance with no known URL. Not on the critical path.
  (Correcting the original "cool, we have API keys" framing: re-reading a known
  doc URL is a plain fetch; keys don't enable it.)

## 5. Drift handling — `reconcile.py`

Diffs the **live `skills.md` frontmatter field set** against the fields
`skill-architecture.md` assumes; also scans changelog entries mentioning
"skill" since the cached version. Emits `{added, removed, changed, notes}`
(JSON stdout + human stderr). It **never edits `skill-architecture.md`**. On
drift it raises a gate-style prompt interactively (*Show diff / Update spec
myself / Proceed on current spec*); under `--agent` it proceeds on the current
spec and records the drift in the run output. You remain the decision-maker on
spec changes — same reason the handoff added Recoverable Setup Gates.

## 6. Generation flow

0. **Step 0 probe** — SCRIPTS (python3 + network) vs NATIVE (built-in web/fetch
   tools + bundled snapshot). Announce the mode.
1. **preflight** — docs cache fresh? target dir writable? `_env` perms sane?
2. **Load + reconcile spec** — `skill-architecture.md` + `docs.py`; run
   `reconcile.py`; surface drift per §5.
3. **Inputs** — skill name (kebab, ≤64), trigger-rich description, needs-scripts?,
   needs-secrets?, external deps/sources. `--agent` takes documented defaults.
4. **Scaffold** against the 10 reusable patterns in `handoff.md` §3:
   - `SKILL.md` — frontmatter validated against the **live** field list from
     `docs.py` (never invent fields not in upstream docs); lean body.
   - `references/` — progressive disclosure for bulky/occasional detail.
   - `scripts/` skeletons only when needed — `_env.py` (verbatim convention),
     `preflight.py` (4-state), `report.py` (self-contained artifact) — each:
     single concern, docstring I/O contract, JSON-stdout/diagnostics-stderr,
     graceful degrade, `--agent`/`--out`/`--days` where applicable.
   - `README.md` — plain-language, high-level "what this is / how it works"
     (house convention; every skill gets one — see §8a).
   - seed a `handoff.md` (decision log + audit rubric stub) for the new skill.
   - print the exact `!/<skill>/` `.gitignore` opt-in line (you run git).
5. **Self-audit (✅ report-only, never blocks)** — run `audit-skill` on the
   output and attach the full report (severity-grouped issues + what's working).
   The generator **always emits** the skill; it never refuses or gates. Its
   final status line states the truth — `✅ ready` vs `⚠ generated — N
   high-severity items to address` — so a flawed skill is never presented as
   clean (handoff §3.10, honest verification). Interactive mode may *offer* to
   fix high-severity items; `--agent` just reports and exits informatively.
6. **Emit** — created tree + honest verdict line + the opt-in line. No git
   actions (you own the `.gitignore` opt-in and commit).

## 7. Flags (consistent with scan-trends handoff §3.7)

`--agent` (no prompts/pauses, documented defaults), `--out=PATH`,
`--refresh-docs` (force `docs.py` re-fetch), `--name=`, `--no-scripts`,
`--dry-run` (print plan + tree, write nothing).

## 8. Reuse, don't duplicate

`_env.py` is copied verbatim from the scan-trends convention (the handoff's §3.3;
hyphenated dirs break `import _env`, so flat script names — handoff §5, "do not
re-propose"). `preflight.py`/`report.py` follow scan-trends's shapes. The
generator should *generate* skills that themselves reuse these, not reinvent.

## 8a. House convention: every skill has a README.md

A `README.md` per skill folder, written in plain language for a reader who is
*not* deep in the code: one-line "what it is", "what you get", "how to run",
"what it needs", and a short "how it works" — distinct from `SKILL.md` (Claude's
operating instructions) and `handoff.md`/`DESIGN.md` (the why/decision record).

Applied now to the existing skills (`scan-trends/README.md`,
`audit-skill/README.md`) and emitted for every generated skill (§6 step 4).

**Flagged, not silently done:** making this an *audited* requirement means
adding a checklist line to `skill-architecture.md` (§4 rubric) — which changes
`audit-skill`'s behavior on every skill. That edit to the canonical spec is
listed as decision (5) below rather than made unilaterally.

## 9. Decisions (resolved 2026-05-19)

1. ✅ **Snapshot bootstrap** — yes; fetch the §2 docs once and commit under
   `references/claude-docs-snapshot/` as the offline fallback.
2. ✅ **Self-audit = report-only, never blocks** — always emit; honest verdict
   line; no hard fail/gate (§6 step 5).
3. ✅ **Fetch mechanism** — stdlib `urllib` in SCRIPTS, `WebFetch` in NATIVE
   (§4); keyless, zero added dependency.
4. ✅ **DESIGN.md long-term** — kept at `generate-skill/DESIGN.md`, committed
   with the skill like scan-trends's `handoff.md`.
5. ✅ **README convention enforced** — added pattern A13 + a §B Structure
   rubric line to `skill-architecture.md` (commit `cc1be62`); `audit-skill`
   now checks it. Not advisory.

## 10. What's next

Decisions 1–5 locked. Build order: **(done)** `docs.py` + `preflight.py` +
committed snapshot → **(next)** the scaffold recipe → wire the self-audit.

## 11. Build status

- **Phase 1 — DONE & tested.** `scripts/docs.py`, `scripts/preflight.py`, and
  the committed `references/claude-docs-snapshot/` (5 docs, Claude Code
  `2.1.144`). Smoke-tested: live→`refreshed`, cache→`fresh`,
  `--refresh`→`refreshed`; degraded chain proven (stale-cache→`stale`,
  no-cache→`snapshot`, nothing→exit 1); preflight 4-state board verified in
  `ready`, `gated`, and `degraded`/offline states. `.cache/` confirmed
  gitignored. SSL/certifi issue found and handled (see §4).
- **Phase 2 — DONE & self-audited.** `scripts/reconcile.py` (cache vs snapshot
  frontmatter diff + changelog skill-mentions), `scripts/_env.py` (verbatim
  copy of scan-trends's key loader — template for generated skills), `SKILL.md`
  (lean orchestration: probe → preflight → docs → reconcile → inputs →
  scaffold → self-audit → emit), `README.md` (plain-language; spec A13), and
  `references/generation-recipe.md` (substitution templates for the scaffold).
  - **Smoke tests pass:** reconcile parser extracts all 15 live frontmatter
    fields; aligned/drift/no-live branches all green; the live↔snapshot
    version delta (live now `2.1.145`, baseline `2.1.144`) correctly reports
    `aligned` (no skill-relevant changelog entries between).
  - **Self-audited.** Ran `audit-skill` on this skill in `--agent` mode
    (the loop the SKILL.md prescribes for generated skills). Verdict:
    0 🔴 critical · 0 🟠 important · 4 🟡 nice — all four addressed before
    commit:
    1. Recipe used `{{...}}` doubled braces under a `.format()` assumption
       that didn't match the model-driven scaffold path. **Fixed:** outer
       placeholders are now `<<NAME>>` style (purely textual substitution);
       inner Python `{...}` left single-brace and correct.
    2. `docs.py` could crash on cache write after a successful live fetch
       (read-only home / denied perms). **Fixed:** writes wrapped in
       try/except OSError; on failure emits `status=refreshed source=live`
       with a "cache write failed" note instead of a traceback. Verified
       with a `NotADirectoryError` harness.
    3. `DOCS_STALE` gate's graceful dead-end (spec A7d) was implicit.
       **Fixed:** SKILL.md Step 1 `gated` row now states that if *Refresh*
       fails, the snapshot path covers it automatically.
    4. `docs.py` `status: "offline"` was overloaded across "snapshot used,
       exit 0" and "nothing available, exit 1". **Fixed:** the fatal case
       now emits a distinct `status: "no-docs"`; JSON KEYS docstring updated.
- **Phase 3 — next, when needed.** End-to-end exercise: actually run
  `generate-skill` to scaffold a throwaway test skill and verify the full
  loop (preflight → docs → reconcile → scaffold → self-audit → emit)
  produces a passing skill from inputs. Not blocking for commit.
