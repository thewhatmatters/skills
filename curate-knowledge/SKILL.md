---
name: curate-knowledge
description: Harvest durable, non-derivable knowledge from the current session or project and file it into the personal OKF vault (the Obsidian knowledge bundle) behind a mandatory human confirmation gate. Use when the user wants to capture what was learned — "curate knowledge", "capture what we learned", "add this to the vault", "save this to the knowledge base", "harvest this session", "remember this in the wiki", "/curate-knowledge". Extracts decisions (with their why), gotchas/platform quirks, playbooks/procedures, and cross-project patterns; filters OUT anything derivable from the repo (code structure, git history, CLAUDE.md content). Dedupes against existing vault concepts, then presents per-article pre-filled recommendations (type, title, description, tags, target path) that the user confirms or edits before ANY write. On approval writes OKF-conformant concepts, wires index.md files, appends to /log.md, and verifies conformance + links. Composes with handoff (session-boundary harvest point) and ingest-source (external URL/PDF captures route into reference/). Also the vault's MAINTENANCE mode — use when the user wants the vault itself cleaned up: "groom the vault", "clean up the claude/ folder in the vault", "find stale or duplicate vault articles", "keep the vault fresh", "vault spring-cleaning" → `--groom[=<vault-folder>]` sweeps existing articles for duplicates, stale claims, orphans, and broken links, proposing merges/updates/archives through the same gate. Never auto-writes — in --agent mode it emits a proposals file instead of touching the vault.
---

# curate-knowledge

Harvest durable knowledge from the current session or project and file it into
the OKF vault — with a mandatory human confirmation gate before any write.

## What it does

Analyzes the conversation and/or the project you're working in for knowledge
worth keeping *outside* the repo, proposes each candidate as a fully-specified
OKF article (frontmatter + target path pre-filled), and — only after you
confirm or edit each one — writes it into the vault, wires the indexes,
logs the change, and verifies the bundle. Extraction and authoring detail
live in `references/` (spec A1).

## How to run

Say "capture what we learned", "add this to the vault", "harvest this
session", or invoke `/curate-knowledge`. Optionally name a topic:
"capture what we learned about notarization".

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive (spec A7b). The HITL gate CANNOT be bypassed, so this mode never writes to the vault — it writes a proposals file to `--out` for later interactive review. |
| `--out=PATH` | where the `--agent` proposals file and `--dry-run` plan go (default: session scratchpad) |
| `--vault=PATH` | vault root override. Default: `/Users/digitalalchemist/Library/CloudStorage/Dropbox/Documents/Obsidian` |
| `--scope=session\|project\|both` | what to harvest (default: `session`) |
| `--relink` | maintenance mode: skip extraction, sweep the existing vault for missing cross-links between articles, and propose them as a batch through the gate |
| `--groom[=FOLDER]` | maintenance mode: sweep an existing vault folder (vault-relative, e.g. `claude/` or `projects/conan/`; omit for the whole vault) for duplicates, stale content, orphans, and mechanical drift; propose merge/update/archive/fix actions through the gate. See "Groom mode" below |
| `--dry-run` | extract, dedupe, and show the proposal table; write nothing |

## Groom mode (`--groom`)

Vault-only maintenance: the current working directory's project is irrelevant
— everything read and written lives inside the vault. Re-routes the steps:

- **Steps 0–2 unchanged.** The Step 2 scan always covers the whole vault even
  when a folder is scoped — backlinks into the scoped folder are needed so
  archives/merges never silently break other articles.
- **Steps 3–5 are replaced** by the grooming sweep per
  `references/grooming-guide.md` (read it first): classify scoped concepts
  into duplicates → merge, stale claims → update/archive, orphans → wire,
  mechanical drift → fix. Age alone is never grounds for removal; archive
  (to `<vault>/archive/`) is the default over delete.
- **Step 6 gate unchanged and mandatory** — every action (merge, update,
  archive, delete, link fix) is a per-proposal confirmation. `--agent` emits
  a grooming report to `--out` and writes nothing; `--dry-run` prints the
  findings table and stops.
- **Steps 7–8 unchanged** in contract: execute only approved actions, wire
  indexes, log entries (`**Merge**`/`**Archive**`/`**Delete**` per the
  guide), then verify the bundle.

## Step 0 — Mode probe

Try `python3 --version` and check `scripts/` exists. Both present → mode =
**SCRIPTS**. Otherwise **NATIVE**: do the same checks and scans with built-in
file tools (read frontmatter directly; verify links by listing files).
Announce the mode in one line.

## Step 1 — Preflight

SCRIPTS: `python3 scripts/preflight.py --vault=<vault>`. Gates:

- `VAULT_MISSING` (gated) — vault root absent. Interactive: offer *Create a
  minimal OKF bundle there / Point me at the right path / Cancel*. `--agent`:
  record the gate, emit an empty proposals file with the gate noted, stop.
  Graceful dead-end (spec A7d): if the chosen fix fails (e.g. create hits a
  permissions error), do not block — fall back to emitting a proposals file
  to `--out`, exactly as `--agent` does, and report the gate in the summary.
- `SYNC_UNMOUNTED` (gated) — the vault's CloudStorage provider root is
  absent, i.e. the sync client (Dropbox) likely isn't running. NEVER offer
  to create a vault here — it would diverge from the synced copy.
  Interactive: ask the user to start the sync client, then re-run preflight.
  `--agent`: record the gate in the proposals file, stop.
- `VAULT_READONLY` (down) — stop; nothing can be written.
- Missing root `index.md` / `log.md` → degraded (they'll be created in Step 7).

## Step 2 — Inventory the vault

`python3 scripts/scan_vault.py --vault=<vault>` → JSON list of every existing
concept (`concept_id`, `type`, `title`, `description`, `tags`, and outgoing
`links` — backlinks are computable from the full list). This feeds dedupe
(Step 4), relating (Step 5), and index wiring (Step 7).

## Step 3 — Extract candidates

Analyze the session transcript and/or project per
`references/curation-guide.md`. Keep only durable, non-derivable insights:
decisions **with their why**, gotchas/quirks, playbooks, cross-project
patterns. Filter OUT anything the repo already records (code structure, git
history, CLAUDE.md content) and anything only relevant to this conversation.
Draft each candidate's full article body, not just a title. Bodies follow
the house markdown style spec at
`~/.claude/skills/format-markdown/references/markdown-style.md` (read it
before drafting); OKF rules (frontmatter, absolute links, reserved files)
win where they overlap — see the deference table in that spec.

## Step 4 — Dedupe

Compare candidates against the Step 2 inventory (by concept_id, title
similarity, and description overlap). A match becomes a proposed **update to
the existing concept** (shown as a diff summary), never a duplicate file.

## Step 5 — Relate

Match each candidate against the inventory (tags, title/description overlap,
link graph) per the Relate rules in `references/curation-guide.md`. Weave
genuine relationships into the draft as inline links or a short `# Related`
section — a link is written only when the prose can say *why*. When a new
article has an obvious hub (a `Decision` and its project `overview.md`),
draft the one-line reverse edit to the existing article as its own gated
proposal. Under `--relink`, this step IS the run: sweep existing articles
for missing links and batch the proposals.

## Step 6 — HITL gate (MANDATORY — this is the skill's contract)

For EACH surviving candidate, present pre-filled recommendations via
AskUserQuestion using the template in `references/curation-guide.md`:
proposed `type`, `title`, `description`, `tags`, and target vault path —
plus *Skip this one*. The user confirms or edits every field. Batch at most
4 candidates per question round; always show the drafted body before asking.

- Nothing is EVER written without explicit per-article confirmation.
- `--dry-run`: print the proposal table and stop here.
- `--agent`: serialize the proposals (fields + drafted bodies) to
  `--out/curate-knowledge-proposals-<date>.md` and stop here. A later
  interactive run consumes that file and resumes at this gate.

## Step 7 — Write + wire (approved articles only)

Author each approved article per `references/okf-conventions.md`: OKF
frontmatter (required `type`; `title`, `description`, `tags`, `timestamp`),
absolute `/path.md` links, `# Citations` where claims have sources. Then wire:
add an entry line to the target directory's `index.md` (create it if new),
add new top-level directories to the root `/index.md`, and append a dated
entry to `/log.md` (newest first, ISO date heading).

## Step 8 — Verify + summary

`python3 scripts/verify_bundle.py --vault=<vault>`. Report honestly (spec
A12): conformance errors and broken links found, articles written vs skipped,
any degraded/gated preflight items. If verification fails on a file this run
wrote, fix it before finishing; pre-existing issues are reported, not fixed.

**Wire suggestion (interactive only):** if this run filed articles under
`projects/<name>/` and the current project's CLAUDE.md lacks the wire-vault
marker block (`<!-- wire-vault:start -->`, checked case-insensitively),
suggest running `/wire-vault` once in the report — a suggestion, not an
action; wire-vault has its own consent gates. Skip under `--agent`.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
- Keyless — no secrets, no network.
- The vault's own OKF rules are mirrored at `<vault>/reference/okf-spec-v0.1.md`;
  `references/okf-conventions.md` here is the operational condensation.
