# Notice

This skill is adapted from `skills/engineering/codebase-design/` and
`skills/engineering/improve-codebase-architecture/` in
[mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock,
licensed under the MIT License. The repo's README explicitly invites this:
"Hack around with them. Make them your own."

## What changed from the source

- Frontmatter rewritten to this house's conventions (trigger-rich
  `description`; no `disable-model-invocation` — the scan is `--improve`,
  not a hidden skill).
- `DEEPENING.md` and `DESIGN-IT-TWICE.md` under `references/`. The scan
  workflow lives in `references/improve.md`; HTML/CONTEXT/ADR formats
  moved here from the former `improve-codebase-architecture/` skill.
- The upstream `/domain-modeling` skill was **not** ported. Only
  `CONTEXT-FORMAT.md` and `ADR-FORMAT.md` were copied. Active
  domain-modeling (challenging terms, etc.) was dropped.
- `--improve` report defaults to markdown; `--html` is the original visual
  report. No sibling-skill preflight (2026-09-11: `grilling` retired).
- Added this NOTICE.md and a plain-language README.md.

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
