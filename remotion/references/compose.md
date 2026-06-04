# compose — how `remotion` coordinates with Remotion's official skill

This is the **coordination layer**, not a Remotion manual. It exists so `remotion`
defers cleanly to the upstream skill instead of duplicating (and drifting from)
its knowledge. Read it at Step 3 after the probe reports `external_skills`.

## The two skills, and the division of labor

| | Official `remotion-best-practices` | This skill (`remotion`) |
|---|---|---|
| Source | `remotion-dev/remotion/packages/skills` (maintained by Remotion) | this repo |
| Scope | **API & domain knowledge** — animation, timing, sequencing, transitions, audio, audio-visualization, captions (display/import-srt/transcribe), 3d, gifs, lottie, maps (maplibre), fonts (google/local), images, videos, trimming, Zod parameters, calculate-metadata, measuring text/DOM, html-in-canvas, ffmpeg, sfx, silence-detection, voiceover, tailwind | **Workflow orchestration** — probe/scaffold, script→scenes, preview, render/export, advanced compositing, the determinism guardrails, no-monoculture |
| Shape | 1 `SKILL.md` + ~37 `rules/*.md` (progressive disclosure) | this `SKILL.md` + 4 references + 2 scripts |
| Updates | every Remotion release | rarely (workflow is stable) |

**Rule of thumb:** if the question is "what's the Remotion API for X / how do I
animate/sequence/caption/transition X" → that's the official skill's job. If it's
"how do I go from a script to a rendered MP4" → that's this skill's job.

## Install gate (the probe's `external_skills["remotion-best-practices"]`)

- **`true`** — installed at `~/.claude/skills/remotion-best-practices`. Defer all
  API/domain questions to it; don't re-derive its rules here. Use this skill for
  the workflow spine and the guardrails.
- **`false`** — not installed on this machine. Before doing API-heavy work, surface
  the install command:

  ```bash
  npx skills add remotion-dev/skills
  # non-interactive / agent variant:
  npx -y skills@latest add remotion-dev/skills -g -y
  ```

  (It's also offered during `npx create-video@latest` — say **yes** to "install
  Skills".) Until it's installed, fall back to general knowledge **and flag the
  caveat plainly**: Remotion's current components, package APIs, and best-practice
  rules may post-date the model's training cutoff, so verify against
  [remotion.dev/docs](https://www.remotion.dev/docs). The determinism guardrails in
  [`guardrails.md`](guardrails.md) are stable and apply regardless.

## No-monoculture rule

Do **not** add Remotion (a `remotion` dependency, a `remotion.config.ts`, a
`src/Root.tsx`) to a project that doesn't already use it without **explicit user
consent**. Adding a video framework is a real, separate decision — same posture as
build-ui's refusal to introduce shadcn/Next/Tailwind unprompted. The probe's
`is_remotion` field is how you know. Greenfield/empty dirs are fine to scaffold
into (that's the user asking for a new Remotion project); an existing *non-Remotion*
app is not.

## Third-party add-ons (not Remotion products)

The tutorial that seeded this skill uses a community **"anti-gravity protocol"**
token-efficiency skill (by KingstarOmega) and a set of personal "resources" docs
(typography / scene-composition / versioning / creative-unlock). These are
**optional, third-party**, and not part of Remotion. Mention them only if the user
asks; never install or assume them.

## The probe vs. live state

`probe.py` plans from files on disk (is this a Remotion project? is the official
skill installed? is Node here?). At execution time, the official skill's own
guidance and `npx remotion …` reflect the live version. If they disagree, trust the
live tool + the official skill over this skill's static notes.
