# Common Email Template Patterns

Ready-to-use patterns for common transactional and marketing email types.

## Table of Contents

1. [Welcome Email](#welcome-email)
2. [Password Reset](#password-reset)
3. [Order Confirmation](#order-confirmation)
4. [Receipt/Invoice](#receiptinvoice)
5. [Newsletter](#newsletter)
6. [Account Notification](#account-notification)
7. [Marketing Promotional](#marketing-promotional)
8. [Reusable Components](#reusable-components)

---

## Welcome Email

Classic onboarding email with CTA button.

```tsx
import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Html,
  Img,
  Preview,
  Section,
  Tailwind,
  Text,
} from '@react-email/components';

interface WelcomeEmailProps {
  username: string;
  loginUrl: string;
}

export const WelcomeEmail = ({
  username = 'there',
  loginUrl = 'https://example.com/login',
}: WelcomeEmailProps) => (
  <Html>
    <Head />
    <Preview>Welcome to our platform, {username}!</Preview>
    <Tailwind>
      <Body className="bg-gray-100 font-sans">
        <Container className="mx-auto my-10 max-w-[600px] rounded-lg bg-white p-8">
          <Img
            src="https://cdn.example.com/logo.png"
            width={120}
            height={40}
            alt="Company Logo"
            className="mx-auto mb-8"
          />
          
          <Heading className="text-center text-2xl font-bold text-gray-900">
            Welcome, {username}! 🎉
          </Heading>
          
          <Text className="text-gray-600 text-base leading-6">
            We're thrilled to have you on board. Your account is all set up and
            ready to go. Here are a few things you can do to get started:
          </Text>
          
          <ul className="text-gray-600 text-base">
            <li>Complete your profile</li>
            <li>Explore our features</li>
            <li>Connect with other users</li>
          </ul>
          
          <Section className="text-center my-8">
            <Button
              href={loginUrl}
              className="bg-blue-600 text-white px-8 py-4 rounded-md font-semibold no-underline"
            >
              Get Started
            </Button>
          </Section>
          
          <Text className="text-gray-500 text-sm text-center">
            If you have any questions, reply to this email or contact our
            support team.
          </Text>
        </Container>
      </Body>
    </Tailwind>
  </Html>
);

export default WelcomeEmail;
```

---

## Password Reset

Security-focused email with reset link.

```tsx
import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Html,
  Link,
  Preview,
  Section,
  Tailwind,
  Text,
} from '@react-email/components';

interface PasswordResetProps {
  username: string;
  resetUrl: string;
  expiresIn: string;
}

export const PasswordResetEmail = ({
  username = 'User',
  resetUrl = 'https://example.com/reset',
  expiresIn = '1 hour',
}: PasswordResetProps) => (
  <Html>
    <Head />
    <Preview>Reset your password</Preview>
    <Tailwind>
      <Body className="bg-gray-100 font-sans">
        <Container className="mx-auto my-10 max-w-[600px] rounded-lg bg-white p-8">
          <Heading className="text-2xl font-bold text-gray-900 mb-4">
            Password Reset Request
          </Heading>
          
          <Text className="text-gray-600 text-base leading-6">
            Hi {username},
          </Text>
          
          <Text className="text-gray-600 text-base leading-6">
            We received a request to reset your password. Click the button
            below to choose a new password:
          </Text>
          
          <Section className="text-center my-8">
            <Button
              href={resetUrl}
              className="bg-red-600 text-white px-8 py-4 rounded-md font-semibold no-underline"
            >
              Reset Password
            </Button>
          </Section>
          
          <Text className="text-gray-500 text-sm">
            This link will expire in {expiresIn}. If you didn't request a
            password reset, you can safely ignore this email.
          </Text>
          
          <Text className="text-gray-500 text-sm mt-4">
            Or copy and paste this URL into your browser:
          </Text>
          <Text className="text-blue-600 text-sm break-all">
            <Link href={resetUrl}>{resetUrl}</Link>
          </Text>
        </Container>
      </Body>
    </Tailwind>
  </Html>
);

export default PasswordResetEmail;
```

---

## Order Confirmation

E-commerce order confirmation with items list.

```tsx
import {
  Body,
  Column,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Img,
  Preview,
  Row,
  Section,
  Tailwind,
  Text,
} from '@react-email/components';

interface OrderItem {
  name: string;
  quantity: number;
  price: string;
  imageUrl: string;
}

interface OrderConfirmationProps {
  orderNumber: string;
  orderDate: string;
  items: OrderItem[];
  subtotal: string;
  shipping: string;
  total: string;
  shippingAddress: string;
}

export const OrderConfirmationEmail = ({
  orderNumber = '12345',
  orderDate = 'January 15, 2025',
  items = [
    { name: 'Product Name', quantity: 1, price: '$29.99', imageUrl: 'https://via.placeholder.com/80' },
  ],
  subtotal = '$29.99',
  shipping = '$5.00',
  total = '$34.99',
  shippingAddress = '123 Main St, City, State 12345',
}: OrderConfirmationProps) => (
  <Html>
    <Head />
    <Preview>Order #{orderNumber} confirmed!</Preview>
    <Tailwind>
      <Body className="bg-gray-100 font-sans">
        <Container className="mx-auto my-10 max-w-[600px] rounded-lg bg-white p-8">
          <Section className="text-center mb-8">
            <Text className="text-green-600 text-4xl mb-2">✓</Text>
            <Heading className="text-2xl font-bold text-gray-900">
              Order Confirmed!
            </Heading>
            <Text className="text-gray-500">
              Order #{orderNumber} • {orderDate}
            </Text>
          </Section>
          
          <Hr className="border-gray-200 my-6" />
          
          <Heading as="h2" className="text-lg font-semibold text-gray-900 mb-4">
            Order Summary
          </Heading>
          
          {items.map((item, index) => (
            <Section key={index} className="mb-4">
              <Row>
                <Column style={{ width: '80px' }}>
                  <Img
                    src={item.imageUrl}
                    width={80}
                    height={80}
                    alt={item.name}
                    className="rounded"
                  />
                </Column>
                <Column className="pl-4">
                  <Text className="text-gray-900 font-medium m-0">
                    {item.name}
                  </Text>
                  <Text className="text-gray-500 text-sm m-0">
                    Qty: {item.quantity}
                  </Text>
                </Column>
                <Column style={{ width: '80px' }} className="text-right">
                  <Text className="text-gray-900 font-medium m-0">
                    {item.price}
                  </Text>
                </Column>
              </Row>
            </Section>
          ))}
          
          <Hr className="border-gray-200 my-6" />
          
          <Section>
            <Row>
              <Column>
                <Text className="text-gray-500 m-1">Subtotal</Text>
              </Column>
              <Column className="text-right">
                <Text className="text-gray-900 m-1">{subtotal}</Text>
              </Column>
            </Row>
            <Row>
              <Column>
                <Text className="text-gray-500 m-1">Shipping</Text>
              </Column>
              <Column className="text-right">
                <Text className="text-gray-900 m-1">{shipping}</Text>
              </Column>
            </Row>
            <Row>
              <Column>
                <Text className="text-gray-900 font-bold m-1">Total</Text>
              </Column>
              <Column className="text-right">
                <Text className="text-gray-900 font-bold m-1">{total}</Text>
              </Column>
            </Row>
          </Section>
          
          <Hr className="border-gray-200 my-6" />
          
          <Section>
            <Heading as="h3" className="text-sm font-semibold text-gray-900">
              Shipping Address
            </Heading>
            <Text className="text-gray-600 text-sm">{shippingAddress}</Text>
          </Section>
        </Container>
      </Body>
    </Tailwind>
  </Html>
);

export default OrderConfirmationEmail;
```

---

## Receipt/Invoice

Professional invoice with itemized billing.

```tsx
import {
  Body,
  Column,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Preview,
  Row,
  Section,
  Tailwind,
  Text,
} from '@react-email/components';

interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: string;
  total: string;
}

interface InvoiceEmailProps {
  invoiceNumber: string;
  invoiceDate: string;
  dueDate: string;
  customerName: string;
  items: InvoiceItem[];
  subtotal: string;
  tax: string;
  total: string;
}

export const InvoiceEmail = ({
  invoiceNumber = 'INV-001',
  invoiceDate = 'January 15, 2025',
  dueDate = 'February 15, 2025',
  customerName = 'John Doe',
  items = [
    { description: 'Service', quantity: 1, unitPrice: '$100.00', total: '$100.00' },
  ],
  subtotal = '$100.00',
  tax = '$10.00',
  total = '$110.00',
}: InvoiceEmailProps) => (
  <Html>
    <Head />
    <Preview>Invoice #{invoiceNumber} - ${total}</Preview>
    <Tailwind>
      <Body className="bg-gray-100 font-sans">
        <Container className="mx-auto my-10 max-w-[600px] bg-white">
          {/* Header */}
          <Section className="bg-gray-900 p-8">
            <Row>
              <Column>
                <Text className="text-white text-2xl font-bold m-0">
                  INVOICE
                </Text>
              </Column>
              <Column className="text-right">
                <Text className="text-white m-0">#{invoiceNumber}</Text>
              </Column>
            </Row>
          </Section>
          
          {/* Details */}
          <Section className="p-8">
            <Row>
              <Column>
                <Text className="text-gray-500 text-sm m-0">Bill To</Text>
                <Text className="text-gray-900 font-medium">{customerName}</Text>
              </Column>
              <Column className="text-right">
                <Text className="text-gray-500 text-sm m-0">Invoice Date</Text>
                <Text className="text-gray-900">{invoiceDate}</Text>
                <Text className="text-gray-500 text-sm m-0 mt-2">Due Date</Text>
                <Text className="text-gray-900">{dueDate}</Text>
              </Column>
            </Row>
          </Section>
          
          {/* Items Table */}
          <Section className="px-8">
            <Row className="bg-gray-100">
              <Column className="p-3" style={{ width: '50%' }}>
                <Text className="text-gray-600 font-semibold text-sm m-0">
                  Description
                </Text>
              </Column>
              <Column className="p-3 text-center" style={{ width: '15%' }}>
                <Text className="text-gray-600 font-semibold text-sm m-0">Qty</Text>
              </Column>
              <Column className="p-3 text-right" style={{ width: '17.5%' }}>
                <Text className="text-gray-600 font-semibold text-sm m-0">Price</Text>
              </Column>
              <Column className="p-3 text-right" style={{ width: '17.5%' }}>
                <Text className="text-gray-600 font-semibold text-sm m-0">Total</Text>
              </Column>
            </Row>
            
            {items.map((item, index) => (
              <Row key={index} className="border-b border-gray-100">
                <Column className="p-3" style={{ width: '50%' }}>
                  <Text className="text-gray-900 m-0">{item.description}</Text>
                </Column>
                <Column className="p-3 text-center" style={{ width: '15%' }}>
                  <Text className="text-gray-900 m-0">{item.quantity}</Text>
                </Column>
                <Column className="p-3 text-right" style={{ width: '17.5%' }}>
                  <Text className="text-gray-900 m-0">{item.unitPrice}</Text>
                </Column>
                <Column className="p-3 text-right" style={{ width: '17.5%' }}>
                  <Text className="text-gray-900 m-0">{item.total}</Text>
                </Column>
              </Row>
            ))}
          </Section>
          
          {/* Totals */}
          <Section className="p-8">
            <Row>
              <Column style={{ width: '60%' }} />
              <Column style={{ width: '40%' }}>
                <Row>
                  <Column>
                    <Text className="text-gray-500 m-1">Subtotal</Text>
                  </Column>
                  <Column className="text-right">
                    <Text className="text-gray-900 m-1">{subtotal}</Text>
                  </Column>
                </Row>
                <Row>
                  <Column>
                    <Text className="text-gray-500 m-1">Tax</Text>
                  </Column>
                  <Column className="text-right">
                    <Text className="text-gray-900 m-1">{tax}</Text>
                  </Column>
                </Row>
                <Hr className="border-gray-200 my-2" />
                <Row>
                  <Column>
                    <Text className="text-gray-900 font-bold text-lg m-1">Total</Text>
                  </Column>
                  <Column className="text-right">
                    <Text className="text-gray-900 font-bold text-lg m-1">{total}</Text>
                  </Column>
                </Row>
              </Column>
            </Row>
          </Section>
        </Container>
      </Body>
    </Tailwind>
  </Html>
);

export default InvoiceEmail;
```

---

## Reusable Components

### Email Header

```tsx
// components/EmailHeader.tsx
import { Column, Img, Link, Row, Section } from '@react-email/components';

interface EmailHeaderProps {
  logoUrl: string;
  homeUrl: string;
}

export const EmailHeader = ({ logoUrl, homeUrl }: EmailHeaderProps) => (
  <Section className="py-6">
    <Row>
      <Column>
        <Link href={homeUrl}>
          <Img src={logoUrl} width={120} height={40} alt="Logo" />
        </Link>
      </Column>
    </Row>
  </Section>
);
```

### Email Footer

```tsx
// components/EmailFooter.tsx
import { Column, Hr, Img, Link, Row, Section, Text } from '@react-email/components';

interface EmailFooterProps {
  companyName: string;
  address: string;
  unsubscribeUrl?: string;
  socialLinks?: {
    twitter?: string;
    linkedin?: string;
    instagram?: string;
  };
}

export const EmailFooter = ({
  companyName,
  address,
  unsubscribeUrl,
  socialLinks,
}: EmailFooterProps) => (
  <Section className="mt-8">
    <Hr className="border-gray-200" />
    
    {socialLinks && (
      <Section className="py-4">
        <Row>
          <Column align="center">
            {socialLinks.twitter && (
              <Link href={socialLinks.twitter} className="mx-2">
                <Img src="/twitter-icon.png" width={24} height={24} alt="Twitter" />
              </Link>
            )}
            {socialLinks.linkedin && (
              <Link href={socialLinks.linkedin} className="mx-2">
                <Img src="/linkedin-icon.png" width={24} height={24} alt="LinkedIn" />
              </Link>
            )}
            {socialLinks.instagram && (
              <Link href={socialLinks.instagram} className="mx-2">
                <Img src="/instagram-icon.png" width={24} height={24} alt="Instagram" />
              </Link>
            )}
          </Column>
        </Row>
      </Section>
    )}
    
    <Text className="text-gray-500 text-xs text-center">
      © {new Date().getFullYear()} {companyName}. All rights reserved.
    </Text>
    <Text className="text-gray-500 text-xs text-center">{address}</Text>
    
    {unsubscribeUrl && (
      <Text className="text-gray-400 text-xs text-center">
        <Link href={unsubscribeUrl} className="text-gray-400 underline">
          Unsubscribe
        </Link>
      </Text>
    )}
  </Section>
);
```

### Primary Button

```tsx
// components/PrimaryButton.tsx
import { Button } from '@react-email/components';

interface PrimaryButtonProps {
  href: string;
  children: React.ReactNode;
}

export const PrimaryButton = ({ href, children }: PrimaryButtonProps) => (
  <Button
    href={href}
    className="bg-blue-600 text-white px-6 py-3 rounded-md font-semibold no-underline text-center inline-block"
  >
    {children}
  </Button>
);
```
