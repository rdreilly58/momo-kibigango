# Week 2 Execution Plan - BigQuery + Looker Studio

## Day 1-2: BigQuery Setup (Manual - Your GCP Console)

### Step 1: Enable BigQuery API
1. Go to: https://console.cloud.google.com/
2. Select project: **rds-analytics-489420**
3. Search: **BigQuery API**
4. Click: **Enable**
5. Wait 1-2 minutes for activation

### Step 2: Link GA4 to BigQuery
1. Go to: https://analytics.google.com/
2. Select property: **ReillyDesignStudio** (526836321)
3. Admin → **Data streams** → Your web stream
4. Scroll down to **Google Cloud linking**
5. Click: **Link BigQuery property**
6. Select: **rds-analytics-489420**
7. Click: **Link**
8. **Wait 24 hours for first data export**

**Status:** Linked but empty until tomorrow

---

## Day 3: Test BigQuery Data

### Step 1: Query Raw Events
Go to: https://console.cloud.google.com/bigquery

```sql
SELECT
  COUNT(*) as total_events,
  COUNT(DISTINCT user_pseudo_id) as unique_users,
  MIN(TIMESTAMP_MICROS(event_timestamp)) as earliest_event,
  MAX(TIMESTAMP_MICROS(event_timestamp)) as latest_event
FROM `rds-analytics-489420.analytics_526836321.events_*`
WHERE _TABLE_SUFFIX = '20260310'
```

**Expected result:** See today's events

### Step 2: Validate Data Format
```sql
SELECT
  event_name,
  COUNT(*) as count
FROM `rds-analytics-489420.analytics_526836321.events_*`
WHERE _TABLE_SUFFIX = '20260310'
GROUP BY event_name
LIMIT 10
```

**Expected:** page_view, session_start, etc.

---

## Day 4-5: Python Integration

### Install BigQuery Client
```bash
pip install google-cloud-bigquery
```

### Create: `bigquery_queries.py`
```python
from google.cloud import bigquery
from datetime import datetime, timedelta

PROJECT_ID = "rds-analytics-489420"
DATASET_ID = "analytics_526836321"

def get_bq_client():
    """Initialize BigQuery client (uses Application Default Credentials)"""
    return bigquery.Client(project=PROJECT_ID)

def get_top_pages_by_engagement(days_back=7):
    """Query top pages by engagement score (not just views)"""
    client = get_bq_client()
    
    query = f"""
    SELECT
      event_params[SAFE.OFFSET(0)].value.string_value as page_path,
      COUNT(*) as page_views,
      ROUND(AVG(engagement_time_msec) / 1000, 1) as avg_duration_seconds,
      ROUND(100 * SUM(CASE WHEN engagement_time_msec < 1000 THEN 1 ELSE 0 END) / COUNT(*), 1) as bounce_rate_pct,
      
      -- Engagement score: (views × 0.3) + (duration × 0.4) + (engagement × 0.3)
      ROUND(
        (COUNT(*) / 10 * 0.3) + 
        (AVG(engagement_time_msec) / 1000 / 100 * 0.4) + 
        ((1 - (SUM(CASE WHEN engagement_time_msec < 1000 THEN 1 ELSE 0 END) / COUNT(*))) * 3),
        1
      ) as engagement_score
      
    FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
    WHERE 
      _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
      AND event_name = 'page_view'
    GROUP BY page_path
    ORDER BY engagement_score DESC
    LIMIT 10
    """
    
    results = client.query(query).result()
    return results.to_dataframe()

def get_visitor_cohorts(days_back=7):
    """Analyze new vs returning visitors"""
    client = get_bq_client()
    
    query = f"""
    WITH user_first_visit AS (
      SELECT
        user_pseudo_id,
        MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) as first_visit_date
      FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
      WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
      GROUP BY user_pseudo_id
    )
    
    SELECT
      CASE
        WHEN DATE(TIMESTAMP_MICROS(e.event_timestamp)) = uv.first_visit_date THEN 'New Visitor'
        ELSE 'Returning Visitor'
      END as visitor_type,
      COUNT(DISTINCT e.user_pseudo_id) as unique_visitors,
      COUNT(*) as total_events,
      ROUND(AVG(e.engagement_time_msec) / 1000, 1) as avg_engagement_seconds
    FROM `{PROJECT_ID}.{DATASET_ID}.events_*` e
    JOIN user_first_visit uv ON e.user_pseudo_id = uv.user_pseudo_id
    WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
    GROUP BY visitor_type
    """
    
    results = client.query(query).result()
    return results.to_dataframe()

def get_conversion_funnel(days_back=7):
    """Track portfolio interest funnel"""
    client = get_bq_client()
    
    query = f"""
    WITH homepage_visits AS (
      SELECT COUNT(DISTINCT user_pseudo_id) as count
      FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
      WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
        AND event_name = 'page_view'
        AND event_params[SAFE.OFFSET(0)].value.string_value = '/'
    ),
    
    portfolio_visits AS (
      SELECT COUNT(DISTINCT user_pseudo_id) as count
      FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
      WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
        AND event_name = 'page_view'
        AND event_params[SAFE.OFFSET(0)].value.string_value LIKE '%/portfolio%'
    ),
    
    contact_visits AS (
      SELECT COUNT(DISTINCT user_pseudo_id) as count
      FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
      WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
        AND event_name = 'page_view'
        AND event_params[SAFE.OFFSET(0)].value.string_value = '/contact'
    )
    
    SELECT
      'Homepage' as step,
      (SELECT count FROM homepage_visits) as visitors,
      ROUND(100 * (SELECT count FROM homepage_visits) / (SELECT count FROM homepage_visits), 1) as pct
    UNION ALL
    SELECT
      'Portfolio',
      (SELECT count FROM portfolio_visits),
      ROUND(100 * (SELECT count FROM portfolio_visits) / (SELECT count FROM homepage_visits), 1)
    UNION ALL
    SELECT
      'Contact',
      (SELECT count FROM contact_visits),
      ROUND(100 * (SELECT count FROM contact_visits) / (SELECT count FROM homepage_visits), 1)
    """
    
    results = client.query(query).result()
    return results.to_dataframe()

if __name__ == "__main__":
    print("BigQuery Analysis - ReillyDesignStudio\n")
    
    print("📊 Top Pages by Engagement:")
    print(get_top_pages_by_engagement(7))
    
    print("\n👥 Visitor Cohorts:")
    print(get_visitor_cohorts(7))
    
    print("\n🔄 Conversion Funnel:")
    print(get_conversion_funnel(7))
```

### Update: `briefing-phase1-enhanced.py`

Add at top:
```python
try:
    from bigquery_queries import get_top_pages_by_engagement, get_visitor_cohorts
    HAS_BIGQUERY = True
except ImportError:
    HAS_BIGQUERY = False
```

Add to morning briefing generation:
```python
# Add BigQuery insights if available
if HAS_BIGQUERY:
    try:
        bq_pages = get_top_pages_by_engagement(7)
        briefing += f"""
🧠 DEEP INSIGHTS (from BigQuery)
Top Engagement Pages:
"""
        for _, page in bq_pages.iterrows():
            briefing += f"• {page['page_path']}: Score {page['engagement_score']:.1f} ⭐\n"
    except Exception as e:
        pass  # Silently fail if BQ not ready
```

---

## Day 6: Test Updated Briefing

```bash
# Test with BigQuery data
python3 /Users/rreilly/.openclaw/workspace/scripts/briefing-phase1-enhanced.py morning

# Expected output includes both GA4 + BigQuery insights
```

---

## Day 7: Looker Studio Dashboard

### Manual Setup (30 min)

1. Go to: https://looker.google.com/
2. Click: **Create** → **Report**
3. Add data source: **Google Analytics 4** → **ReillyDesignStudio**
4. Build dashboard with cards:
   - Sessions (with WoW comparison)
   - Users
   - Bounce Rate
   - Avg Session Duration
5. Add charts:
   - Line: Sessions trend (30 days)
   - Line: Users trend (30 days)
   - Pie: Traffic by source
   - Table: Top pages with scores
6. Click **Share** → Get link

---

## Files to Create/Update

- ✅ `bigquery_queries.py` — BigQuery helper functions
- ✅ Update `briefing-phase1-enhanced.py` — Add BQ integration
- ✅ Looker Studio dashboard (manual build)

---

## Timeline

- **Day 1-2:** Enable BigQuery + link GA4 (5 min setup, 24h wait)
- **Day 3:** Validate BigQuery data (20 min)
- **Day 4-5:** Create `bigquery_queries.py` + integrate (2 hours)
- **Day 6:** Test updated briefing (30 min)
- **Day 7:** Build Looker Studio dashboard (45 min)

**Total implementation:** ~4 hours active work + 24h waiting

---

## Success Criteria

✅ BigQuery receives GA4 events  
✅ Custom SQL queries return data  
✅ Python integration working (briefing includes BQ insights)  
✅ Looker Studio dashboard live with real-time metrics  
✅ Morning/evening briefings include deep insights  

Ready to start? 🍑
