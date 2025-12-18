# Tailwind CSS Reference

Comprehensive guide for Tailwind CSS best practices, class organization, and configuration.

## Table of Contents

-   [Class Ordering](#class-ordering)
-   [Responsive Design](#responsive-design)
-   [Configuration](#configuration)
-   [Common Patterns](#common-patterns)
-   [Anti-Patterns](#anti-patterns)
-   [Tailwind v4 Changes](#tailwind-v4-changes)

## Class Ordering

### Automatic Sorting (Recommended)

Use `prettier-plugin-tailwindcss` for consistent ordering:

```bash
npm install -D prettier prettier-plugin-tailwindcss
```

```json
// .prettierrc
{
    "plugins": ["prettier-plugin-tailwindcss"],
    "tailwindFunctions": ["cva", "cn", "clsx"]
}
```

### Manual Order Reference

When sorting manually, follow this order:

1. **Custom/Third-party classes** (e.g., `select2-dropdown`)
2. **Layout** (`flex`, `grid`, `block`, `hidden`)
3. **Position** (`relative`, `absolute`, `fixed`, `sticky`)
4. **Box Model** (`w-*`, `h-*`, `m-*`, `p-*`)
5. **Typography** (`text-*`, `font-*`, `leading-*`)
6. **Visual** (`bg-*`, `border-*`, `rounded-*`, `shadow-*`)
7. **Effects** (`opacity-*`, `transition-*`)
8. **State variants** (`hover:*`, `focus:*`, `active:*`)
9. **Responsive variants** (`sm:*`, `md:*`, `lg:*`, `xl:*`)

Example:

```html
<!-- Before (unsorted) -->
<div class="hover:bg-gray-100 p-4 flex text-sm bg-white rounded-lg md:p-6">
    <!-- After (sorted) -->
    <div
        class="flex p-4 text-sm bg-white rounded-lg hover:bg-gray-100 md:p-6"
    ></div>
</div>
```

## Responsive Design

### Mobile-First Approach

Always start with mobile styles, then add breakpoints:

```tsx
// Good: Mobile-first
<div className="text-sm p-2 md:text-base md:p-4 lg:text-lg lg:p-6" />

// Bad: Desktop-first (requires more overrides)
<div className="text-lg p-6 sm:text-sm sm:p-2" />
```

### Breakpoint Reference

| Breakpoint | Min Width | CSS                          |
| ---------- | --------- | ---------------------------- |
| `sm`       | 640px     | `@media (min-width: 640px)`  |
| `md`       | 768px     | `@media (min-width: 768px)`  |
| `lg`       | 1024px    | `@media (min-width: 1024px)` |
| `xl`       | 1280px    | `@media (min-width: 1280px)` |
| `2xl`      | 1536px    | `@media (min-width: 1536px)` |

### Targeting Specific Breakpoints

Use stacked modifiers for ranges (v3.2+):

```tsx
// Only apply between sm and xl
<div className="sm:max-xl:bg-blue-500" />

// Only on medium screens
<div className="md:max-lg:grid-cols-2" />
```

### Container Configuration

```css
/* tailwind.css (v4) */
@utility container {
    margin-inline: auto;
    padding-inline: 1rem;
}

@media (width >= 640px) {
    @utility container {
        padding-inline: 2rem;
    }
}
```

## Configuration

### Design Tokens

Centralize design decisions in config:

```js
// tailwind.config.js (v3)
module.exports = {
    theme: {
        extend: {
            colors: {
                primary: {
                    50: "oklch(97% 0.02 270)",
                    500: "oklch(65% 0.2 270)",
                    900: "oklch(30% 0.15 270)",
                },
                // Semantic colors
                success: "oklch(65% 0.2 145)",
                warning: "oklch(75% 0.15 85)",
                error: "oklch(55% 0.25 25)",
            },
            spacing: {
                4.5: "1.125rem",
                18: "4.5rem",
            },
            borderRadius: {
                "4xl": "2rem",
            },
            fontFamily: {
                sans: ["Inter var", "system-ui", "sans-serif"],
                mono: ["JetBrains Mono", "monospace"],
            },
        },
    },
};
```

### CSS Variables Integration

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
    :root {
        --background: 0 0% 100%;
        --foreground: 222.2 84% 4.9%;
        --primary: 221.2 83.2% 53.3%;
        --primary-foreground: 210 40% 98%;
        /* ... */
    }

    .dark {
        --background: 222.2 84% 4.9%;
        --foreground: 210 40% 98%;
        /* ... */
    }
}
```

### The cn() Utility

Essential for merging Tailwind classes:

```ts
// lib/utils.ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}
```

Usage:

```tsx
import { cn } from "@/lib/utils";

function Button({ className, variant, ...props }) {
    return (
        <button
            className={cn(
                "px-4 py-2 rounded-lg font-medium",
                variant === "primary" && "bg-primary text-white",
                variant === "secondary" && "bg-gray-100 text-gray-900",
                className // Allow overrides
            )}
            {...props}
        />
    );
}
```

## Common Patterns

### Flexbox Centering

```tsx
// Center both axes
<div className="flex items-center justify-center" />

// Center with gap
<div className="flex items-center gap-2" />

// Space between with wrapping
<div className="flex flex-wrap items-center justify-between gap-4" />
```

### Grid Layouts

```tsx
// Responsive grid
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4" />

// Auto-fit for dynamic columns
<div className="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4" />

// Named grid areas (use sparingly)
<div className="grid grid-cols-[1fr_2fr] grid-rows-[auto_1fr_auto]">
  <header className="col-span-2" />
  <aside />
  <main />
  <footer className="col-span-2" />
</div>
```

### Truncation

```tsx
// Single line
<p className="truncate" />

// Multi-line (webkit)
<p className="line-clamp-3" />
```

### Aspect Ratios

```tsx
<div className="aspect-video" />      // 16:9
<div className="aspect-square" />     // 1:1
<div className="aspect-[4/3]" />      // Custom
```

### Focus States

```tsx
// Standard focus ring
<button className="focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2" />

// Focus within (for containers)
<div className="focus-within:ring-2 focus-within:ring-primary">
  <input />
</div>
```

## Anti-Patterns

### ❌ Dynamic Class Construction

```tsx
// Bad - Tailwind can't detect these classes
const color = "blue";
<div className={`bg-${color}-500`} />;

// Good - Use complete class names
const bgColors = {
    blue: "bg-blue-500",
    red: "bg-red-500",
};
<div className={bgColors[color]} />;
```

### ❌ Arbitrary Values Overuse

```tsx
// Bad - Creates unique CSS rules, defeats caching
<div className="mt-[23px] w-[847px] text-[13px]" />

// Good - Use design system values or extend config
<div className="mt-6 w-full max-w-4xl text-sm" />
```

### ❌ @apply Overuse

```css
/* Bad - Defeats utility-first benefits */
.btn {
    @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2;
}

/* Acceptable - For third-party integration or complex selectors */
.prose code {
    @apply rounded bg-gray-100 px-1 py-0.5 text-sm;
}
```

### ❌ Inline Important

```tsx
// Bad - Specificity wars
<div className="!mt-0" />

// Good - Fix the source of the conflict
// Or use className merging with cn()
```

### ❌ Ignoring Responsive Prefixes

```tsx
// Bad - Fixed values break on mobile
<div className="w-[500px]" />

// Good - Responsive constraints
<div className="w-full max-w-lg" />
```

## Tailwind v4 Changes

### CSS-First Configuration

```css
/* tailwind.css (v4) */
@import "tailwindcss";

@theme {
    --color-primary: oklch(65% 0.2 270);
    --font-sans: "Inter var", system-ui, sans-serif;
    --spacing-4\.5: 1.125rem;
}
```

### New Utilities

```tsx
// nth-child targeting
<li className="nth-3:bg-gray-100" />
<li className="nth-last-2:font-bold" />

// Container queries (native)
<div className="@container">
  <div className="@md:flex @lg:grid" />
</div>
```

### Deprecated Classes

| v3                 | v4                     |
| ------------------ | ---------------------- |
| `decoration-slice` | `box-decoration-slice` |
| `decoration-clone` | `box-decoration-clone` |
| `flex-grow`        | `grow`                 |
| `flex-shrink`      | `shrink`               |

### PostCSS Changes

v4 uses Lightning CSS by default. Update build config:

```js
// postcss.config.js (v4)
export default {
    plugins: {
        "@tailwindcss/postcss": {},
    },
};
```

## Performance Tips

1. **Use PurgeCSS** (automatic in production builds)
2. **Avoid arbitrary values** when possible
3. **Use `@layer`** for custom CSS to enable purging
4. **Split large configs** with `presets`
5. **Use CSS variables** for theme values that change at runtime
