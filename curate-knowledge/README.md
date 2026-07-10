# curate-knowledge

**What it is:** Captures the durable lessons from a working session — decisions,
gotchas, playbooks — and files them into your personal OKF knowledge vault,
after you approve each one. Also the vault's groundskeeper: `--groom` sweeps
an existing vault folder for duplicates, stale articles, orphans, and broken
links, and proposes the cleanup for your approval.

## What you get

- New (or updated) articles in your Obsidian vault, each a valid OKF concept
  with frontmatter, wired into the directory indexes and the update log.
- A verification pass proving the vault still conforms and no links broke.
- In non-interactive runs: a proposals file you can review later — the vault
  is never touched without you.

## How to run

Say things like "capture what we learned", "add this to the vault", or
"harvest this session" — or invoke `/curate-knowledge`. Example:

> capture what we learned about the Dropbox sync quirks

To clean up the vault instead of adding to it, say "groom the vault" or name
a folder:

> /curate-knowledge --groom=claude/

Duplicates get merged, stale claims updated, superseded articles archived (to
`archive/`, not deleted) — each action shown as a diff you approve or skip.
For always-fresh maintenance, schedule a weekly `--groom --agent` run: it
writes a report of proposed cleanups, and a later interactive pass applies
only what you approve.

## What it needs

Nothing beyond the vault itself (default:
`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/OBSDN`). No API keys, no network.
Python 3 makes the scans faster, but the skill works without it.

## How it works (high level)

1. Checks the vault is present and writable, and inventories what's already in it.
2. Reads back through the session (and optionally the project) for knowledge
   worth keeping — filtering out anything the repo itself already records.
3. Deduplicates against existing vault articles.
4. Shows you each proposed article — type, title, description, tags, target
   path, and the drafted body — and you confirm, edit, or skip each one.
5. Writes only what you approved, updates the indexes and log, and verifies
   the whole bundle still passes OKF conformance with no broken links.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/` — the curation filter and OKF authoring rules.
