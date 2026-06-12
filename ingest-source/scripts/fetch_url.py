#!/usr/bin/env python3
"""Fetch a URL for ingest-source: webpage → readable text, or --raw → file (spec A4).

One concern: turn a URL into ingestable content without any API key. Default
mode fetches an HTML page and extracts readable text (title, headings,
paragraphs, list items — scripts/styles/nav stripped). --raw mode downloads
the response body verbatim to --out (for remote PDFs/images, which Claude
then reads natively).

Transport ladder (audit-ui lesson: macOS stdlib Python often has no CA bundle):
  requests (certifi) → urllib → curl subprocess. First success wins; the
  transport used is reported in the JSON.

I/O: --url URL [--raw --out=PATH] [--timeout=N] · stdout JSON · stderr
diagnostics · never hangs (every transport is timeout-bounded). Exit 0 on
fetched content, 1 on total failure (caller falls back to WebFetch /
automate-browser).

JSON shape (default): {"url", "final_url", "status", "content_type", "title",
                       "text", "transport", "error"}
JSON shape (--raw):   {"url", "status", "content_type", "saved_to",
                       "bytes", "transport", "error"}
"""
import argparse
import json
import re
import subprocess
import sys
from html.parser import HTMLParser

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 ingest-source")

_SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "iframe",
              "nav", "footer", "form", "button"}
_BLOCK_TAGS = {"p", "div", "section", "article", "br", "li", "tr",
               "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre"}


class _TextExtractor(HTMLParser):
    """HTML → plain text. Headings kept as markdown '#' lines; li as '- '."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.title = ""
        self._skip_depth = 0
        self._in_title = False
        self._heading = None

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and not self._skip_depth:
            self._heading = tag
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li" and not self._skip_depth:
            self.parts.append("\n- ")
        elif tag in _BLOCK_TAGS and not self._skip_depth:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False
        elif self._heading and tag == self._heading:
            self._heading = None
            self.parts.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._skip_depth and data.strip():
            self.parts.append(data)

    def text(self):
        raw = "".join(self.parts)
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def _via_requests(url, timeout, raw):
    try:
        import requests
    except Exception:
        return None
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": UA},
                         allow_redirects=True)
        body = r.content if raw else r.text
        return {"status": r.status_code, "final_url": r.url,
                "content_type": r.headers.get("content-type", ""),
                "body": body, "transport": "requests"}
    except Exception as e:
        print(f"  · requests failed: {e}", file=sys.stderr)
        return None


def _via_urllib(url, timeout, raw):
    import urllib.error
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            ctype = resp.headers.get("content-type", "")
            body = data if raw else data.decode(
                resp.headers.get_content_charset() or "utf-8", errors="replace")
            return {"status": resp.status, "final_url": resp.geturl(),
                    "content_type": ctype, "body": body, "transport": "urllib"}
    except Exception as e:  # incl. CERTIFICATE_VERIFY_FAILED on CA-less pythons
        print(f"  · urllib failed: {e}", file=sys.stderr)
        return None


def _via_curl(url, timeout, raw):
    try:
        p = subprocess.run(
            ["curl", "-sSL", "--max-time", str(timeout), "-A", UA,
             "-w", "\\n%{content_type}\\t%{http_code}\\t%{url_effective}", url],
            capture_output=True, timeout=timeout + 10)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"  · curl failed: {e}", file=sys.stderr)
        return None
    if p.returncode != 0:
        tail = (p.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[-1]
        print(f"  · curl rc={p.returncode}: {tail}", file=sys.stderr)
        return None
    out = p.stdout
    nl = out.rfind(b"\n")
    if nl < 0:
        return None
    body, meta = out[:nl], out[nl + 1:].decode("utf-8", "replace")
    fields = meta.split("\t")
    ctype, code, final = (fields + ["", "0", url])[:3]
    return {"status": int(code or 0), "final_url": final, "content_type": ctype,
            "body": body if raw else body.decode("utf-8", errors="replace"),
            "transport": "curl"}


def fetch(url, timeout, raw):
    for transport in (_via_requests, _via_urllib, _via_curl):
        got = transport(url, timeout, raw)
        if got and got["status"] and got["status"] < 400 and got["body"]:
            return got
        if got:
            print(f"  · {got['transport']} HTTP {got['status']} — trying next",
                  file=sys.stderr)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--raw", action="store_true",
                    help="save the body verbatim to --out (binary-safe)")
    ap.add_argument("--out", help="required with --raw")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()
    if args.raw and not args.out:
        print("  ⛔ --raw requires --out", file=sys.stderr)
        sys.exit(2)

    print(f"ingest-source fetch_url ({'raw' if args.raw else 'text'})",
          file=sys.stderr)
    got = fetch(args.url, args.timeout, args.raw)
    if not got:
        print("  ⛔ all transports failed", file=sys.stderr)
        print(json.dumps({"url": args.url, "status": None, "error":
                          "all transports failed (requests/urllib/curl)"}))
        sys.exit(1)

    if args.raw:
        body = got["body"] if isinstance(got["body"], bytes) else got["body"].encode()
        with open(args.out, "wb") as fh:
            fh.write(body)
        print(f"  ✅ {len(body)} bytes → {args.out} via {got['transport']}",
              file=sys.stderr)
        print(json.dumps({"url": args.url, "status": got["status"],
                          "content_type": got["content_type"],
                          "saved_to": args.out, "bytes": len(body),
                          "transport": got["transport"], "error": None}))
        return

    extractor = _TextExtractor()
    try:
        extractor.feed(got["body"])
    except Exception as e:
        print(f"  · parser choked ({e}) — emitting unparsed body", file=sys.stderr)
    text = extractor.text() or got["body"].strip()
    print(f"  ✅ {len(text)} chars extracted via {got['transport']}",
          file=sys.stderr)
    print(json.dumps({"url": args.url, "final_url": got["final_url"],
                      "status": got["status"],
                      "content_type": got["content_type"],
                      "title": extractor.title.strip(), "text": text,
                      "transport": got["transport"], "error": None},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
