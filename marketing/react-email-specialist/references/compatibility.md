# Email Client Compatibility Guide

Comprehensive guide to ensure your emails render correctly across all major email clients.

## Table of Contents

1. [Supported Clients](#supported-clients)
2. [Critical CSS Limitations](#critical-css-limitations)
3. [Client-Specific Issues](#client-specific-issues)
4. [Testing Checklist](#testing-checklist)
5. [Debugging Tips](#debugging-tips)

---

## Supported Clients

React Email components are tested against these clients:

| Client | Platform | Support Level |
|--------|----------|---------------|
| Gmail | Web, Android, iOS | ✅ Full |
| Apple Mail | macOS, iOS | ✅ Full |
| Outlook.com | Web | ✅ Full |
| Outlook | Desktop (Windows) | ⚠️ Limited |
| Outlook | Mac | ✅ Full |
| Yahoo Mail | Web | ✅ Full |
| HEY | Web, Apps | ✅ Full |
| Superhuman | Web, Apps | ✅ Full |

---

## Critical CSS Limitations

### ❌ Never Use

These CSS properties are not supported in major email clients:

```css
/* Flexbox - Not supported in Outlook */
display: flex;
flex-direction: row;
justify-content: center;
align-items: center;

/* Grid - Not supported in Outlook */
display: grid;
grid-template-columns: 1fr 1fr;

/* CSS Variables - Limited support */
--custom-color: #007291;
color: var(--custom-color);

/* Gradients - Not supported in Outlook */
background: linear-gradient(to right, #007291, #00a8e8);

/* Box Shadow - Not supported in most clients */
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

/* SVG - Not supported in Gmail */
<svg>...</svg>

/* rem units - Not supported in some clients */
font-size: 1rem;
padding: 1.5rem;
```

### ✅ Safe Alternatives

```tsx
// Instead of flexbox, use Row/Column components
<Section>
  <Row>
    <Column align="center">Centered content</Column>
  </Row>
</Section>

// Instead of rem, use pixels
<Text style={{ fontSize: '16px', padding: '24px' }}>Content</Text>

// Instead of CSS gradients, use solid colors or images
<Section style={{ backgroundColor: '#007291' }}>
  Content
</Section>

// Instead of SVG, use PNG/JPG images
<Img src="https://cdn.example.com/icon.png" width="24" height="24" alt="Icon" />

// With Tailwind, use pixelBasedPreset
import { Tailwind, pixelBasedPreset } from '@react-email/components';

<Tailwind config={{ presets: [pixelBasedPreset] }}>
  {/* Your email */}
</Tailwind>
```

---

## Client-Specific Issues

### Gmail

**Issues:**
- Maximum `<style>` tag size of ~16KB; excess is removed
- No SVG support
- Limited support for pseudo-classes (`:hover`)
- Strips `<style>` tags in some cases

**Solutions:**
- React Email inlines all styles automatically
- Use PNG/JPG images instead of SVG
- Avoid hover effects; use static styles

```tsx
// Gmail-safe button (no hover states)
<Button
  href="https://example.com"
  style={{
    backgroundColor: '#2563eb',
    color: '#ffffff',
    padding: '12px 24px',
    borderRadius: '6px',
  }}
>
  Click Me
</Button>
```

### Outlook (Desktop - Windows)

**Issues:**
- Uses Word rendering engine (not a browser)
- No flexbox or grid support
- Limited CSS support
- Images may not display without explicit dimensions

**Solutions:**
- Always use table-based layouts (Section/Row/Column)
- Include width/height on all images
- Use MSO conditional comments for fixes

```tsx
// Outlook-safe image with explicit dimensions
<Img
  src="https://cdn.example.com/image.png"
  width={600}
  height={300}
  alt="Description"
  style={{ display: 'block', maxWidth: '100%' }}
/>

// The Button component automatically includes MSO fallbacks
<Button href="https://example.com">
  {/* React Email handles Outlook-specific code */}
</Button>
```

### Apple Mail

**Issues:**
- Generally excellent support
- May add spacing to images

**Solutions:**
```tsx
// Remove spacing around images
<Img
  src="https://cdn.example.com/image.png"
  style={{ display: 'block' }}
  alt="Image"
/>
```

### Yahoo Mail

**Issues:**
- May strip styles from `<style>` tags
- Some font issues

**Solutions:**
- Use inline styles (React Email does this automatically)
- Use web-safe fallback fonts

```tsx
<Font
  fontFamily="Inter"
  fallbackFontFamily="Arial"  // Safe fallback
  webFont={{...}}
/>
```

### Dark Mode

Many clients now support dark mode. Consider:

```tsx
// Use colors that work in both modes
// Avoid pure white (#ffffff) or pure black (#000000)
<Text style={{ color: '#1a1a1a' }}>Light mode optimized</Text>

// Or use slightly off-white backgrounds
<Container style={{ backgroundColor: '#f9fafb' }}>
  Content
</Container>
```

---

## Testing Checklist

### Before Sending

- [ ] Test in Gmail (web)
- [ ] Test in Outlook.com (web)
- [ ] Test in Apple Mail
- [ ] Test on mobile (Gmail app, Apple Mail app)
- [ ] Check plain text version
- [ ] Verify all images load
- [ ] Test all links
- [ ] Check preview text displays correctly
- [ ] Validate HTML with React Email linter

### Visual Checks

- [ ] Layout doesn't break at 600px width
- [ ] Text is readable (min 14px body text)
- [ ] Buttons are large enough to tap (min 44px)
- [ ] Adequate color contrast
- [ ] Images have alt text
- [ ] No broken images

### Content Checks

- [ ] Subject line is compelling
- [ ] Preview text enhances subject
- [ ] Unsubscribe link present (for marketing)
- [ ] Contact information included
- [ ] Links are HTTPS
- [ ] No spam trigger words

---

## Debugging Tips

### React Email Dev Tools

```bash
# Run the preview server
npx email dev

# Features available:
# - Desktop/mobile preview toggle
# - HTML source view
# - Spam score analysis
# - Link validation
# - CSS compatibility warnings
```

### Common Issues

**Issue: Content overflows on mobile**
```tsx
// Fix: Set max-width on Container
<Container style={{ maxWidth: '600px', width: '100%' }}>
```

**Issue: Buttons not clickable in Outlook**
```tsx
// Fix: Button component handles this automatically
// If using custom buttons, include MSO conditional comments
```

**Issue: Fonts not loading**
```tsx
// Fix: Include fallback fonts
<Font
  fontFamily="CustomFont"
  fallbackFontFamily="Arial"  // Always include fallback
  webFont={{...}}
/>
```

**Issue: Images have gaps below them**
```tsx
// Fix: Add display: block
<Img style={{ display: 'block' }} ... />
```

**Issue: Layout breaks in Outlook**
```tsx
// Fix: Use Section/Row/Column, not divs with CSS
<Section>
  <Row>
    <Column style={{ width: '50%' }}>Left</Column>
    <Column style={{ width: '50%' }}>Right</Column>
  </Row>
</Section>
```

### Resources

- [Can I Email](https://www.caniemail.com/) - CSS support reference
- [Email on Acid](https://www.emailonacid.com/) - Testing service
- [Litmus](https://litmus.com/) - Testing and analytics
- [React Email Docs](https://react.email/docs) - Official documentation
