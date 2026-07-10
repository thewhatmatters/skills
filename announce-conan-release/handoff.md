# announce-conan-release — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-06-19  ·  Generator: generate-skill @ CC 2.1.181

## 1. Purpose
The comms half of a Conan release: announce a cut version across the marketing
changelog, the in-app "What's New" popup, and a draft buyer email, from one set
of version + highlights.

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Notable:
- A1 (progressive disclosure): the per-surface detail lives in
  `references/surfaces.md`; SKILL.md stays lean.
- Docs-only skill (no `scripts/`): it orchestrates existing files + an existing
  npm script (`conan-license`'s `draft-broadcast`), so there's nothing to
  preflight in Python.
- Single concern: comms only. Building/signing/shipping is `release-conan`.

## 3. Decision log
- 2026-06-19: scaffolded by generate-skill.
- 2026-06-19: kept SEPARATE from `release-conan` (build/ship) rather than folding
  in — distinct concern, different repos, can run independently as a pure
  post-ship announcement.
- 2026-06-19: email is **draft-only** — the skill must never send; a human sends
  in Resend. (Outward-facing irreversibility.)
- 2026-06-19: encoded the build-ordering gotcha (whatsNew.ts before the app
  build) as Step 2, because it ships in the bundle.

## 4. Known limitations / environment caveats
- Assumes the three repos are siblings under `~/Development/`.
- The email step needs a Full-access `RESEND_API_KEY` passed INLINE (Sensitive in
  Vercel ⇒ not retrievable via `vercel env pull`).
- Highlight data is NOT auto-derived from the release — the user/skill authors
  it per surface (changelog fullest, What's New teaser, email founder-voice).

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.

## 6. Notes
Background on the Resend global-contacts/segment model and the draft-broadcast
script: project memory `project_conan_mailing_list` and
`project_conan_release_announcement_flow`. Related skills: `release-conan`,
and the data files it touches were built in the 2026-06-19 session.
