#!/usr/bin/env python3
"""Detect a project's animation stack so SKILL.md can route tiers instead of guessing (spec A4).

One concern: read the target project's package.json + the local skills dir and
emit a JSON description of the animation-relevant stack — which animation
libraries exist (Motion vs legacy framer-motion vs others), whether Tailwind
and React are present, and whether the official Motion+ `/motion` skill is
installed to defer to. Best-effort, text-only — never executes project code.

What it detects (each may be null/false if absent):
    project_root         : nearest dir up-tree with package.json or .git
    has_package_json     : bool — false for plain HTML/CSS projects (CSS tier only)
    framework            : next | vite | astro | remix | null (best-effort from deps)
    react                : bool — react in deps
    motion               : bool — `motion` OR `framer-motion` in deps
    motion_version       : declared version of whichever is present, or null
    legacy_framer_motion : bool — the dep is the legacy `framer-motion` package
    auto_animate         : bool — @formkit/auto-animate present
    other_anim_libs      : [str] — gsap / react-spring / @react-spring/web /
                           animejs / lottie-react found in deps (respect, don't replace)
    tailwind             : bool — tailwindcss present
    package_manager      : npm | pnpm | yarn | bun | null
    external_skills      : { "motion": bool } — the official Motion+ skill
                           installed under ~/.claude/skills

I/O:
    stdin  : —
    stdout : the JSON described above
    stderr : a short human summary
    exit   : 0 always — an empty/unrecognised project still yields valid JSON
"""
import argparse
import json
import re
import sys
from pathlib import Path

# External skills add-motion defers Motion API knowledge to. False here means
# SKILL.md takes the fallback path (references/motion-library.md + caveat).
DEFERRAL_TARGETS = ("motion",)

OTHER_ANIM_LIBS = ("gsap", "react-spring", "@react-spring/web", "animejs",
                   "lottie-react", "@motionone/dom")

FRAMEWORK_DEPS = (("next", "next"), ("astro", "astro"),
                  ("@remix-run/react", "remix"), ("vite", "vite"))


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


def detect_user_skill(name):
    """True iff ~/.claude/skills/<name>/SKILL.md declares `name: <name>`.

    Follows symlinks, so a symlinked install resolves the same as a real dir.
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
    # --agent is a no-op here (probe is non-interactive); accepted so SKILL.md's
    # standard flag can be passed through without an error.
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    root = find_project_root(args.project)
    pj = load_json(root / "package.json")
    deps = {**((pj or {}).get("dependencies") or {}),
            **((pj or {}).get("devDependencies") or {})}

    framework = next((label for dep, label in FRAMEWORK_DEPS if dep in deps), None)
    legacy = "framer-motion" in deps and "motion" not in deps

    out = {
        "project_root":         str(root),
        "has_package_json":     pj is not None,
        "framework":            framework,
        "react":                "react" in deps,
        "motion":               "motion" in deps or "framer-motion" in deps,
        "motion_version":       deps.get("motion") or deps.get("framer-motion"),
        "legacy_framer_motion": legacy,
        "auto_animate":         "@formkit/auto-animate" in deps,
        "other_anim_libs":      [d for d in OTHER_ANIM_LIBS if d in deps],
        "tailwind":             "tailwindcss" in deps,
        "package_manager":      detect_pkg_manager(root),
        "external_skills":      {n: detect_user_skill(n) for n in DEFERRAL_TARGETS},
    }

    print(f"add-motion probe @ {root}", file=sys.stderr)
    print(f"  framework     {out['framework'] or '—'}    react {out['react']}    "
          f"tailwind {out['tailwind']}", file=sys.stderr)
    motion_note = (f"({out['motion_version']}, legacy framer-motion)" if legacy
                   else f"({out['motion_version']})" if out["motion_version"] else "")
    print(f"  motion        {out['motion']} {motion_note}", file=sys.stderr)
    if out["other_anim_libs"]:
        print(f"  other libs    {', '.join(out['other_anim_libs'])}  "
              "(respect — no-monoculture)", file=sys.stderr)
    for n in DEFERRAL_TARGETS:
        status = "installed" if out["external_skills"][n] else "not installed (fallback: references/)"
        print(f"  /{n} skill    {status}", file=sys.stderr)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
