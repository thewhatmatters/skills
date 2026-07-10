# audit-ui

**What it is:** A pre-ship quality audit for web UI — accessibility, responsive visuals, Core Web Vitals, and design-token drift — reported as severity-grouped findings with concrete fixes.

## What you get

- A markdown findings report (`ui-audit-<date>.md`) grouped 🔴/🟠/🟡, every finding with evidence (selector, screenshot, metric, or `file:line`) and a fix.
- Full-page screenshots of your pages at 375 / 768 / 1280 / 1920px, reviewed for overflow, breakage, and wrapping.
- An honest coverage statement — which dimensions ran, which degraded, and what an automated pass can't claim (full WCAG conformance, field INP).

## How to run

Say "audit the UI", "a11y check this app", "visual QA before ship", "are we hitting Core Web Vitals", "find hard-coded colors" — or directly:

```
/audit-ui --url=http://localhost:3000 --dims=a11y,visual,tokens
```

## What it needs

- A **running dev server** for the live dimensions (it will never start one for you).
- Python 3 + Playwright (`pip install playwright && python3 -m playwright install chromium`) for a11y and visual; Node/npx for the vitals dimension (Lighthouse runs via npx on demand).
- A `DESIGN.md` at the project root for token-drift auditing — without one, the tokens dimension reports internal consistency instead and points you at the `design-md` skill.
- No API keys. axe-core is fetched once from a CDN and cached locally.

## How it works (high level)

1. Preflight checks each dimension's dependencies and shows a readiness board; you pick which dimensions to run.
2. Scripts gather the raw facts: axe-core violations via Playwright, breakpoint screenshots, Lighthouse lab metrics vs budgets, color/font literals vs your DESIGN.md tokens.
3. Claude adds the judgment layer the tools can't — label quality, focus order, screenshot review, drift clustering.
4. Findings are classified by severity and written to the report. The skill never edits your code — fixing is `build-ui`'s job, offered at the end.

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
- `references/` — per-dimension audit method: `a11y-audit.md`, `visual-review.md`, `vitals.md`, `token-drift.md`.
