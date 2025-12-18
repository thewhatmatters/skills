---
name: frontend-ui-expert
description: Expert-level frontend UI engineering with Tailwind CSS, shadcn/ui, and Aceternity UI. Use when building, reviewing, or refactoring React/Next.js components. Covers component architecture, accessibility (WCAG 2.1 AA/AAA), performance optimization, and best practices. Triggers include requests to build UI components, review frontend code, fix UI bugs, improve accessibility, optimize performance, or implement responsive designs. Not applicable for Vue, Svelte, Angular, or non-React frameworks.
---

# Frontend UI Expert

Build production-grade, accessible, performant UI using Tailwind CSS, shadcn/ui, and Aceternity UI.

## Workflow

### 1. Assess the Task

Determine the task type:

| Task                       | Primary Focus                | Key References                    |
| -------------------------- | ---------------------------- | --------------------------------- |
| **Build new component**    | Architecture + accessibility | `shadcn.md`, `patterns.md`        |
| **Review existing code**   | Anti-patterns + a11y         | `patterns.md`, `accessibility.md` |
| **Add animations/effects** | Performance + when to use    | `aceternity.md`                   |
| **Fix UI bug**             | Root cause in patterns       | `tailwind.md`, `patterns.md`      |
| **Improve accessibility**  | WCAG compliance              | `accessibility.md`                |
| **Optimize performance**   | Rendering + bundle           | `patterns.md`, `aceternity.md`    |

### 2. Component Selection

Choose the right library for the component:

```
Is it interactive (buttons, forms, dialogs)?
├── Yes → Use shadcn/ui (Radix primitives, accessible by default)
└── No → Is it decorative/animated?
         ├── Yes → Evaluate Aceternity (see decision matrix below)
         └── No → Plain Tailwind + semantic HTML
```

**Aceternity Decision Matrix:**

| Context             | Use Aceternity? | Reason                    |
| ------------------- | --------------- | ------------------------- |
| Hero/landing        | Yes             | High impact area          |
| Dashboard           | No              | Data density, performance |
| Marketing page      | Yes             | Visual appeal matters     |
| Form-heavy UI       | No              | Distraction from task     |
| Portfolio           | Yes             | Showcase creativity       |
| E-commerce checkout | No              | Conversion risk           |

### 3. Implementation Standards

Every component must meet these criteria:

**Accessibility (non-negotiable):**

-   Keyboard navigable (Tab, Enter, Space, Escape)
-   Screen reader compatible (proper ARIA when needed)
-   Color contrast AA minimum (4.5:1 text, 3:1 UI elements)
-   Respects `prefers-reduced-motion`
-   See `references/accessibility.md` for detailed patterns

**Performance:**

-   No unnecessary re-renders (memoize appropriately)
-   Lazy load heavy components (`React.lazy`, dynamic imports)
-   Virtualize lists > 100 items
-   GPU-accelerated animations only (`transform`, `opacity`)

**Code Quality:**

-   TypeScript types for all props
-   `forwardRef` on input-like components
-   `cn()` for class merging (never string concatenation)
-   Mobile-first responsive design

## Quick Patterns

### Tailwind Class Order

Use `prettier-plugin-tailwindcss` for automatic sorting. Manual order:

```
layout → position → size → spacing → typography → visual → states → responsive
```

Example:

```tsx
<div className="flex absolute w-full p-4 text-sm bg-white rounded-lg hover:bg-gray-50 md:p-6" />
```

### shadcn Component Extension

Wrap, don't modify the source:

```tsx
import { Button, ButtonProps } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

interface LoadingButtonProps extends ButtonProps {
    isLoading?: boolean;
}

export function LoadingButton({
    isLoading,
    children,
    disabled,
    ...props
}: LoadingButtonProps) {
    return (
        <Button disabled={isLoading || disabled} {...props}>
            {isLoading && (
                <Loader2
                    className="mr-2 h-4 w-4 animate-spin"
                    aria-hidden="true"
                />
            )}
            {children}
        </Button>
    );
}
```

### Reduced Motion Support

```tsx
import { useReducedMotion } from "@/hooks/use-reduced-motion";

function AnimatedComponent() {
    const prefersReducedMotion = useReducedMotion();

    return (
        <motion.div
            animate={prefersReducedMotion ? {} : { y: [0, -10, 0] }}
            transition={
                prefersReducedMotion
                    ? { duration: 0 }
                    : { duration: 2, repeat: Infinity }
            }
        />
    );
}
```

### Accessible Form Field

```tsx
<FormField
    control={form.control}
    name="email"
    render={({ field, fieldState }) => (
        <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
                <Input
                    {...field}
                    type="email"
                    aria-describedby="email-description email-error"
                    aria-invalid={!!fieldState.error}
                />
            </FormControl>
            <FormDescription id="email-description">
                We will never share your email.
            </FormDescription>
            <FormMessage id="email-error" role="alert" />
        </FormItem>
    )}
/>
```

### The cn() Utility

Always use `cn()` for conditional classes:

```tsx
import { cn } from "@/lib/utils";

// Good
<div className={cn("base-classes", isActive && "active-classes", className)} />

// Bad - loses class merging
<div className={`base-classes ${isActive ? "active-classes" : ""}`} />
```

## Error Recovery

**shadcn component doesn't exist:**

1. Check if it's available: `npx shadcn@latest add [component]`
2. If not in registry, build from Radix primitives
3. See `references/shadcn.md` for composition patterns

**Aceternity effect causes performance issues:**

1. Check device capability with `navigator.hardwareConcurrency`
2. Reduce particle count or disable on mobile
3. Use `will-change` sparingly
4. See `references/aceternity.md` for performance matrix

**Accessibility audit failures:**

1. Run `axe-core` for automated checks
2. Test keyboard navigation manually
3. Use VoiceOver/NVDA for screen reader testing
4. See `references/accessibility.md` for remediation patterns

## References

Consult these for detailed guidance:

-   **[tailwind.md](references/tailwind.md)** - Utility organization, responsive design, v4 changes, configuration
-   **[shadcn.md](references/shadcn.md)** - Component composition, CVA variants, theming, form integration
-   **[aceternity.md](references/aceternity.md)** - When to use, performance cost matrix, accessibility concerns
-   **[accessibility.md](references/accessibility.md)** - WCAG 2.1 AA/AAA checklist, keyboard nav, ARIA patterns
-   **[patterns.md](references/patterns.md)** - Component architecture, layout patterns, state management

## Code Review Checklist

When reviewing frontend code, verify:

-   [ ] **A11y**: Focus visible, contrast ≥4.5:1, labels present, keyboard works, motion respects preference
-   [ ] **Performance**: Memoization where needed, lazy loading, no layout thrashing
-   [ ] **Tailwind**: Mobile-first, design tokens used, `cn()` for merging, no arbitrary values without reason
-   [ ] **shadcn**: Composition over modification, forwardRef preserved, accessibility intact
-   [ ] **Types**: Props typed, no `any`, discriminated unions for variants
