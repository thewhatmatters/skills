# JavaScript / TypeScript patterns for components

Loaded by `SKILL.md` Step 3 **always** (regardless of stack). Stack-agnostic
hygiene for component code; pairs with [`a11y.md`](a11y.md). Things a model
implementing UI in a real project should remember — and the anti-patterns most
worth catching before they ship.

**Operating principle:** match the project's existing lint, tsconfig strictness,
and library choices over what you'd write from scratch. Reach for the platform
first (modern DOM APIs, native types) → the framework's idiomatic primitives →
libraries only when they earn their keep. If `probe` surfaces a library
(forms, query, state), use it; don't shadow it with a parallel abstraction.

---

## Universal hygiene (every component)

- [ ] **Read the project's lint + tsconfig first.** `.eslintrc*` / `eslint.config.*`
  and `tsconfig.json` encode the project's opinions — don't fight them. With
  `strict: true` or `noUncheckedIndexedAccess`, the idioms shift (you'll narrow
  more, guard more).
- [ ] **Use the project's `cn()`/`clsx` helper** for conditional classNames. Never
  string-concat classes; never ship a duplicate utility.
- [ ] **Use the project's path aliases** (probe surfaces them). `@/components/...`
  beats `../../../components/...`.
- [ ] **Idempotent renders.** A component rendered twice with the same input
  produces the same output and the same side effects. React StrictMode
  double-invokes in dev — effects must be cleanup-safe.
- [ ] **Side effects in handlers, not render.** Reading from local storage,
  fetching, focusing an element, mutating refs — all belong in handlers or
  effects, never in the render body.
- [ ] **No `console.log` in shipped code.** Use the project's logger, or rely on
  the build to strip it. If neither exists, remove before commit.

---

## Async & effects

The single richest source of UI bugs. Three rules cover most of it.

- [ ] **Cancel in-flight work on dependency change.** Pattern: `AbortController`,
  pass `signal` to `fetch` / `addEventListener`, abort in cleanup.
  ```ts
  useEffect(() => {
    const ac = new AbortController()
    fetch(url, { signal: ac.signal }).then(setData).catch(ignoreAbort)
    return () => ac.abort()
  }, [url])
  ```
- [ ] **Last-write-wins races.** Stale closures committing late after the user
  navigated away. `AbortController` is the modern fix; an `ignore = false` flag
  in cleanup is the legacy one. Either way, the cleanup must short-circuit the
  late update.
- [ ] **Never `await` in render.** Don't `await` directly inside a `useEffect`
  callback either — define an inner async function and call it. Suspense + RSC
  is the alternative if the project uses it; don't mix idioms.
- [ ] **Deduplicate concurrent identical requests** at the call site, or via the
  project's query library (`@tanstack/react-query`, SWR) if `probe` finds one.
  Don't roll your own cache.
- [ ] **Cleanup means cleanup.** Removing a listener, aborting a fetch,
  unsubscribing from a store, clearing a timeout — every subscription gets a
  return-from-effect that undoes it.

---

## State discipline

- [ ] **Derive, don't store.** If state X can be computed from props/state Y,
  compute it. Storing both invites desync — and a `useEffect` to sync them is
  the smell that gives it away.
- [ ] **Single source of truth per piece of state.** URL params (shareable),
  component state (ephemeral UI), server state (server data) — don't shadow
  one with another.
- [ ] **`useEffect` is not a sync primitive.** Most "copy this prop into local
  state" effects are wrong — derive, or lift the state up to where the change
  originates.
- [ ] **Lift state only as far as needed** — to the nearest common ancestor that
  actually uses it, not to the root by default.
- [ ] **Reach for context / store / query lib** only when prop drilling crosses
  ~3 layers AND the state changes frequently AND multiple consumers care.
  Otherwise prop-pass.

---

## DOM / performance gotchas

- [ ] **No layout thrash.** Never interleave reads (`offsetHeight`,
  `getBoundingClientRect`, `getComputedStyle`) and writes (`style.x = ...`) in
  a loop. **Batch reads, then writes.** A read after a write forces synchronous
  layout; in a list of 100 items it's death by a thousand cuts.
- [ ] **Animate transform / opacity** (compositor); avoid animating
  width/height/top/left (layout). See `a11y.md` for `prefers-reduced-motion`.
- [ ] **Observers > listeners.** `IntersectionObserver` for visibility /
  lazy-load; `ResizeObserver` for size changes. Both beat scroll/resize handlers
  and don't fight the main thread.
- [ ] **`requestAnimationFrame`** for visual work; `setTimeout(_, 0)` for layout
  timing is brittle. If you need post-paint, use two rAFs.
- [ ] **`content-visibility: auto` + CSS `contain`** for off-screen heavy lists
  when the project uses modern CSS.
- [ ] **Memoize when measured.** `useMemo` / `useCallback` aren't free; default
  them on everywhere and code becomes harder to read for marginal wins.
  Profile first.
- [ ] **List keys are for correctness, not perf.** Use stable IDs (NOT array
  indices) for reorderable lists; otherwise state binds to the wrong item.

---

## TypeScript hygiene (in a component context)

- [ ] **Avoid `any`.** Use `unknown` and narrow with type guards. `any`
  silently disables the typechecker for everything downstream.
- [ ] **Discriminated unions for variants.**
  ```ts
  type ButtonProps =
    | { variant: "primary"; onClick: () => void }
    | { variant: "link"; href: string }
  ```
  Better than booleans for mutually-exclusive features — the type system
  enforces "you can't pass `href` to a primary button."
- [ ] **Narrow at the boundary.** Where data enters (API, user input, parsed
  JSON), narrow once with a guard (or Zod / Valibot if the project uses one).
  Don't sprinkle `as` casts inline.
- [ ] **`as const`** for literal narrowing of objects/arrays you don't mutate
  (route lists, status enums).
- [ ] **No casts without a guard.** If you reach for `as`, write a
  `function isFoo(x: unknown): x is Foo` instead so the narrowing is visible
  and tested.
- [ ] **Export the public props interface.** Don't make consumers reach into
  internal helper types.
- [ ] **Barrel files** (`index.ts` re-exports) can defeat tree-shaking and
  hide circular imports. Follow the project's pattern, but don't add new ones
  by reflex.

---

## Forms (the JS half — pair with `a11y.md` → Forms & Inputs)

- [ ] **Controlled or uncontrolled — pick one per field and stick with it.**
  React warns on switches; users see lost input.
- [ ] **Use the project's form library** if `probe` finds one (`react-hook-form`,
  `formik`, `@tanstack/form`). Don't introduce a parallel abstraction.
- [ ] **Validate on blur and submit, not on every keystroke.** Debounce async
  validation (e.g. "is this username taken").
- [ ] **Server errors map back to fields.**
  `setError("email", { message: ... })` (react-hook-form) or the project's
  equivalent — not a global toast.
- [ ] **Don't disable submit during pending** (it loses focus and feels broken).
  Use a busy state on the button and `aria-busy`; let users re-press for retry.

---

## Modules / imports

- [ ] **Match the project's import style** — same alias, same extension policy
  (`.tsx` vs no extension), same ordering rule (your linter probably enforces).
- [ ] **Side-effect imports** (`import "./global.css"`) belong at the top, never
  conditionally. Put them in the root entry, not deep in a component.
- [ ] **Code-split heavy chunks** with dynamic `import()` only where the gain is
  real (a route, a rich text editor, a chart library). Don't split for the sake
  of it — chunk overhead can outweigh the savings.
- [ ] **Don't import the whole library for a single util.** Tree-shake-friendly
  imports (`import { debounce } from "es-toolkit"`) or pull the one function.

---

## Anti-patterns to stop on sight

- **`setState` in render** without a guard → infinite loop.
- **Mutating props/state in place** (`arr.push(x); setArr(arr)`) — React skips
  the re-render. Spread or use an immer-style updater.
- **`useEffect` as prop→state sync.** Derive, or lift.
- **Long ternary chains in JSX.** Extract a function or use early returns.
- **`setTimeout(_, 0)` for "after layout."** Use `requestAnimationFrame`.
- **Classname concatenation with template strings.** Use the project's `cn()`.
- **`console.log` shipped to prod.**
- **A `useState<any>`** or `as any` cast. Tell the typechecker the truth.
- **Disabling the button while submitting** (focus loss + perceived breakage).
- **Global state for what is component state.**
- **A new `useState` to hold something already in URL / form / server data.**

---

## Verification protocol

Match the project's gates before declaring done:

- [ ] `tsc --noEmit` (or whatever the project calls typecheck) passes.
- [ ] The project's tests pass.
- [ ] The project's lint passes — no new warnings, no disabled rules.
- [ ] For interactive components: also work through
  [`a11y.md`](a11y.md) → **Verification protocol**.

---

### TL;DR

1. Match the **project's** lint, tsconfig strictness, helpers, and libraries.
2. Cancel async work on dependency change; cleanup means cleanup.
3. **Derive state, don't sync it.**
4. Narrow types at the boundary, not inline.
5. Don't animate layout; don't thrash; don't memoize without measuring.
6. The shipped code should not contain a single `as any`, a single
   `console.log`, or a single hand-rolled `cn()` parallel utility.
