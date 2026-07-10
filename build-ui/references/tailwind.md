# Tailwind — working in this project's setup

Loaded by `SKILL.md` Step 3 when `probe.css == "tailwind"`. This file is about
*working in the project's existing config*, not Tailwind from scratch.

## Read the probe first

`probe.tailwind.config_path` tells you which file holds the theme; **always
open it** before writing utilities. Read the `theme.extend` blocks (or `@theme`
inline for v4) for colors, fontFamily, fontSize, spacing, breakpoints,
borderRadius, boxShadow. Match those token names instead of inventing arbitrary
values.

`probe.tailwind.version_hint`: `"v3"` (config in JS/TS) vs `"v4"` (`@import
"tailwindcss"` + `@theme` blocks in CSS). The difference matters for plugins,
arbitrary values, and the `@apply` story — confirm by opening the file.

## Use the project's token vocabulary

| Don't | Do |
|---|---|
| `bg-[#11a8ff]` | `bg-accent` (or whatever the config calls it) |
| `text-[14px]` | `text-sm` (whatever the type scale maps it to) |
| `p-[18px]` | the nearest scale step, or extend the scale once |

Arbitrary values are an escape hatch for genuinely one-off cases, not the
default. If you find yourself reaching for them repeatedly, the right fix is to
*add a token to the config*, not pepper arbitrary values through components.

## Conventions worth matching (read the codebase, then write like it does)

- **`cn()` helper.** Almost every Tailwind+React project has one — `clsx` +
  `tailwind-merge`. Look in `src/lib/utils.ts` (shadcn default) or `src/utils/`.
  Use it for any conditional className; **never** template-string concatenate.
- **Variant style.** Some repos use `cva` (class-variance-authority); some
  inline conditionals; some use `tailwind-variants`. Match what's already there.
- **Order of utilities.** If `prettier-plugin-tailwindcss` is in
  `devDependencies`, the project sorts utilities automatically — don't fight it.
- **Layer discipline.** `@layer components { ... }` for repeated patterns;
  `@apply` sparingly (it's an escape hatch, not a Sass replacement). If the repo
  uses neither, don't introduce them.
- **Dark mode.** Check `darkMode` in the config (`"class"` vs `"media"`). Class
  mode means: a parent toggles a `dark` class, write `dark:bg-foreground`.
- **Container.** If `theme.container` is set, use `<div class="container">`;
  otherwise honor the project's max-width pattern (often `max-w-screen-xl
  mx-auto px-4`).

## Pitfalls

- **Don't introduce a plugin** the project doesn't already have. Adding
  `@tailwindcss/typography` or `@tailwindcss/forms` is a separate user decision.
- **No bare hex / px in components.** Always go through tokens unless the design
  truly is one-off.
- **Negative margins for layout** are a smell — most cases have a Flexbox/Grid
  solution. Save them for visual overlap effects.
- **Don't fight specificity with `!important`** (`bg-red-500!`) unless you're
  overriding a third-party stylesheet. If you need it inside the project's own
  code, the architecture is fighting you.
- **Whitespace within class strings** must not break across lines mid-utility —
  ESLint/Prettier will catch but a manual edit can split `hover:bg-` from its
  value.

## Composition with frontend-design

`frontend-design` may direct you toward distinctive typography, dramatic
shadows, bold color. Implement those by **extending the config tokens** (one
edit to `theme.extend`) rather than scattering arbitrary values across files.
The aesthetic intent and the implementation are not the same job.
