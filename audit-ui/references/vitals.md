# vitals dimension — lab budgets and the INP honesty rule

Loaded by `SKILL.md` Step 2 when the vitals dimension is in scope.
`vitals.py` measures; this file is how to read and report it.

## The honesty rule (first, because it gets violated everywhere)

Lighthouse produces **lab** metrics from one synthetic load. **INP is a field
metric** — it needs real user interactions; the lab proxy is **TBT**. Report
"TBT (lab proxy for INP)" and never write "INP" next to a number from this
skill. For real field data point the user at their RUM/CrUX panel
(Vercel Speed Insights / Search Console).

Lab numbers also vary run-to-run (±10% is normal). One run that *misses* a
budget by a hair is a 🟡 watch item; re-run before calling it 🟠.

## Default budgets (override: `--budget lcp_ms=2000`)

| Metric | Budget | Why |
|---|---|---|
| `perf_score` | ≥ 0.90 | the composite gate |
| `lcp_ms` | ≤ 2500 | Google's "good" threshold |
| `cls` | ≤ 0.10 | "good" threshold |
| `tbt_ms` | ≤ 300 | lab proxy for responsiveness |

Audit against the **production-like** build when possible (`next build &&
next start`, not `next dev`) — dev servers fail budgets by design (no
minification, HMR overhead). If the URL is a dev server, say so and treat
vitals as directional only, never 🔴.

## Mapping failures to fixes (the usual suspects, Next.js flavored)

| Failing signal | First places to look |
|---|---|
| LCP high | hero image not `next/image` + `priority`; font blocking render (use `next/font`); server response slow (check TTFB in `failed_audits`) |
| CLS high | images/embeds without dimensions; fonts swapping (size-adjust); content injected above existing content; ads/banners |
| TBT high | oversized client bundles — look for `'use client'` creep pulling server-renderable trees client-side; third-party scripts (move to `next/script` strategy); hydration of huge lists |
| `render-blocking-resources` | CSS/JS in `<head>` that should be deferred/inlined |
| `unused-javascript` big | dynamic-import heavy components; check bundle for accidental barrel imports |

`failed_audits` in the JSON is sorted by estimated savings — lead with the top
two; don't enumerate all twelve when three explain the score.

## Severity

- 🔴 hard budget fail on a production-like build (e.g. LCP 4s+, CLS 0.25+)
- 🟠 budget fail within ~25% of target, or any fail on the composite score
- 🟡 passes but trending close (within 10%), or dev-server-only measurements
