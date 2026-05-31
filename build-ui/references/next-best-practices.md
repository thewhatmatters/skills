# Next.js — the build-ui complement to the official `next-best-practices` skill

Loaded when `probe.framework == "next"`. The **official `next-best-practices`
skill** (pinned in `skills-lock.json`, symlinked at
`~/.claude/skills/next-best-practices`) owns Next-specific patterns:
file conventions, RSC boundaries, async APIs (Next 15+), runtime selection,
directives, navigation hooks, error files, data patterns, route handlers,
metadata, `next/image`, `next/font`, bundling, and scripts. **Defer to it.**
This file is kept intentionally small so it doesn't drift from upstream.

> **Install gate.** The probe reports `external_skills["next-best-practices"]`
> — `true` if `~/.claude/skills/next-best-practices/SKILL.md` is discoverable,
> `false` otherwise. If it's `false` (fresh clone, new machine), install it
> before deferring:
> ```
> npx skills add https://github.com/vercel-labs/next-skills --skill next-best-practices
> ```
> Source: [skills.sh](https://www.skills.sh); version + hash pinned in
> `skills-lock.json`. Until installed, SKILL.md falls back to general knowledge
> with a caveat about Next 15+ async APIs and the v16 `middleware` → `proxy`
> rename being recent enough that the training cutoff may not have them.

## What build-ui owns here

- **No-monoculture rule.** Don't introduce Next.js into a project that isn't
  already on it. Adding it is a whole-project conversion, not a build-ui task.
  `probe.framework` is the gate — only this reference loads when it's `next`.
- **Probe + the skill's `'use client'` discipline pair up.** The probe reports
  `framework == "next"`, the alias prefix, and the `src/app` vs `app` dir
  shape; the official skill enforces the RSC/Client/Server-Action boundary.
  Use the probe to *locate* (which dir, which alias); defer to the skill for
  *what the file must look like* (async params, directive placement, RSC
  rules).

## Routing — when build-ui defers vs. acts directly

| Need | Where |
|---|---|
| Next-specific file conventions (`page.tsx`, `route.ts`, `layout.tsx`, `error.tsx`, `not-found.tsx`, dynamic/catch-all/groups, parallel/intercepting routes) | **next-best-practices** |
| RSC boundary calls (async client detection, non-serializable props, Server Action exceptions) | **next-best-practices** |
| Async params/searchParams/cookies/headers (Next 15+) | **next-best-practices** |
| Directives (`'use client'`, `'use server'`, `'use cache'`) | **next-best-practices** |
| Navigation hooks (`useRouter`, `usePathname`, `useSearchParams`, `useParams`) | **next-best-practices** |
| Server functions (`cookies`, `headers`, `draftMode`, `after`) and Generate functions (`generateStaticParams`, `generateMetadata`) | **next-best-practices** |
| Error handling (`error.tsx`, `redirect`, `notFound`, `unstable_rethrow`) | **next-best-practices** |
| Data patterns (Server Components vs Server Actions vs Route Handlers; data waterfalls; Suspense/preload) | **next-best-practices** |
| Metadata + OG images (`generateMetadata`, `next/og`, file-based conventions) | **next-best-practices** |
| `next/image`, `next/font`, bundling, `next/script` | **next-best-practices** |
| Where the file goes (alias, dir, naming), project conventions | **build-ui + the probe** |
| The React code *inside* a component (state, effects, types) | **build-ui** + [`javascript-patterns.md`](javascript-patterns.md) |
| Accessibility checklist (Universal + per-pattern) | [`a11y.md`](a11y.md) |
| Styling | [`tailwind.md`](tailwind.md) or [`vanilla-css.md`](vanilla-css.md) |
| Component primitives (shadcn) | [`shadcn.md`](shadcn.md) → the official `shadcn` skill |

## Composition stance

`frontend-design` (taste) → `build-ui` (project conventions, no-monoculture) →
**next-best-practices** (Next.js-specific patterns) + **shadcn skill**
(component execution). When you're writing a Next page or route, defer Next's
*shape* to next-best-practices; write the React/component *body* with build-ui
+ the always-loaded references.
