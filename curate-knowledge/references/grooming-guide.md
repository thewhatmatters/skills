# Grooming guide — sweeping the vault for duplicates, staleness, and drift

Loaded ONLY under `--groom` (spec A1 progressive disclosure). Grooming is a
maintenance mode like `--relink`: no extraction, no new knowledge — it sweeps
what the vault already holds and proposes cleanup actions through the same
HITL gate. Nothing here weakens the gate: **no file is moved, merged,
rewritten, or deleted without an explicit per-proposal accept.**

## Scope resolution

`--groom` takes an optional vault-relative folder: `--groom=claude/`,
`--groom=projects/conan/`, `--groom=playbooks/`. Bare `--groom` sweeps the
whole vault.

- The folder must exist under the vault root. If it doesn't, list the actual
  top-level directories (from the Step 2 scan) and ask which one was meant —
  never guess a near-match silently. Under `--agent`: record the bad scope in
  the report and stop.
- `reference/` (format ground truth) and `archive/` are **excluded from
  findings** even when in scope — grooming never proposes changes to the OKF
  spec mirror or re-grooms what was already archived.
- The Step 2 scan always covers the **whole vault** regardless of scope:
  backlinks into the scoped folder from elsewhere are needed to keep archive
  and merge actions from silently breaking other topics' articles.

## Findings taxonomy

Sweep the scoped concepts and classify. Every finding becomes either a gated
proposal or a report-only flag — never a silent fix.

| Finding | Signals | Default proposal |
|---|---|---|
| **Duplicate / heavy overlap** | Same rules as the Dedupe section of `curation-guide.md`, applied vault-against-itself: title similarity, description overlap, same tags + same claims in the body | **Merge** into one survivor |
| **Stale content** | A claim about checkable reality fails verification (a path, flag, tool, or version that no longer exists); or a newer article supersedes it | **Update** the stale part; archive only when nothing durable remains |
| **Orphan** | Listed in no `index.md` AND no incoming links (invert the scan's `links`) | **Wire** into the right index; archive only if also superseded |
| **Mechanical drift** | `verify_bundle.py` output: missing/empty frontmatter `type`, broken links whose intended target is inferable (file was moved/renamed) | **Fix** (add frontmatter, retarget link) |

## Staleness rules — age is a signal, never a verdict

- The frontmatter `timestamp` (and `/log.md` dates) say *when*, not *whether*.
  An old `Decision` whose rationale still holds is the vault working as
  intended. **Never propose archive or delete on age alone.**
- A claim is *stale* only when checked against current reality and found
  wrong. Checkable from a grooming run: vault-internal facts (the article a
  link points at, what an index lists), filesystem facts on this machine
  (paths, installed tools), and facts about a repo the session can read.
- Claims that can't be checked from here (a vendor's current behavior, a
  remote system's state) are **flagged as `unverifiable` in the run summary**
  — informational, no proposal. Grooming must not launder guesses into
  deletions.
- Prefer surgical updates: rewrite the stale sentence/section and bump
  `timestamp`, keeping the still-true remainder. Archive is for articles
  where nothing durable survives the check.

## Actions

### Merge (duplicates)

One merge = **one proposal** covering every touched file, all diffs shown
together (splitting it would gate-fatigue the user into rubber-stamping):

1. Pick the survivor: better-located per the target-path conventions in
   `curation-guide.md`, more complete body wins ties.
2. Weave the loser's non-duplicated content into the survivor; bump the
   survivor's `timestamp`.
3. Archive the loser (below) — never hard-delete as part of a merge.
4. Retarget every backlink that pointed at the loser to the survivor.
5. Log one `**Merge**` entry in `/log.md` naming both concepts.

### Archive (default over delete)

- Move the file to `<vault>/archive/<original vault-relative path>`,
  preserving the subpath. Body and frontmatter stay intact; add a producer
  key `archived: YYYY-MM-DD` (types and keys are producer-invented — OKF
  allows this).
- Remove its line from the source directory's `index.md`; add a line to
  `<vault>/archive/index.md` (create on first use; wire `archive/` into the
  root index once) with date + one-line reason.
- Backlinks that pointed at it: each referrer edit is shown in the same
  proposal (retarget, or drop the sentence — say which).
- Log an `**Archive**` entry with the reason.
- **Hard delete** happens only when the user explicitly picks it at the gate
  (it is never the pre-filled recommendation); log a `**Delete**` entry.

### Update / Wire / Fix

Follow the existing rules: updates preserve untouched frontmatter keys and
bump `timestamp` (Dedupe rules in `curation-guide.md`); index wiring and log
entries per SKILL.md Step 7. Broken links are legal in OKF — propose a fix
only when the intended target is inferable; otherwise report.

## The gate

Use the HITL question template from `curation-guide.md`, adapted per action —
"Merge 'X' into 'Y' as proposed?", "Archive 'X'?" — with the full diff (or
moved-file summary) printed BEFORE the question, max 4 proposals per round.
Options: *Accept as proposed (Recommended)* / *Edit first* / *Archive
instead* (for update proposals) or *Delete instead* (for archive proposals) /
*Skip this one*.

## Reporting (no silent caps)

The run summary always states: concepts scanned in scope, findings per
bucket, proposals accepted / edited / skipped, and the `unverifiable` flags
with one line each. If any bucket was truncated for practicality, say what
was left unexamined.

## `--agent` grooming report

Same contract as the harvest proposals file: no writes, ever. Serialize to
`--out/curate-knowledge-groom-<date>.md` — one section per proposed action
with the full diffs, plus the flagged-for-review table. A later interactive
run consumes the file and resumes at the gate.

**Recurring freshness:** pair a scheduled run (`/schedule`, e.g. weekly
`/curate-knowledge --groom --agent`) with an occasional interactive pass over
the emitted report. The analysis stays automatic; the writes stay human.
