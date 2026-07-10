# polish-copy

**What it is:** A microcopy review pass that elevates product copy to a luxury-grade bar — proposing before→after rewrites, never mass-rewriting.

## What you get

- A findings report (`copy-review-<date>.md`) grouped by severity, each finding showing the current text with `file:line`, the rule it violates, and one proposed rewrite.
- Two review layers: a universal craft floor (vague CTAs, robotic errors, dead empty states, inconsistent casing) that runs on every project, plus a voice pass against *your* project's voice spec.
- If your project has no voice spec yet: an offer to draft one — a `## Voice` section derived from your existing copy, seeded from a luxury baseline, yours to approve and commit.

## How to run

Say "polish the copy", "review the microcopy on the settings page", "fix these error messages", "copy audit before ship" — or directly:

```
/polish-copy --path=src/app/onboarding
```

## What it needs

- Nothing to install — no keys, no network, stdlib Python (and even that is optional; the skill degrades to reading files by hand).
- A voice spec makes the second layer work: a `## Voice` section in your project's `DESIGN.md` (the default convention) or a standalone `VOICE.md`. Without one, the floor still runs and the skill offers the bootstrap.

## How it works (high level)

1. Preflight locates your voice spec (DESIGN.md `## Voice` → VOICE.md → none) and detects which copy sources exist.
2. A script extracts user-facing strings — JSX/HTML text and attributes, iOS String Catalogs (`.xcstrings`/`.strings`) — each with `file:line`.
3. Claude reviews every string against the floor, then against your voice attributes, and writes one rewrite per finding.
4. You approve findings (all, by severity, or per item); only approved rewrites are written, and nothing is ever committed.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/` — `floor.md` (the universal rules), `voice-pass.md` (the voice attribute set, audit method, bootstrap recipe, luxury baseline).
