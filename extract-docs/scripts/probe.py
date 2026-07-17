#!/usr/bin/env python3
"""Probe the acquisition ladder for a docs site (extract-docs Step 2).

Ladder (first complete manifest wins):
  1. llms-full.txt at site root       → tier "llms-full" (content, not URLs)
  2. llms.txt at root / docs base     → tier "llms" (URL manifest)
  3. per-page .md variant             → tier "page-md" (needs a URL source:
     sitemap if present, else crawl)
  4. sitemap.xml filtered to docs path→ tier "sitemap"
  5. bounded same-prefix crawl        → tier "crawl" (seeded from the docs
     index page's links)

I/O: stdout JSON {tier, manifest:[urls], count, base, docs_prefix, notes}
     · diagnostics stderr · exit 0 (graceful: worst case tier=crawl with a
     seed list; network failure → tier=none, exit 1).
Manifests are emitted IN FULL with the true count — the scope gate and
--max-pages enforcement live with the caller and fetch.py, never here
(no silent caps, spec A12). --max-pages only bounds the crawl-tier seed.
Usage: probe.py --url=https://site.tld/docs [--max-pages=200] [--tier=force]
"""
import argparse
import json
import re
import sys
import urllib.parse

from _net import get


def looks_like_llms_txt(text):
    """Real llms.txt is markdown-ish with links; SPA soft-404s return HTML."""
    if not text.strip() or text.lstrip()[:1] == "<":
        return False
    return bool(re.search(r"^#\s|\[[^\]]+\]\(https?://", text, re.M))


def md_links(text, base):
    urls = re.findall(r"\[[^\]]*\]\((https?://[^\s)]+)\)", text)
    host = urllib.parse.urlparse(base).netloc
    return [u for u in urls if urllib.parse.urlparse(u).netloc == host]


def sitemap_urls(root):
    _, xml = get(root + "/sitemap.xml")
    urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
    # sitemap index? follow one level of child sitemaps
    children = [u for u in urls if u.endswith(".xml")]
    if children and len(children) == len(urls):
        urls = []
        for c in children[:10]:
            _, cx = get(c)
            urls += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", cx)
    return urls


def crawl_seed(docs_url, prefix, cap):
    """One-level link harvest from the docs index (breadth is handled by
    fetch.py's crawl-tier discovery; probe only seeds)."""
    _, html = get(docs_url)
    hrefs = re.findall(r'href="([^"#?]+)"', html)
    base = urllib.parse.urlparse(docs_url)
    out, seen = [], set()
    for h in hrefs:
        u = urllib.parse.urljoin(docs_url, h)
        p = urllib.parse.urlparse(u)
        if p.netloc == base.netloc and p.path.startswith(prefix) and u not in seen:
            seen.add(u)
            out.append(u)
        if len(out) >= cap:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--max-pages", type=int, default=200)
    ap.add_argument("--tier", choices=["llms-full", "llms", "page-md", "sitemap", "crawl"])
    args = ap.parse_args()

    p = urllib.parse.urlparse(args.url)
    root = f"{p.scheme}://{p.netloc}"
    prefix = p.path.rstrip("/") or "/"
    notes = []
    result = None

    def emit(tier, manifest, **extra):
        payload = {"tier": tier, "manifest": manifest, "count": len(manifest),
                   "base": root, "docs_prefix": prefix, "notes": notes, **extra}
        print(json.dumps(payload, indent=1))

    def want(tier):
        return args.tier is None or args.tier == tier

    # 1. llms-full.txt
    if want("llms-full"):
        st, body = get(root + "/llms-full.txt")
        if st == 200 and looks_like_llms_txt(body):
            print("  tier llms-full: hit", file=sys.stderr)
            emit("llms-full", [root + "/llms-full.txt"],
                 inline_content=True)
            return
        notes.append("llms-full.txt: absent")

    # 2. llms.txt (root, then docs-scoped)
    if want("llms"):
        for cand in (root + "/llms.txt", root + prefix + "/llms.txt"):
            st, body = get(cand)
            if st == 200 and looks_like_llms_txt(body):
                links = md_links(body, root)
                docs_links = [u for u in links
                              if urllib.parse.urlparse(u).path.startswith(prefix)] or links
                if docs_links:
                    print(f"  tier llms: hit at {cand} ({len(docs_links)} urls)",
                          file=sys.stderr)
                    emit("llms", docs_links, source=cand)
                    return
        notes.append("llms.txt: absent")

    # need page URLs for tiers 3-4
    pages = [u for u in sitemap_urls(root)
             if urllib.parse.urlparse(u).path.startswith(prefix)]

    # 3. per-page .md variant (probe one sitemap page)
    if want("page-md") and pages:
        sample = pages[min(1, len(pages) - 1)].rstrip("/")
        st, body = get(sample + ".md")
        if st == 200 and body.strip() and body.lstrip()[:1] != "<":
            print("  tier page-md: hit", file=sys.stderr)
            emit("page-md", [u.rstrip("/") + ".md" for u in pages])
            return
        notes.append("per-page .md: absent")

    # 4. sitemap
    if want("sitemap") and pages:
        print(f"  tier sitemap: {len(pages)} docs urls", file=sys.stderr)
        emit("sitemap", pages)
        return
    if want("sitemap"):
        notes.append("sitemap: absent or no docs urls")

    # 5. crawl seed
    seeds = crawl_seed(args.url, prefix, args.max_pages)
    if seeds:
        print(f"  tier crawl: seeded {len(seeds)} urls (bounded, robots.txt "
              "applies in fetch.py)", file=sys.stderr)
        emit("crawl", seeds)
        return

    emit("none", [])
    sys.exit(1)


if __name__ == "__main__":
    main()
