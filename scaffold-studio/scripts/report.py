#!/usr/bin/env python3
"""Render a scaffold-studio run summary to markdown (spec A10).

I/O: stdin JSON · writes markdown to --out (default /tmp/scaffold-studio-report.md) · also echoes markdown to stdout.
"""
import argparse
import json
import sys
from datetime import date


def render(data: dict) -> str:
    today = data.get("date") or date.today().isoformat()
    lines = [
        f"# scaffold-studio report",
        "",
        f"Generated: {today}",
        "",
        f"- Project: {data.get('project', '(unknown)')}",
        f"- Motion: {data.get('motion', '(not run)')}",
        f"- CSS Studio: {data.get('cssStudio', '(not run)')}",
        "",
    ]
    notes = data.get("notes") or []
    if isinstance(notes, str):
        notes = [notes]
    if notes:
        lines.append("## Notes")
        lines.append("")
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/scaffold-studio-report.md")
    args = ap.parse_args()
    data = json.load(sys.stdin)
    out = render(data)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    sys.stdout.write(out)


if __name__ == "__main__":
    main()
