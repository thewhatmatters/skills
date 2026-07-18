#!/usr/bin/env python3
"""Fetch manifest URLs and convert each page to markdown (extract-docs Step 4).

Reads the probe.py JSON (file via --manifest, or stdin), fetches every URL,
extracts the main content (<main>/<article>/largest heading-bearing region),
converts to markdown with a stdlib HTMLParser, and writes one .md per page
under --out mirroring the URL path. Crawl-tier runs discover same-prefix
links breadth-first up to --max-pages and honor robots.txt Disallow rules.

I/O: stdout JSON {fetched:[{url,path,title}], failed:[{url,reason}],
     empty:[url], discovered:int} · progress on stderr · exit 0 (per-page
     failures are data, not crashes); a missing/malformed manifest is the
     one hard error: {"error": ...} JSON + exit 1.
Usage: fetch.py --manifest=probe.json --out=docs/sources/vendor [--max-pages=200] [--delay=0.3]
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
from html.parser import HTMLParser

from _net import get

SKIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "noscript",
             "svg", "button", "form"}
BLOCK_TAGS = {"p", "div", "section", "li", "br", "hr"}


class MdConverter(HTMLParser):
    """Pragmatic HTML→markdown: headings, paragraphs, lists, code, links,
    emphasis, blockquotes, simple tables. Content scoping: once a <main> or
    <article> opens, only that subtree is kept; without one, everything
    outside SKIP_TAGS is kept."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip_depth = 0
        self.main_seen = False
        self.in_main = 0
        self.pre = 0
        self.list_stack = []
        self.href = None
        self.title = ""
        self.in_title = False
        self.table_first = False
        self.table_cols = 0

    def keep(self):
        return self.skip_depth == 0 and (not self.main_seen or self.in_main > 0)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
            return
        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return
        if tag in ("main", "article") or a.get("role") == "main":
            self.main_seen = True
            self.in_main += 1
            return
        if not self.keep():
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "pre":
            self.pre += 1
            self.out.append("\n\n```\n")
        elif tag == "code" and not self.pre:
            self.out.append("`")
        elif tag in ("ul", "ol"):
            self.list_stack.append(tag)
        elif tag == "li":
            depth = max(len(self.list_stack) - 1, 0)
            marker = "- " if (self.list_stack[-1:] or ["ul"])[0] == "ul" else "1. "
            self.out.append("\n" + "  " * depth + marker)
        elif tag == "a":
            self.href = a.get("href")
            self.out.append("[")
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag == "blockquote":
            self.out.append("\n\n> ")
        elif tag == "img" and a.get("alt"):
            self.out.append(f"*[image: {a['alt']}]* ")
        elif tag == "table":
            self.table_first = True
            self.table_cols = 0
            self.out.append("\n\n")
        elif tag == "tr":
            self.out.append("\n|")
        elif tag in ("td", "th"):
            self.out.append(" ")
        elif tag in BLOCK_TAGS:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
            return
        if tag in SKIP_TAGS:
            self.skip_depth = max(self.skip_depth - 1, 0)
            return
        if tag in ("main", "article"):
            self.in_main = max(self.in_main - 1, 0)
            return
        if not self.keep():
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.out.append("\n")
        elif tag == "pre":
            self.pre = max(self.pre - 1, 0)
            self.out.append("\n```\n")
        elif tag == "code" and not self.pre:
            self.out.append("`")
        elif tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
            self.out.append("\n")
        elif tag == "a":
            self.out.append(f"]({self.href})" if self.href else "]")
            self.href = None
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag == "p":
            self.out.append("\n\n")
        elif tag in ("td", "th"):
            self.out.append(" |")
            if self.table_first:
                self.table_cols += 1
        elif tag == "tr":
            if self.table_first and self.table_cols:
                self.out.append("\n|" + " --- |" * self.table_cols)
                self.table_first = False
        elif tag == "table":
            self.out.append("\n")

    def handle_data(self, data):
        if self.in_title:
            if not self.title:
                self.title = data.strip()
            return
        if not self.keep():
            return
        self.out.append(data if self.pre else re.sub(r"\s+", " ", data))

    def markdown(self):
        text = "".join(self.out)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        return text.strip()


def to_markdown(html_text):
    conv = MdConverter()
    try:
        conv.feed(html_text)
    except Exception:
        pass
    md, title = conv.markdown(), conv.title
    if title and not md.startswith("#"):
        md = f"# {title}\n\n{md}"
    return escape_bare_tags(md), title


_BARE_TAG = re.compile(r"(?<![\\`])(</?[a-zA-Z][a-zA-Z0-9-]*(?: [^>`\n]*)?/?>)")


def escape_bare_tags(md):
    """Backtick bare HTML/JSX-ish tags left in prose by conversion.

    Obsidian (and other markdown renderers) treat a bare `<head>`-style tag
    as raw HTML that can swallow the rest of the block. Applied per line,
    skipping fenced blocks and existing inline code spans, so code samples
    stay verbatim. Deterministic + idempotent — safe across refreshes.
    """
    out, in_fence = [], False
    for line in md.split("\n"):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence or "`" in line:
            # lines with existing spans: only wrap tags outside the spans
            if not in_fence and "<" in line:
                parts = re.split(r"(`[^`]*`)", line)
                line = "".join(p if p.startswith("`") else _BARE_TAG.sub(r"`\1`", p)
                               for p in parts)
            out.append(line)
            continue
        if "<" in line:
            line = _BARE_TAG.sub(r"`\1`", line)
        out.append(line)
    return "\n".join(out)


def local_path(url, prefix, out_dir):
    path = urllib.parse.urlparse(url).path
    rel = path[len(prefix):].strip("/") if path.startswith(prefix) else path.strip("/")
    # the docs root maps to home.md — index.md is reserved for the
    # Step-5 manifest the skill writes after fetching (collision found in
    # the first live run: the manifest overwrote the extracted root page)
    rel = re.sub(r"\.md$", "", rel) or "home"
    return os.path.join(out_dir, *[s for s in rel.split("/") if s]) + ".md"


def rewrite_links(md, page_local, prefix, base, out_dir):
    """Rewrite same-site links under the docs prefix to relative local .md
    paths so the mirror is navigable offline; anchors preserved."""
    host = urllib.parse.urlparse(base).netloc
    page_dir = os.path.dirname(page_local)

    def sub(m):
        target, anchor = m.group(1), m.group(2) or ""
        path = target
        if target.startswith("http"):
            pu = urllib.parse.urlparse(target)
            if pu.netloc != host:
                return m.group(0)
            path = pu.path
        if not path.startswith(prefix):
            return m.group(0)
        local = local_path(base + path, prefix, out_dir)
        return "](" + os.path.relpath(local, page_dir) + anchor + ")"

    return re.sub(r"\]\((/[^)#\s]+|https?://[^)#\s]+?)(#[^)]*)?\)", sub, md)


def robots_disallows(base):
    _, body = get(base + "/robots.txt")
    rules, applies = [], False
    for line in body.splitlines():
        line = line.split("#")[0].strip()
        m = re.match(r"(?i)user-agent:\s*(.+)", line)
        if m:
            applies = m.group(1).strip() == "*"
            continue
        m = re.match(r"(?i)disallow:\s*(.+)", line)
        if m and applies:
            rules.append(m.group(1).strip())
    return rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="probe.py JSON file (default: stdin)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-pages", type=int, default=200)
    ap.add_argument("--delay", type=float, default=0.3)
    args = ap.parse_args()

    try:
        probe = (json.load(open(args.manifest)) if args.manifest
                 else json.load(sys.stdin))
        tier, prefix, base = probe["tier"], probe["docs_prefix"], probe["base"]
    except (OSError, ValueError, KeyError) as e:
        print(json.dumps({"error": f"bad manifest: {e.__class__.__name__}: {e}"}))
        sys.exit(1)
    queue = list(probe["manifest"])[: args.max_pages]
    crawl = tier == "crawl"
    disallow = robots_disallows(base) if crawl else []

    fetched, failed, empty, seen = [], [], [], set(queue)
    os.makedirs(args.out, exist_ok=True)

    while queue:
        url = queue.pop(0)
        if crawl and any(urllib.parse.urlparse(url).path.startswith(r)
                         for r in disallow if r):
            failed.append({"url": url, "reason": "robots.txt disallow"})
            continue
        st, body = get(url)
        if st != 200 or not body:
            failed.append({"url": url, "reason": f"HTTP {st}" if st else "network"})
            continue

        if tier in ("llms-full", "page-md") or body.lstrip()[:1] != "<":
            md, title = body, (re.search(r"^#\s+(.+)$", body, re.M) or [None, ""])[1]
        else:
            md, title = to_markdown(body)

        if len(md.strip()) < 80:
            empty.append(url)
            print(f"  ∅ {url} (likely JS-rendered)", file=sys.stderr)
            continue

        dest = local_path(url, prefix, args.out)
        md = rewrite_links(md, dest, prefix, base, args.out)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write(f"<!-- source: {url} · extracted: "
                    f"{time.strftime('%Y-%m-%d')} · by: extract-docs -->\n\n{md}\n")
        fetched.append({"url": url, "path": dest, "title": title or ""})
        print(f"  ✓ {url} → {dest}", file=sys.stderr)

        if crawl and len(seen) < args.max_pages:
            for h in re.findall(r'href="([^"#?]+)"', body):
                u = urllib.parse.urljoin(url, h)
                pu = urllib.parse.urlparse(u)
                if (pu.netloc == urllib.parse.urlparse(base).netloc
                        and pu.path.startswith(prefix) and u not in seen):
                    seen.add(u)
                    queue.append(u)
        time.sleep(args.delay)

    print(json.dumps({"fetched": fetched, "failed": failed, "empty": empty,
                      "discovered": len(seen)}, indent=1))


if __name__ == "__main__":
    main()
