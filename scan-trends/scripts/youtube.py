#!/usr/bin/env python3
"""
YouTube source — uses Playwright headless Chromium.
Usage: python3 youtube.py "<topic>" [--days=N]   (N defaults to 30)
Output: JSON array of videos with title, channel, views, transcript snippet
"""
import sys, os, json, urllib.parse, time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# Resolve a Chromium binary: explicit override, then the sandbox's pinned build,
# else None so Playwright falls back to its own bundled Chromium.
_SANDBOX_CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
_OVERRIDE = os.environ.get("PW_CHROMIUM_PATH")
if _OVERRIDE and os.path.exists(_OVERRIDE):
    BROWSER_PATH = _OVERRIDE
elif os.path.exists(_SANDBOX_CHROMIUM):
    BROWSER_PATH = _SANDBOX_CHROMIUM
else:
    BROWSER_PATH = None

# YouTube upload-date filter tokens (sp param), double URL-encoded for the == padding.
_SP_TODAY = "EgIIAg%253D%253D"
_SP_WEEK = "EgIIAw%253D%253D"
_SP_MONTH = "EgIIBA%253D%253D"
_SP_YEAR = "EgIIBQ%253D%253D"


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


def upload_filter(days):
    """Map a day window to YouTube's coarsest covering upload-date filter."""
    if days <= 1:
        return _SP_TODAY
    if days <= 7:
        return _SP_WEEK
    if days <= 31:
        return _SP_MONTH
    if days <= 365:
        return _SP_YEAR
    return ""  # no filter — all time


def get_transcript(page, video_url):
    try:
        page.goto(video_url, wait_until="domcontentloaded", timeout=20000)
        # Click "More actions" to find transcript option
        page.click("button[aria-label='More actions']", timeout=5000)
        page.wait_for_timeout(500)
        # Look for "Show transcript" in the menu
        transcript_btn = page.locator("text=Show transcript").first
        transcript_btn.click(timeout=3000)
        page.wait_for_selector("ytd-transcript-segment-renderer", timeout=8000)
        segments = page.locator("ytd-transcript-segment-renderer").all()[:30]
        text = " ".join(s.inner_text() for s in segments)
        return text[:800]
    except Exception:
        return ""


def main():
    days, rest = parse_args(sys.argv)
    if not rest:
        print("Usage: youtube.py <topic> [--days=N]", file=sys.stderr)
        sys.exit(1)

    topic = rest[0]
    encoded = urllib.parse.quote(topic)
    sp = upload_filter(days)
    search_url = f"https://www.youtube.com/results?search_query={encoded}"
    if sp:
        search_url += f"&sp={sp}"

    results = []

    launch_kwargs = dict(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox"],
    )
    if BROWSER_PATH:
        launch_kwargs["executable_path"] = BROWSER_PATH

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        try:
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector("ytd-video-renderer", timeout=15000)
        except PWTimeout:
            print("[youtube] timeout loading search results", file=sys.stderr)
            browser.close()
            print(json.dumps([]))
            return

        renderers = page.locator("ytd-video-renderer").all()[:10]
        for renderer in renderers:
            try:
                title_el = renderer.locator("#video-title").first
                title = title_el.inner_text(timeout=2000).strip()
                url = "https://www.youtube.com" + title_el.get_attribute("href", timeout=2000)
                channel = renderer.locator("#channel-name").first.inner_text(timeout=2000).strip()
                views = renderer.locator("#metadata-line span").first.inner_text(timeout=2000).strip()
                results.append({"title": title, "channel": channel, "views": views,
                                 "url": url, "transcript": ""})
            except Exception:
                continue

        # Fetch transcripts for top 3
        for video in results[:3]:
            video["transcript"] = get_transcript(page, video["url"])
            time.sleep(1)

        browser.close()

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
