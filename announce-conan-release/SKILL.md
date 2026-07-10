---
name: announce-conan-release
description: >-
  Fan out a Conan release announcement across three surfaces in three repos from
  one set of version + highlights: the marketing changelog
  (conan-marketing/src/data/releases.ts → /changelog), the in-app "What's New"
  popup (conan/ui/src/data/whatsNew.ts, shown once after a user updates +
  restarts), and a draft buyer email (conan-license `npm run draft-broadcast`, a
  Resend draft a human reviews + sends). Use when the user wants to announce or
  publish release notes for a new Conan version — "announce the conan release",
  "publish the 1.0.6 release notes", "update the changelog + what's new + email
  for this release", "do the release announcement", "draft the release email and
  changelog". This is the COMMS counterpart to release-conan (which builds,
  signs, notarizes, and ships the app) — it does NOT build or ship. It knows the
  exact files, the newest-first changelog ordering, the exact-version keying of
  the What's New popup, the critical build-ordering (whatsNew.ts must be edited
  BEFORE release-conan builds the bundle), and that the buyer email is ALWAYS a
  draft a human sends — never auto-sent.
---

# announce-conan-release

Announce a cut Conan release across the marketing changelog, the in-app What's
New popup, and a draft buyer email — from one set of version + highlights.

## What it does

Takes a version + its highlights and updates **three surfaces in three repos**:
the public changelog (conan-marketing), the in-app What's New popup (conan), and
a draft buyer broadcast (conan-license). It is the comms half of a release; the
[[release-conan]] skill does the build/sign/notarize/ship. The per-surface
files, fields, exact commands, and gotchas live in
[references/surfaces.md](references/surfaces.md) — read it before editing.

## How to run

Say "announce the conan release", "publish the X.Y.Z release notes", "do the
release announcement", or `/announce-conan-release`. Supply the version and a
few user-facing highlights (or point at the GitHub release notes / changelog and
the skill drafts them for your review).

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts. Even so it never **pushes** the marketing repo or **sends** the email unattended — it edits, commits, and creates the draft, then reports what's staged for a human to push/send (spec A7b/A9). |

## Step 0 — Mode probe

Docs-only skill; no probe needed. It edits files in the three repos and runs an
existing npm script — no Python, no `scripts/` dir.

## Steps

1. **Gather inputs.** Get the **exact version string** (e.g. `1.0.6`, no `v`) and
   2–4 user-facing highlights. Pull from the GitHub release notes or the user.
   Note the per-surface emphasis differs (see references): the changelog is
   fullest, What's New is 2–4 teaser bullets, the email is founder-voice.
2. **In-app What's New FIRST** — edit `conan/ui/src/data/whatsNew.ts`
   (exact-version-keyed). ⚠️ This ships **inside the app bundle**, so it must be
   written **before** `release-conan` builds. If the app is already built/shipped
   for this version, STOP and warn that a rebuild + re-release is required.
   Verify `cd ui && npm run build`.
3. **(release-conan builds/ships the app — out of scope here.)** Only proceed to
   the public-facing surfaces below once the release is actually live, so you
   never announce a version users can't get yet.
4. **Marketing changelog** — add a newest-first entry to
   `conan-marketing/src/data/releases.ts`. Verify `npm run build`, commit, and
   **confirm before pushing** (push → Vercel auto-deploys www.conan.sh).
5. **Buyer email** — in `conan-license`, run `npm run draft-broadcast` (inline
   full-access key + segment id). It creates a Resend **DRAFT**. Hand it to the
   user to review + send in the Resend dashboard. **Never send** — draft only.

See [references/surfaces.md](references/surfaces.md) for the exact file shapes,
fields, commands, and gotchas of each step.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Commit/push only in a release context or when asked; **confirm before pushing
  the marketing repo** (it deploys on push) and **before any outward send**.
  Under `--agent`, never push/send unattended — stage and report instead.
- The buyer email is **draft-only** — a human always sends it.
- Single concern: comms, not builds. Composes with [[release-conan]], which
  handles the build/sign/notarize/ship.
