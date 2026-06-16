#!/usr/bin/env python3
"""Render a craft-claude audit summary to one self-contained HTML file (spec A10).

I/O: stdin JSON | stdout HTML | --out PATH writes to file.
"""
import argparse
import html
import json
import sys

TEMPLATE = """<!doctype html><meta charset='utf-8'><title>{title}</title>
<style>body{{font:14px/1.4 system-ui;max-width:760px;margin:2rem auto;padding:0 1rem}}</style>
<h1>{title}</h1><p><small>generated {date}</small></p><pre>{body}</pre>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    data = json.load(sys.stdin)
    out = TEMPLATE.format(
        title=html.escape(data.get("title", "craft-claude report")),
        date=html.escape(data.get("date", "")),
        body=html.escape(json.dumps(data, indent=2)),
    )
    if args.out:
        open(args.out, "w").write(out)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
