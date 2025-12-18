# Aceternity UI Reference

Guide for using Aceternity UI animated components effectively, with performance and accessibility considerations.

## Table of Contents

-   [Overview](#overview)
-   [Setup](#setup)
-   [When to Use (Decision Matrix)](#when-to-use-decision-matrix)
-   [Performance Cost Matrix](#performance-cost-matrix)
-   [Component Categories](#component-categories)
-   [Accessibility Concerns](#accessibility-concerns)
-   [Performance Optimization](#performance-optimization)
-   [Common Patterns](#common-patterns)

## Overview

Aceternity UI provides animated React components built with Framer Motion and Tailwind CSS. These are copy-paste components designed for marketing pages, portfolios, and high-impact sections.

### Key Characteristics

-   **Visual impact**: Designed for wow-factor, not utility
-   **Copy-paste**: No npm package, copy code directly
-   **Framer Motion**: Heavy animation dependency
-   **Performance cost**: Higher than static components
-   **Not accessible by default**: Requires additional work

### When Aceternity is Right

✅ Landing pages and hero sections
✅ Marketing and promotional content
✅ Portfolio showcases
✅ Product demos
✅ Low-data-density pages

### When Aceternity is Wrong

❌ Data-dense dashboards
❌ Form-heavy interfaces
❌ E-commerce checkout flows
❌ Content-focused reading experiences
❌ Mobile-first applications with slow networks

## Setup

### Dependencies

```bash
npm install framer-motion clsx tailwind-merge
```

For React 19 / Next.js 15, use the `motion` package:

```json
{
    "dependencies": {
        "motion": "^12.0.0"
    },
    "overrides": {
        "motion": {
            "react": "^19.0.0",
            "react-dom": "^19.0.0"
        }
    }
}
```

### Utility Function

```ts
// lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}
```

### Tailwind Configuration

```js
// tailwind.config.js
module.exports = {
    content: [
        "./app/**/*.{js,ts,jsx,tsx}",
        "./components/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            animation: {
                spotlight: "spotlight 2s ease .75s 1 forwards",
                shimmer: "shimmer 2s linear infinite",
                "border-beam":
                    "border-beam calc(var(--duration)*1s) infinite linear",
            },
            keyframes: {
                spotlight: {
                    "0%": {
                        opacity: 0,
                        transform: "translate(-72%, -62%) scale(0.5)",
                    },
                    "100%": {
                        opacity: 1,
                        transform: "translate(-50%,-40%) scale(1)",
                    },
                },
                shimmer: {
                    from: { backgroundPosition: "0 0" },
                    to: { backgroundPosition: "-200% 0" },
                },
            },
        },
    },
};
```

## When to Use (Decision Matrix)

### Context-Based Decision

| Context             | Aceternity? | Reasoning                                |
| ------------------- | ----------- | ---------------------------------------- |
| **Hero section**    | ✅ Yes      | High impact, first impression            |
| **Features grid**   | ⚠️ Maybe    | Depends on content density               |
| **Pricing table**   | ❌ No       | Users need to compare, not be distracted |
| **Dashboard**       | ❌ No       | Data focus, performance critical         |
| **Blog/article**    | ❌ No       | Reading focus, accessibility             |
| **Contact form**    | ❌ No       | Task completion focus                    |
| **Portfolio**       | ✅ Yes      | Showcasing creativity                    |
| **404 page**        | ✅ Yes      | Low stakes, brand moment                 |
| **Settings page**   | ❌ No       | Utility focus                            |
| **Onboarding flow** | ⚠️ Maybe    | Sparingly, for delight                   |

### User Context Decision

| User Situation     | Aceternity? | Reasoning                      |
| ------------------ | ----------- | ------------------------------ |
| First-time visitor | ✅ Yes      | Make an impression             |
| Returning user     | ⚠️ Less     | They know you, reduce friction |
| Mobile user        | ⚠️ Reduced  | Performance, battery           |
| Slow connection    | ❌ No       | Prioritize content             |
| Power user         | ❌ No       | Efficiency over aesthetics     |

## Performance Cost Matrix

### Component Performance Tiers

| Tier        | Components                          | GPU Load  | CPU Load | Recommended Use        |
| ----------- | ----------------------------------- | --------- | -------- | ---------------------- |
| **Light**   | Text effects, simple hovers         | Low       | Low      | Anywhere appropriate   |
| **Medium**  | Card effects, scroll animations     | Medium    | Low      | Above the fold         |
| **Heavy**   | Particle effects, 3D transforms     | High      | Medium   | Hero only              |
| **Extreme** | Canvas effects, physics simulations | Very High | High     | Rarely, with fallbacks |

### Specific Component Costs

| Component             | Performance | Mobile Safe?    | Notes                            |
| --------------------- | ----------- | --------------- | -------------------------------- |
| `SparklesCore`        | Heavy       | ⚠️ Reduce count | Reduce `particleCount` on mobile |
| `BackgroundBeams`     | Medium      | ✅ Yes          | GPU-accelerated                  |
| `CardHoverEffect`     | Light       | ✅ Yes          | Simple transforms                |
| `LampEffect`          | Medium      | ✅ Yes          | CSS-only option available        |
| `Vortex`              | Extreme     | ❌ No           | Desktop only                     |
| `BackgroundGradient`  | Light       | ✅ Yes          | Pure CSS                         |
| `InfiniteMovingCards` | Medium      | ⚠️ Reduce speed | Lower on mobile                  |
| `3DCardEffect`        | Heavy       | ⚠️ Simplify     | Disable tilt on touch            |
| `TextGenerateEffect`  | Light       | ✅ Yes          | Text only                        |
| `TypewriterEffect`    | Light       | ✅ Yes          | Text only                        |

## Component Categories

### Background Effects

Use behind content, not as content:

```tsx
// Background Beams - Medium cost, good for heroes
import { BackgroundBeams } from "@/components/ui/background-beams";

function HeroSection() {
    return (
        <div className="relative h-screen w-full bg-neutral-950">
            <div className="relative z-10">
                <h1>Your Content</h1>
            </div>
            <BackgroundBeams className="absolute inset-0" />
        </div>
    );
}
```

### Card Effects

Interactive cards with hover states:

```tsx
// Card Hover Effect - Light cost
import { HoverEffect } from "@/components/ui/card-hover-effect";

const projects = [
    { title: "Project 1", description: "Description", link: "/project-1" },
    // ...
];

function ProjectsGrid() {
    return <HoverEffect items={projects} />;
}
```

### Text Effects

Animated text reveals:

```tsx
// Text Generate Effect - Light cost
import { TextGenerateEffect } from "@/components/ui/text-generate-effect";

function Headline() {
    return (
        <TextGenerateEffect
            words="Build amazing products"
            className="text-4xl font-bold"
        />
    );
}
```

### Scroll Effects

Animations triggered by scroll:

```tsx
// Sticky Scroll Reveal - Medium cost
import { StickyScroll } from "@/components/ui/sticky-scroll-reveal";

const content = [
    {
        title: "Feature 1",
        description: "Description...",
        content: (
            <div className="h-full w-full bg-gradient-to-br from-cyan-500 to-emerald-500" />
        ),
    },
    // ...
];

function FeaturesSection() {
    return <StickyScroll content={content} />;
}
```

## Accessibility Concerns

### Critical Issues

1. **Motion sensitivity**: Many users have vestibular disorders
2. **Screen reader opacity**: Animated text may not be read correctly
3. **Keyboard navigation**: Interactive elements must remain focusable
4. **Color contrast**: Ensure text over effects meets WCAG

### Required Mitigations

#### Reduced Motion Support

```tsx
"use client";

import { useReducedMotion } from "framer-motion";
// OR custom hook:
import { useMediaQuery } from "@/hooks/use-media-query";

function AnimatedComponent() {
    const prefersReducedMotion = useReducedMotion();
    // OR: const prefersReducedMotion = useMediaQuery("(prefers-reduced-motion: reduce)");

    if (prefersReducedMotion) {
        return <StaticFallback />;
    }

    return <AnimatedVersion />;
}
```

#### useReducedMotion Hook

```tsx
// hooks/use-reduced-motion.ts
import { useEffect, useState } from "react";

export function useReducedMotion() {
    const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

    useEffect(() => {
        const mediaQuery = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        );
        setPrefersReducedMotion(mediaQuery.matches);

        const handler = (event: MediaQueryListEvent) => {
            setPrefersReducedMotion(event.matches);
        };

        mediaQuery.addEventListener("change", handler);
        return () => mediaQuery.removeEventListener("change", handler);
    }, []);

    return prefersReducedMotion;
}
```

#### Static Fallbacks

Always provide non-animated alternatives:

```tsx
function HeroWithFallback() {
    const prefersReducedMotion = useReducedMotion();

    return (
        <section className="relative min-h-screen">
            {prefersReducedMotion ? (
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900 to-purple-900" />
            ) : (
                <SparklesCore
                    id="hero-sparkles"
                    background="transparent"
                    minSize={0.6}
                    maxSize={1.4}
                    particleDensity={100}
                    className="absolute inset-0"
                />
            )}
            <div className="relative z-10">{/* Content */}</div>
        </section>
    );
}
```

### Screen Reader Considerations

```tsx
// Ensure animated text is accessible
<div aria-label="Build amazing products with our platform">
  <TextGenerateEffect
    words="Build amazing products with our platform"
    aria-hidden="true" // Hide animated version from SR
  />
</div>

// Or use visually hidden text
<h1>
  <span className="sr-only">Build amazing products</span>
  <TextGenerateEffect words="Build amazing products" aria-hidden="true" />
</h1>
```

## Performance Optimization

### Lazy Loading

```tsx
import dynamic from "next/dynamic";

const SparklesCore = dynamic(
    () => import("@/components/ui/sparkles").then((mod) => mod.SparklesCore),
    {
        ssr: false,
        loading: () => <div className="h-full w-full bg-neutral-950" />,
    }
);
```

### Device-Based Rendering

```tsx
function AdaptiveBackground() {
    const [canRender, setCanRender] = useState(false);

    useEffect(() => {
        // Check device capability
        const cores = navigator.hardwareConcurrency || 2;
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

        setCanRender(cores >= 4 && !isMobile);
    }, []);

    if (!canRender) {
        return <StaticGradient />;
    }

    return <ParticleBackground />;
}
```

### Reduce Particle Count on Mobile

```tsx
function ResponsiveSparkles() {
    const isMobile = useMediaQuery("(max-width: 768px)");

    return (
        <SparklesCore
            particleDensity={isMobile ? 30 : 100}
            minSize={isMobile ? 0.8 : 0.6}
            maxSize={isMobile ? 1.2 : 1.4}
        />
    );
}
```

### Use will-change Sparingly

```tsx
// Only apply will-change when animation is imminent
const [isHovering, setIsHovering] = useState(false);

<motion.div
    style={{ willChange: isHovering ? "transform" : "auto" }}
    onHoverStart={() => setIsHovering(true)}
    onHoverEnd={() => setIsHovering(false)}
/>;
```

### Intersection Observer for Scroll Effects

```tsx
function LazyAnimation() {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });

    return (
        <div ref={ref}>
            {isInView ? <ExpensiveAnimation /> : <Placeholder />}
        </div>
    );
}
```

## Common Patterns

### Hero Section Template

```tsx
"use client";

import { motion } from "framer-motion";
import { SparklesCore } from "@/components/ui/sparkles";
import { useReducedMotion } from "@/hooks/use-reduced-motion";

export function Hero() {
    const prefersReducedMotion = useReducedMotion();

    return (
        <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-neutral-950">
            {/* Background effect with fallback */}
            {!prefersReducedMotion && (
                <SparklesCore
                    id="hero-sparkles"
                    background="transparent"
                    minSize={0.4}
                    maxSize={1}
                    particleDensity={50}
                    className="absolute inset-0"
                    particleColor="#FFFFFF"
                />
            )}

            {/* Content */}
            <div className="relative z-10 px-4 text-center">
                <motion.h1
                    initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-4xl font-bold text-white md:text-6xl"
                >
                    Your Headline
                </motion.h1>
            </div>
        </section>
    );
}
```

### Feature Card with Hover

```tsx
"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface FeatureCardProps {
    title: string;
    description: string;
    icon: React.ReactNode;
}

export function FeatureCard({ title, description, icon }: FeatureCardProps) {
    return (
        <motion.div
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
            className={cn(
                "group relative rounded-xl border border-neutral-800 bg-neutral-900 p-6",
                "hover:border-neutral-700 hover:bg-neutral-800/50"
            )}
        >
            <div className="mb-4 text-neutral-400 transition-colors group-hover:text-white">
                {icon}
            </div>
            <h3 className="mb-2 font-semibold text-white">{title}</h3>
            <p className="text-sm text-neutral-400">{description}</p>
        </motion.div>
    );
}
```

## Checklist Before Using Aceternity

-   [ ] Is this a high-impact, low-data-density area?
-   [ ] Have I implemented `prefers-reduced-motion` fallbacks?
-   [ ] Is text accessible to screen readers?
-   [ ] Does performance degrade gracefully on mobile?
-   [ ] Is color contrast maintained over effects?
-   [ ] Have I lazy-loaded heavy components?
-   [ ] Does the animation serve a purpose beyond decoration?
