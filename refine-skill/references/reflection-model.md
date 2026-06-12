# Reflection model

Loaded by `SKILL.md` Step 4 — progressive disclosure (spec A1). This is the
judgement layer: how to turn extracted signals into classified, validated,
non-overfit proposals. The extractor (`scripts/extract_evidence.py`) finds
signals; the reasoning here decides what (if anything) to do about them.

## Reference example — this loop, done by hand

The motivating case: a session used `summarize-yt` (since absorbed into
`ingest-source`), the caption fetcher returned
1252 rolling/overlapping auto-caption cues, Claude wrote a one-off `python3 -c`
merge to make them readable, then fixed `parse_srt` to do the merge itself and
re-ran it on the real video to prove it. That is exactly one pass of this skill:
*signal* (one-off workaround) → *classify* (skill bug, general) → *propose diff*
→ *validate on the captured input* → human commits. Everything below generalises
that.

## Evidence signals (what the extractor surfaces)

| Signal `kind` | What it usually means |
|---|---|
| `bash` workaround (`python3 -c`, heredoc, inline parse/merge after a skill ran) | the skill's scripts left work for Claude to finish by hand — strong bug signal |
| `edit`/`write` **inside** the skill dir | Claude hand-fixed the skill mid-task — already a candidate change, just unvalidated |
| `edit`/`write` **outside** the skill dir, on the skill's own output | the artifact needed manual correction — output-quality bug |
| `error` (Traceback, non-zero exit, `⛔`) | a script failed or hit an unhandled path |
| `gate`/`degrade` (`gated`, `degraded`, `⚠`, gate id) | a capability was unavailable — may be expected (missing key) or a too-eager gate |

Always cite the message index `i` from the extractor in the finding, the same way
`audit-skill` cites `file:line`. No evidence → no finding.

## Classification — route each finding to exactly one

1. **Skill bug / incomplete logic** → propose a code or doc diff *to the skill*.
   The script does the wrong/partial thing, fails, or makes Claude finish its job.
2. **Routing / description gap** → hand to `audit-skill`'s triggering check. The
   skill mis-triggered, didn't trigger, or `SKILL.md` failed to route Claude to the
   right reference/step. Do **not** rewrite descriptions here — that is audit-skill's
   concern, with its own measurement.
3. **User / task preference** → propose a **memory** entry, never a skill edit.
   "Randy wanted the output in `~`, not the CWD" is about *this user/task*, not the
   skill's correctness. Baking preferences into a shared, version-controlled skill
   is itself a bug. Write a `feedback`/`user` memory instead (see the memory
   convention) and link it.

When a signal is ambiguous between bug and preference, ask: *would this change help
every user of this skill, or just this task?* General → bug. Specific → preference.

## The n=1 overfitting guard (the most important rule)

One session is a single, possibly unrepresentative, data point. Bias hard toward
**propose-an-observation** over **edit-the-skill**:

- **Edit the skill only when the fix is provably general** — it corrects clearly
  wrong/incomplete behavior that would recur for *any* comparable input (rolling
  captions affect every auto-subbed video; that cleared the bar). Validation on the
  captured input is necessary but not sufficient — also argue generality.
- **Otherwise log an observation to memory** (`project`/`feedback` type) describing
  the friction, and act only when the **pattern recurs (n ≥ 2)** across sessions.
  This is the conservative path that keeps the skill from absorbing one-offs.
- **Never add weight cheaply.** Adding a flag, a reference, or SKILL.md prose makes
  every future invocation heavier and fights the house "lean SKILL.md / no
  dead-weight reference" convention. A finding that *removes* friction or *fixes*
  wrong behavior clears a low bar; one that *adds surface area* must clear a high
  one. When unsure, prefer the smaller change or none.

## Validation ladder (before showing any code diff)

A proposed code change is not surfaced until it survives, in order:

1. **Capture the failing input as a fixture** under the **target skill's
   `tests/fixtures/`** (e.g. `ingest-source/tests/fixtures/rolling-captions.srt`).
   It lives with the skill it protects and is committed alongside the fix, seeding
   a regression suite for a codebase that has none — so accrued fixtures are a real
   asset. (This is a committed test asset, not a generated report, so it belongs in
   the repo despite the "generated artifacts stay out" convention.)
2. **Re-run the affected script on the fixture** and show before/after (the
   rolling-caption fix went 1252→635 entries, 68.7k→22.9k chars).
3. **`python3 -m py_compile`** the changed scripts.
4. **Run `audit-skill`** on the modified skill; the diff must not introduce a
   🔴/🟠 finding. If `AUDIT_SKILL_ABSENT` (preflight degraded), say so and mark the
   spec-compliance check as not performed.

Report the validation outcome alongside the diff so the human approves with eyes
open. The skill applies the diff only on approval (or `--apply`) and **never
commits** — the human owns the commit, exactly as `generate-skill` does.

## Trigger wiring (opt-in Stop hook) — implemented

`scripts/stop_hook.py` is registered as a Claude Code `Stop` hook in
`~/.claude/settings.json`. When a session used a skill, it *offers* to reflect — it
does not silently run a reflect-and-edit loop (expensive, noisy, and unsafe to
auto-edit committed shared code). Contract: stdin carries `transcript_path` /
`session_id` / `stop_hook_active`; the hook exits 0 with `{"systemMessage": ...}` to
show a non-blocking notice (never `decision:block` / exit 2, which would force
continuation). It is gated to **once per session** (a `/tmp` marker), scoped to the
user's own skills, silent if refine-skill was already used, and fails silent. The
user opts in per session by actually running `/refine-skill <skill>`; the manual
command is always available regardless of the hook.
