#!/usr/bin/env python3
"""probe.py — detect the project's styling stack so the grid never imposes Tailwind
or silently re-scales a live --spacing (spec A3/A8 — dual-mode + no-monoculture).

Walks a project dir (default: cwd) and reports, as JSON on stdout:
  tailwind        : "v4" | "v3" | "none"
  framework       : "react" | "vue" | "svelte" | "none"
  spacing_base    : the current Tailwind --spacing value if found (else null)
  design_md_grid  : true if a DESIGN.md contains a "## Grid" section
  css_entry       : path of the CSS file importing tailwind (if any)
  recommend       : "tailwind" | "vanilla"  (which grid_tokens path to use)
  notes           : human hints (also mirrored to stderr)

Heuristic, read-only, no network, never hangs. Diagnostics on stderr.
"""
import argparse, json, os, re, sys

SKIP = {"node_modules", ".git", ".next", "dist", "build", ".cache", ".venv", "vendor"}


def read(path, limit=200_000):
    try:
        with open(path, "r", errors="ignore") as fh:
            return fh.read(limit)
    except OSError:
        return ""


def find_files(root, names=None, exts=None, cap=4000):
    """Yield paths under root, skipping heavy dirs; bounded by cap."""
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP and not d.startswith(".")]
        for f in filenames:
            n += 1
            if n > cap:
                return
            if names and f in names:
                yield os.path.join(dirpath, f)
            elif exts and os.path.splitext(f)[1] in exts:
                yield os.path.join(dirpath, f)


def detect(root):
    notes = []
    tailwind = "none"
    framework = "none"
    spacing_base = None
    css_entry = None
    design_md_grid = False

    # package.json → tailwind major + framework
    for pkg in find_files(root, names={"package.json"}, cap=200):
        blob = read(pkg)
        try:
            data = json.loads(blob)
        except ValueError:
            continue
        deps = {}
        for k in ("dependencies", "devDependencies", "peerDependencies"):
            deps.update(data.get(k, {}) or {})
        tw = deps.get("tailwindcss")
        if tw:
            m = re.search(r"(\d+)", str(tw))
            major = int(m.group(1)) if m else 0
            tailwind = "v4" if major >= 4 else ("v3" if major == 3 else "v3")
            notes.append(f"tailwindcss {tw} in {os.path.relpath(pkg, root)}")
        if "react" in deps or "next" in deps:
            framework = "react"
        elif "vue" in deps or "nuxt" in deps:
            framework = "vue"
        elif "svelte" in deps:
            framework = "svelte"
        break  # first package.json wins (project root)

    # CSS entry that imports tailwind (v4 uses @import "tailwindcss")
    for css in find_files(root, exts={".css"}, cap=3000):
        blob = read(css)
        if '@import "tailwindcss"' in blob or "@import 'tailwindcss'" in blob:
            css_entry = os.path.relpath(css, root)
            if tailwind == "none":
                tailwind = "v4"
            m = re.search(r"--spacing\s*:\s*([^;]+);", blob)
            if m:
                spacing_base = m.group(1).strip()
            break

    # DESIGN.md with a Grid section
    for dm in find_files(root, names={"DESIGN.md"}, cap=400):
        blob = read(dm)
        if re.search(r"^##\s+Grid\b", blob, re.MULTILINE):
            design_md_grid = True
            notes.append(f"DESIGN.md ## Grid found: {os.path.relpath(dm, root)}")
            break

    recommend = "tailwind" if tailwind in ("v4", "v3") else "vanilla"
    if recommend == "vanilla":
        notes.append("no Tailwind detected → use --vanilla (do not add Tailwind).")
    if spacing_base and spacing_base not in ("0.25rem", "0.25Rem"):
        notes.append(f"--spacing is {spacing_base}: do NOT re-scale; add the grid "
                     f"namespace on top.")

    return {
        "tailwind": tailwind,
        "framework": framework,
        "spacing_base": spacing_base,
        "design_md_grid": design_md_grid,
        "css_entry": css_entry,
        "recommend": recommend,
        "notes": notes,
    }


def main():
    ap = argparse.ArgumentParser(description="Detect styling stack for use-grid-system")
    ap.add_argument("path", nargs="?", default=".", help="project dir (default: cwd)")
    args = ap.parse_args()
    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        print(f"probe: not a directory: {root}", file=sys.stderr)
        print(json.dumps({"error": "not-a-directory", "path": root}))
        sys.exit(0)
    result = detect(root)
    print("use-grid-system probe", file=sys.stderr)
    for n in result["notes"]:
        print(f"  · {n}", file=sys.stderr)
    print(f"  → tailwind={result['tailwind']} framework={result['framework']} "
          f"recommend={result['recommend']}", file=sys.stderr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
