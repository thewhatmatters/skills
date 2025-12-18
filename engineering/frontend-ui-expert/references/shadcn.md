# shadcn/ui Reference

Complete guide for building with shadcn/ui components, composition patterns, and theming.

## Table of Contents

-   [Core Concepts](#core-concepts)
-   [Installation & Setup](#installation--setup)
-   [Component Composition](#component-composition)
-   [CVA Variants](#cva-variants)
-   [Form Integration](#form-integration)
-   [Theming](#theming)
-   [Common Components](#common-components)
-   [Best Practices](#best-practices)

## Core Concepts

### What shadcn/ui Is (and Isn't)

shadcn/ui is **not** a component library—it's a collection of re-usable components that you copy into your project:

-   **Open Code**: You own the code, modify freely
-   **Composition**: Components share consistent APIs
-   **Accessible**: Built on Radix UI primitives
-   **Customizable**: Full control over styling

### Key Principles

1. **Copy, don't install**: Components live in your codebase
2. **Extend, don't modify**: Wrap components to add features
3. **Compose, don't configure**: Build complex UIs from simple parts
4. **Accessible by default**: Radix handles keyboard/screen reader

## Installation & Setup

### Initial Setup

```bash
npx shadcn@latest init
```

Configuration prompts:

-   Style: `new-york` (recommended) or `default`
-   Base color: Choose your primary
-   CSS variables: `yes` (recommended)
-   Path aliases: `@/components`, `@/lib`

### Adding Components

```bash
# Single component
npx shadcn@latest add button

# Multiple components
npx shadcn@latest add button card dialog

# All components
npx shadcn@latest add --all
```

### components.json

```json
{
    "$schema": "https://ui.shadcn.com/schema.json",
    "style": "new-york",
    "rsc": true,
    "tsx": true,
    "tailwind": {
        "config": "tailwind.config.ts",
        "css": "app/globals.css",
        "baseColor": "zinc",
        "cssVariables": true
    },
    "aliases": {
        "components": "@/components",
        "utils": "@/lib/utils",
        "ui": "@/components/ui",
        "lib": "@/lib",
        "hooks": "@/hooks"
    }
}
```

## Component Composition

### The Wrapper Pattern

Never modify source files in `components/ui/`. Instead, create wrappers:

```tsx
// components/loading-button.tsx
import { forwardRef } from "react";
import { Button, ButtonProps } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export interface LoadingButtonProps extends ButtonProps {
    isLoading?: boolean;
    loadingText?: string;
}

export const LoadingButton = forwardRef<HTMLButtonElement, LoadingButtonProps>(
    (
        { isLoading, loadingText, children, disabled, className, ...props },
        ref
    ) => {
        return (
            <Button
                ref={ref}
                disabled={isLoading || disabled}
                className={cn(isLoading && "cursor-wait", className)}
                {...props}
            >
                {isLoading ? (
                    <>
                        <Loader2
                            className="mr-2 h-4 w-4 animate-spin"
                            aria-hidden="true"
                        />
                        <span>{loadingText ?? children}</span>
                    </>
                ) : (
                    children
                )}
            </Button>
        );
    }
);
LoadingButton.displayName = "LoadingButton";
```

### Compound Components

Build complex components from primitives:

```tsx
// components/stat-card.tsx
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
    title: string;
    value: string | number;
    description?: string;
    trend?: "up" | "down" | "neutral";
    className?: string;
}

export function StatCard({
    title,
    value,
    description,
    trend,
    className,
}: StatCardProps) {
    return (
        <Card className={cn("", className)}>
            <CardHeader className="pb-2">
                <CardDescription>{title}</CardDescription>
                <CardTitle className="text-3xl tabular-nums">
                    {value}
                    {trend && (
                        <span
                            className={cn(
                                "ml-2 text-sm font-medium",
                                trend === "up" && "text-green-600",
                                trend === "down" && "text-red-600"
                            )}
                        >
                            {trend === "up"
                                ? "↑"
                                : trend === "down"
                                ? "↓"
                                : "→"}
                        </span>
                    )}
                </CardTitle>
            </CardHeader>
            {description && (
                <CardContent>
                    <p className="text-xs text-muted-foreground">
                        {description}
                    </p>
                </CardContent>
            )}
        </Card>
    );
}
```

### forwardRef Pattern

Always use `forwardRef` for components that wrap native elements:

```tsx
import { forwardRef, ComponentPropsWithoutRef } from "react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface SearchInputProps extends ComponentPropsWithoutRef<typeof Input> {
    onSearch?: (value: string) => void;
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
    ({ className, onSearch, ...props }, ref) => {
        return (
            <div className="relative">
                <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                    ref={ref}
                    type="search"
                    className={cn("pl-10", className)}
                    onChange={(e) => onSearch?.(e.target.value)}
                    {...props}
                />
            </div>
        );
    }
);
SearchInput.displayName = "SearchInput";
```

## CVA Variants

### Class Variance Authority

shadcn uses CVA for variant management:

```tsx
// components/ui/badge.tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
    "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
    {
        variants: {
            variant: {
                default:
                    "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
                secondary:
                    "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
                destructive:
                    "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
                outline: "text-foreground",
            },
        },
        defaultVariants: {
            variant: "default",
        },
    }
);

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
        VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
    return (
        <div className={cn(badgeVariants({ variant }), className)} {...props} />
    );
}

export { Badge, badgeVariants };
```

### Extending Variants

Add custom variants without modifying source:

```tsx
// components/status-badge.tsx
import { Badge, badgeVariants } from "@/components/ui/badge";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const statusVariants = cva("", {
    variants: {
        status: {
            success: "bg-green-100 text-green-800 border-green-200",
            warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
            error: "bg-red-100 text-red-800 border-red-200",
            info: "bg-blue-100 text-blue-800 border-blue-200",
        },
    },
});

interface StatusBadgeProps extends React.ComponentProps<typeof Badge> {
    status: "success" | "warning" | "error" | "info";
}

export function StatusBadge({ status, className, ...props }: StatusBadgeProps) {
    return (
        <Badge
            variant="outline"
            className={cn(statusVariants({ status }), className)}
            {...props}
        />
    );
}
```

## Form Integration

### React Hook Form + Zod

```tsx
"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

const formSchema = z.object({
    email: z.string().email("Invalid email address"),
    password: z.string().min(8, "Password must be at least 8 characters"),
});

type FormValues = z.infer<typeof formSchema>;

export function LoginForm() {
    const form = useForm<FormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            email: "",
            password: "",
        },
    });

    async function onSubmit(values: FormValues) {
        // Handle submission
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Email</FormLabel>
                            <FormControl>
                                <Input
                                    type="email"
                                    placeholder="you@example.com"
                                    {...field}
                                />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Password</FormLabel>
                            <FormControl>
                                <Input type="password" {...field} />
                            </FormControl>
                            <FormDescription>
                                Must be at least 8 characters
                            </FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <Button type="submit" disabled={form.formState.isSubmitting}>
                    {form.formState.isSubmitting ? "Signing in..." : "Sign in"}
                </Button>
            </form>
        </Form>
    );
}
```

### Accessible Form Patterns

```tsx
<FormField
    control={form.control}
    name="username"
    render={({ field, fieldState }) => (
        <FormItem>
            <FormLabel>
                Username
                <span className="text-destructive ml-1" aria-hidden="true">
                    *
                </span>
                <span className="sr-only">(required)</span>
            </FormLabel>
            <FormControl>
                <Input
                    {...field}
                    aria-required="true"
                    aria-invalid={!!fieldState.error}
                    aria-describedby={
                        fieldState.error
                            ? "username-error"
                            : "username-description"
                    }
                />
            </FormControl>
            <FormDescription id="username-description">
                3-20 characters, letters and numbers only
            </FormDescription>
            <FormMessage id="username-error" role="alert" />
        </FormItem>
    )}
/>
```

## Theming

### CSS Variables

```css
/* globals.css */
@layer base {
    :root {
        --background: 0 0% 100%;
        --foreground: 240 10% 3.9%;
        --card: 0 0% 100%;
        --card-foreground: 240 10% 3.9%;
        --popover: 0 0% 100%;
        --popover-foreground: 240 10% 3.9%;
        --primary: 240 5.9% 10%;
        --primary-foreground: 0 0% 98%;
        --secondary: 240 4.8% 95.9%;
        --secondary-foreground: 240 5.9% 10%;
        --muted: 240 4.8% 95.9%;
        --muted-foreground: 240 3.8% 46.1%;
        --accent: 240 4.8% 95.9%;
        --accent-foreground: 240 5.9% 10%;
        --destructive: 0 84.2% 60.2%;
        --destructive-foreground: 0 0% 98%;
        --border: 240 5.9% 90%;
        --input: 240 5.9% 90%;
        --ring: 240 5.9% 10%;
        --radius: 0.5rem;
    }

    .dark {
        --background: 240 10% 3.9%;
        --foreground: 0 0% 98%;
        /* ... dark theme values */
    }
}
```

### Dark Mode

```tsx
// components/theme-provider.tsx
"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import { type ThemeProviderProps } from "next-themes";

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
    return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}

// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider";

export default function RootLayout({ children }) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body>
                <ThemeProvider
                    attribute="class"
                    defaultTheme="system"
                    enableSystem
                    disableTransitionOnChange
                >
                    {children}
                </ThemeProvider>
            </body>
        </html>
    );
}
```

### Theme Toggle

```tsx
"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
    const { theme, setTheme } = useTheme();

    return (
        <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-transform dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-transform dark:rotate-0 dark:scale-100" />
        </Button>
    );
}
```

## Common Components

### Dialog with Form

```tsx
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";

export function EditProfileDialog() {
    const [open, setOpen] = useState(false);

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="outline">Edit Profile</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Edit profile</DialogTitle>
                    <DialogDescription>
                        Make changes to your profile here. Click save when
                        you're done.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit}>
                    {/* Form fields */}
                    <DialogFooter>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => setOpen(false)}
                        >
                            Cancel
                        </Button>
                        <Button type="submit">Save changes</Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
```

### Data Table

```tsx
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

interface DataTableProps<T> {
    columns: { key: keyof T; header: string }[];
    data: T[];
}

export function DataTable<T extends { id: string }>({
    columns,
    data,
}: DataTableProps<T>) {
    return (
        <div className="rounded-md border">
            <Table>
                <TableHeader>
                    <TableRow>
                        {columns.map((column) => (
                            <TableHead key={String(column.key)}>
                                {column.header}
                            </TableHead>
                        ))}
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {data.map((row) => (
                        <TableRow key={row.id}>
                            {columns.map((column) => (
                                <TableCell key={String(column.key)}>
                                    {String(row[column.key])}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}
```

## Best Practices

### Do's

-   ✅ Use `cn()` for all class merging
-   ✅ Wrap components to extend, don't modify source
-   ✅ Use TypeScript for prop types
-   ✅ Forward refs on interactive components
-   ✅ Keep accessibility attributes intact
-   ✅ Use semantic color names (`primary`, `muted`)

### Don'ts

-   ❌ Modify files in `components/ui/` directly
-   ❌ Use string concatenation for classes
-   ❌ Remove ARIA attributes from Radix components
-   ❌ Override focus-visible styles without replacement
-   ❌ Hardcode colors instead of CSS variables
-   ❌ Skip the Form wrapper for react-hook-form
