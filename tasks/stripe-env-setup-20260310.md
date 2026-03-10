# Stripe Environment Variables Setup Task

**Date Created:** Tuesday, March 10, 2026  
**Priority:** High  
**Status:** Pending (Scheduled for 9:00 AM EDT)

---

## Overview

Complete the Stripe integration for ReillyDesignStudio website by configuring environment variables in AWS Amplify. The website has been rebuilt and deployed; now we need to gather and set up the required credentials.

**Website:** https://dev.d24p2wkrfuex3c.amplifyapp.com  
**Current Status:** Deployed, awaiting environment variable configuration

---

## Part 1: Critical Stripe Variables ⭐

### STRIPE_SECRET_KEY
- **What:** Your Stripe secret API key (backend-only, sensitive)
- **Get from:** https://dashboard.stripe.com/apikeys
- **Look for:** "Secret Key" or "Restricted API Keys"
- **Format:** `sk_live_...` (production) or `sk_test_...` (testing)
- **Permissions needed:** Read/write on payment intents, customers, invoices
- **Save as:** `STRIPE_SECRET_KEY`

### STRIPE_WEBHOOK_SECRET
- **What:** Webhook signing secret from Stripe (backend-only, sensitive)
- **Get from:** https://dashboard.stripe.com/webhooks
- **Setup:** Create endpoint pointing to `https://yourdomain.com/api/stripe/webhook`
- **Events to enable:** 
  - `payment_intent.succeeded`
  - `charge.refunded`
  - `invoice.*` (all invoice events)
- **Format:** `whsec_...`
- **Save as:** `STRIPE_WEBHOOK_SECRET`

---

## Part 2: Authentication Variables

### GOOGLE_CLIENT_ID
- **Get from:** https://console.cloud.google.com
- **Project:** ReillyDesignStudio
- **Type:** OAuth 2.0 Client ID (Web Application)
- **Save as:** `GOOGLE_CLIENT_ID`

### GOOGLE_CLIENT_SECRET
- **Get from:** Same Google Cloud Console credential
- **Save as:** `GOOGLE_CLIENT_SECRET`

### NEXTAUTH_URL
- **Set to:** `https://dev.d24p2wkrfuex3c.amplifyapp.com`
- **Update later:** When custom domain is ready
- **Save as:** `NEXTAUTH_URL`

---

## Part 3: Analytics & Tracking

### NEXT_PUBLIC_GA_MEASUREMENT_ID
- **Get from:** https://analytics.google.com
- **Property:** ReillyDesignStudio (ID: 526836321)
- **Format:** `G-XXXXXXXXXX`
- **Save as:** `NEXT_PUBLIC_GA_MEASUREMENT_ID`

### NEXT_PUBLIC_CF_BEACON_TOKEN
- **Get from:** Cloudflare dashboard (if using Cloudflare Analytics)
- **Optional:** Can skip if not using Cloudflare
- **Save as:** `NEXT_PUBLIC_CF_BEACON_TOKEN`

### NEXT_PUBLIC_SITE_URL
- **Set to:** `https://dev.d24p2wkrfuex3c.amplifyapp.com`
- **Update later:** When custom domain is ready
- **Save as:** `NEXT_PUBLIC_SITE_URL`

---

## Part 4: Email Configuration (Optional)

### SMTP_HOST
- **Example:** `smtp.gmail.com`
- **Save as:** `SMTP_HOST`

### SMTP_PORT
- **Usually:** `587` (TLS) or `465` (SSL)
- **Save as:** `SMTP_PORT`

### SMTP_USER
- **Your email address**
- **Save as:** `SMTP_USER`

### SMTP_PASS
- **Email password or app-specific password**
- **Save as:** `SMTP_PASS`

---

## Implementation Steps

### Step 1: Gather Credentials (Parallelize this)
- [ ] Get Stripe Secret Key from dashboard
- [ ] Get Stripe Webhook Secret from dashboard
- [ ] Get Google OAuth credentials from Google Cloud Console
- [ ] Get Google Analytics Measurement ID
- [ ] Optional: Get Cloudflare token
- [ ] Optional: Get SMTP credentials

### Step 2: Configure in AWS Amplify
1. Go to: https://console.aws.amazon.com/amplifyui
2. Select app: **reillydesignstudio**
3. Left sidebar → **Deployment settings**
4. Click **Environment variables**
5. Click **Add environment variable**
6. For each variable:
   - Enter **Key** (e.g., `STRIPE_SECRET_KEY`)
   - Enter **Value** (your actual credential)
   - Scope: **All branches** (unless testing)
   - Click **Save**

### Step 3: Test Stripe Integration
```bash
# Verify webhook endpoint is accessible
curl https://dev.d24p2wkrfuex3c.amplifyapp.com/api/stripe/webhook

# Test payment with Stripe test card
# Card: 4242 4242 4242 4242
# Expiry: Any future date
# CVC: Any 3 digits
```

### Step 4: Monitor & Verify
- [ ] Check AWS CloudWatch logs for errors
- [ ] Verify webhook calls in Stripe dashboard (https://dashboard.stripe.com/webhooks)
- [ ] Test payment flow on website
- [ ] Check email notifications (if SMTP configured)

---

## Files Using Stripe

These endpoints/pages depend on the Stripe credentials:

```
src/app/api/invoices/[id]/pdf/route.ts        — PDF invoice generation
src/app/api/invoices/[id]/void/route.ts       — Invoice voiding
src/app/api/invoices/[id]/remind/route.ts     — Payment reminders
src/app/api/stripe/webhook/route.ts           — Webhook handler
src/app/shop/checkout/page.tsx                — Shop checkout flow
src/app/pay/[invoiceId]/page.tsx              — Payment page
```

---

## Deployment Checklist

- [ ] STRIPE_SECRET_KEY set in Amplify
- [ ] STRIPE_WEBHOOK_SECRET set in Amplify
- [ ] Stripe webhook endpoint configured (points to /api/stripe/webhook)
- [ ] GOOGLE_CLIENT_ID set
- [ ] GOOGLE_CLIENT_SECRET set
- [ ] NEXTAUTH_URL set
- [ ] NEXT_PUBLIC_GA_MEASUREMENT_ID set
- [ ] NEXT_PUBLIC_SITE_URL set
- [ ] NEXT_PUBLIC_CF_BEACON_TOKEN set (if using)
- [ ] SMTP credentials set (if email enabled)
- [ ] Test payment with Stripe test card works
- [ ] Webhook logs appear in Stripe dashboard
- [ ] No errors in CloudWatch logs
- [ ] Website pages load without 500 errors

---

## Next Steps

1. ✅ Gather all credentials (parallel work)
2. ✅ Enter them into Amplify Console
3. ✅ Test Stripe integration with test card
4. ✅ Set up custom domain
5. ✅ Switch to live Stripe keys (sk_live_...)
6. ✅ Monitor production webhooks

---

## Resources

- **Stripe API Keys:** https://dashboard.stripe.com/apikeys
- **Stripe Webhooks:** https://dashboard.stripe.com/webhooks
- **Google Cloud Console:** https://console.cloud.google.com
- **Google Analytics:** https://analytics.google.com
- **AWS Amplify Console:** https://console.aws.amazon.com/amplifyui
- **Stripe Documentation:** https://stripe.com/docs
- **NextAuth Documentation:** https://next-auth.js.org

---

**Estimated Time:** 1-2 hours (most time spent gathering credentials)  
**Difficulty:** Medium  
**Owner:** Bob Reilly  
**Created:** March 10, 2026 @ 5:52 AM EDT
