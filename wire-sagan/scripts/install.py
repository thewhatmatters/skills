#!/usr/bin/env python3
"""Install or update the .sagan/ overlay in a project.

I/O: stdout JSON {status, installed|synced|flagged, template_version} ·
stderr diagnostics · exit 2 on refusal (existing .sagan without --update,
missing template). Install substitutes {{TOKENS}} into sagan.yaml, writes a
sha256 manifest (.sagan/.template-manifest.json) for --update modification
detection, and merges the commit-policy fragment into the project .gitignore.
Never touches CLAUDE.md/AGENTS.md — the marker block is Claude's native,
consent-gated edit.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

TEMPLATE_VERSION = "0.1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template")
CORE = ["sagan.yaml", "MEMORY.md"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def render_sagan_yaml(subs):
    body = open(os.path.join(TEMPLATE, "sagan.yaml")).read()
    for token, value in subs.items():
        body = body.replace("{{%s}}" % token, value)
    return body


def merge_gitignore(root):
    frag = open(os.path.join(TEMPLATE, "gitignore-fragment")).read()
    gi = os.path.join(root, ".gitignore")
    try:
        existing = (open(gi, encoding="utf-8", errors="replace").read()
                    if os.path.isfile(gi) else "")
        if ".sagan/ledger/*/" in existing:
            return "already-present"
        with open(gi, "a", encoding="utf-8") as f:
            if existing and not existing.endswith("\n"):
                f.write("\n")
            f.write("\n" + frag)
        return "merged"
    except OSError as e:
        return f"failed ({e}) — append the fragment manually"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    ap.add_argument("--roles", default="frontend,critic,verify")
    ap.add_argument("--gates-test", default="")
    ap.add_argument("--gates-typecheck", default="")
    ap.add_argument("--gates-build", default="")
    ap.add_argument("--tickets", default="local-files",
                    choices=["local-files", "linear"])
    ap.add_argument("--promote-target", default="CLAUDE.md")
    ap.add_argument("--update", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(os.path.expanduser(args.project))
    fleet = os.path.join(root, ".sagan")
    manifest_path = os.path.join(fleet, ".template-manifest.json")

    if not os.path.isdir(TEMPLATE):
        print(json.dumps({"status": "error", "detail": "template assets missing"}))
        sys.exit(2)

    if args.update:
        if not os.path.isfile(manifest_path):
            print(json.dumps({"status": "error",
                              "detail": "no manifest — not a wire-sagan install (or NATIVE install); cannot --update safely"}))
            sys.exit(2)
        manifest = json.load(open(manifest_path))
        synced, flagged, missing = [], [], []
        skipped_configured = []
        for rel, recorded in manifest["files"].items():
            if rel == "sagan.yaml":
                # Project-configured at install (rendered {{TOKENS}}); a raw
                # resync would clobber the project's config, so it is always
                # skipped and listed under skipped_project_configured. NB:
                # upstream template changes to sagan.yaml are NOT detected —
                # compare against assets/template/sagan.yaml by hand. Files
                # ADDED to the template after install are likewise not synced
                # (the loop iterates the install-time manifest only).
                skipped_configured.append(rel)
                continue
            src = os.path.join(TEMPLATE, manifest["sources"].get(rel, rel))
            dst = os.path.join(fleet, rel)
            if not os.path.isfile(src):
                continue
            if not os.path.isfile(dst):
                missing.append(rel)
                continue
            if sha256(dst) == recorded:
                shutil.copyfile(src, dst)
                manifest["files"][rel] = sha256(dst)
                synced.append(rel)
            else:
                flagged.append(rel)
        manifest["template_version"] = TEMPLATE_VERSION
        json.dump(manifest, open(manifest_path, "w"), indent=2)
        print(f"update: {len(synced)} synced, {len(flagged)} locally modified (left alone)",
              file=sys.stderr)
        print(json.dumps({"status": "updated", "template_version": TEMPLATE_VERSION,
                          "synced": synced, "flagged_local_edits": flagged,
                          "skipped_project_configured": skipped_configured,
                          "missing": missing}, indent=2))
        return

    if os.path.isdir(fleet):
        print(json.dumps({"status": "error",
                          "detail": ".sagan/ already exists — use --update"}))
        sys.exit(2)

    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    subs = {
        "TEMPLATE_VERSION": TEMPLATE_VERSION,
        "GATE_TEST": args.gates_test or "(none configured)",
        "GATE_TYPECHECK": args.gates_typecheck or "(none configured)",
        "GATE_BUILD": args.gates_build or "(none configured)",
        "TICKET_STORE": args.tickets,
        "PROMOTE_TARGET": args.promote_target,
    }

    files, sources = {}, {}
    os.makedirs(os.path.join(fleet, "memory"))
    os.makedirs(os.path.join(fleet, "ledger"))
    os.makedirs(os.path.join(fleet, "roles"))
    os.makedirs(os.path.join(fleet, "tickets"))
    open(os.path.join(fleet, "ledger", "events.jsonl"), "w").close()

    with open(os.path.join(fleet, "sagan.yaml"), "w") as f:
        f.write(render_sagan_yaml(subs))
    # sagan.yaml is project-configured at render; record its rendered hash so
    # only later *user* edits count as modifications.
    files["sagan.yaml"] = sha256(os.path.join(fleet, "sagan.yaml"))
    sources["sagan.yaml"] = "sagan.yaml"

    shutil.copyfile(os.path.join(TEMPLATE, "MEMORY.md"),
                    os.path.join(fleet, "MEMORY.md"))
    files["MEMORY.md"] = sha256(os.path.join(fleet, "MEMORY.md"))
    sources["MEMORY.md"] = "MEMORY.md"

    for role in roles:
        src = os.path.join(TEMPLATE, "roles", f"{role}.md")
        if not os.path.isfile(src):
            print(f"  ⚠ no template for role '{role}' — skipped", file=sys.stderr)
            continue
        rel = os.path.join("roles", f"{role}.md")
        shutil.copyfile(src, os.path.join(fleet, rel))
        files[rel] = sha256(os.path.join(fleet, rel))
        sources[rel] = rel

    rel = os.path.join("tickets", "T-000-example.md")
    shutil.copyfile(os.path.join(TEMPLATE, rel), os.path.join(fleet, rel))
    files[rel] = sha256(os.path.join(fleet, rel))
    sources[rel] = rel

    json.dump({"template_version": TEMPLATE_VERSION, "files": files,
               "sources": sources}, open(manifest_path, "w"), indent=2)
    gi = merge_gitignore(root)

    print(f"installed .sagan/ ({len(files)} tracked files) · gitignore {gi}",
          file=sys.stderr)
    print(json.dumps({"status": "installed", "template_version": TEMPLATE_VERSION,
                      "installed": sorted(files), "gitignore": gi,
                      "fleet_dir": fleet}, indent=2))


if __name__ == "__main__":
    main()
