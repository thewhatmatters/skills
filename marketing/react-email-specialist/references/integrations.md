# Email Provider Integrations

Complete integration examples for popular email service providers.

## Table of Contents

1. [Resend](#resend)
2. [Nodemailer](#nodemailer)
3. [SendGrid](#sendgrid)
4. [AWS SES](#aws-ses)
5. [Postmark](#postmark)
6. [MailerSend](#mailersend)
7. [Plunk](#plunk)

---

## Resend

Official email service from the React Email team.

### Installation

```bash
npm install resend @react-email/components
```

### Basic Usage

```tsx
// lib/resend.ts
import { Resend } from 'resend';

export const resend = new Resend(process.env.RESEND_API_KEY);
```

```tsx
// api/send.ts
import { resend } from '../lib/resend';
import { WelcomeEmail } from '../emails/welcome';

const { data, error } = await resend.emails.send({
  from: 'Your Company <noreply@yourdomain.com>',
  to: ['user@example.com'],
  subject: 'Welcome to Our Platform',
  react: WelcomeEmail({ username: 'John' }),
});

if (error) {
  console.error('Failed to send email:', error);
}
```

### Next.js API Route

```tsx
// app/api/email/route.ts
import { NextResponse } from 'next/server';
import { resend } from '@/lib/resend';
import { WelcomeEmail } from '@/emails/welcome';

export async function POST(request: Request) {
  const { email, name } = await request.json();

  const { data, error } = await resend.emails.send({
    from: 'Your Company <noreply@yourdomain.com>',
    to: [email],
    subject: 'Welcome!',
    react: WelcomeEmail({ username: name }),
  });

  if (error) {
    return NextResponse.json({ error }, { status: 400 });
  }

  return NextResponse.json({ data });
}
```

---

## Nodemailer

Most popular Node.js email library. Works with any SMTP server.

### Installation

```bash
npm install nodemailer @react-email/components @types/nodemailer
```

### Basic Usage

```tsx
// send-email.ts
import { render } from '@react-email/components';
import nodemailer from 'nodemailer';
import { WelcomeEmail } from './emails/welcome';

const transporter = nodemailer.createTransport({
  host: 'smtp.example.com',
  port: 587,
  secure: false, // true for 465, false for other ports
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

const emailHtml = await render(<WelcomeEmail username="John" />);

const options = {
  from: '"Your Company" <noreply@yourdomain.com>',
  to: 'user@example.com',
  subject: 'Welcome to Our Platform',
  html: emailHtml,
};

await transporter.sendMail(options);
```

### With Plain Text

```tsx
import { render, toPlainText } from '@react-email/components';

const emailHtml = await render(<WelcomeEmail username="John" />);
const emailText = toPlainText(emailHtml);

const options = {
  from: '"Your Company" <noreply@yourdomain.com>',
  to: 'user@example.com',
  subject: 'Welcome!',
  html: emailHtml,
  text: emailText, // Plain text fallback
};

await transporter.sendMail(options);
```

---

## SendGrid

Popular transactional email service by Twilio.

### Installation

```bash
npm install @sendgrid/mail @react-email/components
```

### Basic Usage

```tsx
// send-email.ts
import { render } from '@react-email/components';
import sendgrid from '@sendgrid/mail';
import { WelcomeEmail } from './emails/welcome';

sendgrid.setApiKey(process.env.SENDGRID_API_KEY || '');

const emailHtml = await render(<WelcomeEmail username="John" />);

const options = {
  from: 'noreply@yourdomain.com',
  to: 'user@example.com',
  subject: 'Welcome to Our Platform',
  html: emailHtml,
};

await sendgrid.send(options);
```

### With Dynamic Template Data

```tsx
const options = {
  from: 'noreply@yourdomain.com',
  to: 'user@example.com',
  subject: 'Your Order Confirmation',
  html: emailHtml,
  dynamicTemplateData: {
    orderNumber: '12345',
    customerName: 'John',
  },
};
```

---

## AWS SES

Amazon Simple Email Service - cost-effective at scale.

### Installation

```bash
npm install @aws-sdk/client-ses @react-email/components
```

### Basic Usage

```tsx
// send-email.ts
import { SES, SendEmailCommandInput } from '@aws-sdk/client-ses';
import { render } from '@react-email/components';
import { WelcomeEmail } from './emails/welcome';

const ses = new SES({ region: process.env.AWS_SES_REGION });

const emailHtml = await render(<WelcomeEmail username="John" />);

const params: SendEmailCommandInput = {
  Source: 'noreply@yourdomain.com',
  Destination: {
    ToAddresses: ['user@example.com'],
  },
  Message: {
    Body: {
      Html: {
        Charset: 'UTF-8',
        Data: emailHtml,
      },
    },
    Subject: {
      Charset: 'UTF-8',
      Data: 'Welcome to Our Platform',
    },
  },
};

await ses.sendEmail(params);
```

### With Plain Text

```tsx
import { render, toPlainText } from '@react-email/components';

const emailHtml = await render(<WelcomeEmail username="John" />);
const emailText = toPlainText(emailHtml);

const params: SendEmailCommandInput = {
  Source: 'noreply@yourdomain.com',
  Destination: {
    ToAddresses: ['user@example.com'],
  },
  Message: {
    Body: {
      Html: {
        Charset: 'UTF-8',
        Data: emailHtml,
      },
      Text: {
        Charset: 'UTF-8',
        Data: emailText,
      },
    },
    Subject: {
      Charset: 'UTF-8',
      Data: 'Welcome!',
    },
  },
};
```

---

## Postmark

Fast transactional email delivery with excellent analytics.

### Installation

```bash
npm install postmark @react-email/components
```

### Basic Usage

```tsx
// send-email.ts
import { render } from '@react-email/components';
import postmark from 'postmark';
import { WelcomeEmail } from './emails/welcome';

const client = new postmark.ServerClient(process.env.POSTMARK_API_KEY || '');

const emailHtml = await render(<WelcomeEmail username="John" />);

const options = {
  From: 'noreply@yourdomain.com',
  To: 'user@example.com',
  Subject: 'Welcome to Our Platform',
  HtmlBody: emailHtml,
};

await client.sendEmail(options);
```

### With Message Stream

```tsx
const options = {
  From: 'noreply@yourdomain.com',
  To: 'user@example.com',
  Subject: 'Welcome!',
  HtmlBody: emailHtml,
  MessageStream: 'outbound', // or 'broadcasts' for marketing
};
```

---

## MailerSend

Modern email delivery with drag-and-drop templates.

### Installation

```bash
npm install mailersend @react-email/components
```

### Basic Usage

```tsx
// send-email.ts
import { render } from '@react-email/components';
import { EmailParams, MailerSend, Recipient, Sender } from 'mailersend';
import { WelcomeEmail } from './emails/welcome';

const mailerSend = new MailerSend({
  apiKey: process.env.MAILERSEND_API_KEY || '',
});

const emailHtml = await render(<WelcomeEmail username="John" />);

const sentFrom = new Sender('noreply@yourdomain.com', 'Your Company');
const recipients = [new Recipient('user@example.com', 'John Doe')];

const emailParams = new EmailParams()
  .setFrom(sentFrom)
  .setTo(recipients)
  .setSubject('Welcome to Our Platform')
  .setHtml(emailHtml);

await mailerSend.email.send(emailParams);
```

---

## Plunk

Open-source email platform built for developers.

### Installation

```bash
npm install @plunk/node @react-email/components
```

### Basic Usage

```tsx
// send-email.ts
import plunkImport from '@plunk/node';
import { render } from '@react-email/components';
import { WelcomeEmail } from './emails/welcome';

// Handle default export quirk
const Plunk = (plunkImport as { default: typeof plunkImport }).default;
const plunk = new Plunk(process.env.PLUNK_API_KEY || '');

const emailHtml = await render(<WelcomeEmail username="John" />);

await plunk.emails.send({
  to: 'user@example.com',
  subject: 'Welcome to Our Platform',
  body: emailHtml,
});
```

---

## Common Patterns

### Async/Await Pattern

All integrations support async/await:

```tsx
async function sendWelcomeEmail(email: string, name: string) {
  try {
    const html = await render(<WelcomeEmail username={name} />);
    // Send with your provider
    return { success: true };
  } catch (error) {
    console.error('Email send failed:', error);
    return { success: false, error };
  }
}
```

### Batch Sending

For multiple recipients, check your provider's batch API:

```tsx
// SendGrid example
const messages = users.map(user => ({
  to: user.email,
  from: 'noreply@example.com',
  subject: 'Newsletter',
  html: await render(<Newsletter user={user} />),
}));

await sendgrid.send(messages);
```

### Error Handling

Always implement proper error handling:

```tsx
try {
  await provider.send(options);
  console.log('Email sent successfully');
} catch (error) {
  if (error.response) {
    console.error('Provider error:', error.response.body);
  } else {
    console.error('Send error:', error.message);
  }
  throw error;
}
```
