# CLAUDE.md & rules templates

Skeletons for AUTHOR mode. Fill only the sections a project needs; keep the
primary file under the ~200-line soft target (`claude-md-spec.md` §1.4). These
are starting points to adapt, not boilerplate to paste whole.

---

## A. Project CLAUDE.md skeleton

```markdown
# <Project> — CLAUDE.md

## Project overview
<One paragraph: what this codebase is, like briefing a new contractor.>

## Tech stack
- <language/runtime + version>, <framework>, <styling>
- <db/auth>, <deploy target>

## Architecture
- `src/<dir>/` → <responsibility, one line>
- `src/<dir>/` → <responsibility>
(Only the non-obvious. Don't restate what the tree makes clear.)

## Coding rules
- <Hard, positive invariant — "All async functions have a timeout">
- <"Use `unknown` + a guard, never `any`">
- Imports: <convention, e.g. absolute paths only (@/...)>

## Commands
- build: `<cmd>`
- test:  `<cmd>`
- lint:  `<cmd>`

## Gotchas
- <Trap that has bitten someone — migration order, token expiry, "never commit X">
```

Notes:
- Prefer `file:line` pointers over pasting long code (`spec §3.3`).
- A `## Gotchas` / `# Never Do` block is fine — negative framing is legitimate
  for genuine prohibitions (`spec §4`). Don't force every "don't" into "always".

---

## B. Personal override — `CLAUDE.local.md` (gitignored)

```markdown
# Personal overrides (not committed)
- <your per-project preference that the team file shouldn't carry>
```

Ensure `CLAUDE.local.md` is in `.gitignore`.

---

## C. Path-scoped rule — `.claude/rules/<area>.md`

Move a subsystem-specific block out of the root file when it applies to one
directory. Remember the caveat (`spec §1.2`): this loads when Claude **reads** a
matching file, **not** when it Writes a new one — keep generation-time
invariants in the root CLAUDE.md.

```markdown
---
paths:
  - "src/components/**/*.tsx"
---
# React component rules
- Use shadcn/ui primitives; no inline styles — Tailwind only.
- Props typed with an `interface`, not `type`.
- <…>
```

---

## D. Shared index via `@`-import

Keep the root file lean by importing a topic file (depth ≤ 4, `spec §1.3`):

```markdown
## Sources & domain knowledge
@docs/sources/INDEX.md
```

The imported file inlines each session; its linked bodies load on demand — the
same split MEMORY.md uses.
