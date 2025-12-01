---
name: react-email-specialist
description: Expert guidance for building beautiful, cross-client compatible email templates using React Email and Tailwind CSS. Use this skill when creating transactional emails, marketing emails, or any email templates with React. Triggers include requests to build email templates, create email components, integrate with email providers (Resend, SendGrid, Nodemailer, AWS SES, Postmark, etc.), or troubleshoot email rendering issues across clients like Gmail, Outlook, and Apple Mail.
---

# React Email Specialist

Build beautiful, cross-client compatible email templates using React Email - a modern library for crafting emails with React components and Tailwind CSS.

## Quick Start

Install the components package:

```bash
npm install @react-email/components -E
```

Basic email template structure:

```tsx
import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Html,
  Preview,
  Section,
  Tailwind,
  Text,
} from '@react-email/components';

interface WelcomeEmailProps {
  username: string;
}

export const WelcomeEmail = ({ username = 'User' }: WelcomeEmailProps) => (
  <Html>
    <Head />
    <Preview>Welcome to our platform, {username}!</Preview>
    <Tailwind>
      <Body className="bg-gray-100 font-sans">
        <Container className="mx-auto max-w-[600px] p-5">
          <Heading className="text-2xl font-bold text-gray-900">
            Welcome, {username}!
          </Heading>
          <Text className="text-gray-700">
            We're excited to have you on board.
          </Text>
          <Section className="text-center mt-8">
            <Button
              href="https://example.com/get-started"
              className="bg-blue-600 text-white px-6 py-3 rounded-md font-semibold"
            >
              Get Started
            </Button>
          </Section>
        </Container>
      </Body>
    </Tailwind>
  </Html>
);

export default WelcomeEmail;
```

## Core Components

Always import from the unified package:

```tsx
import {
  Html,        // Root wrapper - required for all emails
  Head,        // Document head for meta tags and fonts
  Preview,     // Inbox preview text (appears after subject line)
  Body,        // Email body container
  Container,   // Centered content wrapper (max-width)
  Section,     // Layout sections (renders as <table>)
  Row,         // Table row for grid layouts
  Column,      // Table column for grid layouts
  Heading,     // h1-h6 headings
  Text,        // Paragraph text
  Button,      // CTA buttons with href
  Link,        // Anchor links
  Img,         // Images with proper attributes
  Hr,          // Horizontal rule divider
  Tailwind,    // Tailwind CSS wrapper
  Font,        // Custom font declarations
  Markdown,    // Markdown content renderer
  CodeBlock,   // Syntax-highlighted code blocks
  CodeInline,  // Inline code snippets
} from '@react-email/components';
```

See `references/components.md` for detailed component documentation and props.

## Styling Approaches

### Tailwind CSS (Recommended)

Wrap your email in the `<Tailwind>` component:

```tsx
import { Tailwind, Button, pixelBasedPreset } from '@react-email/components';

const Email = () => (
  <Tailwind
    config={{
      presets: [pixelBasedPreset], // Use pixels instead of rem for compatibility
      theme: {
        extend: {
          colors: {
            brand: '#007291',
          },
        },
      },
    }}
  >
    <Button
      href="https://example.com"
      className="bg-brand px-4 py-2 text-white font-medium rounded"
    >
      Click me
    </Button>
  </Tailwind>
);
```

**Important Tailwind limitations:**
- Use `pixelBasedPreset` - rem units are not supported by many email clients
- No support for `display: flex` or `display: grid` (use Row/Column components)
- No support for `@tailwindcss/typography` prose classes
- No CSS gradients, shadows, or complex selectors
- Context providers must be placed ABOVE the Tailwind component

### Inline Styles

For precise control or when Tailwind isn't suitable:

```tsx
const styles = {
  button: {
    backgroundColor: '#007291',
    color: '#ffffff',
    padding: '12px 24px',
    borderRadius: '4px',
    textDecoration: 'none',
    fontWeight: 600,
  },
};

<Button href="https://example.com" style={styles.button}>
  Click me
</Button>
```

## Layout Patterns

### Centered Container Layout

```tsx
<Body className="bg-gray-100 m-0 p-0">
  <Container className="mx-auto my-10 max-w-[600px] bg-white rounded-lg p-8">
    {/* Content */}
  </Container>
</Body>
```

### Multi-Column Grid

```tsx
<Section>
  <Row>
    <Column className="w-1/2 pr-2">
      <Text>Left column</Text>
    </Column>
    <Column className="w-1/2 pl-2">
      <Text>Right column</Text>
    </Column>
  </Row>
</Section>
```

### Three-Column Footer Icons

```tsx
<Section className="w-[150px] mx-auto">
  <Row>
    <Column align="left">
      <Link href="#">
        <Img src="/twitter.png" width="24" height="24" alt="Twitter" />
      </Link>
    </Column>
    <Column align="center">
      <Link href="#">
        <Img src="/linkedin.png" width="24" height="24" alt="LinkedIn" />
      </Link>
    </Column>
    <Column align="right">
      <Link href="#">
        <Img src="/instagram.png" width="24" height="24" alt="Instagram" />
      </Link>
    </Column>
  </Row>
</Section>
```

## Rendering and Sending

### Convert to HTML

```tsx
import { render, toPlainText, pretty } from '@react-email/render';
import { WelcomeEmail } from './emails/welcome';

// Generate HTML
const html = await render(<WelcomeEmail username="John" />);

// Optional: Beautify output for debugging
const prettyHtml = await pretty(html);

// Generate plain text version (important for deliverability)
const plainText = toPlainText(html);
```

### Integration Examples

See `references/integrations.md` for complete examples with:
- Resend
- Nodemailer
- SendGrid
- AWS SES
- Postmark
- MailerSend

## Email Client Compatibility

React Email components are tested against:
- Gmail (web, Android, iOS)
- Apple Mail (macOS, iOS)
- Outlook (desktop, web, mobile)
- Yahoo! Mail
- HEY
- Superhuman

### Critical Compatibility Rules

1. **No flexbox or grid** - Use `Section`, `Row`, and `Column` components
2. **No SVG** - Gmail doesn't support SVG; use PNG/JPG images
3. **No external stylesheets** - All styles must be inline
4. **Use pixel units** - rem/em not widely supported
5. **Max width 600px** - Standard email width for compatibility
6. **Always include plain text** - Some clients disable HTML
7. **Host images externally** - Use absolute URLs, not base64
8. **Test Preview component** - Some clients show preview text differently

See `references/compatibility.md` for detailed client-specific considerations.

## Development Workflow

### Local Preview Server

```bash
# Add to package.json scripts
"email": "email dev"

# Run preview server
npm run email
```

This opens a browser preview at `localhost:3000` with:
- Live reload on file changes
- Desktop/mobile responsive preview
- Send test emails to your inbox

### Project Structure

```
emails/
├── components/          # Reusable email components
│   ├── Header.tsx
│   ├── Footer.tsx
│   └── Button.tsx
├── templates/           # Complete email templates
│   ├── welcome.tsx
│   ├── password-reset.tsx
│   └── order-confirmation.tsx
└── lib/
    └── constants.ts     # Shared styles, colors, URLs
```

### Default Export Required

Every email template must have a default export for the preview app:

```tsx
export const WelcomeEmail = (props: WelcomeEmailProps) => ( ... );

export default WelcomeEmail;
```

## Best Practices

### Always Include

1. **Preview text** - Shows in inbox list after subject
2. **Plain text version** - Improves deliverability
3. **Unsubscribe link** - Required for marketing emails
4. **Alt text for images** - Accessibility and when images blocked
5. **Fallback fonts** - System fonts as backup

### Image Guidelines

```tsx
<Img
  src="https://cdn.example.com/logo.png"  // Absolute URL
  width="150"                              // Explicit dimensions
  height="50"                              // Prevents layout shift
  alt="Company Logo"                       // Always include
  style={{ display: 'block' }}            // Prevents gaps
/>
```

### Button Best Practices

```tsx
<Button
  href="https://example.com"              // Use full URL
  className="bg-blue-600 text-white px-6 py-3 rounded no-underline text-center inline-block"
>
  Call to Action
</Button>
```

### Font Loading

```tsx
<Head>
  <Font
    fontFamily="Inter"
    fallbackFontFamily="Arial"
    webFont={{
      url: 'https://fonts.gstatic.com/s/inter/v13/font.woff2',
      format: 'woff2',
    }}
    fontWeight={400}
    fontStyle="normal"
  />
</Head>
```

## Common Patterns

See `references/patterns.md` for complete examples of:
- Welcome emails
- Password reset
- Order confirmations
- Invoice/receipt emails
- Newsletter layouts
- Account notifications
- Marketing promotional emails
