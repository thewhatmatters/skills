#!/usr/bin/env python3
"""Web search for deep-research — Tavily (primary) → Exa (fallback).

One concern: turn a query string into a normalized list of search results.
The skill's NATIVE mode (built-in WebSearch) covers the keyless case — this
script exists for SCRIPTS mode where Tavily/Exa keys give better ranking.

Keys are loaded via the shared `_env.py` convention (spec A5):
  TAVILY_API_KEY — sent in `Authorization: Bearer <key>` header.
  EXA_API_KEY    — sent in `x-api-key: <key>` header.
Neither key is ever logged or written to stdout (spec A5; scan-trends handoff §3).

USAGE
    python3 scripts/search.py "<query>" [--provider=tavily|exa|auto] \\
        [--n=10] [--agent]

    --provider  which provider to call (default `auto`: Tavily if key set,
                else Exa).
    --n         max results to return (default 10; capped at 25).
    --agent     non-interactive; never prompts (this script never prompts;
                flag is here for CLI consistency).

I/O CONTRACT
    stdin  : ignored
    stdout : a JSON array of result objects, sorted by score desc:
             [{"url", "title", "snippet", "score", "provider"}, ...]
    stderr : human diagnostics (which provider used, result count, timing)
    exit   : 0 on success;
             1 if no keys, the chosen provider fails AND fallback fails, or
             the query is empty.

NORMALIZED RESULT SHAPE
    {
      "url":      "https://...",
      "title":    "...",
      "snippet":  "...",         # short extract (1–2 sentences)
      "score":    0.0..1.0,      # provider-reported relevance (normalized)
      "provider": "tavily" | "exa"
    }
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import _env  # noqa: E402 - sibling module

TAVILY_URL = "https://api.tavily.com/search"
EXA_URL = "https://api.exa.ai/search"
HTTP_TIMEOUT = 15  # seconds; bounds total runtime, never hangs
MAX_N = 25


def log(msg):
    print(msg, file=sys.stderr)


def _requests():
    """Lazy import of `requests` so the script can at least show --help
    without it. scan-trends uses `requests` widely; certifi ships with it."""
    try:
        import requests  # noqa: PLC0415
        return requests
    except ImportError as e:
        raise SystemExit(
            "FATAL: `requests` not installed. deep-research relies on it "
            "(also used by scan-trends). Install: pip install requests."
        ) from e


def tavily_search(query, n):
    """Returns a list of normalized result dicts, or raises on failure."""
    requests = _requests()
    key = os.environ.get("TAVILY_API_KEY", "")
    if not key:
        raise RuntimeError("TAVILY_API_KEY not set")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "deep-research-search/1.0",
    }
    body = {
        "query": query,
        "max_results": n,
        "search_depth": "advanced",
        "include_answer": False,
    }
    r = requests.post(TAVILY_URL, headers=headers, json=body,
                      timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    out = []
    for item in (data.get("results") or [])[:n]:
        out.append({
            "url": item.get("url", ""),
            "title": item.get("title", ""),
            "snippet": (item.get("content") or "")[:500],
            "score": float(item.get("score", 0.0) or 0.0),
            "provider": "tavily",
        })
    return out


def exa_search(query, n):
    """Returns a list of normalized result dicts, or raises on failure."""
    requests = _requests()
    key = os.environ.get("EXA_API_KEY", "")
    if not key:
        raise RuntimeError("EXA_API_KEY not set")
    headers = {
        "x-api-key": key,
        "Content-Type": "application/json",
        "User-Agent": "deep-research-search/1.0",
    }
    body = {
        "query": query,
        "numResults": n,
        "type": "auto",  # let Exa choose between neural and keyword
        "contents": {"text": {"maxCharacters": 500}},
    }
    r = requests.post(EXA_URL, headers=headers, json=body,
                      timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    out = []
    for item in (data.get("results") or [])[:n]:
        text = (item.get("text") or "").strip()
        out.append({
            "url": item.get("url", ""),
            "title": item.get("title", ""),
            "snippet": text[:500],
            "score": float(item.get("score", 0.0) or 0.0),
            "provider": "exa",
        })
    return out


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("query", help="search query string")
    ap.add_argument("--provider", choices=("auto", "tavily", "exa"),
                    default="auto")
    ap.add_argument("--n", type=int, default=10,
                    help=f"max results (capped at {MAX_N})")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    if not args.query.strip():
        log("FATAL: empty query")
        sys.exit(1)

    n = max(1, min(args.n, MAX_N))
    _env.load()
    tav_set = bool(os.environ.get("TAVILY_API_KEY"))
    exa_set = bool(os.environ.get("EXA_API_KEY"))
    if not (tav_set or exa_set):
        log("FATAL: neither TAVILY_API_KEY nor EXA_API_KEY set — "
            "use NATIVE mode (Claude's built-in WebSearch) instead")
        sys.exit(1)

    # Provider resolution. `auto` prefers Tavily, falls back to Exa.
    order = []
    if args.provider == "tavily":
        order = ["tavily"]
    elif args.provider == "exa":
        order = ["exa"]
    else:  # auto
        if tav_set:
            order.append("tavily")
        if exa_set:
            order.append("exa")

    start = time.monotonic()
    results, used, errors = [], None, []
    for prov in order:
        fn = tavily_search if prov == "tavily" else exa_search
        try:
            results = fn(args.query, n)
            used = prov
            break
        except Exception as e:  # noqa: BLE001
            errors.append(f"{prov}: {e.__class__.__name__}: {e}")
            continue

    elapsed = time.monotonic() - start
    if not results:
        for e in errors:
            log(f"  FAIL  {e}")
        log("FATAL: no provider returned results")
        sys.exit(1)

    log(f"provider={used} results={len(results)} elapsed={elapsed:.1f}s")
    # Sort by score desc so consumers can take top-k easily.
    results.sort(key=lambda r: r["score"], reverse=True)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
