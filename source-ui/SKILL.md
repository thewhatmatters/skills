---
name: source-ui
description: Source real-world UI references — screens, components, user flows, and visual-style direction — by routing a design need to the right library (Mobbin or Refero) with the right tool, then returning a curated, cited reference set. Use when the user wants design inspiration or precedent for an interface — "show me examples of X screen", "how do other apps do Y", "find footer/pricing/onboarding references", "what does good Z look like", "UI inspiration for", "reference designs for", "moodboard for this screen", "how should this look". Mobbin returns cropped screens as inline images for fast visual sweeps; Refero adds visual-style systems, page-level screens with metadata/hex colors, and multi-step flows. Composes with render-html and generate-prd as a design-inspiration step. Scoped to Mobbin + Refero only; falls back to built-in WebSearch/WebFetch when neither MCP server is connected.
---

# source-ui

Source real UI references — screens, components, flows, and visual styles — by routing a design need to Mobbin or Refero with the right tool.

## What it does

Takes a UI need stated in plain language and routes it to the best library + tool, then returns a curated reference set. The routing rules (which library wins for which kind of need) live in `references/routing.md` and are loaded only when a request comes in — spec A1. Scoped to two MCP servers, Mobbin and Refero; it does not aggregate other sources.

## How to run

Triggers on phrases like "show me examples of a pricing page", "how do other apps do onboarding", "find footer references", "UI inspiration for a settings screen", or invoke `/source-ui <need>` directly. Add `--platform`, `--limit`, or `--styles` to steer the routing.

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | write the curated reference set to a markdown file (spec A9) |
| `--platform=ios\|web` | constrain results to one platform (default: infer from the need, else web) |
| `--limit=N` | cap screens returned per query (Mobbin 1–30; keeps context lean) |
| `--styles` | force the Refero `search_styles` path (visual-system direction, not screens) |

## Step 0 — Mode probe (spec A3)

Docs-only skill — no Python, no `scripts/`. The mode probe is **native**: check the available tool list for `mcp__mobbin__*` and `mcp__refero__*`.

- **Both present →** FULL: route freely across Mobbin + Refero per `references/routing.md`.
- **One present →** DEGRADED: use the one that is connected; note the gap in the summary.
- **Neither present →** surface the gap as a Setup Gate (spec A7), don't degrade silently: name the missing servers (Mobbin / Refero are client-side MCP config Claude can't connect for you) and offer the choice — *connect them and retry* vs *proceed now on the web fallback*. Interactive: ask. Under `--agent`: skip the prompt, proceed on FALLBACK, and record the gate in the summary. FALLBACK = built-in WebSearch / WebFetch for textual precedent and named examples (no images). Never block.

## Steps 1..N — flow

1. **Classify the need** — screen / component / flow / visual-style? (decides the tool — see `references/routing.md`).
2. **Probe** — Step 0 native MCP check; pick FULL / DEGRADED / FALLBACK.
3. **Route & fetch** — call the matched tool (e.g. Mobbin `search_screens` for fast image sweeps; Refero `search_styles` for visual systems; Refero `search_screens` → `get_screen_image` for page-level detail; Refero `search_flows` → `get_flow` for journeys).
4. **Curate** — dedupe, keep the on-target hits, summarize why each fits; cite the source URL per item.
5. **Hand off** — present inline, or with `--out` write a self-contained markdown set whose header records the original need, the date, and which servers answered (FULL/DEGRADED/FALLBACK) — spec A10. When the set spans more than one source (e.g. Mobbin + Refero), wrap the per-source groups in a render-html `::: tabs` block (one `=== <source>` tab each) so the rendered page tabs between them; keep meta sections (e.g. "How these were routed") outside the tabs. Interactive: offer to pipe into render-html or generate-prd. Under `--agent`: skip that offer; just write `--out` if given.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Composition by reference, not import — names render-html / generate-prd; runs neither's code (spec A8 family convention).
- Keyless: the MCP servers own their own auth; this skill loads no secrets.
- Degrades rather than blocks (spec A3/A7): MCP → WebSearch/WebFetch fallback.
