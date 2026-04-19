# GA4 Setup Guide for momo-kiji.dev

## Phase 1: Create GA4 Property (Manual, 5 min)

### Step 1: Go to Google Analytics
1. Navigate to: https://analytics.google.com
2. Click **Create** (or **+ Create Property** if you have existing properties)

### Step 2: Property Configuration
- **Property Name:** momo-kiji
- **Website URL:** https://momo-kiji.dev
- **Industry Category:** Software
- **Timezone:** America/New_York
- **Currency:** USD

### Step 3: Create Web Data Stream
- **Platform:** Web
- **Website URL:** https://momo-kiji.dev
- **Stream Name:** momo-kiji-web

### Step 4: Get Measurement ID
After creating the data stream, you'll get a **Measurement ID** that looks like:
```
G-XXXXXXXXXX
```

**Save this ID** — you'll need it for the code.

---

## Phase 2: Add GA4 to Next.js (Automated, 2 min)

### Option A: Using Google Tag Manager (Recommended for Production)

1. Create GTM container at: https://tagmanager.google.com
2. Add GA4 tag
3. Add GTM script to `pages/_app.tsx`

### Option B: Direct gtag Implementation (Simpler for Now)

**File:** `pages/_app.tsx`

```typescript
import Script from 'next/script'

export default function App({ Component, pageProps }) {
  return (
    <>
      <Script
        strategy="afterInteractive"
        src={`https://www.googletagmanager.com/gtag/js?id=G-YOUR_MEASUREMENT_ID`}
      />
      <Script
        id="google-analytics"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-YOUR_MEASUREMENT_ID', {
              page_path: window.location.pathname,
            });
          `,
        }}
      />
      <Component {...pageProps} />
    </>
  )
}
```

**Replace:** `G-YOUR_MEASUREMENT_ID` with your actual Measurement ID

---

## Phase 3: Track Custom Events (Optional but Recommended)

Add event tracking for important user actions:

```typescript
// Track when users visit docs/GitHub
export const trackExternalClick = (destination: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'external_link_click', {
      destination: destination,
      timestamp: new Date().toISOString()
    })
  }
}

// Track newsletter signups
export const trackNewsletterSignup = (email: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'newsletter_signup', {
      email_domain: email.split('@')[1]
    })
  }
}

// Track documentation page views
export const trackDocView = (docPath: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('pageview', {
      page_path: docPath,
      page_title: docPath
    })
  }
}
```

---

## Phase 4: Verify Installation (5 min)

### Check in Google Analytics
1. Go back to: https://analytics.google.com
2. Navigate to **Real-time** → **Overview**
3. Visit momo-kiji.dev in a browser
4. You should see traffic appear in real-time within 30 seconds

### Check in Browser Console
```javascript
// In DevTools console:
window.gtag('event', 'test_event')
```

---

## Phase 5: Set Up Conversion Tracking (Optional)

### Key Conversions for momo-kiji:
1. **GitHub Link Click** — Users exploring the project
2. **Discord Join** — Community engagement
3. **Newsletter Signup** — (when added)
4. **Documentation View** — Research interest

**To set up in GA4:**
1. Go to **Admin** → **Events** → **Create Event**
2. Create matching events for each conversion
3. Set conversion goals in **Conversions** section

---

## Phase 6: Connect to BigQuery (Optional, for Advanced Analytics)

Once GA4 is collecting data (after 24 hours):

1. Go to **Admin** → **BigQuery Links**
2. Link to project: `127601657025`
3. Dataset: Create new dataset `ga4_momo_kiji` or reuse existing
4. Authorize

This enables:
- Real-time SQL queries on raw event data
- Custom dashboards
- Integration with data pipelines

---

## Dashboard Setup (Recommended)

### Key Metrics to Track:
- **Users:** Unique visitors to momo-kiji.dev
- **Sessions:** How long users spend on site
- **Engagement Rate:** Pages viewed, time on page
- **Traffic Sources:** Where users come from (GitHub, social, direct)
- **Top Pages:** Which content resonates
- **Conversions:** GitHub clicks, Discord joins

### Create Custom Dashboard:
1. Click **+ Create** in Analytics home
2. Add cards for each metric
3. Pin important cards
4. Share with team

---

## Monitoring & Alerts

### Set Up Conversion Alerts:
1. **Admin** → **Events**
2. Create alerts for:
   - Unusual drop in traffic
   - Spike in conversions
   - New traffic sources

### Weekly Checks:
- Traffic trends
- Top referring sources
- User behavior flow
- Conversion rates

---

## Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Create GA4 Property | 5 min | TODO |
| 2 | Add gtag to Next.js | 2 min | TODO |
| 3 | Deploy to Vercel | 1 min | TODO |
| 4 | Verify in Real-time | 5 min | TODO |
| 5 | Set Up Conversions | 10 min | TODO |
| 6 | Link BigQuery | 5 min | TODO |
| **Total** | | **~30 min** | |

---

## Next Steps After GA4 Setup

1. **Monitor launch week traffic** (next week, 3/24+)
   - Track HackerNews, Reddit, dev.to referrals
   - Watch conversion rate on GitHub/Discord links
   - Analyze user behavior flow

2. **Set up automated reports** (weekly)
   - Email traffic summary
   - User engagement trends
   - Conversion funnel analysis

3. **Optimize based on data**
   - Identify high-traffic pages
   - Improve low-engagement sections
   - A/B test landing page copy

4. **Integrate with BigQuery** (after 24h)
   - Build custom analytics queries
   - Create dashboards in Data Studio
   - Track detailed user journeys

---

## Support

- **GA4 Setup Help:** https://support.google.com/analytics/answer/10089681
- **Next.js Analytics:** https://nextjs.org/docs/guides/analytics
- **BigQuery Integration:** https://support.google.com/analytics/answer/9358801

---

**Questions?** Let me know what's blocking you! 🍑
