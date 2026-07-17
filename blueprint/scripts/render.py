#!/usr/bin/env python3
"""Render a validated blueprint architecture IR to a themed artifact
(spec A4: one concern — geometry + SVG; styling lives in CSS classes).

Deterministic grid layout (same constants as validate.py), orthogonal
elbow-routed connections, boundaries drawn behind, kind legend, house-brand
dual-theme styling. Never edit the output — change the IR and re-render.

I/O: render.py <ir.json> --out=PATH [--svg] · writes a self-contained HTML
page (default; template: ../assets/template.html) or a standalone
dual-theme SVG (--svg) · stdout JSON {status, out, width, height} ·
diagnostics stderr · exit 0 ok / 1 render failure / 2 unreadable input.
Run validate.py first; this script trusts the IR's shape.
"""
import json
import os
import sys
from xml.sax.saxutils import escape

CW, CH, GX, GY, MARGIN = 180, 90, 70, 70, 40
BPAD = 26            # boundary padding around member cards
LEGEND_H = 56
KIND_ORDER = ["client", "gateway", "service", "queue", "store", "external"]

SVG_STYLE = """
  .bp-card { fill: var(--bp-surface); stroke: var(--bp-line); stroke-width: 1.5; rx: 8; }
  .bp-card-external { stroke-dasharray: 5 4; }
  .bp-accent { rx: 2; }
  .bp-accent-service { fill: #CC785C; } .bp-accent-store { fill: #7A8B74; }
  .bp-accent-queue { fill: #8A7AA0; } .bp-accent-client { fill: #5B7B94; }
  .bp-accent-external { fill: #9C9A90; } .bp-accent-gateway { fill: #B98A2F; }
  .bp-label { fill: var(--bp-fg); font: 600 14px var(--bp-sans); text-anchor: middle; }
  .bp-sublabel { fill: var(--bp-muted); font: 400 12px var(--bp-sans); text-anchor: middle; }
  .bp-conn { stroke: var(--bp-muted); stroke-width: 1.5; fill: none; }
  .bp-conn-dashed { stroke-dasharray: 5 4; }
  .bp-conn-label { fill: var(--bp-muted); font: 400 12px var(--bp-sans); text-anchor: middle;
                   paint-order: stroke; stroke: var(--bp-bg); stroke-width: 4px; }
  .bp-boundary { fill: var(--bp-boundary-fill); stroke: var(--bp-line);
                 stroke-width: 1.2; stroke-dasharray: 7 5; rx: 12; }
  .bp-boundary-label { fill: var(--bp-muted); font: 600 12px var(--bp-sans);
                       letter-spacing: 0.06em; text-transform: uppercase; }
  .bp-legend-label { fill: var(--bp-muted); font: 400 12px var(--bp-sans); }
  .bp-arrow { fill: var(--bp-muted); }
"""

SVG_VARS_LIGHT = """--bp-bg:#F0EEE6; --bp-surface:#F7F6F2; --bp-fg:#191917;
    --bp-muted:#6B6A63; --bp-line:#DEDBD0; --bp-boundary-fill:rgba(222,219,208,0.18);
    --bp-sans:'Styrene B','Hanken Grotesk',ui-sans-serif,system-ui,sans-serif;"""
SVG_VARS_DARK = """--bp-bg:#1F1E1B; --bp-surface:#26241F; --bp-fg:#EDEAE0;
    --bp-muted:#A7A498; --bp-line:#3A372F; --bp-boundary-fill:rgba(58,55,47,0.28);"""


def box_of(c):
    x = MARGIN + c["col"] * (CW + GX)
    y = MARGIN + c["row"] * (CH + GY)
    w = c.get("colspan", 1) * CW + (c.get("colspan", 1) - 1) * GX
    h = c.get("rowspan", 1) * CH + (c.get("rowspan", 1) - 1) * GY
    return x, y, w, h


def center(b):
    return b[0] + b[2] / 2, b[1] + b[3] / 2


def route(src, dst):
    """Orthogonal path between two boxes: edge midpoints, single elbow."""
    sx, sy = center(src)
    dx, dy = center(dst)
    if abs(dx - sx) >= abs(dy - sy):        # horizontal-dominant
        x0 = src[0] + src[2] if dx > sx else src[0]
        x1 = dst[0] if dx > sx else dst[0] + dst[2]
        if abs(dy - sy) < 1:                 # straight
            pts = [(x0, sy), (x1, dy)]
        else:                                # H-V-H elbow at mid-gap
            xm = (x0 + x1) / 2
            pts = [(x0, sy), (xm, sy), (xm, dy), (x1, dy)]
    else:                                    # vertical-dominant
        y0 = src[1] + src[3] if dy > sy else src[1]
        y1 = dst[1] if dy > sy else dst[1] + dst[3]
        if abs(dx - sx) < 1:
            pts = [(sx, y0), (dx, y1)]
        else:                                # V-H-V elbow
            ym = (y0 + y1) / 2
            pts = [(sx, y0), (sx, ym), (dx, ym), (dx, y1)]
    return pts


def midpoint(pts):
    if len(pts) == 2:
        return (pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2
    return (pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2


def build_svg(ir):
    comps = {c["id"]: c for c in ir["components"]}
    boxes = {cid: box_of(c) for cid, c in comps.items()}
    kinds_used = [k for k in KIND_ORDER
                  if any(c.get("kind") == k for c in ir["components"])]

    max_x = max(b[0] + b[2] for b in boxes.values()) + MARGIN
    max_y = max(b[1] + b[3] for b in boxes.values()) + MARGIN
    if kinds_used:
        max_y += LEGEND_H

    parts = []

    for b in ir.get("boundaries") or []:
        members = [boxes[m] for m in b["contains"] if m in boxes]
        if not members:
            continue
        x0 = min(m[0] for m in members) - BPAD
        y0 = min(m[1] for m in members) - BPAD - 8
        x1 = max(m[0] + m[2] for m in members) + BPAD
        y1 = max(m[1] + m[3] for m in members) + BPAD
        parts.append(f'<rect class="bp-boundary" x="{x0}" y="{y0}" '
                     f'width="{x1 - x0}" height="{y1 - y0}" rx="12"/>')
        parts.append(f'<text class="bp-boundary-label" x="{x0 + 14}" '
                     f'y="{y0 + 20}">{escape(b["label"])}</text>')

    for cn in ir.get("connections") or []:
        if cn["from"] not in boxes or cn["to"] not in boxes:
            continue
        pts = route(boxes[cn["from"]], boxes[cn["to"]])
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        cls = "bp-conn" + (" bp-conn-dashed" if cn.get("style") == "dashed" else "")
        markers = 'marker-end="url(#bp-head)"'
        if cn.get("bidirectional"):
            markers += ' marker-start="url(#bp-tail)"'
        parts.append(f'<path class="{cls}" d="{d}" {markers}/>')
        if cn.get("label"):
            mx, my = midpoint(pts)
            parts.append(f'<text class="bp-conn-label" x="{mx:.1f}" '
                         f'y="{my - 6:.1f}">{escape(cn["label"])}</text>')

    for cid, c in comps.items():
        x, y, w, h = boxes[cid]
        ext = " bp-card-external" if c.get("kind") == "external" else ""
        parts.append(f'<rect class="bp-card{ext}" x="{x}" y="{y}" '
                     f'width="{w}" height="{h}" rx="8"/>')
        if c.get("kind"):
            parts.append(f'<rect class="bp-accent bp-accent-{c["kind"]}" '
                         f'x="{x + 14}" y="{y + 12}" width="26" height="4" rx="2"/>')
        cx = x + w / 2
        if c.get("sublabel"):
            parts.append(f'<text class="bp-label" x="{cx}" y="{y + h / 2 + 1}">'
                         f'{escape(c["label"])}</text>')
            parts.append(f'<text class="bp-sublabel" x="{cx}" y="{y + h / 2 + 20}">'
                         f'{escape(c["sublabel"])}</text>')
        else:
            parts.append(f'<text class="bp-label" x="{cx}" y="{y + h / 2 + 5}">'
                         f'{escape(c["label"])}</text>')

    if kinds_used:
        lx, ly = MARGIN, max_y - LEGEND_H / 2
        for k in kinds_used:
            parts.append(f'<rect class="bp-accent bp-accent-{k}" x="{lx}" '
                         f'y="{ly - 4}" width="18" height="4" rx="2"/>')
            parts.append(f'<text class="bp-legend-label" x="{lx + 26}" '
                         f'y="{ly + 1}">{escape(k)}</text>')
            lx += 26 + len(k) * 7 + 34

    defs = ('<defs>'
            '<marker id="bp-head" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto">'
            '<path class="bp-arrow" d="M0,0 L9,4 L0,8 z"/></marker>'
            '<marker id="bp-tail" markerWidth="9" markerHeight="8" refX="1" refY="4" orient="auto">'
            '<path class="bp-arrow" d="M9,0 L0,4 L9,8 z"/></marker>'
            '</defs>')
    body = defs + "".join(parts)
    return body, int(max_x), int(max_y)


def standalone_svg(body, w, h):
    style = (f"<style>svg{{{SVG_VARS_LIGHT}}}"
             f"@media (prefers-color-scheme: dark){{svg{{{SVG_VARS_DARK}}}}}"
             f"{SVG_STYLE} svg{{background:var(--bp-bg)}}</style>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">{style}'
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="var(--bp-bg)"/>'
            f'{body}</svg>')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = next((a.split("=", 1)[1] for a in sys.argv[1:]
                if a.startswith("--out=")), None)
    as_svg = "--svg" in sys.argv
    if len(args) != 1 or not out:
        print("usage: render.py <ir.json> --out=PATH [--svg]", file=sys.stderr)
        sys.exit(2)
    try:
        ir = json.load(open(args[0]))
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"status": "error", "detail": f"cannot read IR: {e}"}))
        sys.exit(2)

    try:
        body, w, h = build_svg(ir)
        if as_svg:
            doc = standalone_svg(body, w, h)
        else:
            tpl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "assets", "template.html")
            tpl = open(tpl_path).read()
            svg = (f'<svg id="bp-svg" xmlns="http://www.w3.org/2000/svg" '
                   f'viewBox="0 0 {w} {h}"><style>{SVG_STYLE}</style>{body}</svg>')
            import datetime
            today = datetime.date.today().isoformat()
            doc = (tpl.replace("__TITLE__", escape(ir["meta"]["title"]))
                      .replace("__DESCRIPTION__", escape(ir["meta"].get("description", "")))
                      .replace("__DATE__", today)
                      .replace("__SVG__", svg))
        with open(out, "w") as f:
            f.write(doc)
    except (OSError, KeyError, TypeError, ValueError) as e:
        print(f"render: failed: {e}", file=sys.stderr)
        print(json.dumps({"status": "error", "detail": str(e)}))
        sys.exit(1)

    print(f"render: wrote {out} ({w}×{h})", file=sys.stderr)
    print(json.dumps({"status": "ok", "out": out, "width": w, "height": h}))


if __name__ == "__main__":
    main()
