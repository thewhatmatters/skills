#!/usr/bin/env python3
"""
Polymarket source — fetches prediction markets matching a topic.
Usage: python3 polymarket.py "<topic>" [--days=N]   (N defaults to 30)
Note: Polymarket has no created-date filter that maps to a lookback window, so
--days is accepted for interface consistency but does not constrain results
(only currently-active markets are returned).
Output: JSON array of markets with odds and volume
"""
import sys, json, urllib.parse
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


def parse_prices(raw):
    """gamma-api returns outcomePrices as a JSON-encoded string, not a list."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (ValueError, TypeError):
            return []
    return raw if isinstance(raw, list) else []


def main():
    days, rest = parse_args(sys.argv)
    if not rest:
        print("Usage: polymarket.py <topic> [--days=N]", file=sys.stderr)
        sys.exit(1)

    query = urllib.parse.quote(rest[0])
    url = f"https://gamma-api.polymarket.com/markets?search={query}&active=true&limit=10"

    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        markets = r.json()
    except Exception as e:
        print(f"[polymarket] error: {e}", file=sys.stderr)
        print(json.dumps([]))
        return

    if not isinstance(markets, list):
        markets = markets.get("data", []) if isinstance(markets, dict) else []

    results = []
    for m in markets:
        prices = parse_prices(m.get("outcomePrices", []))
        results.append({
            "question": m.get("question", ""),
            "yes_odds": prices[0] if prices else None,
            "no_odds": prices[1] if len(prices) > 1 else None,
            "volume": m.get("volume"),
            "end_date": m.get("endDate", ""),
            "url": f"https://polymarket.com/event/{m.get('slug', '')}"
        })

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
