# Stripe Integration Setup Guide

## Deployment Status ✅

**Website:** https://dev.d24p2wkrfuex3c.amplifyapp.com
**Status:** Rebuilt and deployed to AWS Amplify
**Last Deploy:** March 10, 2026

## Environment Variables Needed

### 1. Stripe Configuration ⭐ CRITICAL
These enable payment processing and webhooks.

```
STRIPE_SECRET_KEY
  └─ Get from: https://dashboard.stripe.com/apikeys
  └─ Label: "Restricted API Keys" or "Secret Key"
  └─ Format: sk_live_... (production) or sk_test_... (testing)
  └─ Permissions: Needs read/write on payment intents, customers, invoices

STRIPE_WEBHOOK_SECRET
  └─ Get from: https://dashboard.stripe.com/webhooks
  └─ Create endpoint: https://yourdomain.com/api/stripe/webhook
  └─ Format: whsec_... 
  └─ Events: payment_intent.succeeded, charge.refunded, invoice.*
```

### 2. Authentication (Google OAuth)

```
GOOGLE_CLIENT_ID
  └─ Get from: https://console.cloud.google.com/
  └─ Project: ReillyDesignStudio or similar
  └─ OAuth 2.0 Client ID (Web Application)

GOOGLE_CLIENT_SECRET
  └─ From same OAuth credential

NEXTAUTH_URL
  └─ Set to: https://dev.d24p2wkrfuex3c.amplifyapp.com
  └─ Or custom domain when ready
```

### 3. Analytics & Tracking

```
NEXT_PUBLIC_GA_MEASUREMENT_ID
  └─ Get from: https://analytics.google.com
  └─ Property: ReillyDesignStudio (526836321)
  └─ Format: G-XXXXXXXXXX

NEXT_PUBLIC_CF_BEACON_TOKEN
  └─ Cloudflare Web Analytics token
  └─ Get from: Cloudflare dashboard
  └─ (Optional, remove if not used)

NEXT_PUBLIC_SITE_URL
  └─ Set to: https://dev.d24p2wkrfuex3c.amplifyapp.com
  └─ Or your production domain
```

### 4. Email Configuration (SMTP)

```
SMTP_HOST
  └─ Your email server (e.g., smtp.gmail.com)

SMTP_PORT
  └─ Usually 587 (TLS) or 465 (SSL)

SMTP_USER
  └─ Your email address

SMTP_PASS
  └─ Email password or app-specific password
```

## How to Set These in AWS Amplify

### Step 1: Open AWS Amplify Console
https://console.aws.amazon.com/amplifyui

### Step 2: Select Your App
- Find "reillydesignstudio"
- Click to open

### Step 3: Navigate to Environment Variables
- Left sidebar → **Deployment settings**
- Under "Environment variables"
- Click **Add environment variable**

### Step 4: Add Variables
For each variable above:
1. Enter **Key** (e.g., STRIPE_SECRET_KEY)
2. Enter **Value** (your actual key)
3. Choose scope: **All branches** or specific branch
4. Click **Save**

**Important:** Variables starting with `NEXT_PUBLIC_` are visible in frontend code (safe for public values like IDs). Others are backend-only (safe for secrets like keys).

## Testing Stripe Integration

### 1. Verify Webhook Endpoint
```bash
# Check if /api/stripe/webhook is accessible
curl https://dev.d24p2wkrfuex3c.amplifyapp.com/api/stripe/webhook
```

### 2. Test with Stripe Test Mode
- Go to: https://dashboard.stripe.com/test/dashboard
- Use test card: 4242 4242 4242 4242
- Expiry: Any future date
- CVC: Any 3 digits

### 3. Monitor Logs
AWS CloudWatch → Amplify logs → Look for Stripe webhook calls

## Deployment Checklist

- [ ] STRIPE_SECRET_KEY set in Amplify
- [ ] STRIPE_WEBHOOK_SECRET configured in Amplify
- [ ] Stripe webhook endpoint pointing to /api/stripe/webhook
- [ ] GOOGLE_CLIENT_ID and SECRET set
- [ ] NEXTAUTH_URL set
- [ ] GA4 measurement ID set
- [ ] SMTP credentials set (if email enabled)
- [ ] Test payment with Stripe test card
- [ ] Verify webhook logs in Stripe dashboard
- [ ] Deploy to production with live Stripe keys

## Files Using Stripe

```
src/app/api/invoices/[id]/pdf/route.ts      — PDF generation
src/app/api/invoices/[id]/void/route.ts     — Invoice voiding
src/app/api/invoices/[id]/remind/route.ts   — Payment reminders
src/app/api/stripe/webhook/route.ts         — Webhook handler
src/app/shop/checkout/page.tsx              — Checkout flow
src/app/pay/[invoiceId]/page.tsx            — Payment page
```

## Custom Domain Setup (When Ready)

1. Go to Amplify → Domain management
2. Connect your custom domain
3. Update NEXTAUTH_URL and NEXT_PUBLIC_SITE_URL
4. Update Stripe webhook URL
5. Redeploy

## Support

- Stripe docs: https://stripe.com/docs
- NextAuth docs: https://next-auth.js.org
- AWS Amplify docs: https://docs.amplify.aws
