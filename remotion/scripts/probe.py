#!/usr/bin/env python3
"""Detect a Remotion project + toolchain so SKILL.md can route instead of guess (spec A4).

One concern: read the target project's package.json + a few key files and the
local skills dir, and emit a JSON description so SKILL.md knows whether this is
a Remotion project, whether Node/npx are usable, and whether Remotion's official
`remotion-best-practices` skill is installed to defer to. Best-effort, text-only
— never executes project code.

What it detects (each may be null/false if absent):
    project_root      : nearest dir up-tree with package.json or .git
    is_remotion       : bool — `remotion` in package.json deps/devDeps
    remotion_version  : the declared version string, or null
    has_config        : bool — remotion.config.ts/.js present
    root_file         : path to src/Root.tsx | src/index.ts | null (registerRoot entry)
    node              : node version string, or null if not on PATH
    npx               : bool — npx resolvable on PATH
    package_manager   : npm | pnpm | yarn | bun | null
    tailwind          : bool — tailwindcss present (informs the "no Tailwind animation" caveat)
    external_skills   : { "remotion-best-practices": bool } — installed under ~/.claude/skills

I/O:
    stdin  : —
    stdout : the JSON described above
    stderr : a short human summary
    exit   : 0 always — an empty/unrecognised project still yields valid JSON
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# External skills `remotion` defers execution/knowledge to. A False here means
# SKILL.md takes the degraded path (surface the install command + fall back).
DEFERRAL_TARGETS = ("remotion-best-practices",)


def find_project_root(start):
    cur = Path(start).expanduser().resolve()
    for p in [cur, *cur.parents]:
        if (p / "package.json").is_file() or (p / ".git").exists():
            return p
    return cur


def load_json(path):
    try:
        return json.loads(Path(path).read_text("utf-8"))
    except (OSError, ValueError):
        return None


def detect_pkg_manager(root):
    for f, name in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"),
                    ("bun.lockb", "bun"), ("package-lock.json", "npm")):
        if (root / f).is_file():
            return name
    return None


def detect_root_file(root):
    for rel in ("src/Root.tsx", "src/Root.jsx", "src/index.ts", "src/index.tsx",
                "src/index.js", "remotion/Root.tsx"):
        if (root / rel).is_file():
            return str(root / rel)
    return None


def detect_config(root):
    return any((root / f).is_file()
               for f in ("remotion.config.ts", "remotion.config.js",
                         "remotion.config.mjs"))


def node_version():
    if not shutil.which("node"):
        return None
    try:
        out = subprocess.run(["node", "--version"], capture_output=True,
                             text=True, timeout=5)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def detect_user_skill(name):
    """True iff ~/.claude/skills/<name>/SKILL.md declares `name: <name>`.

    Follows symlinks (skills.sh drops a symlink into .agents/skills/<name>),
    so a symlinked install resolves the same as a real directory.
    """
    sk = Path.home() / ".claude" / "skills" / name / "SKILL.md"
    try:
        text = sk.read_text("utf-8", errors="replace")
    except OSError:
        return False
    return bool(re.search(rf"^name:\s*{re.escape(name)}\s*$", text, re.MULTILINE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".", help="project root (default: cwd; walks up)")
    # --agent is a no-op here (probe is non-interactive); accepted so the harness
    # can pass SKILL.md's standard flag through without an error.
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    root = find_project_root(args.project)
    pj = load_json(root / "package.json") or {}
    deps = {**(pj.get("dependencies") or {}), **(pj.get("devDependencies") or {})}

    out = {
        "project_root":     str(root),
        "is_remotion":      "remotion" in deps,
        "remotion_version": deps.get("remotion"),
        "has_config":       detect_config(root),
        "root_file":        detect_root_file(root),
        "node":             node_version(),
        "npx":              bool(shutil.which("npx")),
        "package_manager":  detect_pkg_manager(root),
        "tailwind":         "tailwindcss" in deps,
        "external_skills":  {n: detect_user_skill(n) for n in DEFERRAL_TARGETS},
    }

    print(f"remotion probe @ {root}", file=sys.stderr)
    print(f"  is_remotion   {out['is_remotion']}"
          + (f" ({out['remotion_version']})" if out['remotion_version'] else ""),
          file=sys.stderr)
    print(f"  root_file     {out['root_file']}", file=sys.stderr)
    print(f"  node          {out['node'] or 'MISSING'}    npx {out['npx']}", file=sys.stderr)
    for n in DEFERRAL_TARGETS:
        status = "installed" if out["external_skills"][n] else "MISSING (see SKILL.md fallback)"
        print(f"  {n:24} skill: {status}", file=sys.stderr)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
