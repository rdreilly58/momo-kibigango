# AWS Amplify — Environment Variables Setup

**Date:** Wednesday, March 11, 2026, 3:21 PM EDT  
**Status:** Ready to add to Amplify

---

## Your 5 Environment Variables

### 1. STRIPE_SECRET_KEY
```
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
```

### 2. STRIPE_WEBHOOK_SECRET
```
whsec_WW2b178oPoVz88rux7g4PszQzxvbeE5y
```

### 3. GOOGLE_CLIENT_ID
```
127601657025-qfm1cpg8l8u7v61ohcub6t3f9if00qql.apps.googleusercontent.com
```

### 4. GOOGLE_CLIENT_SECRET
```
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
```

### 5. NEXTAUTH_URL
```
https://dev.d24p2wkrfuex3c.amplifyapp.com
```

---

## How to Add These to AWS Amplify

### Step 1: Open AWS Amplify Console
https://console.aws.amazon.com/amplifyui/

### Step 2: Select Your App
- Look for **reillydesignstudio**
- Click to open

### Step 3: Go to Deployment Settings
- Left sidebar → **Deployment settings**
- Scroll down to **Environment variables**

### Step 4: Add Each Variable
For each of the 5 variables above:

1. Click **Add environment variable**
2. Enter **Key** (from list above)
3. Enter **Value** (from list above)
4. Choose scope: **All branches** (recommended)
5. Click **Save**

**Repeat for all 5 variables.**

---

## After Adding Variables

### Step 5: Redeploy
1. Go to **Deployments** (left sidebar)
2. Click the most recent deployment
3. Click **Redeploy this version**
4. Wait for build to complete (5-10 minutes)
5. Check status: Green checkmark = Success ✅

### Step 6: Test Stripe
1. Open: https://dev.d24p2wkrfuex3c.amplifyapp.com
2. Go to **Shop** or **Invoices**
3. Try to make a payment
4. Use test card: `4242 4242 4242 4242`
5. Any future expiry date + any CVC
6. Should succeed

### Step 7: Verify Webhook
1. Go to: https://dashboard.stripe.com/webhooks
2. Click your endpoint
3. Look for **Recent Events**
4. Should see `charge.succeeded` events when you make test payments

---

## Troubleshooting

### Build fails after adding variables
- Check for typos in key names (case-sensitive)
- Make sure values are complete (no missing characters)
- Redeploy again

### Stripe payment fails
- Verify STRIPE_SECRET_KEY is correct (starts with `sk_live_`)
- Check STRIPE_WEBHOOK_SECRET is set
- Look at function logs in CloudWatch

### OAuth fails
- Verify Google OAuth redirect URI includes `/api/auth/callback/google`
- Check GOOGLE_CLIENT_ID and SECRET are correct
- Make sure OAuth consent screen is configured

### Still stuck?
Check AWS Amplify build logs:
1. Go to **Deployments**
2. Click failed deployment
3. Click **Build logs**
4. Search for errors

---

## What These Variables Do

| Variable | Purpose |
|----------|---------|
| `STRIPE_SECRET_KEY` | Backend payment processing, charges, invoices |
| `STRIPE_WEBHOOK_SECRET` | Receive webhook events from Stripe (payments confirmed, etc.) |
| `GOOGLE_CLIENT_ID` | Frontend OAuth login button |
| `GOOGLE_CLIENT_SECRET` | Backend OAuth token verification |
| `NEXTAUTH_URL` | Where OAuth redirects back to (your domain) |

---

## Production Checklist

- [ ] All 5 variables added to Amplify
- [ ] Deployment successful (green checkmark)
- [ ] Website loads without errors
- [ ] Test Stripe payment works
- [ ] Webhook events appear in Stripe dashboard
- [ ] OAuth login works (test with Google account)
- [ ] Email confirmations sending

---

## Next Steps

Once verified:
1. Add custom domain (optional)
2. Update NEXTAUTH_URL to custom domain
3. Switch to production (if you want)
4. Monitor webhook logs daily

---

**Status:** Ready to deploy ✅  
**Time to add variables:** 5 minutes  
**Time for build:** 5-10 minutes  
**Total:** 10-15 minutes
