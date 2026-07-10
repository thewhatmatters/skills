# Notice

This skill is adapted from `skills/engineering/improve-codebase-architecture/`
in [mattpocock/skills](https://github.com/mattpocock/skills) by Matt
Pocock, licensed under the MIT License. The repo's README explicitly
invites this: "Hack around with them. Make them your own."

## What changed from the source

- Frontmatter rewritten to this house's `skill-architecture.md` conventions.
  `disable-model-invocation: true` was kept from the source — a deliberate
  call, not a blind copy: see `handoff.md` for the reasoning. Per spec A14,
  because this skill is user-invoked its `description` is written for the
  human skill list (plain sentence, no quoted trigger-phrase block) rather
  than the trigger-rich style used for model-invoked skills — an early draft
  used the trigger-rich style regardless and was corrected after the
  skill-auditor fan-out caught the mismatch (see `handoff.md`).
- Cross-skill references changed from the source's slash-command style
  (`/codebase-design`, `/grilling`) to plain skill-name references (`the
  codebase-design skill`, `the grilling skill`), matching how skills in
  this suite refer to each other elsewhere.
- The upstream skill's `/domain-modeling` dependency (an entire separate
  skill for actively building and challenging a domain model) was **not**
  ported. Instead, `CONTEXT-FORMAT.md` and `ADR-FORMAT.md` — the two format
  references this skill actually consumes — were copied directly into this
  skill's `references/`. The *active* domain-modeling behaviors (challenging
  terms, sharpening fuzzy language, cross-referencing code against the
  glossary) were dropped; only the passive "read/write CONTEXT.md and
  docs/adr/ opportunistically" behavior survives, inline in SKILL.md Step 3.
  See `codebase-design/handoff.md` for when to revisit this.
- Added this NOTICE.md and a plain-language README.md (required by this
  house's spec, pattern A13; the upstream repo doesn't have per-skill
  READMEs).
- No changes to the exploration method, the HTML report format, the
  deferred-interface-design discipline, or the grilling handoff — those are
  unchanged from the source.

## Original license

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
```
