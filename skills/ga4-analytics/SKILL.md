---
name: ga4-analytics
description: Access Google Analytics 4 data and generate reports. Use when you need traffic stats, user behavior, conversions, revenue, device data, or custom analytics reports for your website.
---

# GA4 Analytics

Access Google Analytics 4 (GA4) data and generate custom reports using the Google Analytics API.

## Setup

**Prerequisites:**
1. GA4 property ID (found in GA4 Admin → Property → Property Settings)
2. Google Cloud service account with Analytics Reporting API access
3. Service account key (JSON file)

**First-time setup:**
```bash
# Store service account credentials
export GA4_PROPERTY_ID="12345678"  # Your GA4 Property ID
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

## Get GA4 Property ID

1. Go to: https://analytics.google.com
2. Select "ReillyDesignStudio" property
3. Admin → Property → Property Settings
4. Copy the **Property ID** (format: `12345678`)

## Create Service Account

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Create a new service account
3. Grant role: **Viewer** (minimal read-only access)
4. Create and download JSON key
5. Save to: `~/.openclaw/workspace/secrets/ga4-service-account.json`

## Query GA4 Data

```bash
# Using gog (Google CLI)
gog analytics report \
  --property-id=12345678 \
  --date-ranges="7daysAgo,today" \
  --dimensions="date" \
  --metrics="sessions,users,bounceRate"

# Using API directly (Python/Node)
# See examples below
```

## Common Reports

### Traffic Overview (Last 7 Days)
```bash
gog analytics report \
  --property-id=12345678 \
  --date-ranges="7daysAgo,today" \
  --dimensions="date" \
  --metrics="sessions,users,newUsers,bounceRate,sessionDuration"
```

### Traffic by Device
```bash
gog analytics report \
  --property-id=12345678 \
  --date-ranges="7daysAgo,today" \
  --dimensions="deviceCategory" \
  --metrics="sessions,users,bounceRate"
```

### Traffic by Page
```bash
gog analytics report \
  --property-id=12345678 \
  --date-ranges="7daysAgo,today" \
  --dimensions="pagePath" \
  --metrics="sessions,users,bounceRate,avgSessionDuration"
```

### Traffic by Country
```bash
gog analytics report \
  --property-id=12345678 \
  --date-ranges="7daysAgo,today" \
  --dimensions="country" \
  --metrics="sessions,users"
```

### Conversions (Goals)
```bash
gog analytics report \
  --property-id=12345678 \
  --date-ranges="7daysAgo,today" \
  --dimensions="eventName" \
  --metrics="eventCount,conversionRate"
```

### Top Landing Pages
```bash
gog analytics report \
  --property-id=12345678 \
  --date-ranges="7daysAgo,today" \
  --dimensions="landingPage" \
  --metrics="sessions,users,conversionRate"
```

## Date Ranges

```
--date-ranges="TODAY"              # Today only
--date-ranges="7daysAgo,today"     # Last 7 days
--date-ranges="30daysAgo,today"    # Last 30 days
--date-ranges="1monthAgo,today"    # Last month
--date-ranges="YEARTODATE"         # Year to date
```

## Key Metrics

| Metric | Definition |
|--------|-----------|
| `sessions` | Number of sessions (visits) |
| `users` | Number of unique users |
| `newUsers` | New visitor count |
| `bounceRate` | % of sessions that bounced (left after 1 page) |
| `sessionDuration` | Average time per session |
| `pageviews` | Total page views |
| `eventsPerSession` | Average events per session |
| `conversionRate` | % of sessions with conversions |

## Key Dimensions

| Dimension | Description |
|-----------|-------------|
| `date` | Date |
| `deviceCategory` | Desktop, mobile, tablet |
| `country` | Geographic location |
| `pagePath` | Page URL path |
| `eventName` | Event/goal name |
| `source` | Traffic source (google, direct, etc) |
| `medium` | Traffic medium (organic, cpc, referral) |
| `campaign` | Campaign name |

## Generate Reports

### Monthly Report
```bash
gog analytics report \
  --property-id=12345678 \
  --date-ranges="30daysAgo,today" \
  --dimensions="date,deviceCategory" \
  --metrics="sessions,users,bounceRate" \
  --json > monthly_report.json
```

### Compare Periods
```bash
# This month vs last month
gog analytics report \
  --property-id=12345678 \
  --date-ranges="1monthAgo,today" "2monthsAgo,1monthAgo" \
  --dimensions="date" \
  --metrics="sessions,users,conversionRate"
```

## Python Example (Full API Access)

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

client = BetaAnalyticsDataClient()
request = RunReportRequest(
    property=f"properties/12345678",
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    dimensions=[Dimension(name="date")],
    metrics=[Metric(name="sessions"), Metric(name="users")]
)

response = client.run_report(request)

for row in response.rows:
    print(f"{row.dimension_values[0].value}: {row.metric_values[0].value} sessions")
```

## Node.js Example

```javascript
const {BetaAnalyticsDataClient} = require('@google-analytics/data');

const client = new BetaAnalyticsDataClient();

async function getReport() {
  const [response] = await client.runReport({
    property: `properties/12345678`,
    dateRanges: [{startDate: '7daysAgo', endDate: 'today'}],
    dimensions: [{name: 'date'}],
    metrics: [{name: 'sessions'}, {name: 'users'}]
  });

  return response;
}
```

## Troubleshooting

**"Property not found"**
- Verify Property ID in GA4 Admin
- Check service account has access to property

**"Invalid credentials"**
- Regenerate service account key
- Check GOOGLE_APPLICATION_CREDENTIALS path
- Verify Analytics Reporting API is enabled in Cloud Console

**"Rate limit exceeded"**
- Stagger API requests
- Cache results when possible
- Use date range filters to reduce data

## Resources

- **GA4 Admin:** https://analytics.google.com
- **Google Cloud Console:** https://console.cloud.google.com
- **Analytics API Docs:** https://developers.google.com/analytics/devguides/reporting/data/v1
- **Dimension/Metric Reference:** https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema
