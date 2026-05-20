# automate-browser

**What it is:** a way for Claude to drive a real Chromium browser — navigate,
click, fill forms, log in, take screenshots, and extract or scrape data — with
your **login sessions remembered between runs**.

## What you get

- A browser Claude can operate step by step against any site.
- **Persistent logins:** sign in once; later runs are already authenticated.
- **Token-efficient page reading:** instead of burning vision tokens on
  screenshots, Claude can pull a compact list of the clickable elements, the
  visible text, or the page structure.
- Screenshots when you actually want to *see* the page.

## How to run it

Just ask, e.g.:

- "go to news.ycombinator.com and list the top stories"
- "log into my dashboard and screenshot the billing page"
- "fill out the contact form on example.com with these details"
- "scrape the product names and prices from this catalog"

## What it needs

- **`python3`** + the **`playwright`** package. If `playwright` isn't
  installed, Claude will offer to install it — one line:
  ```bash
  pip install playwright && python3 -m playwright install chromium
  ```
  (Chromium is often already cached, so the second step may be instant.)
- No API keys, no accounts, no external services.

If Playwright can't be set up, the skill **falls back to read-only mode** —
it can still fetch and read a page's content via Claude's built-in tools, it
just can't click or fill. It never hard-fails on a missing browser.

## How it works (high level)

1. **Preflight** checks that Playwright + Chromium are available and the
   workspace is writable; if not, it offers the one-line install or falls
   back to read-only.
2. **Persistent profile.** Chromium runs against a saved profile under
   `~/.claude/skills/automate-browser/.cache/profile`, so cookies and logins
   survive across runs. (This folder is never committed.)
3. **Small-scripts loop.** Claude writes a short script to do one thing
   (navigate, discover, click, fill), looks at the result, and decides the
   next step — repeating until the task is done.
4. **Discover then act.** Claude lists the page's interactive elements
   (cheap), then clicks/fills using real Playwright locators.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `references/browser-api.md` — the `browser.py` library + Playwright Page API.
- `references/scraping.md` — scraping large datasets via network interception.
- `handoff.md` — design decisions and how this differs from the original
  Amp dev-browser skill.
