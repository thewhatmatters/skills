#!/usr/bin/env python3
"""Shared dependency preflight for skills/agents (spec A6 companion).

Checks that declared cross-dependencies exist on disk before a skill run:
  --skills=a,b   each must have ~/.cursor/skills/<name>/SKILL.md
  --agents=c,d   each must have ~/.claude/agents/<name>.md
  --files=p,q    each literal path must exist (~ expanded)

Contract: JSON to stdout, human board to stderr, always exits 0. Overall is
`ready` (all present) or `gated` with gate id DEPS_MISSING — a missing dep
is a recoverable setup gap (git pull / reinstall), and per spec A7 the
CALLING skill decides how to degrade; this script never blocks anything.
Session-only dependencies (MCP tools, the Agent tool) cannot be checked
from a script — those are model-side Step-0 probes in the calling SKILL.md.
"""

import argparse
import json
import sys
from pathlib import Path

HOME = Path.home()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", default="")
    ap.add_argument("--agents", default="")
    ap.add_argument("--files", default="")
    args = ap.parse_args()

    deps = []
    for name in filter(None, args.skills.split(",")):
        path = HOME / ".cursor/skills" / name.strip() / "SKILL.md"
        deps.append(("skill", name.strip(), path))
    for name in filter(None, args.agents.split(",")):
        path = HOME / ".claude/agents" / f"{name.strip()}.md"
        deps.append(("agent", name.strip(), path))
    for raw in filter(None, args.files.split(",")):
        path = Path(raw.strip().replace("~", str(HOME), 1))
        deps.append(("file", raw.strip(), path))

    results, missing = [], []
    for kind, name, path in deps:
        ok = path.exists()
        results.append({"kind": kind, "name": name,
                        "status": "ok" if ok else "missing",
                        "path": str(path)})
        if not ok:
            missing.append(f"{kind}:{name}")
        print(f"  {'✅' if ok else '⛔'} {kind:<5} {name}", file=sys.stderr)

    overall = "ready" if not missing else "gated"
    print(f"  → overall: {overall}"
          + (f" (DEPS_MISSING: {', '.join(missing)})" if missing else ""),
          file=sys.stderr)
    print(json.dumps({
        "overall": overall,
        "gate": "DEPS_MISSING" if missing else None,
        "missing": missing,
        "deps": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
