# The three announcement surfaces

Loaded by SKILL.md (progressive disclosure, spec A1). Exact files, fields,
commands, and gotchas for each surface. Repos are siblings under
`~/Development/` (`conan`, `conan-marketing`, `conan-license`).

## Ordering (why it matters)

1. **What's New (conan)** — edit **before** the app build, because it ships in
   the bundle.
2. **release-conan** builds + ships the app (not this skill).
3. **Changelog (conan-marketing)** and **buyer email (conan-license)** — after
   the release is live, so you never point users at a build they can't download.

Running purely as a post-ship announcement (app already built with the What's
New entry)? Then only steps 3's surfaces remain — changelog + email.

---

## Surface 1 — In-app "What's New" popup (`conan`)

- **File:** `conan/ui/src/data/whatsNew.ts` — the `WHATS_NEW` record.
- **Component:** `conan/ui/src/components/WhatsNew.tsx` (shows once after a
  returning user updates + restarts; gated on version-change + prior-run).
- **Add an entry keyed to the EXACT app version string** (must match
  package.json / src-tauri/tauri.conf.json), e.g.:
  ```ts
  "1.0.6": {
    version: "1.0.6",
    highlights: [
      "Claude Radio always finds the live stream now — no more “Offline”.",
      "A What's New note after each update.",
    ],
  },
  ```
- **Fields:** `version` (string) + `highlights` (string[], **2–4 short teaser
  bullets**). There is **NO title field** (removed by design).
- **Gotchas:**
  - A version with **no entry** simply shows no popup — fine for trivial
    patches you don't want to interrupt anyone over.
  - It ships in the app bundle ⇒ **edit before `release-conan` builds**. If the
    build/release already happened for this version, a rebuild + re-release is
    required for the popup to appear.
- **Verify:** `cd conan/ui && npm run build` (clean).

## Surface 2 — Marketing changelog (`conan-marketing`)

- **File:** `conan-marketing/src/data/releases.ts` — the `releases` array.
- **Add a NEW entry at the TOP** (newest-first; the page badges index 0 as
  "Latest"). Renders the ember-rail timeline at `/changelog`.
- **Fields:** `version`, `date` (ISO `YYYY-MM-DD`), `title` (short headline),
  `summary` (one sentence), `highlights` (string[], the fullest of the three
  surfaces), `kind` (`"launch" | "feature" | "fix"`).
- **Verify:** `cd conan-marketing && npm run build` (clean).
- **Deploy:** commit, then **confirm before `git push` to main** — Vercel
  auto-deploys www.conan.sh on push.

## Surface 3 — Buyer announcement email (`conan-license`)

- **Command (run from `conan-license/`):**
  ```bash
  RESEND_API_KEY=re_… RESEND_SEGMENT_ID=… npm run draft-broadcast -- \
    --version 1.0.6 \
    --point "…" --point "…"
  ```
- Creates a Resend **DRAFT** broadcast (founder voice) via `POST /broadcasts`
  with `send` omitted. `--dry-run` prints the subject + HTML without calling
  Resend (use it to preview).
- **Gotchas:**
  - `RESEND_API_KEY` must be **Full-access** and passed **INLINE** — it's marked
    Sensitive in Vercel, so `vercel env pull` will NOT retrieve it. A send-only
    key returns 401/403.
  - `RESEND_SEGMENT_ID` **does** pull from `vercel env pull` (it's non-sensitive)
    — or pass inline too.
  - **NEVER send programmatically.** The skill creates the draft; the human
    reviews + clicks Send in the Resend dashboard (https://resend.com/broadcasts).
- Background on the Resend model (global contacts, segment-targeted broadcasts):
  see the project memory `project_conan_mailing_list`.

## Per-surface emphasis

Same release, three voices:
- **Changelog** — fullest: a one-sentence `summary` + several `highlights`.
- **What's New** — 2–4 short teaser bullets, no summary.
- **Email** — founder voice, the same few points as `--point` lines.
