# Summary header & content-type templates

Loaded by `SKILL.md` Step 4 (progressive disclosure, spec A1). Classify the
content, then apply the matching shape. Every bullet carries a real locator
from the source — `[MM:SS]` for video, `[p. N]` for PDFs, `[§ Heading]` for
pages/documents.

## Header (every ingestion, all types — spec A10/A12)

```
# <Title>
**Source:** <URL or path> · **Type:** <youtube|webpage|pdf|image|document> [· **Channel/Author:** <name>] [· **Length:** <H:MM:SS> | <N> pages]
**Ingested:** <YYYY-MM-DD> via <tier — e.g. "watched (Gemini)" | "transcript (yt-dlp)" | "text (fetched)" | "native read (pdf)" | "metadata only — NOT read">

[one-sentence tl;dr]
```

(`persist.py` adds machine-greppable YAML frontmatter above this; the header
is the human-facing copy of the same facts.)

## Video / article shapes

**Tutorial / how-to** — ordered, reproducible:
```
## Steps
1. **[00:42] <action>** — <detail>; `command if shown`
2. **[02:15] <action>** — …
## Gotchas / notes
- [05:30] <caveat the presenter called out>
```

**Ranked / top-N list:**
```
## The list
- **#1 — <item> [01:10]** — <why; one line>
- **#2 — <item> [02:45]** — …
[honor the source's own ordering; note if it counts down]
```

**Review / comparison — pros/cons:**
```
## Verdict — [tl;dr + the locator where it's stated]
| Pros | Cons |
|------|------|
| <point> [03:10] | <point> [06:20] |
## Notable moments
- [08:05] <benchmark / demo / price>
```

**Talk / interview / explainer / essay — key points:**
```
## Key points
- **[00:30] <claim/idea>** — <supporting detail>
- **[04:10] <claim/idea>** — …
## Quotable
> "<short quote>" — [12:40]
```

## Document & image shapes

**Reference document (spec, paper, report, manual):**
```
## What this covers
<one paragraph — scope and intended use>
## Key facts
- **<fact>** [p. 4 | § Heading] — <detail>
## Structure map
- § <section> [p. N] — <one line on what's there>
[so a future session can jump straight to the right section of the source]
```

**Image (diagram, screenshot, chart, whiteboard photo):**
```
## What it shows
<plain description of the visual>
## Text in the image
<verbatim transcription of any text — usually the reason it's ingested>
## Reading
<what the diagram/chart actually says; relationships, values, takeaways>
```

**Unknown / mixed:** default to the key-points template and note the type was
ambiguous.

## Rules

- Never invent a locator; only use timestamps/pages/headings present in the
  source material.
- Keep the tier line honest — if you transcribed, don't imply you watched; if
  you only saw metadata, say the source was NOT read.
- Long sources: summarize section-by-section using chapters / headings / page
  ranges as anchors.
- Write for a **future session that hasn't seen the source**: expand acronyms
  on first use, name the entities, keep claims self-contained.
- The one-line `--hook` for INDEX.md answers "when would a future task need
  this file?" — not a repeat of the title.
