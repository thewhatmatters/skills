# announce-conan-release

**What it is:** the comms half of a Conan release — it announces a cut version
across the marketing changelog, the in-app "What's New" popup, and a draft buyer
email, from one set of version + highlights.

## What you get

- A newest-first entry in the marketing changelog (`/changelog` on www.conan.sh).
- An in-app "What's New" popup entry that shows once after users update + restart.
- A ready-to-review **draft** buyer broadcast in Resend (you click Send).

## How to run

Say "announce the conan release", "publish the 1.0.6 release notes", or
`/announce-conan-release`, and give the version + a few highlights.

## What it needs

- The three sibling repos under `~/Development/`: `conan`, `conan-marketing`,
  `conan-license`.
- For the email step: a **Full-access** `RESEND_API_KEY` (passed inline) and
  `RESEND_SEGMENT_ID`. No other secrets; the skill itself stores nothing.

## How it works (high level)

1. Gather the exact version string + 2–4 user-facing highlights.
2. Add the in-app "What's New" entry **first** (it ships in the app build, so it
   must land before `release-conan` builds).
3. After the release is live, add the newest-first changelog entry and push
   conan-marketing (Vercel deploys it).
4. Draft the buyer email in Resend via `npm run draft-broadcast` — a human
   reviews and sends it.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `references/surfaces.md` — exact files, fields, commands, and gotchas per surface.
- `handoff.md` — design decisions and the "why".
