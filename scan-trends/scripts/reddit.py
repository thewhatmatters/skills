#!/usr/bin/env python3
"""
Reddit source — fetches top posts and top comments for a topic over a configurable window.
Usage: python3 reddit.py "<topic>" [--days=N]   (N defaults to 30)
Output: JSON array of posts with top_comments
"""
import sys, json, time, urllib.parse, datetime
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (research-bot/1.0)"}


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


def reddit_time_filter(days):
    """Map a day window to Reddit's coarse `t` param (we still client-filter for precision)."""
    if days <= 1:
        return "day"
    if days <= 7:
        return "week"
    if days <= 31:
        return "month"
    if days <= 365:
        return "year"
    return "all"


def fetch_json(url, retries=2, delay=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 429:
                if attempt < retries - 1:
                    time.sleep(delay)
                    continue
                # marker the caller/model can see — a rate limit must be
                # distinguishable from a genuinely empty result so the
                # documented web.py fallback can fire
                print("[reddit] 429 rate limited — retries exhausted",
                      file=sys.stderr)
                return None
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == retries - 1:
                print(f"[reddit] fetch error: {e}", file=sys.stderr)
                return None
            time.sleep(delay)


def main():
    days, rest = parse_args(sys.argv)
    if not rest:
        print("Usage: reddit.py <topic> [--days=N]", file=sys.stderr)
        sys.exit(1)

    topic = rest[0]
    cutoff = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(days=days)
    query = urllib.parse.quote(topic)
    results = []

    t = reddit_time_filter(days)
    url = f"https://www.reddit.com/search.json?q={query}&sort=top&t={t}&limit=25"
    data = fetch_json(url)
    if not data:
        print(json.dumps([]))
        return

    posts = data.get("data", {}).get("children", [])
    for post in posts:
        p = post["data"]
        created = datetime.datetime.fromtimestamp(p["created_utc"], datetime.UTC).replace(tzinfo=None)
        if created < cutoff:
            continue
        results.append({
            "title": p["title"],
            "subreddit": p["subreddit"],
            "score": p["score"],
            "comments": p["num_comments"],
            "url": f"https://reddit.com{p['permalink']}",
            "text": p.get("selftext", "")[:400],
            "top_comments": []
        })

    # Enrich top 5 posts with top comments
    top5 = sorted(results, key=lambda x: x["score"], reverse=True)[:5]
    for post in top5:
        thread_url = post["url"] + ".json?limit=10&sort=top"
        thread = fetch_json(thread_url)
        if thread and len(thread) > 1:
            children = thread[1]["data"]["children"][:3]
            post["top_comments"] = [
                {"body": c["data"]["body"][:300], "score": c["data"]["score"]}
                for c in children if c.get("kind") == "t1"
            ]
        time.sleep(1)  # be polite

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
