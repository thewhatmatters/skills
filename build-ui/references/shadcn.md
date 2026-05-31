# shadcn/ui — working in this project's setup

Loaded by `SKILL.md` Step 3 when `probe.components == "shadcn"`. shadcn is not
a component *library* — it's a CLI that copies source into your repo, so the
components are *yours*. That changes how you reason about them.

## Read the probe first

`probe.shadcn`:
- `style` — `default` or `new-york`. Affects the copied source (border radius,
  density, sometimes a different shape entirely). Don't mix styles.
- `baseColor` — `slate | gray | zinc | neutral | stone`. Drives the CSS variable
  palette (`--background`, `--foreground`, `--primary`, …) the components read.
- `rsc` — `true` if React Server Components are honored. Affects when you must
  add `"use client"`.
- `components_alias` / `ui_alias` — usually `@/components` and
  `@/components/ui`. Imports look like `@/components/ui/button`.

## Conventions worth matching

- **Edit the copies, don't fork.** Components live under `components/ui/` (or
  the configured alias). They're yours — change them directly when you need a
  variant or behavior. Don't add a wrapper that re-implements styling.
- **Composition over forking.** Prefer building a *new* component that *uses*
  the primitive (e.g. a `StatCard` that uses `Card`/`CardHeader`/`CardContent`)
  over copying-and-renaming.
- **Variants.** shadcn components use `cva` (`class-variance-authority`) for
  variants — read the existing `variants` definition before adding a new size
  or intent. Add to the same `cva` block; don't define a parallel system.
- **`cn()`** is in `lib/utils.ts`. Use it for any conditional className.
- **Importing.** Always go through the alias: `import { Button } from
  "@/components/ui/button"`. Relative paths defeat the convention.
- **Server vs client.** With `rsc: true`, default to server. Reach for `"use
  client"` only when a component needs interactivity, refs, or browser APIs.
  Most shadcn primitives that use Radix (Dialog, Popover, Tooltip, …) are
  already client.
- **Theming.** Theme is CSS variables (`--background`, `--primary`, etc.) in
  `globals.css`. To change the palette, edit those variables — don't override
  Tailwind utilities per-component.

## When to `shadcn add ...` vs hand-write

- Adding a **primitive** the project doesn't have (Toast, Dialog, Command,
  DropdownMenu) → run `pnpm dlx shadcn@latest add toast` (use the project's
  package manager from the probe). This is an explicit dep change — surface it
  in your plan.
- A **composition** of existing primitives (a custom card pattern, a layout
  shell) → hand-write it under the project's components dir, importing from
  `@/components/ui/...`.

## Pitfalls

- **Don't introduce shadcn** in a project that doesn't already use it. The
  install is invasive (writes config + copies sources). If `probe.components !=
  "shadcn"`, this reference shouldn't be loaded.
- **Don't ship a duplicate `cn()`** — there is exactly one in `lib/utils.ts`.
- **`asChild` slot.** Many shadcn primitives accept `asChild` (Radix Slot) so
  consumers can pass their own element. Use it instead of wrapping/cloning.
- **Forms.** If `react-hook-form` is present, shadcn's Form components
  (`Form`, `FormField`, `FormItem`, …) wrap it idiomatically. Don't build a
  parallel forms abstraction.

## Composition with Tailwind + frontend-design

shadcn copies use the project's Tailwind theme. To re-skin the look:
1. Adjust the CSS variables in `globals.css` (palette, radius).
2. Adjust the `cva` `variants` in the affected primitive (default sizes,
   intents).
3. Keep the *structure* (Radix primitives, slots, ARIA) — only the surface
   should change.

`frontend-design` may push toward distinctive type/color; honor that by editing
tokens + variants, not by spraying utilities at call sites.
