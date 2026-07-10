#!/usr/bin/env python3
"""
X/Twitter source — authenticated scrape of X search.

X requires auth for search. Two ways to authenticate, in precedence order:

  1. COOKIE injection (preferred) — set X_AUTH_TOKEN and X_CT0 in the shared
     .env (loaded by _env.py). Copy them from a browser already logged into
     x.com: DevTools → Application/Storage → Cookies → x.com → `auth_token`
     and `ct0`. No login flow runs, so there is nothing for X to block.
  2. PERSISTENT profile — `python3 x.py --login` opens a browser once; the
     session is saved to ~/.scan-trends/x-profile (override X_PROFILE_DIR).

Normal use:  python3 x.py "<topic>" [--days=N]   (N defaults to 30)

The lookback window is honored via X's native `since:` search operator.
No valid auth → prints [] and a NO_SESSION note on stderr; the skill then
falls back to a web `site:x.com` search (see SKILL.md).

Output: JSON array of posts with text, author, engagement, timestamp, url
"""
import sys, os, json, re, urllib.parse, datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _env  # noqa: E402

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

PROFILE_DIR = os.environ.get("X_PROFILE_DIR") or os.path.expanduser(
    "~/.scan-trends/x-profile"
)
HEADFUL = os.environ.get("X_HEADFUL") == "1"

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def parse_args(argv):
    """Pull --days=N and the --login flag out of argv; return (days, login, [pos])."""
    days = 30
    login = False
    rest = []
    for a in argv[1:]:
        if a == "--login":
            login = True
        elif a.startswith("--days="):
            try:
                days = max(1, int(a.split("=", 1)[1]))
            except ValueError:
                pass
        else:
            rest.append(a)
    return days, login, rest


def x_cookies():
    """(auth_token, ct0) from the shared .env, or None if not both present."""
    _env.load()
    a = (os.environ.get("X_AUTH_TOKEN") or "").strip()
    c = (os.environ.get("X_CT0") or "").strip()
    return (a, c) if a and c else None


def _cookie_objs(auth, ct0):
    base = {"domain": ".x.com", "path": "/", "secure": True}
    return [
        {**base, "name": "auth_token", "value": auth,
         "httpOnly": True, "sameSite": "None"},
        {**base, "name": "ct0", "value": ct0,
         "httpOnly": False, "sameSite": "Lax"},
    ]


def _launch_persistent(p, headless):
    kwargs = dict(
        headless=headless,
        args=["--no-sandbox", "--disable-setuid-sandbox"],
        user_agent=_UA,
        viewport={"width": 1280, "height": 1000},
    )
    if BROWSER_PATH:
        kwargs["executable_path"] = BROWSER_PATH
    os.makedirs(PROFILE_DIR, exist_ok=True)
    return p.chromium.launch_persistent_context(PROFILE_DIR, **kwargs)


def make_context(p, headless):
    """Return (context, browser_or_None). Cookie mode if X_AUTH_TOKEN/X_CT0 set,
    else the persistent logged-in profile."""
    cookies = x_cookies()
    if cookies:
        lk = dict(headless=headless,
                  args=["--no-sandbox", "--disable-setuid-sandbox"])
        if BROWSER_PATH:
            lk["executable_path"] = BROWSER_PATH
        browser = p.chromium.launch(**lk)
        ctx = browser.new_context(user_agent=_UA,
                                  viewport={"width": 1280, "height": 1000})
        ctx.add_cookies(_cookie_objs(*cookies))
        return ctx, browser
    return _launch_persistent(p, headless), None


def do_login():
    """Interactive one-time login into the persistent profile (fallback path)."""
    with sync_playwright() as p:
        ctx = _launch_persistent(p, headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://x.com/login", wait_until="domcontentloaded", timeout=60000)
        print("[x] A browser window is open. Log into X. Waiting up to 5 min for "
              "login to complete (this window closes itself once you're in)...",
              file=sys.stderr)
        try:
            page.wait_for_selector(
                '[data-testid="SideNav_AccountSwitcher_Button"]', timeout=300000
            )
            print(f"[x] Login detected — session saved to {PROFILE_DIR}",
                  file=sys.stderr)
        except PWTimeout:
            print("[x] Timed out waiting for login. Re-run `x.py --login`.",
                  file=sys.stderr)
        ctx.close()


def _looks_logged_out(page):
    if re.search(r"/(login|i/flow/login)", page.url):
        return True
    for sel in ('input[autocomplete="username"]',
                '[data-testid="loginButton"]',
                '[data-testid="login"]'):
        try:
            if page.locator(sel).first.is_visible(timeout=1500):
                return True
        except Exception:
            pass
    return False


def _count(article, testid):
    """Read a reply/retweet/like count from its button aria-label, e.g. '12 Likes'."""
    try:
        el = article.locator(f'[data-testid="{testid}"]').first
        label = el.get_attribute("aria-label", timeout=1000) or ""
        m = re.search(r"[\d,.]+\s*[KMB]?", label)
        return m.group(0).replace(" ", "") if m else "0"
    except Exception:
        return "0"


def scrape(topic, days):
    cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days)
    q = f"{topic} since:{cutoff.strftime('%Y-%m-%d')}"
    url = ("https://x.com/search?q=" + urllib.parse.quote(q)
           + "&src=typed_query&f=live")

    results = []
    seen = set()

    with sync_playwright() as p:
        ctx, browser = make_context(p, headless=not HEADFUL)

        def _shut():
            try:
                ctx.close()
            except Exception:
                pass
            if browser:
                try:
                    browser.close()
                except Exception:
                    pass

        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except PWTimeout:
                return "TIMEOUT"  # transient — plain skip, NOT a setup gate

            try:
                page.wait_for_selector('article[data-testid="tweet"]',
                                       timeout=12000)
            except PWTimeout:
                if _looks_logged_out(page):
                    return "NO_SESSION"  # unambiguous: triggers the auth gate
                return []  # authenticated but genuinely no posts

            for _ in range(8):
                for art in page.locator('article[data-testid="tweet"]').all():
                    try:
                        link = art.locator('a[href*="/status/"]').first
                        href = link.get_attribute("href", timeout=1000) or ""
                        m = re.match(r"/([^/]+)/status/(\d+)", href)
                        if not m:
                            continue
                        handle, sid = m.group(1), m.group(2)
                        if sid in seen:
                            continue
                        seen.add(sid)
                        try:
                            text = art.locator(
                                '[data-testid="tweetText"]'
                            ).first.inner_text(timeout=1500).strip()
                        except Exception:
                            text = ""
                        try:
                            ts = art.locator("time").first.get_attribute(
                                "datetime", timeout=1000)
                        except Exception:
                            ts = ""
                        results.append({
                            "text": text[:500],
                            "author": f"@{handle}",
                            "likes": _count(art, "like"),
                            "reposts": _count(art, "retweet"),
                            "replies": _count(art, "reply"),
                            "timestamp": ts or "",
                            "url": f"https://x.com{href}",
                        })
                    except Exception:
                        continue
                if len(results) >= 40:
                    break
                page.mouse.wheel(0, 4000)
                page.wait_for_timeout(1500)
        finally:
            _shut()
    return results[:40]


def main():
    days, login, rest = parse_args(sys.argv)

    if login:
        do_login()
        return

    if not rest:
        print("Usage: x.py <topic> [--days=N] | x.py --login", file=sys.stderr)
        sys.exit(1)

    data = scrape(rest[0], days)
    if data == "NO_SESSION":
        # Unambiguous setup-gap marker — the skill's Recoverable Setup Gate keys
        # on the literal token "NO_SESSION" on stderr.
        how = ("cookies invalid/expired — refresh X_AUTH_TOKEN/X_CT0"
               if x_cookies() else
               "no auth — add X_AUTH_TOKEN and X_CT0 to ~/.claude/skills/.env "
               "(copy from a logged-in x.com browser via DevTools → Cookies), "
               "or run `python3 scripts/x.py --login`")
        print(f"[x] NO_SESSION — {how}.", file=sys.stderr)
        print(json.dumps([]))
        return
    if data == "TIMEOUT" or data is None:
        # Transient failure — plain skip, do NOT print NO_SESSION (no gate).
        print("[x] TIMEOUT — could not load X search (transient). Skipping.",
              file=sys.stderr)
        print(json.dumps([]))
        return

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
