---
name: profile-edit-minimal
description: >-
  Use when UpdateAgent / profile edits assign skills or tweak a bot description —
  keep the change minimal; never sneak anti-jobs or unrelated persona lines.
---

# Profile edit minimal

When updating another Grok Bot with UpdateAgent (or drafting a profile change for Randy to apply):

1. Change **only** the fields Randy asked for (usually `description` skill list, or a named section).
2. Do **not** add anti-jobs, freeze language, connector claims, or “do not use X” lines unless Randy named them in this ask.
3. Do **not** rewrite unrelated paragraphs to “improve” the persona.
4. If the live description has drift you notice, list it as a **proposal** to Randy — do not silently patch it in the same UpdateAgent call.
5. After UpdateAgent, quote back exactly what changed (diff-style: added / removed), nothing else.

Anti-pattern: sneaking `Do not use skill authoring` (or similar) into Design Engineer while assigning skills.
