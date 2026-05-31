#!/usr/bin/env python3
"""Detect the frontend stack of the target project (spec A4).

One concern: read the project's package.json + a few key config files and emit
a JSON description of the stack so SKILL.md can load the matching references
instead of guessing. Best-effort, text-only — does not execute any config.

What it detects (each may be `null` if absent):
    framework    : next | react | vue | svelte | astro | remix | nuxt | sveltekit
                   | solid | qwik | preact | null
    css          : tailwind | css-modules | sass | styled-components |
                   vanilla-extract | emotion | unocss | panda | vanilla
    components   : shadcn | radix | headlessui | mantine | chakra | mui | none
    motion       : motion | framer-motion | gsap | autoanimate | tailwindcss-animate | none
    aliases      : { "@/": "src/", ... } from tsconfig.compilerOptions.paths
    dirs         : { "components": "src/components", "app": "app", "pages": null, ... }
    tailwind     : { config_path, version_hint }   (when css=tailwind)
    shadcn       : { style, baseColor, rsc, components_alias }   (when components=shadcn)
    design_md    : project-root DESIGN.md path if present, else null
    package_manager : npm | pnpm | yarn | bun | null

I/O:
    stdin  : —
    stdout : the JSON described above
    stderr : a short human summary
    exit   : 0 always — an empty/unrecognised project still produces a valid JSON
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

CONFIG_GLOBS = (
    "tailwind.config.js", "tailwind.config.ts", "tailwind.config.mjs",
    "tailwind.config.cjs",
)


def find_project_root(start):
    """Walk up from `start` to the nearest dir containing package.json or .git."""
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


def _any(deps, *names):
    return next((n for n in names if n in deps), None)


def detect_framework(deps):
    for k in ("next", "remix", "@remix-run/react", "nuxt", "@sveltejs/kit",
             "astro", "@builder.io/qwik", "solid-js"):
        if k in deps:
            if k == "@remix-run/react": return "remix"
            if k == "@sveltejs/kit":   return "sveltekit"
            if k == "@builder.io/qwik": return "qwik"
            if k == "solid-js":        return "solid"
            return k
    return _any(deps, "react", "vue", "svelte", "preact")


def detect_css(deps):
    if "tailwindcss" in deps or "@tailwindcss/postcss" in deps:
        return "tailwind"
    for k, v in (("styled-components", "styled-components"),
                 ("@emotion/react",    "emotion"),
                 ("@vanilla-extract/css", "vanilla-extract"),
                 ("@unocss/core",      "unocss"),
                 ("@pandacss/dev",     "panda"),
                 ("sass",              "sass")):
        if k in deps:
            return v
    return "vanilla"


def detect_components(deps, root):
    if (root / "components.json").is_file():
        return "shadcn"
    libs = {"@mantine/core": "mantine", "@chakra-ui/react": "chakra",
            "@mui/material": "mui", "@radix-ui/react-dialog": "radix",
            "@headlessui/react": "headlessui"}
    for pkg, name in libs.items():
        if pkg in deps:
            return name
    return "none"


def detect_motion(deps):
    if "motion" in deps:           return "motion"
    if "framer-motion" in deps:    return "framer-motion"
    if "gsap" in deps:             return "gsap"
    if "@formkit/auto-animate" in deps: return "autoanimate"
    if "tailwindcss-animate" in deps:   return "tailwindcss-animate"
    return "none"


def detect_aliases(root):
    ts = load_json(root / "tsconfig.json") or {}
    paths = (((ts.get("compilerOptions") or {}).get("paths")) or {})
    out = {}
    for alias, targets in paths.items():
        if isinstance(targets, list) and targets:
            # "@/*" -> "src/*"  → record "@/" -> "src/"
            out[alias.rstrip("*")] = str(targets[0]).rstrip("*")
    return out


def detect_dirs(root):
    return {k: str((root / k).resolve()) if (root / k).is_dir() else None
            for k in ("src", "src/components", "src/app", "app", "pages",
                      "src/lib", "lib")}


def detect_pkg_manager(root):
    for f, name in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"),
                    ("bun.lockb", "bun"),       ("package-lock.json", "npm")):
        if (root / f).is_file():
            return name
    return None


def shadcn_info(root):
    cj = load_json(root / "components.json")
    if not cj:
        return None
    aliases = cj.get("aliases") or {}
    return {"style": cj.get("style"),
            "baseColor": (cj.get("tailwind") or {}).get("baseColor"),
            "rsc": cj.get("rsc"),
            "components_alias": aliases.get("components"),
            "ui_alias": aliases.get("ui")}


# Deferral targets — external skills build-ui hands execution off to. SKILL.md
# Step 3 surfaces an install command from the fallback path when one is False.
DEFERRAL_TARGETS = ("shadcn", "next-best-practices")


def detect_user_skill(name):
    """True iff ~/.claude/skills/<name>/SKILL.md is discoverable with that name.

    Follows symlinks (the installer drops a symlink at ~/.claude/skills/<name>
    pointing into .agents/skills/<name>), so a symlinked install resolves the
    same as a real directory.
    """
    sk = Path.home() / ".claude" / "skills" / name / "SKILL.md"
    try:
        text = sk.read_text("utf-8", errors="replace")
    except OSError:
        return False
    return bool(re.search(rf"^name:\s*{re.escape(name)}\s*$", text, re.MULTILINE))


def detect_design_md(root):
    """Project-root DESIGN.md path if present, else None.

    The file is a portable visual-language source-of-truth — google-labs
    `design.md` (YAML tokens + rationale) or Stitch flavor (natural-language
    + hex). build-ui reads whichever is there as override for taste/tokens
    during a build. Sibling generator: the `design-md` skill (Stitch → file).
    """
    p = root / "DESIGN.md"
    return str(p) if p.is_file() else None


def tailwind_info(root):
    found = next((p for p in CONFIG_GLOBS if (root / p).is_file()), None)
    if not found:
        return None
    text = (root / found).read_text("utf-8", errors="replace")
    v = "v4" if "@tailwindcss/postcss" in text or "@import \"tailwindcss\"" in text else "v3"
    return {"config_path": found, "version_hint": v}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".", help="project root (default: cwd; walks up)")
    # --agent is a no-op here (probe is non-interactive by nature); accepted so
    # the harness can pass SKILL.md's standard flag through without an error.
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    root = find_project_root(args.project)
    pj = load_json(root / "package.json") or {}
    deps = {**(pj.get("dependencies") or {}), **(pj.get("devDependencies") or {})}

    out = {
        "project_root": str(root),
        "framework":    detect_framework(deps),
        "css":          detect_css(deps),
        "components":   detect_components(deps, root),
        "motion":       detect_motion(deps),
        "aliases":      detect_aliases(root),
        "dirs":         detect_dirs(root),
        "package_manager": detect_pkg_manager(root),
        "tailwind":     tailwind_info(root) if detect_css(deps) == "tailwind" else None,
        "shadcn":       shadcn_info(root)   if detect_components(deps, root) == "shadcn" else None,
        "design_md":    detect_design_md(root),
        # External skills build-ui defers to. False here means SKILL.md takes the
        # degraded path (surface the install command + fall back to general knowledge).
        "external_skills": {n: detect_user_skill(n) for n in DEFERRAL_TARGETS},
    }

    print(f"build-ui probe @ {root}", file=sys.stderr)
    for k in ("framework", "css", "components", "motion", "package_manager"):
        print(f"  {k:12} {out[k]}", file=sys.stderr)
    if out["aliases"]:
        print(f"  aliases      {out['aliases']}", file=sys.stderr)
    if out["design_md"]:
        print(f"  design_md    {out['design_md']}", file=sys.stderr)
    # Surface install-state ONLY for skills the project would actually use,
    # so a non-shadcn / non-Next project doesn't get noise.
    relevant = []
    if out["components"] == "shadcn":
        relevant.append("shadcn")
    if out["framework"] == "next":
        relevant.append("next-best-practices")
    for n in relevant:
        status = "installed" if out["external_skills"][n] else "MISSING (see SKILL.md fallback)"
        print(f"  {n:20} skill: {status}", file=sys.stderr)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
