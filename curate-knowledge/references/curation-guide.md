# Curation guide — what to extract, how to dedupe, how to ask

Loaded by SKILL.md Steps 3–5 (spec A1 progressive disclosure).

## The filter: what belongs in the vault

Save knowledge that **survives refactors and applies beyond one repo**:

| Save (type) | Test |
|---|---|
| `Decision` | A choice was made between real alternatives, and the *why* isn't written anywhere durable. Capture context, options, choice, rationale. |
| `Gotcha` | A non-obvious fact that cost real time to learn (platform quirk, vendor behavior, API trap). Would past-you have avoided pain knowing it? |
| `Playbook` | A procedure that will be executed again (release steps, incident triage, setup ritual). Capture as numbered steps with links. |
| `Project` | Standing facts about a project that aren't in its repo: what it is, where things live, who/what it talks to. |
| `Reference` | An external source worth mirroring — route through `ingest-source` when available; target a **topic directory** (e.g. `<vault>/claude/best-practices/`), proposing the best-fitting existing topic before inventing a new one. `ingest-source`'s own vault destination hands this skill a pre-drafted candidate: skip extraction, but dedupe, relate, and the HITL gate still apply. |

Do NOT save:

- Anything derivable from the repo: code structure, what functions do, git
  history, CLAUDE.md content, test results.
- Session state: open threads, half-done work, "next steps" — that is
  `handoff` territory.
- Secrets, tokens, or key values — ever (spec A12).
- Speculation. Only things that were actually established/learned.

Rule of thumb: **the vault gets the *why* and the *hard-won*; the repo keeps
the *what* and the *derivable*.**

## Target paths (vault conventions)

- `<topic>/<subtopic>/<slug>.md` — type `Reference` for external captures,
  organized by subject (e.g. `claude/best-practices/`); provenance lives in
  the `type`, not the location. Prefer existing topic directories; new ones
  are fine — wire them into the root index.
- `projects/<project-name>/overview.md` — type `Project`, one per project.
- `projects/<project-name>/decisions/<slug>.md` — type `Decision`.
- `projects/<project-name>/gotchas/<slug>.md` — type `Gotcha`.
- `playbooks/<slug>.md` — type `Playbook` (cross-project procedures).
- `reference/` — reserved for format ground truth (the OKF spec mirror); do
  NOT file new captures here.
- `notes/<slug>.md` — type `Note` (fallback when no topic fits yet).

Slugs: short-kebab-case. New directories are fine — wire them into the root
index. Types are producer-invented; prefer the table above for consistency,
but a better-fitting type is allowed (say why in the proposal).

## Relate rules (Step 5)

Written links are **curation, not indexing** — Obsidian's backlinks/graph and
the `tags` field already cover "these mention similar things." Write a link
only when the relationship is worth a sentence.

- **Signals**: shared tags, title/description token overlap, same project or
  topic directory, and the existing link graph (`links` in the scan — compute
  backlinks by inverting it).
- **Forward links (new → existing)**: weave into the draft body inline where
  the prose naturally references the concept; use a short `# Related` section
  only for relationships that don't fit the prose. Absolute form always.
- **Reverse links (existing → new)**: propose ONLY for hub relationships —
  a project `overview.md` listing a new `Decision`/`Gotcha`, a `Playbook`
  gaining a step-relevant reference. Each reverse edit is its own gated
  proposal (it modifies an existing article). Never mechanical reciprocity.
- **`--relink` mode**: skip extraction; for every pair of existing articles
  with strong signals and no link either way, draft the specific edit (where
  the link lands, what the sentence says) and batch the proposals through the
  gate. Report pairs considered-but-rejected in one summary line (no silent
  caps).

## Dedupe rules

Compare each candidate against the `scan_vault.py` inventory:

1. Same intended `concept_id` → propose an **update** to that file.
2. Title similarity or heavy description overlap with an existing concept →
   show the existing concept in the proposal and ask: update it, create
   anyway, or skip. Never silently create a near-duplicate.
3. When updating: preserve the existing frontmatter keys you don't touch,
   bump `timestamp`, and log an `**Update**` (not `**Creation**`) entry.

## The HITL gate — question template

For each candidate (max 4 per AskUserQuestion round), FIRST print the drafted
article body in full, THEN ask. Per candidate, the question presents the
pre-filled recommendation and edit paths:

- **Question:** "File '<proposed title>' into the vault as proposed?"
- **Options:**
  1. `Accept as proposed (Recommended)` — description states the full spec:
     type, target path, tags.
  2. `Edit fields first` — follow up with per-field questions (type, title,
     description, tags, path), each with the recommendation as option 1.
  3. `Change target path` — offer the other plausible directories.
  4. `Skip this one` — drop it; note it in the run summary.

The user can always answer "Other" with free text — treat that as the edited
value. Re-confirm only if their edit changes the article's meaning (not for
cosmetic field tweaks). **No file is written for a candidate until it has an
explicit accept.**

## Writing back (`--agent` proposals file)

Serialize unconfirmed proposals as markdown: one section per candidate with a
fenced YAML block of the proposed frontmatter + target path, followed by the
drafted body. Header notes the source session/date. An interactive run given
this file skips Steps 2–4 and resumes at the gate.
