---
version: alpha
name: blueprint brand
description: House-brand technical diagrams — the anthropic.com reading aesthetic (warm ivory, clay accent, serif title, grotesque-sans diagram text) applied to architecture artifacts, light/dark aware, with a muted six-hue kind palette.
colors:
  background: "#F0EEE6"
  surface: "#F7F6F2"
  foreground: "#191917"
  muted: "#6B6A63"
  accent: "#CC785C"
  line: "#DEDBD0"
  boundary-fill: "rgba(222,219,208,0.18)"
  background-dark: "#1F1E1B"
  surface-dark: "#26241F"
  foreground-dark: "#EDEAE0"
  muted-dark: "#A7A498"
  accent-dark: "#E0937A"
  line-dark: "#3A372F"
  boundary-fill-dark: "rgba(58,55,47,0.28)"
  kind-service: "#CC785C"
  kind-store: "#7A8B74"
  kind-queue: "#8A7AA0"
  kind-client: "#5B7B94"
  kind-gateway: "#B98A2F"
  kind-external: "#9C9A90"
typography:
  page-title: { fontFamily: "Tiempos Headline, Source Serif 4, Georgia, serif", fontSize: 1.6rem, fontWeight: 600 }
  card-label: { fontFamily: "Styrene B, Hanken Grotesk, ui-sans-serif, system-ui, sans-serif", fontSize: 14px, fontWeight: 600 }
  card-sublabel: { fontFamily: "Styrene B, Hanken Grotesk, ui-sans-serif, system-ui, sans-serif", fontSize: 12px, fontWeight: 400 }
  edge-label: { fontFamily: "Styrene B, Hanken Grotesk, ui-sans-serif, system-ui, sans-serif", fontSize: 12px, fontWeight: 400 }
  boundary-label: { fontFamily: "Styrene B, Hanken Grotesk, ui-sans-serif, system-ui, sans-serif", fontSize: 12px, fontWeight: 600, letterSpacing: 0.06em, textTransform: uppercase }
rounded: { card: 8px, boundary: 12px, accent: 2px }
spacing: { cell-w: 180px, cell-h: 90px, gutter: 70px, margin: 40px, boundary-pad: 26px }
components:
  card: { backgroundColor: "{colors.surface}", borderColor: "{colors.line}", rounded: "{rounded.card}" }
  card-external: { borderStyle: "dashed" }
  accent-bar: { width: 26px, height: 4px, rounded: "{rounded.accent}" }
  connection: { strokeColor: "{colors.muted}", strokeWidth: 1.5px }
  boundary: { backgroundColor: "{colors.boundary-fill}", borderStyle: "dashed", rounded: "{rounded.boundary}" }
---

## Overview

Same voice as render-html's "Anthropic Reading" identity, applied to
diagrams: warm, papery, restrained. A diagram should look like a figure
from a well-set book, not a neon dashboard. Ink is dark-on-ivory; color is
rationed to the small kind accent bars and the legend, so the eye follows
structure, not decoration.

## Colors

Base tokens are shared with `render-html/DESIGN.md` — one house look
across documents and diagrams. The six kind hues are deliberately muted
(clay, sage, violet, slate, ochre, gray) so no card shouts; `external` is
gray + dashed border, reading as "outside our control". Light/dark pairs
must both pass against their surface — dark mode lightens accents rather
than brightening saturation.

## Typography

Serif is reserved for the page title (the "figure caption" register).
Everything inside the SVG is the grotesque sans: 14px/600 labels,
12px/400 sublabels and edge labels, uppercase-tracked 12px/600 boundary
labels. Edge labels carry a `paint-order: stroke` halo in the background
color so they stay legible crossing lines.

## Do's and Don'ts

- DO style SVG via CSS classes only (`.bp-*`); never inline fills — the
  theme toggle and dual-theme SVG export depend on it.
- DO keep the kind palette closed at six; a new kind is a schema + DESIGN
  + renderer change, not an ad-hoc color.
- DON'T introduce gradients, shadows, or icons — the accent bar is the
  entire per-kind decoration.
- DON'T restyle in the renderer: scripts hard-code these token values to
  stay stdlib (no YAML parser) — when a token changes here, change
  `render.py`'s SVG_STYLE/SVG_VARS and `assets/template.html` in the same
  commit (noted in handoff §4).
