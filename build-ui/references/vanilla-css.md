# Vanilla CSS — working in this project's setup

Loaded by `SKILL.md` Step 3 when `probe.css == "vanilla"` (no Tailwind, no
CSS-in-JS framework). Modern vanilla CSS is genuinely capable — use the
platform; don't reinvent.

## What "vanilla" still means in 2026

Treat these as default unless the project's existing CSS explicitly avoids them:

- **CSS custom properties** (`--token`) for *all* design tokens. Define on
  `:root` (and `:root[data-theme="dark"]` or `@media (prefers-color-scheme)`).
  This is the project's token system.
- **`@layer`** for ordering specificity (`reset, base, components, utilities`).
  Cleaner than `!important` chasing.
- **Container queries** (`@container`) when a component's layout should depend
  on its container, not the viewport. They're widely supported now.
- **Logical properties** (`margin-inline`, `padding-block`) for any text that
  could be RTL; otherwise `margin-left`/`right` is fine.
- **`color-mix()` / `oklch()`** for derived colors instead of pre-computing
  shades — fewer tokens, more flexibility.
- **`:has()`** for parent-selector cases (a card that styles itself when it
  contains an image).

## Conventions worth matching

Read the existing CSS first; mimic the shape rather than imposing one:

- **File layout.** Project-wide → `src/styles/` (`tokens.css`, `globals.css`,
  `reset.css`). Per-component → CSS Modules (`Component.module.css`) or
  co-located CSS the project imports. Don't introduce a second pattern.
- **Naming.** BEM (`block__element--modifier`), suffix utility (`-sm`), or
  semantic by section — whatever the repo already uses. Pick the dominant
  pattern and follow it.
- **Reset.** A modern reset is probably already in place (Andy Bell, Josh
  Comeau, or hand-rolled). Don't add a second.
- **Units.** Match what the project uses for sizing (`rem` for type and
  spacing; `px` for hairline borders; `%`/`fr`/`ch` where they make sense).

## When vanilla beats utilities/CSS-in-JS

- **Marketing pages and one-off layouts** with strong typography and rhythm.
- **Print stylesheets, email-safe HTML, embeddable widgets.**
- **Component libraries that must work outside the project's runtime** (Web
  Components, distributed bundles).

## Pitfalls

- **Don't introduce CSS-in-JS** the project doesn't use (no `styled-components`,
  no `emotion`) — that's a runtime + tooling change.
- **Don't fight cascade** with `!important`. Use `@layer` to control ordering.
- **Don't hand-write rgba shades** when `color-mix(in oklch, var(--ink) 60%,
  transparent)` does the same and stays tied to the token.
- **No anonymous `<div>` salad.** Use semantic elements (`<header>`, `<nav>`,
  `<main>`, `<section>` with a heading, `<article>`, `<footer>`). The a11y
  reference will catch this in review but it's faster to get it right first.
- **No deeply nested selectors.** `nav ul li a span` is fragile. Use classes or
  the cascade thoughtfully.

## Tokens (when the project doesn't already have a system)

A small viable starting set, kept in `tokens.css`:

```css
:root {
  --bg: #ffffff;
  --fg: #0a0a0a;
  --muted: color-mix(in oklch, var(--fg) 60%, transparent);
  --line: color-mix(in oklch, var(--fg) 12%, transparent);
  --accent: oklch(70% 0.18 230);
  --space-1: 0.5rem;
  --space-2: 1rem;
  --space-3: 1.5rem;
  --radius: 8px;
  --font-display: "Tiempos Headline", ui-serif, Georgia, serif;
  --font-body: "Hanken Grotesk", ui-sans-serif, system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #0a0a0a; --fg: #ededed; --line: color-mix(in oklch, var(--fg) 16%, transparent); }
}
```

If the project already has tokens, *extend* them — don't shadow.

## Composition with frontend-design

Vanilla CSS gives `frontend-design`'s direction the most room: dramatic
typography stacks, unusual layouts (CSS Grid with `subgrid`,
asymmetric/diagonal flows), considered backgrounds. The implementation isn't
exotic; the *choices* are.
