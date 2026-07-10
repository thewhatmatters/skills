# source-ui

**What it is:** Source real UI references — screens, components, flows, and visual styles — by routing a design need to Mobbin or Refero with the right tool.

## What you get

- A curated set of real-product UI references for your need — screens (with images), visual-style systems, or multi-step flows — each with a one-line "why it fits" and a source link.
- Optionally a markdown file (`--out`) you can hand to render-html or generate-prd.

## How to run

Say what you're looking for — "find footer references", "how do apps do onboarding", "UI inspiration for a pricing page" — or invoke `/source-ui <need>`. Steer with `--platform=ios|web`, `--limit=N`, or `--styles`.

## What it needs

The **Mobbin** and **Refero** MCP servers connected (they handle their own login). No keys or `.env` for this skill. If neither is connected, it falls back to built-in web search and tells you so.

## How it works (high level)

1. Reads your need and classifies it: screen, component, flow, or visual-style.
2. Checks which MCP servers are available (Mobbin, Refero).
3. Routes to the best tool for that need (see `references/routing.md`).
4. Curates the results — keeps the on-target hits, drops the rest, cites each.
5. Presents them inline, or writes a markdown set you can style or spec further.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/routing.md` — the library/tool decision table.
