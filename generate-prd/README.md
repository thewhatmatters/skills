# generate-prd

**What it is:** turns a conversational product brainstorm — the kind of
back-and-forth that fills a chat — into a written Product Requirements
Document you can hand to engineering, design, or your future self.

## What you get

- `prd-<slug>.md` — a markdown PRD with sections: **Problem · Solution · UX
  flow · Technical architecture · Data model · Pricing · Roadmap · Risks ·
  Open questions**. Drops in cleanly anywhere Claude Code reads markdown.
- `prd-<slug>.html` *(optional)* — a single self-contained HTML file (inline
  CSS, no external assets) for sharing or print.

## How to run it

Just ask, e.g.:

- "turn this discussion into a PRD"
- "write a PRD from our conversation"
- "make me a PRD for [product]"
- "spec this product idea out"

By default it synthesizes from the **current chat** (whatever you've been
discussing in this session). You can also point it at a saved transcript:
`--transcript=path/to/chat.txt`.

Want to sanity-check coverage before writing files? Add `--dry-run` — you'll
get the section inventory and the proposed file paths, with nothing committed
to disk.

## What it needs

Nothing required. Optional:

- **`python3`** — for the HTML output. Without it the skill still produces
  the markdown PRD and prints a one-line "HTML skipped" notice.
- No API keys, no external services.

## How it works (high level)

1. **Identifies** the discussion source — your current chat or a transcript
   file — and confirms the product/feature scope.
2. **Synthesizes** the discussion into a structured PRD, staying grounded in
   what was actually said. Sections you didn't discuss are labelled
   "(not discussed)" and pushed into **Open questions** rather than invented.
3. **Writes** the markdown PRD to `<out>/prd-<slug>.md`. If a file with that
   name already exists, the new one gets a numeric suffix — never clobbers.
4. **Renders** an HTML copy (when Python is available and `--no-html`
   wasn't passed) using `scripts/report.py`, with inline CSS so the file is
   shareable as one self-contained artifact.
5. **Reports** what was written, which sections came through cleanly, and
   how many open questions remain — so you know what still needs your input.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `references/output-templates.md` — the JSON shape, markdown layout, and
  synthesis rules in detail.
- `handoff.md` — design decisions and the "why".
