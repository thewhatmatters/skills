#!/usr/bin/env python3
"""
Web source — LLM-native search, provider-pluggable.

Provider precedence (by which key is present; hard errors fail over to the next):
  1. Tavily   (TAVILY_API_KEY)  — native recency (topic=news + days / time_range)
  2. Exa      (EXA_API_KEY)     — neural search, exact published-date range
  3. DuckDuckGo (no key)        — keyless last resort

Keys are loaded by scripts/_env.py from: real env -> ~/.claude/.env ->
~/.claude/skills/.env. Keys are sent in request HEADERS only, never in URLs,
so they cannot leak into the stderr lines this script prints.

Usage: python3 web.py "<topic>" [QUERY_TYPE] [--days=N]   (N defaults to 30)
QUERY_TYPE: RECOMMENDATIONS | NEWS | PROMPTING | COMPARISON | GENERAL | XFALLBACK
  XFALLBACK = the X/Twitter fallback: restricts results to x.com/twitter.com
  (used when scripts/x.py has no session). Tag those results as X/Twitter.
Output: JSON array of {title, source, url, snippet, text}
"""
import sys, os, json, urllib.parse, time
from datetime import datetime, timedelta, UTC

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _env  # noqa: E402

HEADERS = {"User-Agent": "Mozilla/5.0 (research-bot/1.0)"}
YEAR = str(datetime.now().year)

QUERY_TEMPLATES = {
    "RECOMMENDATIONS": ["{topic} recommendations " + YEAR, "{topic} best list examples"],
    "NEWS":            ["{topic} news " + YEAR, "{topic} latest update announcement"],
    "PROMPTING":       ["{topic} prompts examples " + YEAR, "{topic} techniques tips"],
    "COMPARISON":      ["{topic} comparison review " + YEAR],
    "GENERAL":         ["{topic} " + YEAR, "{topic} discussion guide"],
    "XFALLBACK":       ["{topic}"],
}

# Dedicated-source domains + low-value socials — excluded from normal web results.
SKIP_DOMAINS = {"reddit.com", "x.com", "twitter.com", "tiktok.com"}
X_DOMAINS = ["x.com", "twitter.com"]


def parse_args(argv):
    days = 30
    rest = []
    for a in argv[1:]:
        if a.startswith("--days="):
            try:
                days = max(1, int(a.split("=", 1)[1]))
            except ValueError:
                pass
        else:
            rest.append(a)
    return days, rest


def _time_range(days):
    if days <= 1:
        return "day"
    if days <= 7:
        return "week"
    if days <= 31:
        return "month"
    if days <= 365:
        return "year"
    return None


def source_name(url):
    try:
        return urllib.parse.urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url


# ---- Providers --------------------------------------------------------------
# Each returns a list[dict] (possibly empty) on success, or None on a hard error
# so the caller can fail over to the next provider.

def tavily_search(query, days, query_type, key):
    is_x = query_type == "XFALLBACK"
    is_news = query_type == "NEWS"
    body = {
        "query": query,
        "topic": "news" if is_news else "general",
        "search_depth": "basic",
        "max_results": 5,
        "include_raw_content": True,
    }
    if is_news:
        body["days"] = days
    else:
        tr = _time_range(days)
        if tr:
            body["time_range"] = tr
    if is_x:
        body["include_domains"] = X_DOMAINS
    else:
        body["exclude_domains"] = sorted(SKIP_DOMAINS)
    try:
        r = requests.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {key}"},
            json=body, timeout=20,
        )
        r.raise_for_status()
        out = []
        for x in r.json().get("results", []):
            u = x.get("url", "")
            if not u:
                continue
            content = x.get("content", "") or ""
            raw = x.get("raw_content") or content
            out.append({
                "title": x.get("title", ""),
                "source": source_name(u),
                "url": u,
                "snippet": content[:300],
                "text": (raw or "")[:1500],
            })
        return out
    except Exception as e:
        print(f"[web] Tavily error: {e}", file=sys.stderr)
        return None


def exa_search(query, days, query_type, key):
    is_x = query_type == "XFALLBACK"
    end = datetime.now(UTC)
    start = end - timedelta(days=days)
    body = {
        "query": query,
        "type": "auto",
        "numResults": 5,
        "startPublishedDate": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "endPublishedDate": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "contents": {"text": True},
    }
    if is_x:
        body["includeDomains"] = X_DOMAINS
    else:
        body["excludeDomains"] = sorted(SKIP_DOMAINS)
    try:
        r = requests.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": key, "Content-Type": "application/json"},
            json=body, timeout=20,
        )
        r.raise_for_status()
        out = []
        for x in r.json().get("results", []):
            u = x.get("url", "")
            if not u:
                continue
            text = (x.get("text") or "")
            out.append({
                "title": x.get("title", ""),
                "source": source_name(u),
                "url": u,
                "snippet": text[:300],
                "text": text[:1500],
            })
        return out
    except Exception as e:
        print(f"[web] Exa error: {e}", file=sys.stderr)
        return None


def _resolve_ddg(href):
    """DuckDuckGo HTML results wrap the real URL in /l/?uddg=<encoded>. Unwrap it."""
    if href.startswith("//"):
        href = "https:" + href
    parsed = urllib.parse.urlparse(href)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        qs = urllib.parse.parse_qs(parsed.query)
        if "uddg" in qs:
            return urllib.parse.unquote(qs["uddg"][0])
    return href


def _fetch_page_text(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in ["article", "main", "[role='main']"]:
            el = soup.select_one(tag)
            if el:
                return el.get_text(separator=" ", strip=True)[:1500]
        return soup.get_text(separator=" ", strip=True)[:1500]
    except Exception:
        return ""


def ddg_search(query, days, query_type, _key=None):
    is_x = query_type == "XFALLBACK"
    skip = set() if is_x else SKIP_DOMAINS
    q = ("site:x.com OR site:twitter.com " + query) if is_x else query
    try:
        r = requests.get(
            f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}",
            headers=HEADERS, timeout=15,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        out = []
        for a in soup.select("a.result__a")[:8]:
            href = _resolve_ddg(a.get("href", ""))
            if not href or any(d in href for d in skip):
                continue
            sib = a.find_parent().find_next_sibling()
            snippet = sib.get_text(strip=True)[:200] if sib else ""
            out.append({
                "title": a.get_text(strip=True),
                "source": source_name(href),
                "url": href,
                "snippet": snippet,
                "text": "",
            })
        # DDG gives no body text — fetch the top few.
        for item in out[:5]:
            item["text"] = _fetch_page_text(item["url"])
            time.sleep(0.4)
        return out
    except Exception as e:
        print(f"[web] DDG error: {e}", file=sys.stderr)
        return None


def select_providers():
    """Ordered (name, fn, key) by precedence; only those usable in this env."""
    _env.load()
    chain = []
    tav = os.environ.get("TAVILY_API_KEY")
    exa = os.environ.get("EXA_API_KEY")
    if tav:
        chain.append(("Tavily", tavily_search, tav))
    if exa:
        chain.append(("Exa", exa_search, exa))
    chain.append(("DuckDuckGo", ddg_search, None))
    return chain


def main():
    days, rest = parse_args(sys.argv)
    if not rest:
        print("Usage: web.py <topic> [QUERY_TYPE] [--days=N]", file=sys.stderr)
        sys.exit(1)

    topic = rest[0]
    query_type = rest[1] if len(rest) > 1 else "GENERAL"
    templates = QUERY_TEMPLATES.get(query_type, QUERY_TEMPLATES["GENERAL"])
    queries = [t.format(topic=topic) for t in templates]

    for name, fn, key in select_providers():
        seen, results, hard_error = set(), [], False
        for q in queries:
            hits = fn(q, days, query_type, key)
            if hits is None:        # hard error -> try next provider
                hard_error = True
                break
            for h in hits:
                if h["url"] not in seen:
                    seen.add(h["url"])
                    results.append(h)
        if hard_error:
            continue
        print(f"[web] provider={name} results={len(results)}", file=sys.stderr)
        print(json.dumps(results[:5], indent=2))
        return

    # Every provider hard-errored.
    print("[web] all providers failed", file=sys.stderr)
    print(json.dumps([]))


if __name__ == "__main__":
    main()
