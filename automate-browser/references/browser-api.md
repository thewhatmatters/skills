# automate-browser API reference

Loaded on demand by `SKILL.md` (spec A1). Covers the `scripts/browser.py`
library and the slice of the Playwright Page API you'll use most.

## Table of contents
1. `browser.py` library
2. CLI (`goto`)
3. Extraction modes
4. Playwright Page API — navigation, interaction, content, waits, screenshots
5. Browser evaluation (JS in page)
6. Hostile DOM tactics (Angular Material / Google consoles)

---

## 1. `browser.py` library

Import in an inline script run from the skill dir
(`cd ~/.claude/skills/automate-browser`).

### `launch(headless=False, viewport=(1280, 800))`
Context manager. Yields `(ctx, page)` where `ctx` is a Playwright
`BrowserContext` on the persistent profile and `page` is its first page.
Closes the context on exit. Cookies/sessions persist across runs via the
profile dir; the live page does not persist between processes.

```python
from scripts.browser import launch, wait_for_load
with launch() as (ctx, page):
    page.goto("https://example.com")
    wait_for_load(page)
    print(page.title())
```

### `wait_for_load(page, timeout=20000)`
Best-effort settle: tries `networkidle`, falls back to `load`. Never hangs
past `timeout` (ms).

### `visible_text(page, selector=None, limit=None)`
Rendered visible text (hidden elements already excluded by Playwright's
`inner_text`). `selector` scopes it; `limit` truncates.

### `interactive_outline(page, selector=None)`
Token-efficient tree of **interactive elements + landmarks** — the best way
to discover what you can click/fill without spending vision tokens.

```
header
  a "Home" [href=/]
  a "Products" [href=/products]
main
  button "Add to Cart"
  input [type=text] "Search"
footer
  a "Contact" [href=/contact]
```

### `outline(page, max_depth=6, selector=None)`
DOM structure outline; collapses repeated siblings as `(×N)`. `selector`
scopes it to a subtree; a selector that matches nothing returns
`(selector not found: …)` rather than silently falling back to the page.

```
body
  header#main-header
    nav a "Home" a "Products"
  main
    div.product-list (×24)
```

### `aria_snapshot(page, selector="body")`
Playwright's accessibility-tree YAML for the subtree. Read-only — for
interaction use locators (next section), not snapshot refs.

---

## 2. CLI — `goto`

One self-contained process: navigate, optionally extract + screenshot.

```bash
python3 scripts/browser.py goto "<url>" \
  [--mode interactive|text|outline|aria|none] \
  [--selector CSS] [--limit N] [--screenshot PATH] [--headless] [--timeout MS]
```

Emits JSON: `{url, title, http_status, mode, extract?, screenshot?}`. Use it
for "open this and tell me what's here"; use the library for multi-step
interaction.

---

## 3. Extraction modes (cheapest → richest)

| Mode | Use case | Cost |
|------|----------|------|
| `interactive` | discover clickable elements + landmarks | ⭐⭐⭐ cheapest |
| `outline` | understand page structure | ⭐⭐ |
| `text` | extract readable content | ⭐⭐ |
| `aria` | read the accessibility tree | ⭐ |
| screenshot | actually *see* the page | vision tokens |

Default to `interactive` for discovery; reach for a screenshot only when you
genuinely need to see layout/visuals.

---

## 4. Playwright Page API

`page` is a standard Playwright `Page`. Most-used methods:

### Navigation
```python
page.goto("https://example.com")
page.go_back(); page.go_forward(); page.reload()
```

### Interaction (prefer role/text locators over brittle CSS)
```python
page.get_by_role("button", name="Submit").click()
page.get_by_role("link", name="Sign in").click()
page.get_by_text("Add to cart").click()
page.get_by_label("Email").fill("user@example.com")
page.locator("input[name='q']").fill("query"); page.keyboard.press("Enter")
page.get_by_role("combobox").select_option("US")
page.get_by_role("checkbox").check()
```

### Content
```python
page.title(); page.url
page.inner_text(".article")
page.locator(".price").all_inner_texts()
page.content()   # full HTML
```

### Waits (all bounded)
```python
page.wait_for_selector(".results")
page.wait_for_selector(".modal", state="hidden")
page.wait_for_url("**/success")
page.wait_for_load_state("networkidle")
page.wait_for_function("() => window.dataLoaded === true")
# add timeout=<ms> to any of the above
```

### Screenshots
```python
page.screenshot(path="tmp/page.png")
page.screenshot(path="tmp/full.png", full_page=True)
page.locator(".card").screenshot(path="tmp/card.png")
```

---

## 5. Browser evaluation (JS in the page)

`page.evaluate` runs **plain JavaScript in the browser** — no TypeScript, no
Python.

```python
data = page.evaluate("""() => ({
    scrollY: window.scrollY,
    links: Array.from(document.querySelectorAll('a')).map(a => a.href),
})""")

page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
```

For large datasets, don't scroll-and-scrape the DOM — intercept the network
requests the page itself makes. See [`scraping.md`](scraping.md).

---

## 6. Hostile DOM tactics (Angular Material / Google consoles)

Patterns for component-framework UIs (GA4, Google admin, Material/MDC apps)
where naive locators miss.

- **ALL-CAPS labels are usually CSS `text-transform`.** The DOM text may be
  ` Steps ` when you see "STEPS". Match case-insensitively; if `get_by_text`
  still misses, probe for the real element from JS:
  ```python
  page.evaluate("""() => [...document.querySelectorAll('*')]
      .filter(e => /^steps$/i.test(e.textContent?.trim()) && !e.children.length)
      .map(e => e.outerHTML.slice(0, 300))""")
  ```
- **Material radios/checkboxes ignore label clicks.** Clicking the label text
  often doesn't toggle the control. Click the control itself:
  `dlg.get_by_role("radio").nth(i).click(force=True)`. A still-disabled
  Save/Apply button is your signal the selection didn't register.
- **Read strict-mode violation errors — they're a map.** The error lists every
  matching candidate with its classes and ids (it can disclose a stable id
  like `#breakdown` you didn't know existed). Narrow to the real control
  (`button[aria-label='…']` beats a wrapper `div[role=button]`) or use the
  disclosed id.
- **Manual-login handoff:** launch headed, `goto` the target, then poll until
  the user signs in (run as a background task; the persistent profile keeps
  the session for every later run):
  ```python
  for _ in range(60):                      # up to 5 minutes
      page.wait_for_timeout(5000)
      if "accounts.google.com" not in page.url:
          break
  ```
