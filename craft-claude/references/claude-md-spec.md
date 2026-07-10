# The CLAUDE.md spec — canon for craft-claude

This is the **single source of truth** for every craft-claude mode (author,
audit, maintain), the way `skill-architecture.md` is the canon for
`audit-skill`/`generate-skill` (spec A1). Both AUTHOR and AUDIT read *this* —
SKILL.md does not duplicate the rubric, it points here.

**Authority:** the official Claude Code memory docs (`code.claude.com/docs`),
verified at CC 2.1.145. Where popular guides (e.g. the AllyHub infographic in
this folder) disagree with the docs, **the docs win** — see §6 Folklore.

---

## 1. Verified mechanics (the ground truth)

These are the load-bearing facts. Re-verify against the live memory docs when
Claude Code updates; do not encode folklore as law.

### 1.1 Scopes & load order
Claude Code reads CLAUDE.md from several scopes, highest-precedence last:

| Scope | Path | Shared? | Purpose |
|---|---|---|---|
| Managed/enterprise | `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS), `/etc/claude-code/CLAUDE.md` (Linux), `C:\Program Files\ClaudeCode\CLAUDE.md` (Win) | org policy | org-wide instructions an admin sets |
| Global / user | `~/.claude/CLAUDE.md` | no (you) | personal style across all projects |
| Project | `./CLAUDE.md` **or** `./.claude/CLAUDE.md` | git ✓ | team standards & architecture |
| Nested / directory | `./<subdir>/CLAUDE.md` | git ✓ | subsystem-specific rules |
| Personal local | `./CLAUDE.local.md` | no (gitignore) | your per-project overrides |

- **Nested CLAUDE.md loads on demand** — only when Claude *reads* a file in
  that subdirectory, not eagerly at session start.
- `CLAUDE.local.md` is **current**, not deprecated; it's the gitignored
  personal override layer.

### 1.2 Path-scoped rules — `.claude/rules/*.md`
Rule files in `.claude/rules/` can target paths via YAML frontmatter:

```
---
paths:
  - "src/components/**/*.tsx"
---
# React component rules
- …
```

- **CRITICAL CAVEAT:** a path-scoped rule loads when Claude **reads** a file
  matching the glob — **not** when it **Writes** a new file at that path. Do
  not rely on these for generation-time guidance on brand-new files; put
  must-always-hold generation rules in the project CLAUDE.md instead.

### 1.3 `@`-imports
- `@path/to/file` inside a CLAUDE.md inlines that file. Relative paths resolve
  against the file containing the import (not cwd); absolute paths allowed.
- **Max recursion depth: 4 hops.** Keep import chains shallow.

### 1.4 Size
- Target **~200 lines** per CLAUDE.md (docs guidance). This is a **soft**
  efficiency target, **not** an enforced limit — longer files consume context
  and reduce instruction adherence. (Folklore "under 300, always" is both
  looser than the docs and overstated as a hard law.)

### 1.5 Auto memory & `/memory`
- Auto memory lives at `~/.claude/projects/<project>/memory/MEMORY.md`; the
  loader reads the **first 200 lines or 25 KB, whichever comes first** — move
  detail to topic files it loads on demand.
- `/memory` lists every CLAUDE.md, CLAUDE.local.md, and rules file loaded in
  the session, toggles auto memory, and opens files in your editor. This is the
  verify-what-loaded command; recommend it after any author/maintain change.

---

## 2. What a healthy CLAUDE.md looks like (AUTHOR target)

Structure to scaffold (omit sections a project doesn't need; keep it lean):

1. **Project overview** — one brief paragraph: what the codebase is, written
   like briefing a new contractor.
2. **Tech stack** — the few facts Claude can't cheaply infer.
3. **Architecture** — directory → responsibility map (only the non-obvious).
4. **Coding rules** — *hard* rules (see §3.2), positive where natural.
5. **Commands** — build / test / lint, the exact invocations.
6. **Gotchas** — the traps (migration order, token expiry, "never commit X").

Layer *above* `/init`, don't duplicate it: `/init` writes a generic file;
craft-claude adds the scope/rules/memory layering — split a large subsystem
into `.claude/rules/<area>.md` with a `paths:` glob, wire shared indexes via
`@`-import, point personal overrides at `CLAUDE.local.md`.

---

## 3. Audit rubric (AUDIT mode)

Each finding gets a **severity**, a `file:line` (or section) locator, and a
concrete fix. Severities follow `skill-architecture.md` §C
(🔴 critical / 🟠 important / 🟡 minor).

### 3.1 Size & bloat — 🟡 (🟠 if ≫ target)
- Primary CLAUDE.md over **~200 lines** → flag; over ~400 → 🟠. Fix: split the
  largest cohesive subsystem into `.claude/rules/<area>.md` (`paths:` glob) or
  an `@`-imported topic file.

### 3.2 Soft rules where hard rules belong — 🟠
- Lines like "consider using X", "try to", "prefer X when possible" for a rule
  that should always hold. Fix: rewrite as an imperative invariant ("Use X",
  "All async functions have a timeout"). Genuine preferences may stay soft —
  judgment, not a blunt grep.

### 3.3 Inlined examples that should be references — 🟡
- Long code blocks pasted into CLAUDE.md that duplicate real source. Fix:
  replace with a `file:line` pointer ("see `src/api/client.ts:42`"); Claude
  reads the file on demand. Keep tiny illustrative snippets.

### 3.4 Stale / drifted rules — 🟠
- Rules referencing files, scripts, commands, or deps that no longer exist
  (cross-check the repo). Fix: update or delete. This is the maintain-mode core.

### 3.5 Missed scoped-rules split — 🟡
- A clearly subsystem-specific block (e.g. "React component rules", "DB
  migration rules") sitting in the root file, applying to one directory. Fix:
  move to `.claude/rules/<area>.md` with a `paths:` glob — but note §1.2: it
  loads on read, not write, so keep generation-time invariants in CLAUDE.md.

### 3.6 Broken imports / depth — 🟠
- `@`-import to a missing path, or a chain deeper than 4 hops. Fix: correct the
  path or flatten the chain.

### 3.7 Invented mechanics / folklore — 🟠
- Instructions that assume behavior Claude Code doesn't have (see §6). Fix:
  remove or replace with the real mechanism.

### 3.8 Self-contradiction — 🟡
- The file bans a pattern it then uses (the classic: a "don't use negative
  framing" rule beside a `# Never Do` block). Fix: reconcile to one stance.

---

## 4. Framing guidance (nuanced — not a blunt rule)

Hard, specific, positive rules adhere best ("Use `unknown` + a guard, never
`any`"). But **negative framing is legitimate** for genuine prohibitions — a
`# Never Do` / `# Gotchas` block is fine and common. Do **not** mechanically
rewrite every "don't" into an "always"; flag negative framing only when a
positive imperative is clearly stronger. (This is exactly where the AllyHub
infographic contradicts itself — §6.)

---

## 5. MAINTAIN mode
A focused pass: §3.4 staleness (dead refs/commands/deps), §3.1 bloat →
propose splits, §3.6 broken imports. Output a short prune list; edits go behind
the A7 consent gate.

---

## 6. Folklore vs docs (what NOT to encode as law)
The AllyHub "CLAUDE.md — The Complete Guide" infographic (in `references/`) is
a useful visual but wrong in three places — treat it as a poster, not a spec:
- **"Under 300 lines. Always."** — docs target ~200 and it's *soft*, not a hard
  cap (§1.4).
- **Negative framing banned** — yet its own model Global example ships a
  `# Never Do` block. Negative framing is fine for prohibitions (§4).
- **Path-scoped rules "load on demand"** — true, but it omits that they load on
  **read, not write** (§1.2), and it omits the managed/enterprise scope (§1.1).
