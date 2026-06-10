# The voice pass — spec format, audit method, bootstrap

Loaded by `SKILL.md` Step 4 when a voice spec resolved (or at Step 2 to
bootstrap one). The spec is per-project and checked in; this file only defines
the *shape* and the *method*.

## The attribute set (what a `## Voice` section declares)

A usable spec pins these — each one auditable per string:

| Attribute | Example values |
|---|---|
| **Formality** | crisp-professional · warm-casual · editorial |
| **Person** | second person ("your projects") · possessive-neutral ("projects") |
| **Contractions** | always ("you're") · never ("you are") |
| **Exclamation policy** | never · success-moments-only |
| **Capitalization** | sentence case everywhere · Title Case for headings only |
| **Emotion ceiling** | restrained (no "awesome!", no emoji) · expressive |
| **Humor** | none · dry, never in errors |
| **Terminology** | the canonical term per concept ("workspace", not "team space") |
| **Words we never use** | e.g. "simply", "just", "please" in errors, "oops" |

Plus 3–5 **calibration pairs** — real before→after examples from this product —
which do more work than any adjective list.

## Auditing against the spec

For each extracted string, check only the attributes the spec actually pins
(don't invent constraints the project didn't choose). A violation finding
names the attribute: *"`Oops! Something broke!` — violates exclamation policy
(never) and emotion ceiling (restrained)"* → one rewrite that fixes all named
attributes at once. Voice findings are 🟡 unless they collide with the floor
(then the floor's severity wins).

## Bootstrap (no spec found — interactive only)

1. Read the product's 3–4 best surfaces (the ones the user is proudest of, or
   the highest-traffic routes) from the extraction.
2. Derive the de-facto value for each attribute above from what the copy
   *already does* — the spec should describe the product's voice at its best,
   not impose this template's.
3. Where the existing copy is silent or inconsistent, seed from the **luxury
   baseline** below — and mark those rows "(default — confirm)".
4. Propose the section for the user to paste into DESIGN.md (or VOICE.md if
   they prefer). **Never write it into their project unasked; never commit.**

## Luxury baseline (the seed, not the law)

```markdown
## Voice

- Formality: crisp, assured, unhurried — confident enough to be brief
- Person: second person; the product never says "I"
- Contractions: yes — "you're", "it's" (stiffness reads as cheap, not formal)
- Exclamations: never
- Capitalization: sentence case everywhere, including buttons
- Emotion ceiling: restrained — no "awesome", no emoji in UI chrome
- Humor: none in errors or destructive flows
- Words we never use: "simply", "just", "oops", "please wait"
- Errors: name what happened and the next step; never blame, never apologize twice
- Calibration:
  - "Oops! Something went wrong!" → "Something went wrong on our end. Try again,
    or check status.example.com."
  - "Submit" → "Save changes"
  - "Are you sure?" → "Delete this project? This can't be undone."
```

Luxury in microcopy is mostly **restraint + precision**: fewer words, exact
verbs, no manufactured enthusiasm. The baseline encodes that; a project's
spec may consciously diverge — the spec wins.
