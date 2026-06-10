---
name: audit-ui
description: Run a layered quality audit on a web app's UI — accessibility (axe-core via Playwright plus judgment checks), responsive visual review at breakpoints, Core Web Vitals lab budgets (Lighthouse), and design-token drift against the project's DESIGN.md. Use when the user wants a UI quality pass — "audit the UI", "a11y check this page/app", "check accessibility", "run an accessibility audit", "is this page accessible", "visual QA before ship", "check the responsive breakpoints", "are we hitting Core Web Vitals", "performance budget check", "find token drift / hard-coded colors", "pre-ship UI checklist". Live dimensions need a running dev-server URL; degrades to static source analysis (token drift + judgment a11y) when Playwright or the server is unavailable. Report-only — severity-grouped findings with evidence and concrete fixes; never edits. Hand the fixes to build-ui. Composes with automate-browser (shares the Playwright engine), design-md (produces the token spec), render-html (branded report). Do NOT use to audit a skill's architecture — that's audit-skill — or to implement/fix UI — that's build-ui.
---

# audit-ui

Audit a web UI across four dimensions — accessibility, responsive visuals, Core Web Vitals, token drift — and report severity-grouped findings. Report only; never fix unless asked (then hand to `build-ui`).

Per-dimension audit method lives in `references/` (spec A1), loaded only for the dimensions in scope:

- [`references/a11y-audit.md`](references/a11y-audit.md) — interpreting axe violations + the judgment checklist tools can't decide
- [`references/visual-review.md`](references/visual-review.md) — breakpoint set + what to look for in the screenshots
- [`references/vitals.md`](references/vitals.md) — lab-metric budgets, the INP honesty rule, finding→fix mapping
- [`references/token-drift.md`](references/token-drift.md) — DESIGN.md parsing (both flavors), what counts as drift, noise control

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses; run all available dimensions (spec A7b/A9) |
| `--url=URL` | page(s) to audit live (repeatable / comma-separated). No URL → preflight probes `http://localhost:3000`; if unreachable, live dimensions gate |
| `--project=PATH` | project root for static dimensions (default: cwd; walks up to `package.json`/`.git`) |
| `--dims=a,b,c` | run exactly these dimensions: `a11y`, `visual`, `vitals`, `tokens` (no picker) |
| `--out=PATH` | findings-report markdown location (default: `./ui-audit-<date>.md`, outside the skills repo) |
| `--breakpoints=N,N` | visual-dimension viewport widths (default: `375,768,1280,1920`) |
| `--no-network` | forbid the axe-core CDN fetch; a11y gates if no cached copy |

## Step 0 — Mode probe (spec A3)

Run `python3 --version`. python3 + `scripts/` present → **SCRIPTS**. Otherwise → **NATIVE**: only the static dimensions are available — do token drift by hand (grep hex/font literals against DESIGN.md) and judgment a11y on source per `references/a11y-audit.md` §Judgment; say plainly that live axe/visual/vitals need the scripts. Announce the mode in one line.

## Step 0.5 — Preflight + dimension picker

`python3 scripts/preflight.py [--url=URL] [--project=PATH]`. Per-check states map to dimensions:

| Check | Gates / degrades |
|---|---|
| `playwright` | gated `PLAYWRIGHT_MISSING` / `BROWSERS_MISSING` → a11y + visual unavailable until fixed (fix: `pip install playwright && python3 -m playwright install chromium`) |
| `server` | gated `SERVER_UNREACHABLE` → all live dimensions blocked on a URL; **fix is the user's**: start the dev server (or pass `--url`). Never start it ourselves |
| `axe` | ready (cached) / needs one-time CDN fetch / gated `AXE_UNAVAILABLE` with `--no-network` and no cache |
| `lighthouse` | degraded `NODE_MISSING` → vitals unavailable; everything else still runs |
| `design_md` | absent → tokens runs in no-spec mode (internal-consistency only) and points at the `design-md` skill |

Scope precedence: `--agent` → all non-gated dimensions, no prompt. `--dims=` → exactly those (a gated selection fires its gate). Otherwise ask ONE `AskUserQuestion` (multiSelect, 4 options: a11y / visual / vitals / tokens), each option's description showing its live preflight status. Gates follow spec A7: unambiguous trigger, ask-don't-degrade interactively (*Fix it for me / I'll do it myself / Skip*), `--agent` bypass, graceful dead-end — a gate never blocks the other dimensions.

## Steps

1. **Resolve targets** — the URL(s) for live dimensions (flag → preflight's localhost probe → ask; under `--agent` with no URL, run static dimensions only and say so). For multi-page apps prefer 2–4 representative routes over one.
2. **Run the scoped dimensions** (each script: JSON stdout, diagnostics stderr, bounded timeouts):
   - **a11y** — `python3 scripts/axe_scan.py --url=<u> [--url=<u2>…]` → violations with impact, selector, snippet. Then work the **judgment checklist** in `references/a11y-audit.md` (labels, alt quality, focus order, contrast in context) — axe alone is ~30–50% coverage; say which half you did.
   - **visual** — `python3 scripts/screenshots.py --url=<u> --breakpoints=… --out=<dir>` → then **read each screenshot** and review per `references/visual-review.md` (overflow, wrapping, tap targets, layout breakage between breakpoints).
   - **vitals** — `python3 scripts/vitals.py --url=<u>` → Lighthouse lab metrics vs budgets (defaults in `references/vitals.md`; LCP/CLS/TBT — INP is field-only, never claim it from lab).
   - **tokens** — `python3 scripts/token_drift.py --project=<root> [--design=PATH]` → hard-coded colors/fonts not in the DESIGN.md token set, with file:line.
3. **Classify findings** by spec §C severity: 🔴 critical (axe critical/serious, layout broken at a breakpoint, hard budget fail), 🟠 important (axe moderate, near-budget, drift clusters, judgment-checklist failures), 🟡 nice (isolated drift, minor polish). Every finding: evidence (`file:line`, selector, metric, or screenshot), the rule it violates, a concrete fix.
4. **Write the report** to `--out` — led by the target URL(s)/project, the date, the dimensions run (and which were skipped/degraded — disclose partial runs, spec A12), then findings grouped by severity, then a short ✅ pass list. Offer the `render-html` step.
5. **Offer, don't act** — stop after the report. Offer: fix via `build-ui` (all / critical-only) / leave as-is. Under `--agent`: report and stop.

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- **Report-only, like `audit-skill`** — same severity grammar, same offer-don't-act ending. Fixing is `build-ui`'s job (composition by reference, spec A8).
- **Deterministic gate + judgment layer**: tools (axe, Lighthouse, drift scan) provide the floor; the model's judgment pass covers what they can't. Never present the tool layer alone as a complete audit (A12 honesty).
- **Layered resolution (A11)**: axe-core `$AXE_JS → .cache/axe.min.js → CDN (one-time, cached)`; Lighthouse `$LIGHTHOUSE_BIN → lighthouse on PATH → npx`. Node optional; never a committed `node_modules`.
- **Scripts (A4)**: one concern each, JSON stdout / stderr diagnostics, time-bounded, graceful failure. Keyless — no secrets, no `_env.py`.
- Screenshots and reports are written to `--out` / the working dir — never into `~/.claude/skills/` (commit-by-default repo).
- Tauri carryover: point the live dimensions at the dev-server URL a Tauri webview loads; vitals budgets matter less there, a11y/visual/tokens apply unchanged.
