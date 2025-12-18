# Accessibility Reference

WCAG 2.1 AA/AAA compliance guide for React components with practical patterns and testing strategies.

## Table of Contents

-   [WCAG Quick Reference](#wcag-quick-reference)
-   [Keyboard Navigation](#keyboard-navigation)
-   [Focus Management](#focus-management)
-   [ARIA Patterns](#aria-patterns)
-   [Color & Contrast](#color--contrast)
-   [Motion & Animation](#motion--animation)
-   [Forms](#forms)
-   [Testing](#testing)
-   [Common Fixes](#common-fixes)

## WCAG Quick Reference

### Level AA Requirements (Must Have)

| Criterion                      | Requirement                          | How to Test                                    |
| ------------------------------ | ------------------------------------ | ---------------------------------------------- |
| **1.1.1** Text Alternatives    | All images have `alt` text           | Inspect images, check decorative have `alt=""` |
| **1.3.1** Info & Relationships | Semantic HTML, proper headings       | Validate heading hierarchy                     |
| **1.4.3** Contrast (Minimum)   | 4.5:1 for text, 3:1 for large text   | Use contrast checker tool                      |
| **1.4.4** Resize Text          | Text resizable to 200% without loss  | Zoom browser to 200%                           |
| **1.4.11** Non-text Contrast   | 3:1 for UI components and graphics   | Check button borders, icons                    |
| **2.1.1** Keyboard             | All functionality via keyboard       | Tab through entire page                        |
| **2.1.2** No Keyboard Trap     | Can exit any component with keyboard | Tab in and out of modals                       |
| **2.4.3** Focus Order          | Logical tab sequence                 | Tab through page, verify order                 |
| **2.4.4** Link Purpose         | Link text describes destination      | Read links out of context                      |
| **2.4.7** Focus Visible        | Visible focus indicator              | Tab through, check focus rings                 |
| **3.1.1** Language of Page     | `lang` attribute on `<html>`         | Check document head                            |
| **4.1.2** Name, Role, Value    | Components have accessible names     | Test with screen reader                        |

### Level AAA Requirements (Should Have)

| Criterion                          | Requirement                        |
| ---------------------------------- | ---------------------------------- |
| **1.4.6** Enhanced Contrast        | 7:1 for text, 4.5:1 for large text |
| **2.4.8** Location                 | Breadcrumbs or site map            |
| **2.4.9** Link Purpose (Link Only) | Link purpose from link text alone  |
| **3.2.5** Change on Request        | No automatic context changes       |

## Keyboard Navigation

### Required Keyboard Support

| Key            | Expected Behavior                        |
| -------------- | ---------------------------------------- |
| `Tab`          | Move to next focusable element           |
| `Shift + Tab`  | Move to previous focusable element       |
| `Enter`        | Activate buttons, links, submit forms    |
| `Space`        | Activate buttons, toggle checkboxes      |
| `Escape`       | Close modals, dropdowns, dismiss         |
| `Arrow keys`   | Navigate within components (menus, tabs) |
| `Home` / `End` | Jump to first/last item in list          |

### Focusable Elements

```tsx
// Naturally focusable (tabindex not needed)
<button>Click me</button>
<a href="/page">Link</a>
<input type="text" />
<select><option>Option</option></select>
<textarea />

// Made focusable with tabindex
<div tabIndex={0} role="button" onClick={handleClick} onKeyDown={handleKeyDown}>
  Custom button
</div>

// Removed from tab order but programmatically focusable
<div tabIndex={-1} ref={errorRef}>
  Error message
</div>

// Never use tabindex > 0
// ❌ <div tabIndex={1}>Bad</div>
```

### Keyboard Event Handling

```tsx
function CustomButton({
    onClick,
    children,
}: {
    onClick: () => void;
    children: React.ReactNode;
}) {
    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            onClick();
        }
    };

    return (
        <div
            role="button"
            tabIndex={0}
            onClick={onClick}
            onKeyDown={handleKeyDown}
            className="cursor-pointer rounded bg-primary px-4 py-2 text-white focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        >
            {children}
        </div>
    );
}
```

### Roving TabIndex Pattern

For composite widgets like tabs or menus:

```tsx
function TabList({ tabs, activeTab, onTabChange }) {
    const [focusedIndex, setFocusedIndex] = useState(0);
    const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

    const handleKeyDown = (event: React.KeyboardEvent, index: number) => {
        let newIndex = index;

        switch (event.key) {
            case "ArrowRight":
                newIndex = (index + 1) % tabs.length;
                break;
            case "ArrowLeft":
                newIndex = (index - 1 + tabs.length) % tabs.length;
                break;
            case "Home":
                newIndex = 0;
                break;
            case "End":
                newIndex = tabs.length - 1;
                break;
            default:
                return;
        }

        event.preventDefault();
        setFocusedIndex(newIndex);
        tabRefs.current[newIndex]?.focus();
    };

    return (
        <div role="tablist">
            {tabs.map((tab, index) => (
                <button
                    key={tab.id}
                    ref={(el) => (tabRefs.current[index] = el)}
                    role="tab"
                    aria-selected={activeTab === tab.id}
                    tabIndex={focusedIndex === index ? 0 : -1}
                    onClick={() => onTabChange(tab.id)}
                    onKeyDown={(e) => handleKeyDown(e, index)}
                >
                    {tab.label}
                </button>
            ))}
        </div>
    );
}
```

## Focus Management

### Focus Visible Styles

```css
/* globals.css */
@layer base {
    /* Remove default outline, add custom focus-visible */
    *:focus {
        outline: none;
    }

    *:focus-visible {
        outline: 2px solid hsl(var(--ring));
        outline-offset: 2px;
    }

    /* For components where outline doesn't work well */
    .focus-ring:focus-visible {
        outline: none;
        box-shadow: 0 0 0 2px hsl(var(--background)), 0 0 0 4px hsl(var(--ring));
    }
}
```

### Focus Trap for Modals

```tsx
import { useEffect, useRef } from "react";

function useFocusTrap(isOpen: boolean) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!isOpen) return;

        const container = containerRef.current;
        if (!container) return;

        const focusableElements = container.querySelectorAll<HTMLElement>(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        // Focus first element
        firstElement?.focus();

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key !== "Tab") return;

            if (event.shiftKey) {
                if (document.activeElement === firstElement) {
                    event.preventDefault();
                    lastElement?.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    event.preventDefault();
                    firstElement?.focus();
                }
            }
        };

        container.addEventListener("keydown", handleKeyDown);
        return () => container.removeEventListener("keydown", handleKeyDown);
    }, [isOpen]);

    return containerRef;
}
```

### Restore Focus After Modal

```tsx
function Modal({ isOpen, onClose, children }) {
    const previousActiveElement = useRef<HTMLElement | null>(null);
    const modalRef = useFocusTrap(isOpen);

    useEffect(() => {
        if (isOpen) {
            previousActiveElement.current =
                document.activeElement as HTMLElement;
        } else {
            previousActiveElement.current?.focus();
        }
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div ref={modalRef} role="dialog" aria-modal="true">
            {children}
        </div>
    );
}
```

## ARIA Patterns

### Common ARIA Attributes

| Attribute          | Purpose                       | Example                                 |
| ------------------ | ----------------------------- | --------------------------------------- |
| `aria-label`       | Provides accessible name      | `<button aria-label="Close">×</button>` |
| `aria-labelledby`  | References element with label | `<div aria-labelledby="heading-id">`    |
| `aria-describedby` | References description        | `<input aria-describedby="hint-id">`    |
| `aria-hidden`      | Hides from assistive tech     | `<span aria-hidden="true">🎉</span>`    |
| `aria-live`        | Announces dynamic content     | `<div aria-live="polite">`              |
| `aria-expanded`    | Indicates expandable state    | `<button aria-expanded="false">`        |
| `aria-controls`    | References controlled element | `<button aria-controls="menu-id">`      |
| `aria-current`     | Indicates current item        | `<a aria-current="page">Home</a>`       |
| `aria-invalid`     | Indicates validation error    | `<input aria-invalid="true">`           |
| `aria-required`    | Indicates required field      | `<input aria-required="true">`          |

### Accessible Icon Button

```tsx
// Method 1: aria-label
<button aria-label="Close dialog">
  <XIcon aria-hidden="true" />
</button>

// Method 2: Visually hidden text
<button>
  <span className="sr-only">Close dialog</span>
  <XIcon aria-hidden="true" />
</button>

// sr-only utility
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

### Live Regions

```tsx
// Polite announcements (waits for user to stop)
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// Assertive announcements (interrupts immediately)
<div aria-live="assertive" role="alert">
  {errorMessage}
</div>

// Status messages
<div role="status" aria-live="polite">
  Loading... {progress}%
</div>
```

### Disclosure Pattern (Accordion)

```tsx
function Accordion({ title, children }) {
    const [isOpen, setIsOpen] = useState(false);
    const contentId = useId();

    return (
        <div>
            <button
                aria-expanded={isOpen}
                aria-controls={contentId}
                onClick={() => setIsOpen(!isOpen)}
            >
                {title}
                <ChevronIcon
                    className={isOpen ? "rotate-180" : ""}
                    aria-hidden="true"
                />
            </button>
            <div
                id={contentId}
                role="region"
                aria-labelledby={/* button id */}
                hidden={!isOpen}
            >
                {children}
            </div>
        </div>
    );
}
```

## Color & Contrast

### Contrast Requirements

| Element Type                     | AA Minimum | AAA Enhanced |
| -------------------------------- | ---------- | ------------ |
| Normal text (< 18pt)             | 4.5:1      | 7:1          |
| Large text (≥ 18pt or 14pt bold) | 3:1        | 4.5:1        |
| UI components (borders, icons)   | 3:1        | 3:1          |
| Focus indicators                 | 3:1        | 3:1          |

### Testing Contrast

```tsx
// Use CSS custom properties for consistent colors
:root {
  --text-primary: hsl(0 0% 9%);      /* Very dark for body text */
  --text-secondary: hsl(0 0% 32%);   /* Dark gray for secondary */
  --text-muted: hsl(0 0% 45%);       /* Meets 4.5:1 on white */
  --background: hsl(0 0% 100%);
}

/* Avoid this - too low contrast */
.bad-text {
  color: hsl(0 0% 60%); /* Only ~3:1 on white */
}
```

### Color Not Sole Indicator

```tsx
// ❌ Bad: Color only indicates error
<input className={hasError ? "border-red-500" : "border-gray-300"} />

// ✅ Good: Color + icon + text
<div>
  <input
    className={hasError ? "border-red-500" : "border-gray-300"}
    aria-invalid={hasError}
    aria-describedby={hasError ? "error-message" : undefined}
  />
  {hasError && (
    <p id="error-message" className="text-red-500 flex items-center gap-1">
      <AlertCircle className="h-4 w-4" aria-hidden="true" />
      This field is required
    </p>
  )}
</div>
```

## Motion & Animation

### Respecting Reduced Motion

```css
/* CSS approach */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

```tsx
// React approach
import { useReducedMotion } from "framer-motion";

function AnimatedComponent() {
    const prefersReducedMotion = useReducedMotion();

    return (
        <motion.div
            initial={prefersReducedMotion ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={
                prefersReducedMotion ? { duration: 0 } : { duration: 0.3 }
            }
        />
    );
}
```

### Safe Animation Properties

```tsx
// GPU-accelerated, less likely to cause issues
<motion.div
  animate={{
    opacity: 1,        // ✅ Safe
    transform: "...",  // ✅ Safe (translateX, translateY, scale, rotate)
  }}
/>

// Can cause layout shifts, use carefully
<motion.div
  animate={{
    width: "100px",    // ⚠️ Causes layout shift
    height: "100px",   // ⚠️ Causes layout shift
    margin: "10px",    // ⚠️ Causes layout shift
  }}
/>
```

## Forms

### Accessible Form Pattern

```tsx
function ContactForm() {
    const [errors, setErrors] = useState<Record<string, string>>({});

    return (
        <form aria-describedby="form-instructions">
            <p id="form-instructions" className="sr-only">
                Required fields are marked with an asterisk.
            </p>

            <div className="space-y-4">
                <div>
                    <label htmlFor="name" className="block font-medium">
                        Name
                        <span aria-hidden="true" className="text-red-500 ml-1">
                            *
                        </span>
                        <span className="sr-only">(required)</span>
                    </label>
                    <input
                        id="name"
                        type="text"
                        required
                        aria-required="true"
                        aria-invalid={!!errors.name}
                        aria-describedby={
                            errors.name ? "name-error" : undefined
                        }
                        className="mt-1 block w-full rounded border px-3 py-2"
                    />
                    {errors.name && (
                        <p
                            id="name-error"
                            role="alert"
                            className="mt-1 text-sm text-red-500"
                        >
                            {errors.name}
                        </p>
                    )}
                </div>

                <div>
                    <label htmlFor="email" className="block font-medium">
                        Email
                        <span aria-hidden="true" className="text-red-500 ml-1">
                            *
                        </span>
                        <span className="sr-only">(required)</span>
                    </label>
                    <input
                        id="email"
                        type="email"
                        required
                        aria-required="true"
                        aria-invalid={!!errors.email}
                        aria-describedby="email-hint email-error"
                        className="mt-1 block w-full rounded border px-3 py-2"
                    />
                    <p id="email-hint" className="mt-1 text-sm text-gray-500">
                        We'll never share your email.
                    </p>
                    {errors.email && (
                        <p
                            id="email-error"
                            role="alert"
                            className="mt-1 text-sm text-red-500"
                        >
                            {errors.email}
                        </p>
                    )}
                </div>

                <button
                    type="submit"
                    className="rounded bg-primary px-4 py-2 text-white"
                >
                    Submit
                </button>
            </div>
        </form>
    );
}
```

### Error Summary

```tsx
function ErrorSummary({ errors }: { errors: Record<string, string> }) {
    const errorList = Object.entries(errors);

    if (errorList.length === 0) return null;

    return (
        <div
            role="alert"
            aria-labelledby="error-summary-title"
            className="rounded border border-red-500 bg-red-50 p-4"
        >
            <h2 id="error-summary-title" className="font-medium text-red-800">
                There {errorList.length === 1 ? "is" : "are"} {errorList.length}{" "}
                error
                {errorList.length === 1 ? "" : "s"} in the form
            </h2>
            <ul className="mt-2 list-inside list-disc text-red-700">
                {errorList.map(([field, message]) => (
                    <li key={field}>
                        <a href={`#${field}`} className="underline">
                            {message}
                        </a>
                    </li>
                ))}
            </ul>
        </div>
    );
}
```

## Testing

### Automated Testing Tools

```bash
# axe-core with Playwright
npm install -D @axe-core/playwright

# axe-core with Cypress
npm install -D cypress-axe

# eslint-plugin-jsx-a11y
npm install -D eslint-plugin-jsx-a11y
```

### Playwright + axe Example

```ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("should not have accessibility violations", async ({ page }) => {
    await page.goto("/");

    const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa"])
        .analyze();

    expect(results.violations).toEqual([]);
});
```

### Manual Testing Checklist

1. **Keyboard navigation**

    - [ ] Tab through entire page
    - [ ] No keyboard traps
    - [ ] Logical focus order
    - [ ] All controls reachable

2. **Screen reader**

    - [ ] Test with VoiceOver (Mac) or NVDA (Windows)
    - [ ] All content announced
    - [ ] Images have alt text
    - [ ] Form labels read correctly

3. **Visual**

    - [ ] 200% zoom works
    - [ ] High contrast mode works
    - [ ] Focus indicators visible
    - [ ] Color not sole indicator

4. **Motion**
    - [ ] Test with reduced motion enabled
    - [ ] No flashing content (< 3 flashes/sec)

## Common Fixes

### Missing Button Labels

```tsx
// ❌ Problem
<button><SearchIcon /></button>

// ✅ Fix
<button aria-label="Search">
  <SearchIcon aria-hidden="true" />
</button>
```

### Non-Interactive Elements with Click Handlers

```tsx
// ❌ Problem
<div onClick={handleClick}>Click me</div>

// ✅ Fix
<button onClick={handleClick}>Click me</button>

// ✅ Or if must be div
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => e.key === "Enter" && handleClick()}
>
  Click me
</div>
```

### Missing Form Labels

```tsx
// ❌ Problem
<input type="text" placeholder="Email" />

// ✅ Fix
<label>
  Email
  <input type="email" />
</label>

// ✅ Or with ID
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// ✅ Or visually hidden
<label htmlFor="search" className="sr-only">Search</label>
<input id="search" type="search" placeholder="Search..." />
```

### Focus Not Visible

```tsx
// ❌ Problem
<button className="outline-none">Button</button>

// ✅ Fix
<button className="outline-none focus-visible:ring-2 focus-visible:ring-primary">
  Button
</button>
```

### Color-Only Error States

```tsx
// ❌ Problem
<input className={error ? "border-red-500" : ""} />

// ✅ Fix
<input
  className={error ? "border-red-500" : ""}
  aria-invalid={!!error}
  aria-describedby={error ? "error-msg" : undefined}
/>
{error && (
  <span id="error-msg" role="alert">
    <AlertIcon aria-hidden="true" /> {error}
  </span>
)}
```
