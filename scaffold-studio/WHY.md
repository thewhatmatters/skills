# scaffold-studio — Why

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: 2026-08-27  ·  Generator: generate-skill @ 2026-08-20

## 1. Purpose

Install Motion (machine-wide Cursor plugin) and CSS Studio (per-project,
dev-only) so new web projects share the same agent tooling as LiveATX.

## 2. Reusable patterns (link to spec A1..A15)

Follows `skill-architecture.md` A1–A15. Deliberate notes:

- **A14 model-invoked** despite file/npm side effects: the user wants this
  picked up while *starting* projects ("scaffold with Motion and CSS Studio"),
  not only via a slash they might forget. Side effects still run only when
  that request is explicit. If context cost becomes a problem, flip to
  `disable-model-invocation: true`.
- **A10 artifact** is markdown, not the generate-skill HTML skeleton — a
  scaffold log is read in chat/files, not a branded page (`needs_design` = no).
- **A8** scopes Motion vs CSS Studio; default is both.

## 3. Decision log

- 2026-08-27: scaffolded by generate-skill; filled with LiveATX-proven steps
  (plugin clone to `~/.cursor/plugins/local/motion`; `cssstudio` as `-D`;
  `mkdir .cursor` before `npx cssstudio install`; never edit user `mcp.json`
  for Motion).
- 2026-08-27: Motion plugin is **machine-wide**; CSS Studio is **per-project**.
  Do not add `motion` the npm package unless the user asked for animation code.
- 2026-08-27: CSS Studio must stay **dev-only** (Next `NODE_ENV`, Vite
  `import.meta.env.DEV`, or localhost script tag).

## 4. Known limitations / environment caveats

- Cursor must be fully restarted to load a newly copied local plugin.
- `npx cssstudio install` may write project `.cursor/mcp.json` via `add-mcp`;
  that is intended. User-level `~/.cursor/mcp.json` is not required for Motion.
- Motion+ MCP at `https://mcp.motion.dev/plus` needs a Motion+ account; the
  free plugin MCP still works for docs/springs.
- Cloud agents do not see `~/.cursor/plugins/local` on this Mac.

## 5. Audit rubric coverage

See `skill-architecture.md` §B; this skill targets every PASS that applies.

## 6. Notes

Proven on LiveATX (Next 16 App Router). Recipe files cover Vite and script-tag
apps without assuming Next.
