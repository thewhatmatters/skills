# React Email Components Reference

Comprehensive documentation for all React Email components.

## Table of Contents

1. [Structure Components](#structure-components)
2. [Layout Components](#layout-components)
3. [Content Components](#content-components)
4. [Styling Components](#styling-components)
5. [Utility Components](#utility-components)

---

## Structure Components

### Html

Root component that wraps the entire email. Required for all emails.

```tsx
import { Html } from '@react-email/components';

<Html lang="en" dir="ltr">
  {/* Email content */}
</Html>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `lang` | string | - | Language code (e.g., "en", "fr") |
| `dir` | "ltr" \| "rtl" | - | Text direction |

### Head

Document head for meta tags, fonts, and styles. Place immediately after `<Html>`.

```tsx
import { Head, Font } from '@react-email/components';

<Head>
  <title>Email Subject</title>
  <Font
    fontFamily="Roboto"
    fallbackFontFamily="Verdana"
    webFont={{
      url: 'https://fonts.gstatic.com/s/roboto/v30/font.woff2',
      format: 'woff2',
    }}
    fontWeight={400}
    fontStyle="normal"
  />
</Head>
```

### Preview

Text shown in inbox list after subject line. Critical for engagement.

```tsx
import { Preview } from '@react-email/components';

<Preview>Your order #12345 has shipped! Track your package here.</Preview>
```

**Tips:**
- Keep under 90 characters for best visibility
- Include key information or call-to-action
- Avoid repetition with subject line
- Use dynamic content when relevant

### Body

Container for all visible email content.

```tsx
import { Body } from '@react-email/components';

<Body style={{ backgroundColor: '#f6f9fc', margin: 0, padding: 0 }}>
  {/* Content */}
</Body>
```

---

## Layout Components

### Container

Centered wrapper with max-width. Standard email width is 600px.

```tsx
import { Container } from '@react-email/components';

<Container style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
  {/* Content */}
</Container>

// With Tailwind
<Container className="mx-auto max-w-[600px] p-5">
  {/* Content */}
</Container>
```

### Section

Creates table-based sections for layout. Use for grouping content.

```tsx
import { Section, Text } from '@react-email/components';

// Simple section
<Section style={{ padding: '20px 0' }}>
  <Text>Section content</Text>
</Section>

// Section with background
<Section className="bg-blue-600 py-8 text-center">
  <Text className="text-white text-xl">Hero Section</Text>
</Section>
```

### Row

Table row for creating horizontal layouts. Must contain Column components.

```tsx
import { Section, Row, Column } from '@react-email/components';

<Section>
  <Row>
    <Column>First column</Column>
    <Column>Second column</Column>
    <Column>Third column</Column>
  </Row>
</Section>
```

### Column

Table cell for multi-column layouts. Must be inside a Row.

```tsx
import { Row, Column, Text } from '@react-email/components';

<Row>
  <Column style={{ width: '50%', paddingRight: '10px' }}>
    <Text>Left content</Text>
  </Column>
  <Column style={{ width: '50%', paddingLeft: '10px' }}>
    <Text>Right content</Text>
  </Column>
</Row>

// With alignment
<Row>
  <Column align="center" valign="middle">
    Centered content
  </Column>
</Row>
```

**Props:**
| Prop | Type | Description |
|------|------|-------------|
| `align` | "left" \| "center" \| "right" | Horizontal alignment |
| `valign` | "top" \| "middle" \| "bottom" | Vertical alignment |

---

## Content Components

### Heading

Semantic heading elements (h1-h6).

```tsx
import { Heading } from '@react-email/components';

<Heading as="h1" style={{ fontSize: '32px', fontWeight: 'bold', color: '#1a1a1a' }}>
  Main Heading
</Heading>

<Heading as="h2" className="text-2xl font-semibold text-gray-800">
  Subheading
</Heading>
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `as` | "h1" \| "h2" \| "h3" \| "h4" \| "h5" \| "h6" | "h1" | Heading level |
| `m` | string \| number | - | Margin shorthand |
| `mx` | string \| number | - | Horizontal margin |
| `my` | string \| number | - | Vertical margin |

### Text

Paragraph text with sensible defaults.

```tsx
import { Text } from '@react-email/components';

<Text style={{ fontSize: '16px', lineHeight: '24px', color: '#374151' }}>
  Regular paragraph text with good readability.
</Text>

// With margin control
<Text className="text-base text-gray-600 my-4">
  Spaced paragraph
</Text>
```

### Link

Anchor element for hyperlinks.

```tsx
import { Link } from '@react-email/components';

<Link 
  href="https://example.com" 
  style={{ color: '#2563eb', textDecoration: 'underline' }}
>
  Click here
</Link>

// Styled as text (no underline)
<Link href="https://example.com" className="text-blue-600 no-underline hover:underline">
  Learn more
</Link>
```

### Button

Call-to-action button with href. Renders as bulletproof button pattern.

```tsx
import { Button } from '@react-email/components';

// With inline styles
<Button
  href="https://example.com/action"
  style={{
    backgroundColor: '#2563eb',
    color: '#ffffff',
    padding: '12px 24px',
    borderRadius: '6px',
    fontWeight: 600,
    textDecoration: 'none',
    display: 'inline-block',
  }}
>
  Get Started
</Button>

// With Tailwind
<Button
  href="https://example.com"
  className="bg-blue-600 text-white px-6 py-3 rounded-md font-semibold no-underline"
>
  Call to Action
</Button>
```

**Props:**
| Prop | Type | Description |
|------|------|-------------|
| `href` | string | **Required.** Button URL |
| `target` | string | Link target (_blank, etc.) |

### Img

Image component with email-safe attributes.

```tsx
import { Img } from '@react-email/components';

<Img
  src="https://cdn.example.com/hero.png"
  width={600}
  height={300}
  alt="Hero image description"
  style={{ display: 'block', width: '100%', maxWidth: '600px' }}
/>

// Logo example
<Img
  src="https://cdn.example.com/logo.png"
  width={150}
  height={40}
  alt="Company Name"
  className="block"
/>
```

**Best Practices:**
- Always use absolute URLs (https://)
- Include width and height to prevent layout shift
- Add descriptive alt text
- Use `display: block` to prevent gaps
- Keep file sizes small (< 1MB recommended)

### Hr

Horizontal rule divider.

```tsx
import { Hr } from '@react-email/components';

<Hr style={{ borderTop: '1px solid #e5e7eb', margin: '24px 0' }} />

// With Tailwind
<Hr className="border-gray-200 my-6" />
```

---

## Styling Components

### Tailwind

Wrapper component that enables Tailwind CSS classes.

```tsx
import { Tailwind, pixelBasedPreset, Body, Text } from '@react-email/components';

<Tailwind
  config={{
    presets: [pixelBasedPreset], // Converts rem to px
    theme: {
      extend: {
        colors: {
          brand: {
            primary: '#2563eb',
            secondary: '#1e40af',
          },
        },
        fontFamily: {
          sans: ['Inter', 'Arial', 'sans-serif'],
        },
      },
    },
  }}
>
  <Body className="bg-gray-100 font-sans">
    <Text className="text-brand-primary text-lg">
      Styled with Tailwind
    </Text>
  </Body>
</Tailwind>
```

**Props:**
| Prop | Type | Description |
|------|------|-------------|
| `config` | TailwindConfig | Tailwind configuration object |

**Limitations:**
- No flexbox (`flex`) - use Row/Column
- No grid (`grid`) - use Row/Column  
- No gradients
- No shadows
- No prose classes from typography plugin
- No complex selectors (hover: works poorly)

### Font

Declare custom web fonts.

```tsx
import { Head, Font } from '@react-email/components';

<Head>
  <Font
    fontFamily="Inter"
    fallbackFontFamily="Helvetica"
    webFont={{
      url: 'https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hjp-Ek-_EeA.woff2',
      format: 'woff2',
    }}
    fontWeight={400}
    fontStyle="normal"
  />
  {/* Add multiple weights */}
  <Font
    fontFamily="Inter"
    fallbackFontFamily="Helvetica"
    webFont={{
      url: 'https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuI6fAZ9hjp-Ek-_EeA.woff2',
      format: 'woff2',
    }}
    fontWeight={700}
    fontStyle="normal"
  />
</Head>
```

**Props:**
| Prop | Type | Description |
|------|------|-------------|
| `fontFamily` | string | Font family name |
| `fallbackFontFamily` | string | Fallback font |
| `webFont` | object | Web font URL and format |
| `fontWeight` | number | Font weight |
| `fontStyle` | string | Font style (normal, italic) |

---

## Utility Components

### Markdown

Render Markdown content as email-safe HTML.

```tsx
import { Markdown } from '@react-email/components';

const content = `
# Welcome

Thanks for signing up! Here's what you can do:

- **Explore** our features
- **Connect** with others
- **Create** amazing things

[Get Started](https://example.com)
`;

<Markdown
  markdownContainerStyles={{ padding: '20px' }}
  markdownCustomStyles={{
    h1: { fontSize: '28px', color: '#1a1a1a' },
    p: { fontSize: '16px', lineHeight: '24px' },
    a: { color: '#2563eb' },
  }}
>
  {content}
</Markdown>
```

### CodeBlock

Syntax-highlighted code blocks using Prism.js.

```tsx
import { CodeBlock, dracula } from '@react-email/components';

<CodeBlock
  code={`const greeting = "Hello World";
console.log(greeting);`}
  language="javascript"
  theme={dracula}
  showLineNumbers
/>
```

**Props:**
| Prop | Type | Description |
|------|------|-------------|
| `code` | string | Code content |
| `language` | string | Programming language |
| `theme` | object | Prism theme object |
| `showLineNumbers` | boolean | Show line numbers |

### CodeInline

Inline code snippets.

```tsx
import { Text, CodeInline } from '@react-email/components';

<Text>
  Run <CodeInline>npm install</CodeInline> to get started.
</Text>
```
