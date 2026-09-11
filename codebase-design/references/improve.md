# `--improve` — scan for shallow modules

Only run this file when the user asked for a **scan / architecture review**
(`--improve`, `/improve-codebase-architecture`, "find shallow modules",
"improve the architecture of this codebase"). Do **not** enter this path
for ordinary "design this module" questions — those stay on SKILL.md.

Informed by `CONTEXT.md` (format: `references/CONTEXT-FORMAT.md`) and ADRs
in `docs/adr/` (format: `references/ADR-FORMAT.md`). Use the glossary in
SKILL.md exactly — don't drift into "component," "service," "API," or
"boundary."

## 0. Preflight

No sibling skills. Proceed.

## 1. Explore

Read `CONTEXT.md` and any ADRs covering the area, if they exist.

Then use the Agent tool with `subagent_type=Explore` (fall back to
`general-purpose`; if the Agent tool is unavailable, explore inline: degrade,
never block). Note friction:

- Understanding one concept requires bouncing between many small modules
- Modules **shallow** — interface nearly as complex as the implementation
- Pure functions extracted just for testability; real bugs hide in how
  they're called (no **locality**)
- Tightly-coupled modules leak across their seams
- Untested, or hard to test through the current interface

Apply the **deletion test** to anything suspected shallow: would deleting
it concentrate complexity, or just move it? A "yes, concentrates" is the
signal.

## 2. Report

Default: **markdown in the conversation**. `--html` for a visual HTML file.

**Markdown.** One `##` section per candidate. Before/after in fenced
`mermaid` when graph-shaped, else a compact table or tree — never pad.
No file.

**HTML (`--html`).** Write to the OS temp dir (`$TMPDIR` → `/tmp` /
`%TEMP%`): `<tmpdir>/architecture-review-<timestamp>.html`. Open it
(`open` / `xdg-open` / `start`) and print the absolute path. Skip auto-open
under `--agent`. Tailwind + Mermaid via CDN. Mix Mermaid (graphs) with
hand-built divs/SVG (editorial). Scaffold:
[`HTML-REPORT.md`](HTML-REPORT.md).

Each candidate:

- **Files**
- **Problem**
- **Solution** (plain English; no interface yet)
- **Benefits** (locality, leverage, tests)
- **Before / After diagram**
- **Recommendation strength** — `Strong` / `Worth exploring` /
  `Speculative`

End with **Top recommendation**. Domain names from `CONTEXT.md`;
architecture terms from SKILL.md. If `CONTEXT.md` defines "Order," say
"the Order intake module" — not "the FooBarHandler" and not "the Order
service."

**ADR conflicts:** only surface a contradicting candidate when friction is
real enough to reopen the ADR. Mark it. Don't list every theoretical
refactor an ADR forbids.

Do NOT propose interfaces yet. Ask: "Which of these would you like to
explore?"

Under `--agent`: report, then stop (no selection, no Step 3).

## 3. Interview

Once the user picks a candidate, interview **one question at a time**,
each with a recommended answer — constraints, dependencies, shape of
the deepened module, what sits behind the seam, what tests survive.
Wait for an answer before the next question. Look up facts in the
codebase; put decisions to the human.

`CONTEXT.md` edits happen inline inside that conversation (user is
steering). An ADR is a new file — offer before writing.

- New concept not in `CONTEXT.md` → add it
  ([`CONTEXT-FORMAT.md`](CONTEXT-FORMAT.md)); create the file lazily.
- Fuzzy term sharpened → update `CONTEXT.md` there.
- User rejects with a load-bearing reason → offer an ADR: *"Want me to
  record this so future reviews don't re-suggest it?"* Skip ephemeral
  ("not now") and self-evident reasons. Format:
  [`ADR-FORMAT.md`](ADR-FORMAT.md).
- Alternative interfaces → [`DESIGN-IT-TWICE.md`](DESIGN-IT-TWICE.md).
