# curate-knowledge

**What it is:** Captures the durable lessons from a working session — decisions,
gotchas, playbooks — and files them into your personal OKF knowledge vault,
after you approve each one.

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

## What it needs

Nothing beyond the vault itself (default:
`~/Library/CloudStorage/Dropbox/Documents/Obsidian`). No API keys, no network.
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
