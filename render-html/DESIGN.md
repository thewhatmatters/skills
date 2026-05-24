---
version: alpha
name: Anthropic Reading
description: The anthropic.com reading aesthetic — warm ivory page, clay accent, serif headings over a clean grotesque-sans body, light/dark aware
colors:
  background: "#F0EEE6"
  surface: "#F7F6F2"
  foreground: "#191917"
  muted: "#6B6A63"
  accent: "#CC785C"
  accent-ink: "#B0613F"
  line: "#DEDBD0"
  code-bg: "#E7E4D8"
  background-dark: "#1F1E1B"
  surface-dark: "#26241F"
  foreground-dark: "#EDEAE0"
  muted-dark: "#A7A498"
  accent-dark: "#E0937A"
  line-dark: "#3A372F"
  code-bg-dark: "#2A2823"
typography:
  h1:
    fontFamily: "Tiempos Headline, Source Serif 4, Georgia, serif"
    fontSize: 2.4rem
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.01em
  h2:
    fontFamily: "Tiempos Headline, Source Serif 4, Georgia, serif"
    fontSize: 1.6rem
    fontWeight: 600
    lineHeight: 1.2
  h3:
    fontFamily: "Tiempos Headline, Source Serif 4, Georgia, serif"
    fontSize: 1.25rem
    fontWeight: 600
    lineHeight: 1.2
  body-md:
    fontFamily: "Styrene B, Hanken Grotesk, ui-sans-serif, system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"
    fontSize: 17px
    fontWeight: 400
    lineHeight: 1.65
  mono:
    fontFamily: "ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, monospace"
    fontSize: 0.88em
rounded:
  sm: 4px
  md: 8px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
components:
  page:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: 16px
  code-inline:
    backgroundColor: "{colors.code-bg}"
    rounded: "{rounded.sm}"
  link:
    textColor: "{colors.accent-ink}"
  blockquote:
    textColor: "{colors.muted}"
---

## Overview

The anthropic.com reading aesthetic: a warm **ivory** page, near-black slate
text, a single **clay/terracotta** accent for links and rules, **serif** display
headings over a clean **grotesque-sans** body, generous line-height, and a
narrow reading column. Editorial and calm — a premium broadsheet, not a
dashboard. This is the visual identity `render-html` applies (and the palette
`draw-diagram`'s `--theme=brand` mirrors).

This DESIGN.md is the **canonical source of truth** for the brand. The render
scripts currently hard-code these values (they're pure-stdlib, no YAML parser);
when the brand changes, change it here **and** in the scripts together. Runtime
parsing of this file is a possible future enhancement.

## Colors

High-contrast warm neutrals with one accent driver. Each token has a `*-dark`
counterpart used under `@media (prefers-color-scheme: dark)`.

- **background (#F0EEE6 / dark #1F1E1B):** ivory page; warm dark in dark mode.
- **surface (#F7F6F2 / #26241F):** raised fills — cards, table headers, TOC,
  `<details>` panels.
- **foreground (#191917 / #EDEAE0):** body text.
- **muted (#6B6A63 / #A7A498):** meta, captions, footer, blockquote text.
- **accent (#CC785C / #E0937A):** "Crail" clay — rules, the blockquote bar, the
  `<details>` marker.
- **accent-ink (#B0613F / #E0937A):** link text (darker on ivory for contrast).
- **line (#DEDBD0 / #3A372F):** hairline borders.
- **code-bg (#E7E4D8 / #2A2823):** inline-code and code-block background.

## Typography

- **Headings (h1–h4):** `Tiempos Headline` → `Source Serif 4` → `Georgia` →
  serif, weight 600. (h4 is the same stack but recolored `--muted` for a quieter
  sub-heading, per `render.py`.)
- **Body:** `Styrene B` → `Hanken Grotesk` → system sans, 17px / line-height 1.65.
- **Mono:** `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`.

**Font licensing (non-negotiable).** Anthropic's real brand fonts — **Styrene**
and **Tiempos** — are licensed/proprietary and are **not** bundled. The stacks
name them first (so they render for anyone who has them), then fall back to free
Google-Fonts substitutes (**Source Serif 4** ≈ Tiempos, **Hanken Grotesk** ≈
Styrene), then to the system serif/sans stack offline. The Google-Fonts `<link>`
is the *only* external reference in the output and loads at view time, never at
render time; `--no-webfonts` drops it for a fully offline file. The result is a
faithful approximation, not a pixel-exact copy — by license and by design.

## Layout

- Single centered reading column, `max-width: 720px`, `padding: 4rem 1.25rem 6rem`.
- Spacing roughly on an 8px rhythm (`spacing.sm/md/lg`).
- Corner radii: `sm` (4px) for inline code, `md` (8px) for cards / code blocks /
  TOC / `<details>`.

## Components

- **page** — ivory background, slate text; `color-scheme: light dark`.
- **card / surface** — `surface` fill, `md` radius, 1px `line` border (TOC nav,
  `<details>` accordions, table headers).
- **link** — `accent-ink`, underline with offset; underline drops on hover.
- **blockquote** — 3px `accent` left bar, `muted` text.
- **code** — `code-bg` fill; inline gets `sm` radius, blocks get `md` + border.

## Do's and Don'ts

- **Do** keep the single clay accent sparing — links, rules, markers. One accent
  driver, not many.
- **Do** preserve the light/dark pairing for every color token.
- **Don't** introduce a second accent hue or heavy color fills — the look is
  matte and neutral.
- **Don't** claim pixel-parity with anthropic.com; the licensed fonts are
  substituted on purpose.
- **Don't** add runtime/network/JS dependencies to achieve the look — it must
  stay self-contained.
