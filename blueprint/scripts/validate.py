#!/usr/bin/env python3
"""Gate a blueprint architecture IR before rendering (spec A4: one concern).

Structural checks (hand-rolled against schemas/architecture.schema.json —
stdlib only, no jsonschema dependency) plus layout checks the schema cannot
express: grid overlaps, boundary bbox interlock, stray components inside a
boundary's box, and label-width budgets. Every error names the JSON path
and proposes a concrete fix — the authoring agent iterates on the IR, never
on rendered output.

I/O: validate.py <ir.json> [--layout] · stdout JSON
{valid, errors: [{path, message, fix}], warnings: [...], layout?} ·
diagnostics stderr · exit 0 valid / 1 invalid / 2 unreadable input.
"""
import json
import sys

KINDS = {"service", "store", "queue", "client", "external", "gateway"}
MAX_ROW, MAX_COL = 7, 5
CW, CH, GX, GY, MARGIN = 180, 90, 70, 70, 40
CHAR_W = 7.5          # ~14px sans average glyph width
SUB_CHAR_W = 6.3      # ~12px
PAD_X = 24

COMPONENT_KEYS = {"id", "label", "sublabel", "kind", "row", "col", "rowspan", "colspan"}
CONNECTION_KEYS = {"from", "to", "label", "style", "bidirectional"}
BOUNDARY_KEYS = {"id", "label", "contains"}


def cells_of(c):
    for r in range(c["row"], c["row"] + c.get("rowspan", 1)):
        for k in range(c["col"], c["col"] + c.get("colspan", 1)):
            yield (r, k)


def box_of(c):
    x = MARGIN + c["col"] * (CW + GX)
    y = MARGIN + c["row"] * (CH + GY)
    w = c.get("colspan", 1) * CW + (c.get("colspan", 1) - 1) * GX
    h = c.get("rowspan", 1) * CH + (c.get("rowspan", 1) - 1) * GY
    return {"x": x, "y": y, "w": w, "h": h}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want_layout = "--layout" in sys.argv
    if len(args) != 1:
        print("usage: validate.py <ir.json> [--layout]", file=sys.stderr)
        sys.exit(2)
    try:
        ir = json.load(open(args[0]))
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"valid": False, "errors": [
            {"path": "/", "message": f"cannot read IR: {e}",
             "fix": "produce well-formed JSON"}], "warnings": []}))
        sys.exit(1)

    errors, warnings = [], []

    def err(path, message, fix):
        errors.append({"path": path, "message": message, "fix": fix})

    def warn(path, message, fix):
        warnings.append({"path": path, "message": message, "fix": fix})

    # --- structural ---
    if ir.get("schema_version") != 1:
        err("/schema_version", "must be 1", "set schema_version: 1")
    if ir.get("diagram_type") != "architecture":
        err("/diagram_type", "must be 'architecture'",
            "set diagram_type: 'architecture' (other types are not in v1)")
    meta = ir.get("meta") or {}
    if not isinstance(meta, dict) or not meta.get("title"):
        err("/meta/title", "meta.title is required", "add a short title")

    comps = ir.get("components")
    if not isinstance(comps, list) or not comps:
        err("/components", "components must be a non-empty array",
            "add at least one component")
        comps = []
    if len(comps) > 16:
        err("/components", f"{len(comps)} components (max 16)",
            "split into two diagrams or merge minor components into one card")

    ids = {}
    for i, c in enumerate(comps):
        p = f"/components/{i}"
        if not isinstance(c, dict):
            err(p, "component must be an object", "use {id, label, row, col}")
            continue
        for k in set(c) - COMPONENT_KEYS:
            warn(f"{p}/{k}", f"unknown key '{k}'",
                 f"remove it or check spelling (allowed: {sorted(COMPONENT_KEYS)})")
        cid = c.get("id")
        if not cid or not isinstance(cid, str):
            err(f"{p}/id", "id is required", "add a kebab-case id")
            continue
        if cid in ids:
            err(f"{p}/id", f"duplicate id '{cid}' (also /components/{ids[cid]})",
                "make ids unique")
        ids[cid] = i
        if not c.get("label"):
            err(f"{p}/label", "label is required", "add a display label")
        if c.get("kind") is not None and c["kind"] not in KINDS:
            err(f"{p}/kind", f"unknown kind '{c['kind']}'",
                f"use one of {sorted(KINDS)} or omit")
        for field, mx in (("row", MAX_ROW), ("col", MAX_COL)):
            v = c.get(field)
            if not isinstance(v, int) or v < 0 or v > mx:
                err(f"{p}/{field}", f"{field} must be an integer 0–{mx}",
                    f"set {field} within the grid")
                c[field] = 0
        for field, mx in (("rowspan", 4), ("colspan", 3)):
            v = c.get(field, 1)
            if not isinstance(v, int) or v < 1 or v > mx:
                err(f"{p}/{field}", f"{field} must be an integer 1–{mx}",
                    f"set {field} within 1–{mx}")
                c[field] = 1

    # --- grid overlap ---
    occupied = {}
    for i, c in enumerate(comps):
        if not isinstance(c, dict) or "row" not in c or "col" not in c:
            continue
        for cell in cells_of(c):
            if cell in occupied:
                err(f"/components/{i}",
                    f"'{c.get('id')}' overlaps '{comps[occupied[cell]].get('id')}' at row {cell[0]}, col {cell[1]}",
                    "move one component to a free cell or reduce its span")
                break
            occupied[cell] = i

    # --- label budgets ---
    for i, c in enumerate(comps):
        if not isinstance(c, dict) or not c.get("label"):
            continue
        budget = c.get("colspan", 1) * CW + (c.get("colspan", 1) - 1) * GX - PAD_X
        if len(c["label"]) * CHAR_W > budget:
            fit = int(budget / CHAR_W)
            err(f"/components/{i}/label",
                f"label '{c['label']}' is wider than its card",
                f"shorten to ≤{fit} chars, or set colspan: {c.get('colspan', 1) + 1}")
        sub = c.get("sublabel", "")
        if sub and len(sub) * SUB_CHAR_W > budget:
            fit = int(budget / SUB_CHAR_W)
            err(f"/components/{i}/sublabel",
                f"sublabel is wider than its card",
                f"shorten to ≤{fit} chars, or widen the card")

    # --- connections ---
    seen_conn = set()
    for i, cn in enumerate(ir.get("connections") or []):
        p = f"/connections/{i}"
        if not isinstance(cn, dict):
            err(p, "connection must be an object", "use {from, to}")
            continue
        for k in set(cn) - CONNECTION_KEYS:
            warn(f"{p}/{k}", f"unknown key '{k}'",
                 f"remove it (allowed: {sorted(CONNECTION_KEYS)})")
        f, t = cn.get("from"), cn.get("to")
        for side, v in (("from", f), ("to", t)):
            if v not in ids:
                err(f"{p}/{side}", f"unknown component '{v}'",
                    "reference an existing component id")
        if f == t:
            err(p, "self-loop (from == to)", "remove it or connect two components")
        key = (f, t, cn.get("label", ""))
        if key in seen_conn:
            err(p, f"duplicate connection {f} → {t}", "remove the duplicate")
        seen_conn.add(key)
        if cn.get("style") not in (None, "solid", "dashed"):
            err(f"{p}/style", f"unknown style '{cn.get('style')}'",
                "use 'solid' or 'dashed'")

    if len(ir.get("connections") or []) > 24:
        warn("/connections", "more than 24 connections — the diagram will read as a hairball",
             "keep the main path; drop or merge secondary edges")

    # --- boundaries ---
    bids = set()
    bboxes = []
    for i, b in enumerate(ir.get("boundaries") or []):
        p = f"/boundaries/{i}"
        if not isinstance(b, dict):
            err(p, "boundary must be an object", "use {id, label, contains}")
            continue
        for k in set(b) - BOUNDARY_KEYS:
            warn(f"{p}/{k}", f"unknown key '{k}'",
                 f"remove it (allowed: {sorted(BOUNDARY_KEYS)})")
        if b.get("id") in bids:
            err(f"{p}/id", f"duplicate boundary id '{b.get('id')}'", "make ids unique")
        bids.add(b.get("id"))
        members = [m for m in (b.get("contains") or []) if m in ids]
        for m in (b.get("contains") or []):
            if m not in ids:
                err(f"{p}/contains", f"unknown component '{m}'",
                    "reference existing component ids")
        if not members:
            continue
        boxes = [box_of(comps[ids[m]]) for m in members]
        x0 = min(bx["x"] for bx in boxes)
        y0 = min(bx["y"] for bx in boxes)
        x1 = max(bx["x"] + bx["w"] for bx in boxes)
        y1 = max(bx["y"] + bx["h"] for bx in boxes)
        bboxes.append((i, b, set(members), (x0, y0, x1, y1)))
        # strays: non-members whose box sits inside the boundary bbox
        for cid, ci in ids.items():
            if cid in members:
                continue
            cb = box_of(comps[ci])
            if cb["x"] >= x0 and cb["y"] >= y0 and \
               cb["x"] + cb["w"] <= x1 and cb["y"] + cb["h"] <= y1:
                err(f"{p}/contains",
                    f"'{cid}' sits inside boundary '{b.get('id')}' but is not a member",
                    f"add '{cid}' to contains, or move it outside the boundary's grid area")

    # boundary interlock: overlapping bboxes without full containment
    for a in range(len(bboxes)):
        for bkey in range(a + 1, len(bboxes)):
            _, ba, ma, (ax0, ay0, ax1, ay1) = bboxes[a]
            _, bb, mb, (bx0, by0, bx1, by1) = bboxes[bkey]
            overlap = ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1
            nested = ma <= mb or mb <= ma
            if overlap and not nested:
                err(f"/boundaries",
                    f"boundaries '{ba.get('id')}' and '{bb.get('id')}' interlock without nesting",
                    "make one fully contain the other's members, or separate their grid areas")

    result = {"valid": not errors, "errors": errors, "warnings": warnings}
    if want_layout:
        result["layout"] = {
            c["id"]: box_of(c) for c in comps
            if isinstance(c, dict) and c.get("id") and isinstance(c.get("row"), int)
        }
    print(f"validate: {'OK' if not errors else f'{len(errors)} error(s)'}"
          f"{f', {len(warnings)} warning(s)' if warnings else ''}", file=sys.stderr)
    print(json.dumps(result, indent=2))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
