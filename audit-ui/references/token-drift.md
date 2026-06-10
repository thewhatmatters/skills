# tokens dimension — drift rules and noise control

Loaded by `SKILL.md` Step 2 when the tokens dimension is in scope.
`token_drift.py` finds literals; this file is how to judge them.

## What the script gives you

- **spec mode** (DESIGN.md found): every color (`#hex`, `oklch(...)`) and
  font-family first-name in source that is **not** in the DESIGN.md token set,
  with `file:line` + context. Handles both DESIGN.md flavors (google-labs YAML
  tokens; Stitch natural-language-with-hex).
- **no-spec mode** (no DESIGN.md): `top_values` — the most-repeated hard-coded
  colors/fonts. That's an internal-consistency signal, not drift; recommend the
  `design-md` skill (or hand-writing a DESIGN.md) to get a spec to audit against.

## Judging drift (the script can't)

1. **Cluster before reporting.** 30 uses of `#6b7280` across files = ONE
   finding ("`#6b7280` used 30× — likely wants a `muted-foreground` token"),
   not 30 rows. The per-line list is evidence, not the report.
2. **Near-misses are the real signal.** A color one step off the palette
   (`#f8f8f7` vs token `#faf9f5`) is classic copy-tweak drift — 🟠. A
   completely foreign color in one place may be intentional (a brand logo,
   a syntax theme) — ask, or 🟡 with a question mark.
3. **Whitelist the legit sources before judging:**
   - shadcn/Tailwind projects: colors *should* flow through CSS variables /
     `@theme` — a hex in `globals.css`/`tailwind.config.*`/`@theme` blocks IS
     the token definition, not drift. Check the file path before flagging.
   - Third-party CSS, email templates, and OG-image generators legitimately
     hard-code.
4. **Fonts:** any first-family not in the spec is 🟠 (fonts are few and
   deliberate); a generic stack difference (`system-ui` vs `ui-sans-serif`) is 🟡.
5. **Spacing is judgment-only in v1.** The script doesn't flag spacing (too
   noisy: every `px` literal isn't a violation). If the visual dimension's
   screenshots show inconsistent rhythm, raise it there.

## Severity

- 🔴 — reserved; token drift alone doesn't block a ship. (Exception: a
  contrast-breaking off-palette color — but that surfaces via a11y.)
- 🟠 — clustered drift (a repeated off-token value), any off-spec font,
  near-miss palette values.
- 🟡 — isolated one-off literals, generic-stack font variance, anything in
  no-spec mode.

## Fix shape (for the build-ui handoff)

The fix is almost always "promote to a token, then reference it": add/identify
the CSS variable (or `@theme` entry), replace the literals. List the exact
`file:line` set per cluster so build-ui can sweep it mechanically.
