#!/usr/bin/env python3
"""Refresh an existing extract-docs mirror against the live site and report
the delta (extract-docs `--refresh`; spec A4: one concern).

Given a fresh probe manifest and an existing mirror dir, classifies every
page as added / removed / changed / unchanged and applies the delta:
  - added   → fetched + converted + written (no frontmatter; the caller's
              conformance pass owns that, same as first extraction)
  - changed → body replaced with fresh conversion; an existing OKF
              frontmatter block on the local file is PRESERVED verbatim
  - removed → file deleted (index regeneration is the caller's step)
Change detection hashes the *normalized* body — frontmatter block and the
`<!-- source: … extracted: … -->` header (whose date changes every run) are
excluded, so a refresh minutes after an extraction reports all-unchanged.
Note: the full manifest is still fetched for comparison — the savings are
write-churn and the DELTA REPORT (what the vendor changed), not bandwidth.

I/O: refresh.py --manifest=probe.json --out=DIR [--max-pages=N]
[--dry-run] · stdout JSON {added, removed, changed, unchanged, applied} ·
diagnostics stderr · exit 0 ok (delta or not) / 1 bad manifest / 2 out dir
missing. --dry-run computes and reports the delta without writing.
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import get, to_markdown, local_path, rewrite_links  # noqa: E402

SRC_RX = re.compile(r"<!-- source: (\S+)[^>]*-->")


def split_frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            close = text.find("\n", end + 4)
            close = len(text) if close == -1 else close + 1
            return text[:close], text[close:]
    return "", text


def normalize(body):
    body = SRC_RX.sub("", body)
    return re.sub(r"\s+", " ", body).strip()


def digest(body):
    return hashlib.sha256(normalize(body).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-pages", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    try:
        probe = json.load(open(args.manifest))
        prefix, base = probe["docs_prefix"], probe["base"]
        manifest = list(probe["manifest"])[: args.max_pages]
    except (OSError, ValueError, KeyError) as e:
        print(json.dumps({"error": f"bad manifest: {e}"}))
        sys.exit(1)
    out = os.path.expanduser(args.out)
    if not os.path.isdir(out):
        print(json.dumps({"error": f"mirror dir missing: {out} — run a full "
                          f"extraction first"}))
        sys.exit(2)

    # existing pages by source URL (ground truth: each page's source comment)
    existing = {}
    for dirpath, dirs, files in os.walk(out):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if not f.endswith(".md") or f == "index.md":
                continue
            path = os.path.join(dirpath, f)
            text = open(path, encoding="utf-8").read()
            m = SRC_RX.search(text)
            if m:
                existing[m.group(1)] = path

    added, removed, changed, unchanged, applied = [], [], [], 0, []
    manifest_set = set(manifest)

    for url, path in sorted(existing.items()):
        if url not in manifest_set:
            removed.append(url)
            if not args.dry_run:
                os.unlink(path)
                applied.append(f"deleted {os.path.relpath(path, out)}")

    for url in manifest:
        st, body = get(url)
        if st != 200 or not body:
            print(f"refresh: fetch failed {url} (HTTP {st}) — skipped",
                  file=sys.stderr)
            continue
        if body.lstrip()[:1] != "<":
            md, _ = body, None
        else:
            md, _ = to_markdown(body)
        header = f"<!-- source: {url} · extracted: refresh · by: extract-docs -->\n\n"
        md_full = header + rewrite_links(md, local_path(url, prefix, out),
                                         prefix, base, out)
        if url not in existing:
            added.append(url)
            if not args.dry_run:
                dest = local_path(url, prefix, out)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                open(dest, "w").write(md_full)
                applied.append(f"added {os.path.relpath(dest, out)}")
            continue
        local_text = open(existing[url], encoding="utf-8").read()
        fm, local_body = split_frontmatter(local_text)
        if digest(local_body) == digest(md_full):
            unchanged += 1
            continue
        changed.append(url)
        if not args.dry_run:
            open(existing[url], "w").write(fm + md_full)
            applied.append(f"updated {os.path.relpath(existing[url], out)}")

    print(f"refresh: +{len(added)} added, -{len(removed)} removed, "
          f"~{len(changed)} changed, {unchanged} unchanged"
          f"{' (dry-run — nothing written)' if args.dry_run else ''}",
          file=sys.stderr)
    print(json.dumps({
        "added": added, "removed": removed, "changed": changed,
        "unchanged": unchanged, "dry_run": args.dry_run,
        "applied": applied,
    }, indent=2))


if __name__ == "__main__":
    main()
