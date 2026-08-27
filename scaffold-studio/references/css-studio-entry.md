# CSS Studio — per-project, dev-only

Package: `cssstudio` as a **devDependency**. Then `mkdir -p .cursor && npx cssstudio install`.

## Detect the entry

| Signal | Path |
|--------|------|
| `next.config.*`, `src/app/layout.tsx`, `app/layout.tsx` | Next App Router |
| `vite.config.*`, `src/main.tsx` / `src/main.ts` | Vite |
| `index.html` and no bundler | script tag |
| none of the above | ask (or `--agent`: stop this layer) |

## Next.js (App Router)

Client component; `startStudio()` uses `window`. Gate production with
`next/dynamic` + `ssr: false` so the GUI is not in the production graph.

`src/components/css-studio.tsx`:

```tsx
"use client";

import { startStudio } from "cssstudio";
import { useEffect } from "react";

export function CssStudio() {
  useEffect(() => {
    if (process.env.NODE_ENV !== "development") return;
    startStudio();
  }, []);
  return null;
}
```

Root layout (server):

```tsx
import dynamic from "next/dynamic";

const CssStudio =
  process.env.NODE_ENV === "development"
    ? dynamic(() => import("@/components/css-studio").then((m) => m.CssStudio), {
        ssr: false,
      })
    : () => null;
```

Render `<CssStudio />` in `<body>`. If `tsc` errors on the module:

```ts
declare module "cssstudio" {
  export function startStudio(options?: unknown): () => void;
}
```

## Vite

In `src/main.tsx` (or `main.ts`), after `createRoot`:

```ts
if (import.meta.env.DEV) {
  const { startStudio } = await import("cssstudio");
  startStudio();
}
```

Or a small `css-studio.ts` imported only from a `if (import.meta.env.DEV)` branch.

## Script tag (no bundler)

```html
<script>
  if (["localhost"].includes(location.hostname)) {
    const s = document.createElement("script");
    s.src = "https://unpkg.com/cssstudio";
    document.head.appendChild(s);
  }
</script>
```

## After install

Restart the agent, then `/studio`. Keep `npm run dev` (or equivalent) running.
