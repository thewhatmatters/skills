# visual dimension — breakpoint review method

Loaded by `SKILL.md` Step 2 when the visual dimension is in scope. The script
captures; **you review** — read every screenshot `screenshots.py` produced
(they are images; look at them), comparing across breakpoints.

## Default breakpoints and what each represents

| Width | Stands for | Extra attention |
|---|---|---|
| 375 | small phone | tap targets, text wrap, horizontal overflow |
| 768 | tablet / split view | layout mode transitions (stacked→side-by-side) |
| 1280 | laptop | the "designed" view — baseline for comparison |
| 1920 | desktop | max-width behavior, line lengths, stretched layouts |

## The checklist (per page, across its set of captures)

1. **Horizontal overflow** — content clipped at the right edge or a phantom
   horizontal scrollbar at 375 (the classic fixed-width offender). 🔴 if
   content is unreachable.
2. **Breakage between breakpoints** — components that overlap, collapse to
   zero height, or stack wrongly at exactly one width. 🔴.
3. **Text behavior** — orphaned single words in headings, truncation that eats
   meaning, line lengths > ~80ch at 1920 (no max-width), font sizes that don't
   step down on mobile. 🟠.
4. **Tap targets at 375** — nav links, icon rows, table actions too small/dense
   (cross-feeds the a11y dimension's touch-target check). 🟠.
5. **Spacing rhythm** — margins/padding that visibly change scale between
   sections (8 vs 11 vs 13px gaps reads as drift; cross-feeds tokens). 🟡.
6. **Empty/loading states** — if a capture caught a skeleton or spinner
   mid-load, re-run that capture before judging (the 500ms settle usually
   suffices; flag if a page never settles).
7. **Dark mode** *(when the app has it)* — capture twice if the user asks;
   default is the OS-light capture only — say so in the report.

## Reporting

Every visual finding cites its evidence: the screenshot path + breakpoint
("`dashboard-375.png`: nav overflows viewport by ~80px"). Findings that need
motion or interaction to see (hover states, focus styles, transitions) are out
of scope for static captures — note them for `automate-browser` follow-up rather
than guessing.

## What this dimension is NOT (v1)

No pixel-diff baselines — first runs have nothing to diff against, and
baseline management (Docker font determinism, update workflows) is CI
machinery, not an agent pass. The model's eye across breakpoints catches the
breakage class that matters pre-ship; revisit baselines only if regressions
start slipping through repeat audits.
