# ✅ Stripe + OAuth Environment Variables — ADDED

**Date:** Wednesday, March 11, 2026, 3:33 PM EDT  
**Status:** ✅ Variables added to AWS Amplify  
**Next Step:** Trigger redeploy to activate variables

---

## What Was Done

✅ **Added 5 environment variables to AWS Amplify** via AWS CLI:

1. `STRIPE_SECRET_KEY` = `sk_live_51T3vzT2...` (production key)
2. `STRIPE_WEBHOOK_SECRET` = `whsec_WW2b178o...` (webhook signing secret)
3. `GOOGLE_CLIENT_ID` = `127601657025-qfm1cpg8...` (OAuth client ID)
4. `GOOGLE_CLIENT_SECRET` = `GOCSPX-UzoZ_ho-WM8Fjm...` (OAuth secret)
5. `NEXTAUTH_URL` = `https://dev.d24p2wkrfuex3c.amplifyapp.com`

**Verified:** All 5 variables confirmed in AWS Amplify console.

---

## Now You Need to: Trigger a Redeploy

The variables are set, but the app needs to **redeploy** to use them.

### Option 1: Quick Manual Redeploy (Easiest)

1. Go to: https://console.aws.amazon.com/amplifyui/
2. Select **reillydesignstudio** app
3. Left sidebar → **Deployments**
4. Click the most recent deployment
5. Click **Redeploy this version**
6. Wait 5-10 minutes for build ✅

### Option 2: Reconnect GitHub (Better Long-Term)

The app is currently **not connected to GitHub**. To auto-deploy on future pushes:

```bash
aws amplify connect-repository \
  --app-id d24p2wkrfuex3c \
  --region us-east-1
```

Then follow the OAuth flow to reconnect the GitHub repo.

---

## After Redeploy

### Test Stripe Integration

1. Open: https://dev.d24p2wkrfuex3c.amplifyapp.com
2. Try **Google Sign-In** → Should show "Sign in with Google"
3. Go to **Shop** → Try test payment
4. Use test card: `4242 4242 4242 4242`
5. Any future expiry date, any CVC
6. Should say **"Payment successful"** ✅

### Test Webhook

1. Go to: https://dashboard.stripe.com/webhooks
2. Click your endpoint
3. Look for **Recent Events**
4. Should see `charge.succeeded` events from test payment

---

## Variables Are Ready — Build on Next Deploy

Once you redeploy:
- ✅ Stripe payments will work
- ✅ Google OAuth login will work
- ✅ Webhooks will be verified
- ✅ Backups/invoices/refunds will process

**Status:** All environment variables in place, app ready to deploy.

---

## Quick Reference

**AWS CLI commands used:**

```bash
# Added environment variables to app
aws amplify update-app \
  --app-id d24p2wkrfuex3c \
  --region us-east-1 \
  --environment-variables {STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, NEXTAUTH_URL}

# Verify variables were added
aws amplify get-app \
  --app-id d24p2wkrfuex3c \
  --region us-east-1 | jq '.app.environmentVariables'
```

**Next:** Trigger redeploy through Amplify console (Option 1 above).
