# Scraping large datasets

Loaded on demand by `SKILL.md` (spec A1). The golden rule: **don't
scroll-and-scrape the DOM** for big datasets — intercept the network requests
the page itself makes, or call the API it calls. It's faster, more complete,
and far less brittle.

## Decision order

1. **Is there an API the page calls?** Open the page, watch network traffic,
   and replay/iterate that endpoint. Best option by far.
2. **Server-rendered HTML?** Extract with locators / `visible_text`, paginate
   by URL.
3. **Infinite scroll with no clean API?** Scroll in a loop, de-dupe, stop on
   no-new-items. Last resort.

## 1. Intercept the page's own network calls

Attach a response handler before navigating, collect the JSON the page
fetches:

```python
from scripts.browser import launch, wait_for_load

rows = []
with launch(headless=True) as (ctx, page):
    def on_response(resp):
        if "/api/items" in resp.url and resp.ok:
            try:
                rows.extend(resp.json().get("items", []))
            except Exception:
                pass
    page.on("response", on_response)
    page.goto("https://example.com/catalog")
    wait_for_load(page)

print(len(rows), "rows")
```

Find the right URL substring first by logging every XHR/fetch:

```python
page.on("response", lambda r: print(r.status, r.request.resource_type, r.url))
```

Look for `resource_type` of `xhr`/`fetch` returning JSON.

## 2. Replay the API directly (fastest)

Once you know the endpoint and it doesn't need browser-only auth, call it
straight from Playwright's request context (carries the profile's cookies):

```python
with launch(headless=True) as (ctx, page):
    page.goto("https://example.com")          # establish session/cookies
    all_items = []
    for pg in range(1, 11):
        r = ctx.request.get(f"https://example.com/api/items?page={pg}")
        if not r.ok:
            break
        batch = r.json().get("items", [])
        if not batch:
            break
        all_items.extend(batch)
```

`ctx.request` reuses the persistent profile's cookies, so authenticated
endpoints work once you've logged in.

## 3. Pagination by URL (server-rendered)

```python
from scripts.browser import launch, wait_for_load

results = []
with launch(headless=True) as (ctx, page):
    pg = 1
    while True:
        page.goto(f"https://example.com/list?page={pg}")
        wait_for_load(page)
        titles = page.locator(".item h2").all_inner_texts()
        if not titles:
            break
        results.extend(titles)
        pg += 1
        if pg > 100:                # always bound the loop
            break
```

## 4. Infinite scroll (last resort)

```python
seen = set()
with launch(headless=True) as (ctx, page):
    page.goto("https://example.com/feed")
    wait_for_load(page)
    stagnant = 0
    while stagnant < 3:                       # stop after 3 no-growth rounds
        before = len(seen)
        for t in page.locator(".card").all_inner_texts():
            seen.add(t)
        page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        stagnant = stagnant + 1 if len(seen) == before else 0
```

## Etiquette & honesty

- **Respect the site.** Check `robots.txt` and terms; rate-limit loops; don't
  hammer. Bound every loop (a max page/iteration count) so a script never runs
  away.
- **Disclose gaps (spec A12).** If interception missed some rows or a loop hit
  its cap, say so in the result — don't present a partial scrape as complete.
- **Prefer the API the page already uses** over scraping rendered HTML — it's
  the difference between reading structured data and reverse-engineering a
  layout.
