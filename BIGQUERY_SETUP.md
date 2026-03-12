# BigQuery Setup Guide - Phase 1 Week 2

## Overview
BigQuery gives you direct SQL access to all GA4 data, enabling custom analyses beyond the UI.

---

## Step 1: Enable BigQuery in Google Cloud

1. Go to: **Google Cloud Console** → https://console.cloud.google.com
2. Select Project: **rds-analytics-489420**
3. Search for: **BigQuery API**
4. Click: **Enable**
5. Wait for activation (1-2 minutes)

---

## Step 2: Link GA4 to BigQuery

1. Go to **Google Analytics 4** → **Admin** → **Data streams**
2. Click your property stream (ReillyDesignStudio)
3. Scroll to **Google Cloud**
4. Click: **Link BigQuery property**
5. Select: **rds-analytics-489420** (your GCP project)
6. Click: **Link**
7. Wait for data export to start (can take 24 hours for first export)

---

## Step 3: Set Up Python BigQuery Client

### Install BigQuery library
```bash
pip install google-cloud-bigquery
```

### Test connection
```python
from google.cloud import bigquery

client = bigquery.Client(project="rds-analytics-489420")

# Test query
query = """
SELECT
  COUNT(*) as total_events,
  COUNT(DISTINCT user_pseudo_id) as unique_users
FROM `rds-analytics-489420.analytics_526836321.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20260303' AND '20260310'
"""

results = client.query(query).result()
for row in results:
    print(f"Total events: {row.total_events}, Unique users: {row.unique_users}")
```

---

## Step 4: Example Queries for RDS

### Query 1: Top Pages by Engagement (Not Just Views)
```sql
SELECT
  event_params[SAFE.OFFSET(0)].value.string_value as page_title,
  COUNT(*) as page_views,
  AVG(CAST(event_params[SAFE.OFFSET(1)].value.int_value AS FLOAT64)) as avg_session_duration,
  COUNTIF(event_name = 'page_view' AND engagement_time_msec < 1000) / COUNT(*) as bounce_rate,
  
  -- Content score calculation
  ROUND((COUNT(*) * 0.3) + (AVG(CAST(event_params[SAFE.OFFSET(1)].value.int_value AS FLOAT64)) * 0.4) + ((1 - (COUNTIF(event_name = 'page_view' AND engagement_time_msec < 1000) / COUNT(*))) * 3), 1) as engagement_score
  
FROM `rds-analytics-489420.analytics_526836321.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20260303' AND '20260310'
  AND event_name = 'page_view'
GROUP BY page_title
ORDER BY engagement_score DESC
LIMIT 10;
```

### Query 2: Visitor Cohorts (New vs Returning)
```sql
WITH first_visit AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) as first_visit_date
  FROM `rds-analytics-489420.analytics_526836321.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20260303' AND '20260310'
  GROUP BY user_pseudo_id
),

current_visits AS (
  SELECT
    e.user_pseudo_id,
    DATE(TIMESTAMP_MICROS(e.event_timestamp)) as visit_date,
    COUNTIF(e.event_name = 'page_view') as pages_viewed,
    SUM(e.engagement_time_msec) as session_duration
  FROM `rds-analytics-489420.analytics_526836321.events_*` e
  WHERE _TABLE_SUFFIX BETWEEN '20260303' AND '20260310'
  GROUP BY e.user_pseudo_id, visit_date
)

SELECT
  CASE
    WHEN cv.visit_date = fv.first_visit_date THEN 'New Visitor'
    ELSE 'Returning Visitor'
  END as visitor_type,
  COUNT(DISTINCT cv.user_pseudo_id) as unique_users,
  AVG(cv.pages_viewed) as avg_pages_per_session,
  AVG(cv.session_duration / 1000) as avg_session_duration_seconds
FROM current_visits cv
JOIN first_visit fv ON cv.user_pseudo_id = fv.user_pseudo_id
GROUP BY visitor_type;
```

### Query 3: Conversion Funnel (Portfolio Interest)
```sql
SELECT
  'Step 1: Homepage' as step,
  COUNT(DISTINCT user_pseudo_id) as users
FROM `rds-analytics-489420.analytics_526836321.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20260303' AND '20260310'
  AND event_name = 'page_view'
  AND event_params[SAFE.OFFSET(0)].value.string_value = '/'

UNION ALL

SELECT
  'Step 2: Portfolio' as step,
  COUNT(DISTINCT user_pseudo_id) as users
FROM `rds-analytics-489420.analytics_526836321.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20260303' AND '20260310'
  AND event_name = 'page_view'
  AND event_params[SAFE.OFFSET(0)].value.string_value LIKE '/portfolio%'

UNION ALL

SELECT
  'Step 3: Contact Form' as step,
  COUNT(DISTINCT user_pseudo_id) as users
FROM `rds-analytics-489420.analytics_526836321.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20260303' AND '20260310'
  AND event_name = 'form_submit'
ORDER BY users DESC;
```

### Query 4: Traffic Source Quality
```sql
SELECT
  traffic_source.source as source,
  COUNT(*) as sessions,
  COUNT(DISTINCT user_pseudo_id) as unique_users,
  AVG(engagement_time_msec / 1000) as avg_engagement_seconds,
  ROUND(100 * COUNTIF(engagement_time_msec < 1000) / COUNT(*), 1) as bounce_rate_pct,
  
  -- Quality score (duration × engagement × returning rate)
  ROUND((AVG(engagement_time_msec / 1000) / 100) * (1 - (COUNTIF(engagement_time_msec < 1000) / COUNT(*))) * 10, 1) as quality_score
  
FROM `rds-analytics-489420.analytics_526836321.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20260303' AND '20260310'
GROUP BY source
ORDER BY quality_score DESC;
```

---

## Step 5: Integrate BigQuery Results into Briefing

### Python snippet to add to briefing script
```python
from google.cloud import bigquery

def get_bigquery_insights():
    """Fetch custom insights from BigQuery"""
    client = bigquery.Client(project="rds-analytics-489420")
    
    # Query top engagement pages
    query = """
    SELECT
      event_params[SAFE.OFFSET(0)].value.string_value as page,
      COUNT(*) as views,
      AVG(engagement_time_msec) as avg_engagement
    FROM `rds-analytics-489420.analytics_526836321.events_*`
    WHERE _TABLE_SUFFIX BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()
    GROUP BY page
    ORDER BY views DESC
    LIMIT 5
    """
    
    results = client.query(query).result()
    return results.to_dataframe()

# In briefing generation:
bq_insights = get_bigquery_insights()
for _, row in bq_insights.iterrows():
    briefing += f"• {row['page']}: {row['views']} views ({row['avg_engagement']/1000:.1f}s avg)\n"
```

---

## Step 6: Example Looker Studio with BigQuery

1. Create new Looker Studio report
2. Create data source → BigQuery
3. Select project: **rds-analytics-489420**
4. Select table: **events_YYYYMMDD** (raw events)
5. Create custom dimensions/metrics using SQL expressions
6. Build visualizations from custom queries

---

## Useful BigQuery Patterns

### Date range parameter (for easy updates)
```sql
DECLARE start_date DATE DEFAULT DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY);
DECLARE end_date DATE DEFAULT CURRENT_DATE();

SELECT ...
WHERE _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', start_date) AND FORMAT_DATE('%Y%m%d', end_date)
```

### Event parameter parsing
```sql
-- Extract page title from event params
SELECT
  event_params[SAFE.OFFSET(0)].value.string_value as page_title
FROM events_*
WHERE event_name = 'page_view'
```

### Session reconstruction (without events table)
```sql
SELECT
  user_pseudo_id,
  TIMESTAMP_MICROS(event_timestamp) as event_time,
  event_name,
  ROW_NUMBER() OVER (PARTITION BY user_pseudo_id ORDER BY event_timestamp) as event_sequence
FROM events_*
ORDER BY user_pseudo_id, event_timestamp
```

---

## Cost Considerations

- **Free tier:** 1 TB of query data per month
- **Overage:** $6.25 per TB after free tier
- **Your expected usage:** ~10-50 GB/month (very cheap)

**Recommendation:** Set up cost alerts in Google Cloud Console to avoid surprises.

---

## Week 2 Implementation Timeline

- **Day 1:** Enable BigQuery, link GA4 property
- **Day 2:** Wait for GA4 to export data to BigQuery (24 hour window)
- **Day 3-4:** Test queries, validate data
- **Day 5:** Integrate top 1-2 queries into Python briefing script
- **Day 6-7:** Build Looker Studio dashboard with BigQuery data

---

## Next Steps

1. Enable BigQuery in Google Cloud (5 min)
2. Link GA4 property (2 min, then wait 24h for data)
3. Run test queries in BigQuery console (30 min)
4. Integrate into Python briefing script (1-2 hours)
5. Monitor for next 3 days (ensure data accuracy)

Ready when you are! 🍑
