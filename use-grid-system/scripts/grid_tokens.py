#!/usr/bin/env python3
"""grid_tokens.py — Müller-Brockmann grid source-of-truth generator (spec A4).

Emits ONE source of truth for a real, visible, verifiable modular grid:
  • Tailwind v4 path (default): an @theme block + @utility band/grid-page/overlay,
    placing children by column LINE via grid-cols-subgrid (Baseline Mar 2026) with
    an @supports fallback. Vertical rhythm rides Tailwind's --spacing scale + a
    leading token; the 8px baseline IS the token system.
  • Vanilla path (--vanilla): a framework-free :root scaffold (same discipline,
    plain CSS) for projects without Tailwind — never impose Tailwind (no-monoculture).

Profiles: editorial (strict whole-field) | app (column-line + baseline, relaxed
rows) — see references/profiles.md. The optical-alignment JS and verification are
documented in references/ (not emitted here; they are framework-agnostic).

I/O contract: the generated CSS goes to STDOUT (the artifact); warnings/diagnostics
go to STDERR; --json wraps {profile, mode, tokens, css, warnings} as JSON on stdout.
Graceful, deterministic, no network, no credentials.

Usage:
  python3 grid_tokens.py                         # Tailwind @theme + @utility, app profile
  python3 grid_tokens.py --profile editorial
  python3 grid_tokens.py --vanilla               # framework-free :root scaffold
  python3 grid_tokens.py --design-md             # a `## Grid` block for a project DESIGN.md
  python3 grid_tokens.py --cols 12 --baseline 8 --gutter 24 --margin 72 \
                         --maxw 1296 --accent "#e4002b"
  python3 grid_tokens.py --json                  # JSON envelope for tooling
"""
import argparse, json, sys


def warnings_for(cfg):
    w = []
    for name, v in (("gutter", cfg.gutter), ("margin", cfg.margin)):
        if v % cfg.baseline != 0:
            w.append(f"--{name} ({v}) is not a multiple of --baseline "
                     f"({cfg.baseline}); spacing/vertical rhythm will drift off the grid.")
    if cfg.cols < 1:
        w.append(f"--cols ({cfg.cols}) must be >= 1.")
    return w


def tokens_dict(cfg):
    lh = cfg.baseline * 3
    return {
        "cols": cfg.cols, "baseline_px": cfg.baseline, "leading_px": lh,
        "gutter_px": cfg.gutter, "margin_px": cfg.margin, "maxw_px": cfg.maxw,
        "accent": cfg.accent, "profile": cfg.profile,
    }


def tailwind_css(cfg):
    lh = cfg.baseline * 3
    # On a live project we keep the 4px Tailwind base (even multiples = 8px baseline)
    # and add an explicit leading; greenfield may set --spacing to the baseline.
    return f"""@import "tailwindcss";

/* === Müller-Brockmann grid — ONE source of truth (profile: {cfg.profile}) === */
@theme {{
  /* vertical quantum — keep Tailwind's 4px base on existing projects (even
     multiples already land on the {cfg.baseline}px baseline). Uncomment to
     re-base ONLY on a greenfield project (it re-scales every spacing utility): */
  /* --spacing: {cfg.baseline / 16:.4f}rem; */            /* {cfg.baseline}px base */
  --leading-base: {lh / 16:.4f}rem;                       /* {lh}px = 3 × {cfg.baseline}px */

  --grid-cols: {cfg.cols};
  --grid-gutter: {cfg.gutter / 16:.4f}rem;                /* {cfg.gutter}px */
  --grid-margin: {cfg.margin / 16:.4f}rem;                /* {cfg.margin}px */
  --grid-maxw: {cfg.maxw / 16:.4f}rem;                    /* {cfg.maxw}px */

  --color-paper: #ffffff;
  --color-ink: #111315;
  --color-ink-soft: #5b6066;
  --color-accent: {cfg.accent};
}}

/* place children by column LINE; the band re-exposes the page columns as subgrid */
@utility grid-page {{
  display: grid;
  grid-template-columns: repeat(var(--grid-cols), 1fr);
  column-gap: var(--grid-gutter);
  row-gap: var(--leading-base);
  max-width: var(--grid-maxw);
  margin-inline: auto;
  padding-inline: var(--grid-margin);
}}
@utility band {{
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: subgrid;
  column-gap: var(--grid-gutter);
  align-items: start;
}}
@supports not (grid-template-columns: subgrid) {{
  @utility band {{ grid-template-columns: repeat(var(--grid-cols), 1fr); }}
}}

/* author markup: <div class="grid-page"><div class="band">
     <h2 class="col-start-1 col-end-6">…</h2>
     <figure class="col-start-6 col-end-13">…</figure>   <!-- height = ×leading -->
   </div></div>
   Overlay (the g-key toggle) + optical-alignment JS: see references/optical-alignment.md
   and references/tailwind.md. Verify via audit-ui: see references/verification.md. */
"""


def vanilla_css(cfg):
    lh = cfg.baseline * 3
    pad = cfg.baseline * 12
    return f""":root{{
  --cols:{cfg.cols};
  --bl:{cfg.baseline}px;            /* baseline unit */
  --lh:{lh}px;                      /* leading = 3 × baseline */
  --gutter:{cfg.gutter}px;
  --margin:{cfg.margin}px;
  --maxw:{cfg.maxw}px;
  --pad:{pad}px;                    /* spread top/bottom pad (× baseline) */
  --paper:#ffffff; --ink:#111315; --ink-soft:#5b6066; --accent:{cfg.accent};
  --g-col:rgba(228,0,43,.075); --g-edge:rgba(228,0,43,.40);
  --g-base:rgba(0,150,140,.34); --g-base-min:rgba(0,150,140,.12);
}}
*{{box-sizing:border-box;}}
.wrap{{position:relative;max-width:var(--maxw);margin:0 auto;padding:var(--pad) var(--margin);}}
.grid{{display:grid;grid-template-columns:repeat(var(--cols),1fr);column-gap:var(--gutter);row-gap:var(--lh);}}
.band{{grid-column:1 / -1;display:grid;grid-template-columns:subgrid;column-gap:var(--gutter);align-items:start;}}
@supports not (grid-template-columns:subgrid){{ .band{{grid-template-columns:repeat(var(--cols),1fr);}} }}
/* children: style="grid-column:<startline> / <endline>". Overlay CSS + toggle JS +
   optical alignment: see references/non-tailwind.md and references/optical-alignment.md. */
"""


def design_md_block(cfg):
    """A `## Grid` section for a project DESIGN.md — design-md owns this spec; the
    skill emits a draft the project can adopt, then CONSUMES it as the source of
    truth on later runs."""
    lh = cfg.baseline * 3
    return f"""## Grid

Müller-Brockmann modular grid · profile: **{cfg.profile}** · owned by this
DESIGN.md (design-md). `use-grid-system` reads these tokens and emits the
matching `@theme` / `:root` source of truth — do not hand-edit the generated CSS;
change it here.

| Token | Value | Notes |
|-------|-------|-------|
| columns | {cfg.cols} | page column count |
| baseline | {cfg.baseline}px | vertical quantum (all spacing a multiple) |
| leading | {lh}px | 3 × baseline |
| gutter | {cfg.gutter}px | column gutter (baseline multiple) |
| margin | {cfg.margin}px | page margin |
| max-width | {cfg.maxw}px | content max-width |
| accent | `{cfg.accent}` | one accent only (Swiss red canonical) |

- Place every element by **column line** (subgrid bands); occupy whole fields
  ({'strict' if cfg.profile == 'editorial' else 'relaxed rows for app UI'}).
- Lock spacing / leading / media heights to the **{cfg.baseline}px baseline**.
- Display type uses runtime optical alignment (ink on the line, not its box).
"""


def build(cfg):
    if cfg.design_md:
        return design_md_block(cfg)
    return vanilla_css(cfg) if cfg.vanilla else tailwind_css(cfg)


def main():
    ap = argparse.ArgumentParser(description="Müller-Brockmann grid source-of-truth generator")
    ap.add_argument("--profile", choices=["editorial", "app"], default="app")
    ap.add_argument("--cols", type=int, default=12)
    ap.add_argument("--baseline", type=int, default=8, help="baseline unit in px (leading = 3×)")
    ap.add_argument("--gutter", type=int, default=24)
    ap.add_argument("--margin", type=int, default=72)
    ap.add_argument("--maxw", type=int, default=1296)
    ap.add_argument("--accent", default="#e4002b")
    ap.add_argument("--vanilla", action="store_true", help="emit a framework-free :root scaffold")
    ap.add_argument("--design-md", dest="design_md", action="store_true",
                    help="emit a `## Grid` block for a project DESIGN.md (design-md owns the spec)")
    ap.add_argument("--json", action="store_true", help="emit a JSON envelope instead of raw CSS")
    ap.add_argument("--out", help="write CSS to this path instead of stdout")
    cfg = ap.parse_args()

    warns = warnings_for(cfg)
    for w in warns:
        print(f"# WARNING: {w}", file=sys.stderr)

    css = build(cfg)
    if cfg.json:
        payload = {
            "profile": cfg.profile,
            "mode": "design-md" if cfg.design_md else ("vanilla" if cfg.vanilla else "tailwind"),
            "tokens": tokens_dict(cfg),
            "css": css,
            "warnings": warns,
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    elif cfg.out:
        with open(cfg.out, "w") as fh:
            fh.write(css)
        print(f"# wrote {cfg.out}", file=sys.stderr)
    else:
        sys.stdout.write(css)


if __name__ == "__main__":
    main()
