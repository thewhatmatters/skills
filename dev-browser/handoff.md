# dev-browser — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Rewritten: 2026-05-19  ·  Generator: generate-skill @ CC 2.1.145

## 1. Purpose
Drive a real Chromium browser via Playwright with a persistent login profile —
navigate, click, fill, extract, scrape, screenshot — through small, focused
scripts in a discover→act→verify loop.

## 2. Why this is a rewrite (what the original was)
The previous `dev-browser` here was the **Amp** coding-agent skill: a thin
SKILL.md pointing at a Node/TypeScript + Playwright implementation under
`~/.config/amp/skills/dev-browser/` (a long-running server holding live page
state, a `client.js` API, custom token-efficient extraction).

Two problems motivated the rewrite:
1. **Broken here.** `~/.config/amp/skills/dev-browser/` does not exist on this
   machine, so the original SKILL.md's `server.sh` / `npm` paths can't run.
2. **Spec gaps.** Hard-coded external install path (violates A11); no
   preflight (A6), no dual-mode/NATIVE fallback (A3), no setup gate (A7), no
   README (A13), no handoff.

## 3. Design decisions (the "why")

- **Python + Playwright, not Node.** Matches the house Python convention
  (`preflight.py`, JSON-stdout scripts). The environment already has Chromium
  cached in `~/Library/Caches/ms-playwright`, which Python Playwright shares,
  so the only setup step is `pip install playwright`.
- **Persistent context, not a long-running server.** The original kept a
  server alive so a *live page* survived between script runs. We use
  `launch_persistent_context(user_data_dir=…)` instead: cookies/sessions
  persist across runs, but the live page does not (each process opens/closes
  its own context). Trade-off accepted: far simpler and more robust; "log in
  once, re-`goto` later" covers the dominant use cases. A warm-page server is
  a possible future enhancement, not needed for v1.
- **Standard Playwright locators, not custom snapshot refs.** The original
  exposed `getAISnapshot()` + `selectSnapshotRef("e5")`. We provide
  `aria_snapshot()` for *reading* structure but interact via
  `get_by_role` / `get_by_text` / CSS locators — idiomatic Playwright, more
  robust, and no custom ref-resolution machinery to maintain.
- **Token-efficient extraction preserved (the real IP).** `interactive_outline`
  and `outline` are ported to Python via `page.evaluate` JS;
  `visible_text` uses Playwright's `inner_text`; `aria_snapshot` uses
  Playwright's built-in. These keep the original's cheap-discovery advantage
  over screenshots.
- **Dual-mode (A3) with an honest NATIVE path.** SCRIPTS = Playwright (full
  automation). NATIVE = read-only via Claude's built-in `WebFetch` — it can
  fetch/read a page but cannot click or fill. NATIVE is honestly labelled as
  read-only, not pretended to be equivalent.
- **Setup gates never block (A7d).** `PLAYWRIGHT_MISSING` /
  `BROWSERS_MISSING` are recoverable with a one-line install; if the user
  declines, NATIVE read-only is the automatic dead-end.
- **Headed by default.** It's a *dev* browser — you usually want to watch.
  `--headless` / `launch(headless=True)` for no-display servers.

## 4. Known limitations / environment caveats
- **Live-verified in this environment.** Playwright 1.57.0 is installed; a
  real `python3 scripts/browser.py goto https://example.com --mode
  interactive --headless` run succeeded — title "Example Domain", HTTP 200,
  and `interactive_outline` correctly extracted the page's link in ~1.6s.
  (An earlier `import playwright` probe misreported it as absent; the live
  run is the authoritative check — spec A12.) Not yet exercised against an
  auth-gated site or a heavy SPA; those are the next things to try.
- Live page state does not persist between processes (see §3).
- Headed mode needs a display; use `--headless` on servers/CI.
- The ported `interactive_outline` / `outline` JS are heuristic — good for
  discovery, not a guaranteed-complete DOM model. Fall back to `aria` mode or
  a screenshot when a page is unusual.

## 5. Audit rubric coverage
See `skill-architecture.md` §B. Items expected to be N/A for this skill:
- **A5 secrets / `_env`** — no API keys; browser automation needs none. N/A.
- **A8 multi-source scope picker** — single tool (one browser); the scope
  controls are the extraction `--mode`, `--headless`, `--selector` flags.
- **A10 self-contained artifact** — the output is the *effect* on the page
  plus optional screenshots / extracted JSON; there is no single report
  artifact (this is an interactive driver, not a report generator). Screens
  and extracted JSON are the artifacts.

## 6. Notes
Self-contained under `~/.claude/skills/dev-browser/`. Profile lives at
`.cache/profile` (gitignored). Browsers resolved from the shared ms-playwright
cache (per-OS path, `PLAYWRIGHT_BROWSERS_PATH` override). Composes naturally
with `/scan-trends` (which has its own authenticated-X browser path) and
`/deep-research` (which can hand off interactive fetches here).
