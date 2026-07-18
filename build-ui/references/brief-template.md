# Showcase brief template

The grilling interview (SKILL.md Step 4, showcase tier) fills this template one
question at a time — every question presented WITH a recommended answer the user
can accept or override. The brief locks only when the user confirms it; the
locked file is written to `docs/briefs/<slug>.md` in the project and governs the
art gate, the build, and the checkpoint QA.

Interview order = the order below (dependency-sorted: later answers depend on
earlier ones). Fields marked **[required]** must be explicitly confirmed — no
silent defaults. Optional fields may take the recommended answer without a
question if the user asks to move faster (`--quick` collapses ALL of this into
one pre-filled form round).

```markdown
# <Project / feature name> — showcase brief

## Subject  [required]
- What is being showcased (product, feature, brand moment, destination):
- Audience and the single job of this experience:
- Primary message (one sentence):
- Desired user response / final CTA:

## Art direction  [required — this decides the quality ceiling]
- Imagery source [required; ask FIRST within this section]:
    photography / generated imagery / illustration / code-authored (canvas-WebGL
    painterly) / code-authored (flat vector). State what exists today vs what
    must be produced, and where files live.
    ⚠ If the answer is "none yet", resolve HOW imagery will be produced before
    locking — an experience without an imagery plan caps at flat-vector quality.
- Visual direction (composition, light, texture, era, mood — concrete nouns,
  not adjectives; "make it premium" is not an answer):
- Reference works (URLs, screenshots, sites to match or beat; route to
  `source-ui` if the user has none):
- Palette (existing tokens / DESIGN.md, or 4–6 named values to propose):
- Typography (display + body; webfont constraints):
- Styles to avoid:

## Sequence  [required]
- Beats, in order (hero → … → final interactive state), one line each,
  with the intended transition between beats:
- Scroll-driven, time-driven, or interaction-driven:
- The signature moment (the ONE thing this experience is remembered by):

## Motion character  [optional]
- Pacing (calm/patient vs energetic), easing character, parallax appetite:
- Reduced-motion plan (what the static/normal-flow alternative preserves):

## Constraints  [required]
- Where this lives (route/page/component in the repo):
- Stack constraints beyond the probe (SSR, CMS content, perf budgets):
- Dependencies allowed / forbidden (e.g. Motion yes, GSAP no):
- Deadline / scope ceiling:

## Acceptance  [required]
- QA checkpoints (states or scroll positions that will be screenshot-verified,
  ≥2 viewports; forward AND reverse if scroll-driven):
- Definition of done beyond the checkpoints (a11y, console, perf):

## Assumptions log
- (anything the interview settled by recommendation rather than user words)
```

Interview conduct (borrows `grilling`'s discipline):

- One question per turn; always lead with the recommended answer and why.
- Chase vague answers once ("cinematic how — what does the camera do?"), then
  record the best concrete reading in the Assumptions log and move on.
- Surface conflicts immediately (palette vs existing DESIGN.md, beats vs scope
  ceiling) — do not lock a brief with a known contradiction.
- The user can end the interview anytime with "lock it" — unfilled required
  fields become flagged assumptions, and the art gate is where they get caught.
