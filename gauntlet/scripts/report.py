#!/usr/bin/env python3
"""Render a gauntlet run ledger to one self-contained HTML file (spec A10).

I/O: stdin JSON ledger {request, date, species, rounds: [{round, floor,
verdict, driving, tracked}], converged, final_audit, disclosures} |
stdout HTML | --out PATH writes to file. No network, no external assets.
"""
import argparse
import html
import json
import sys

TEMPLATE = """<!doctype html><meta charset='utf-8'><title>{title}</title>
<style>
body{{font:15px/1.5 system-ui;max-width:820px;margin:2rem auto;padding:0 1rem;color:#222}}
h1{{font-size:1.5rem}} .meta{{color:#666}} .ok{{color:#1a7f37}} .bad{{color:#b35900}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}
td,th{{border:1px solid #ddd;padding:.4rem .6rem;text-align:left;vertical-align:top}}
pre{{background:#f6f6f6;padding:.8rem;overflow-x:auto}}
</style>
<h1>Gauntlet run — {title}</h1>
<p class='meta'>{date} · species: {species} · {converged_line}</p>
<h2>Request</h2><pre>{request}</pre>
<h2>Rounds</h2>{rounds_html}
<h2>Close-out</h2><pre>{final_audit}</pre>
<h2>Tracked (not acted on)</h2>{tracked_html}
<h2>Disclosures</h2>{disclosures_html}"""

ROUND_ROW = ("<tr><td>{n}</td><td>{floor}</td><td>{verdict}</td>"
             "<td>{driving}</td></tr>")


def esc(v):
    return html.escape(str(v)) if v is not None else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    try:
        d = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"report: invalid ledger JSON: {e}", file=sys.stderr)
        sys.exit(2)

    rounds = d.get("rounds", [])
    rows = "".join(ROUND_ROW.format(
        n=esc(r.get("round")),
        floor=esc(r.get("floor", "—")),
        verdict=esc(r.get("verdict", "—")),
        driving="<br>".join(esc(f) for f in r.get("driving", [])) or "—",
    ) for r in rounds)
    rounds_html = (f"<table><tr><th>#</th><th>Floor</th><th>Verdict</th>"
                   f"<th>Driving findings</th></tr>{rows}</table>"
                   if rows else "<p>(none)</p>")

    tracked = [t for r in rounds for t in r.get("tracked", [])]
    tracked = tracked or d.get("tracked", [])
    tracked_html = ("<ul>" + "".join(f"<li>{esc(t)}</li>" for t in tracked)
                    + "</ul>") if tracked else "<p>(none)</p>"
    disclosures = d.get("disclosures", [])
    disclosures_html = ("<ul>" + "".join(f"<li>{esc(x)}</li>"
                                         for x in disclosures)
                        + "</ul>") if disclosures else "<p>(none)</p>"

    converged = d.get("converged")
    converged_line = ("<span class='ok'>converged</span>" if converged
                      else "<span class='bad'>did not converge</span>")
    out = TEMPLATE.format(
        title=esc(d.get("title", "untitled")),
        date=esc(d.get("date", "")),
        species=esc(d.get("species", "?")),
        converged_line=converged_line,
        request=esc(d.get("request", "")),
        rounds_html=rounds_html,
        final_audit=esc(d.get("final_audit", "(not run)")),
        tracked_html=tracked_html,
        disclosures_html=disclosures_html,
    )
    if args.out:
        with open(args.out, "w") as f:
            f.write(out)
        print(f"report: wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
