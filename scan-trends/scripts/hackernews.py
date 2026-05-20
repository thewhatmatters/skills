#!/usr/bin/env python3
"""
Hacker News source — uses Algolia public API.
Usage: python3 hackernews.py "<topic>" [--days=N]   (N defaults to 30)
Output: JSON array of stories with top comments
"""
import sys, json, urllib.parse, datetime, time
import requests


def parse_args(argv):
    """Pull an optional --days=N out of argv; return (days, [positional args])."""
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


def fetch(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[hn] fetch error: {e}", file=sys.stderr)
        return None


def main():
    days, rest = parse_args(sys.argv)
    if not rest:
        print("Usage: hackernews.py <topic> [--days=N]", file=sys.stderr)
        sys.exit(1)

    cutoff_ts = int((datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(days=days)).timestamp())
    topic = urllib.parse.quote(rest[0])
    url = (
        f"https://hn.algolia.com/api/v1/search"
        f"?query={topic}&tags=story"
        f"&numericFilters=created_at_i>{cutoff_ts}"
        f"&hitsPerPage=20"
    )
    data = fetch(url)
    if not data:
        print(json.dumps([]))
        return

    results = []
    for hit in data.get("hits", []):
        entry = {
            "title": hit.get("title", ""),
            "points": hit.get("points", 0),
            "comments": hit.get("num_comments", 0),
            "url": hit.get("url", ""),
            "hn_url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
            "top_comments": []
        }
        if entry["points"] and entry["points"] > 30:
            thread = fetch(f"https://hn.algolia.com/api/v1/items/{hit['objectID']}")
            if thread:
                entry["top_comments"] = [
                    c["text"][:300]
                    for c in (thread.get("children") or [])[:3]
                    if c.get("text")
                ]
            time.sleep(0.5)
        results.append(entry)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
