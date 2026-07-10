# Routing: which library + tool for which need

Loaded by `SKILL.md` Step 1 (progressive disclosure, spec A1). Scoped to two
servers — Mobbin and Refero. Do not add other sources here; new capability
composes *between* skills, not inside this one.

## Decision table

| The need is… | Reach for | Why |
|---|---|---|
| "Show me N real examples of a **component/screen type**, fast, as images" | **Mobbin** `search_screens` | Crops to the component and returns base64 images inline — one call, ready to eyeball. `mode=deep` for nuanced intent, `fast` for low latency. |
| "How does this component fit a whole **visual system** (palette, type, rhythm)" | **Refero** `search_styles` → `get_style` | Styles capture footer/hero/etc. *as part of* a page's design language. `get_style` is large (~10–15k chars) — batch ≤3–4. Web marketing/product pages only. |
| "A specific **page** + structured metadata / exact hex colors" | **Refero** `search_screens` → `get_screen` / `get_screen_image` | Page-level, with `UI Elements` / `UX Patterns` / `Page Types` tags and described hexes. Fetch the image explicitly (`thumbnail`\|`full`). |
| "More like **this one** good find" | **Refero** `get_similar_screens` | Expand one screen into a comparable set (limit 1–20). |
| "A complete **multi-step journey** (onboarding, checkout, cancellation)" | **Refero** `search_flows` → `get_flow` | Per-step goal / action / system_response and the user-problem framing. |

## Notes that bite

- **Component queries dilute in Refero `search_screens`** — it matches on the
  `Footer`/etc. UI-element *tag*, so it returns whole pages that merely contain
  the component. For component-level visual sweeps, prefer Mobbin; for visual
  language, prefer Refero `search_styles`.
- **Platform:** Mobbin and Refero screens/flows take `ios|web`. Refero
  **styles are web-only**. Infer platform from the need; default web.
- **Images:** Mobbin returns them inline; Refero requires an explicit
  `get_screen_image` call (search returns image *URLs* + text only).
- **Context cost:** every image and every full style spends context. Cap with
  `--limit`, batch style fetches, and keep only the on-target hits in the
  curated set.

## Fallback (neither MCP server connected)

Degrade to built-in WebSearch / WebFetch: find named products known for the
pattern, describe their approach, link sources. State plainly that visual
references are unavailable without the MCP servers (spec A3/A7).
