# a11y dimension — axe interpretation + the judgment layer

Loaded by `SKILL.md` Step 2 when the a11y dimension is in scope. The dimension
is two layers and the report must say which ran: **axe** (deterministic floor,
~30–50% of WCAG issues) and **judgment** (what no engine can decide).

## Layer 1 — interpreting `axe_scan.py` output

Severity mapping (axe `impact` → spec §C):

| axe impact | report severity |
|---|---|
| `critical`, `serious` | 🔴 critical |
| `moderate` | 🟠 important |
| `minor` | 🟡 nice |

Per violation, the finding needs: the axe rule id + `helpUrl`, the selector
(`nodes[].target`), the snippet, and a **concrete fix in the project's idiom**
(e.g. a shadcn/Radix project usually fixes `button-name` with the component's
built-in `aria-label` prop, not raw ARIA).

Noise control:
- Collapse repeats — 40 instances of `color-contrast` on the same token pair is
  ONE finding with a count, not 40.
- On Radix/shadcn primitives, a violation often means custom markup *broke* the
  primitive's built-in semantics — say that, and fix the markup, not the primitive.
- `color-contrast` on text over images/gradients: axe can't always compute it
  (`impact: serious`, `incomplete` bucket) — verify by eye in the screenshots.

## Layer 2 — the judgment checklist (run it; tools can't)

For each audited page, check and report explicitly:

1. **Label quality** — fields may *have* labels (axe passes) that are still
   wrong: placeholder-as-label, "Name" on an email field, unlabeled icon buttons
   with a generic `aria-label="button"`.
2. **Alt text quality** — `alt=""` on meaningful images, filename alts,
   alt text that repeats the caption. Decorative images should be `alt=""` —
   presence isn't correctness in either direction.
3. **Focus order & visibility** — tab through the page top-to-bottom mentally
   from the DOM order: does focus follow the visual order? Is `:focus-visible`
   styled (not `outline: none` with no replacement)? Does a modal trap and
   restore focus?
4. **Error handling** — are form errors announced (`aria-describedby` /
   `role="alert"`), specific ("Email needs an @" not "Invalid input"), and
   visible without color alone?
5. **Reading order vs visual order** — CSS `order`/grid placement that diverges
   from DOM order breaks screen-reader narrative.
6. **Touch targets** — interactive elements ≥ ~44×44px effective hit area on
   the mobile breakpoint (cross-check the 375px screenshot).
7. **Motion** — animations honor `prefers-reduced-motion` (grep for the media
   query / `useReducedMotion`). If `add-motion` built them, this should pass.

Judgment findings default to 🟠 important; promote to 🔴 when they block a task
(unlabeled primary action, focus trap with no escape, error invisible to AT).

## Honesty rules

- Always state coverage: "axe (automated) + judgment checklist on N pages" —
  never imply a full WCAG conformance audit; that needs human AT testing.
- `incomplete` axe results are *unverified*, not passes — list them under a
  "needs manual check" note if relevant.
