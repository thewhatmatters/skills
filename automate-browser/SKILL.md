---
name: automate-browser
description: Browser automation with a persistent login profile. Use when the user wants to navigate websites, fill forms, click through flows, take screenshots, extract or scrape web data, or test/debug a web app. Trigger phrases include "go to [url]", "click on", "fill out the form", "log into", "take a screenshot", "scrape", "extract data from", "automate this site", "test the website", "check my dashboard", or any request that needs a real browser driving a page (not just fetching HTML). Drives Chromium via Playwright with cookies/sessions that persist across runs; falls back to read-only WebFetch when Playwright isn't installed.
---

# automate-browser

Drive a real Chromium browser via Playwright, with a **persistent profile** so
logins/cookies survive across runs. Work the way the original Amp skill taught:
write **small, focused scripts**, observe state, decide the next step, repeat.

Detailed API and scraping guidance live in `references/` (loaded on demand,
spec A1):
- [`references/browser-api.md`](references/browser-api.md) — the `browser.py`
  library + the Playwright Page API you'll use most.
- [`references/scraping.md`](references/scraping.md) — large-dataset scraping
  via network interception (don't scroll the DOM).

## Step 0 — Mode probe

Run `python3 scripts/preflight.py`. Read the JSON:

- `playwright` + `browsers` **ready** → **SCRIPTS** mode (full automation:
  navigate, click, fill, extract, screenshot).
- either **gated** (`PLAYWRIGHT_MISSING` / `BROWSERS_MISSING`) → see Step 1.
- `workspace` **down** → STOP; the profile/out dir isn't writable.

If `python3` itself is unavailable → **NATIVE** mode: you can only *read*
pages via Claude's built-in `WebFetch` (no clicking/filling/JS). Say so.

## Step 1 — Setup gate (recoverable, never blocks — spec A7)

On `PLAYWRIGHT_MISSING` or `BROWSERS_MISSING`:

- **Interactive:** offer *Install it / I'll do it myself / Use NATIVE read-only*.
  The install is one or two lines:
  ```bash
  pip install playwright
  python3 -m playwright install chromium   # browsers are often already cached
  ```
- **`--agent`:** don't prompt — fall back to NATIVE read-only and note it in
  the summary.
- **Graceful dead-end (A7d):** NATIVE read-only always works for fetching a
  page's content; only interaction needs the SCRIPTS path. The gate never
  blocks.

## Persistence model (important — differs from the original)

Sessions/cookies/localStorage persist across runs via a persistent profile at
`<skill>/.cache/profile` (gitignored). There is **no long-running server**, so
a *live page* does not survive between separate processes. Implications:

- Log in **once**; later runs are already authenticated → re-`goto` is cheap.
- A multi-step interaction on one live page must happen inside **one script**.
- This is a deliberate simplification over the Amp skill's server (simpler,
  more robust; see `handoff.md`).

## Operating: the small-scripts loop

1. Write a script that performs ONE action (navigate, discover, click, fill).
2. Run it; observe the JSON / printed state.
3. Decide: done, or another step?
4. Repeat.

**One-shot (CLI)** — navigate + discover what's on the page:

```bash
cd ~/.claude/skills/automate-browser && python3 scripts/browser.py \
  goto "https://example.com" --mode interactive
```

Modes: `interactive` (clickable elements + landmarks — best for discovery),
`text` (visible text), `outline` (DOM structure), `aria` (accessibility tree),
`none`. Add `--screenshot tmp/page.png`, `--headless`, `--selector CSS`
(scopes any extract mode to that element), `--limit N` (truncates `text`
output only).

**Multi-step (inline library script)** — interaction on one live page:

```bash
cd ~/.claude/skills/automate-browser && python3 <<'EOF'
from scripts.browser import launch, wait_for_load, interactive_outline

with launch(headless=False) as (ctx, page):
    page.goto("https://news.ycombinator.com")
    wait_for_load(page)
    print(interactive_outline(page))          # discover elements
    page.get_by_role("link", name="new").click()   # standard Playwright locator
    wait_for_load(page)
    print({"url": page.url, "title": page.title()})
EOF
```

## Discovering & interacting

1. **Discover** with `interactive_outline(page)` — a token-efficient list of
   clickable elements + landmarks (far cheaper than a screenshot).
2. **Act** with standard Playwright locators — `page.get_by_role(...)`,
   `page.get_by_text(...)`, `page.locator("css")`. (We use real locators
   rather than the original's custom snapshot refs — more robust; see
   `handoff.md`.)
3. **Verify** by printing `page.url` / `page.title()` or re-extracting.

`page` is a standard Playwright `Page` — full API in
[`references/browser-api.md`](references/browser-api.md).

## Screenshots

```python
page.screenshot(path="tmp/page.png", full_page=True)
```

Prefer `interactive_outline` / `text` extraction over screenshots when you
just need to *understand* a page — screenshots cost vision tokens.

## Common pitfalls

- **Headed vs headless:** default is headed (visible) so you can watch. On a
  no-display server pass `--headless` / `launch(headless=True)`.
- **Re-`goto` after a fresh process:** the live page is gone between scripts,
  but your login isn't — just navigate again.
- **Bounded waits:** `wait_for_load(page)` settles the page but never hangs
  past the timeout. For specifics use `page.wait_for_selector(...)`.
- **Unsaved dialog state dies with the script:** when the script exits, the
  browser closes and anything staged in an open dialog/wizard (an unclicked
  Apply/Save) is discarded — only committed state persists. Always finish
  open → edit → **Apply → verify** inside one script.
- **Heavy SPAs amortize badly:** each script re-pays launch + full app load
  (a GA4/console-class SPA costs ~10s before the first action). Batch
  discover→act→verify into fewer, larger scripts instead of one action per run.

## Conventions this skill follows

- Dual-mode (A3): SCRIPTS = Playwright; NATIVE = read-only `WebFetch`.
- Setup-Gate (A7): `PLAYWRIGHT_MISSING` / `BROWSERS_MISSING` recoverable, never
  block; one-line install fix; `--agent` degrades to NATIVE.
- Scripts (A4): `browser.py` and `preflight.py` emit JSON on stdout,
  diagnostics on stderr, bounded waits, graceful failure.
- No unguarded paths (A11): browser cache + profile resolved per-OS with an
  env override; no hard-coded external install path.
- No secrets: browser automation needs none here; no `_env.py`.
- Self-contained: everything lives under `~/.claude/skills/automate-browser/`.
