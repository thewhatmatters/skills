# source-ui — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-05-24  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
Source real UI references — screens, components, flows, and visual styles — by routing a design need to Mobbin or Refero with the right tool.

## 2. Reusable patterns (link to spec A1..A13)
Follows `~/.claude/skills/skill-architecture.md` A1–A13. Deliberate notes:
- **A1 progressive disclosure:** the library/tool decision table lives in `references/routing.md`, loaded only when a request arrives; `SKILL.md` stays lean.
- **A3 dual-mode + degraded ladder:** mode probe is *native* (inspect the tool list for `mcp__mobbin__*` / `mcp__refero__*`), not a Python script — Python cannot see harness-provided MCP tools. Ladder: both servers → one server → WebSearch/WebFetch fallback.
- **No `scripts/` (A4/A6):** like `audit-skill`, this is an orchestration/routing skill. A Python preflight would be hollow (it can't probe MCP connectivity), so the readiness check is folded into the native Step 0.
- **A8 composition by reference:** names render-html / generate-prd as downstream styling/spec steps; imports neither.

## 3. Decision log
- 2026-05-24: scaffolded by generate-skill.
- 2026-05-24: scoped to **Mobbin + Refero only** (no Figma, no other sources) — a tight skill is easier to build to spec and audit; new capability composes between skills, not inside this one.
- 2026-05-24: chose `--no-scripts` (docs-only) over a stub preflight, mirroring `audit-skill`.
- 2026-05-24: routing rules captured from a live "footers" comparison — Mobbin wins for component-level image sweeps; Refero `search_styles` for visual systems; Refero `search_screens` is page-level and dilutes component queries.
- 2026-05-24: **multi-source output tabs.** When a set spans both libraries, the `--out` markdown wraps per-source groups in a render-html `::: tabs` block (Mobbin / Refero tabs) — verified end-to-end via the pricing-page route test. Drove a no-JS `::: tabs` addition to render-html.
- 2026-05-24: self-audit polish (post-scaffold) — (1) "neither MCP connected" now surfaces a Setup Gate with connect/retry-vs-fallback choice instead of bare degrade (A7); (2) `--out` artifact records need + date + which servers answered (A10); (3) `--agent` explicitly suppresses the render-html/generate-prd pipe offer.

## 4. Known limitations / environment caveats
- Requires the Mobbin and/or Refero MCP servers connected; without either, results degrade to textual web precedent only (no images).
- Refero **styles are web-only**; ios visual-system direction is not available from styles.
- Image/style fetches spend context — cap with `--limit`, batch style fetches.

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.

## 6. Notes
Two MCP servers: Mobbin (1 tool, `search_screens`, inline images) and Refero
(8 tools across styles → screens → flows, search-then-fetch). Full tool surface
and routing rationale: see `references/routing.md`. Future direction: chain into
a `source-ui` → `generate-designs` → render-html/generate-prd pipeline.
