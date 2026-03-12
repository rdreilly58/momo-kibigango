#!/usr/bin/env python3
"""
BigQuery Analytics Queries for ReillyDesignStudio
Provides custom insights: cohorts, funnels, engagement scoring
"""

from google.cloud import bigquery
from datetime import datetime, timedelta
import pandas as pd

PROJECT_ID = "rds-analytics-489420"
DATASET_ID = "analytics_526836321"

def get_bq_client():
    """Initialize BigQuery client (uses Application Default Credentials)"""
    try:
        return bigquery.Client(project=PROJECT_ID)
    except Exception as e:
        print(f"BigQuery client error: {e}")
        return None

def get_top_pages_by_engagement(days_back=7):
    """Query top pages by engagement score (not just views)"""
    client = get_bq_client()
    if not client:
        return pd.DataFrame()
    
    try:
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
          AND event_params[SAFE.OFFSET(0)].value.string_value IS NOT NULL
        GROUP BY page_path
        ORDER BY engagement_score DESC
        LIMIT 10
        """
        
        results = client.query(query).result()
        return results.to_dataframe()
    except Exception as e:
        print(f"Error fetching top pages: {e}")
        return pd.DataFrame()

def get_visitor_cohorts(days_back=7):
    """Analyze new vs returning visitors"""
    client = get_bq_client()
    if not client:
        return pd.DataFrame()
    
    try:
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
    except Exception as e:
        print(f"Error fetching visitor cohorts: {e}")
        return pd.DataFrame()

def get_conversion_funnel(days_back=7):
    """Track portfolio interest funnel"""
    client = get_bq_client()
    if not client:
        return pd.DataFrame()
    
    try:
        query = f"""
        WITH homepage_visitors AS (
          SELECT COUNT(DISTINCT user_pseudo_id) as count
          FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
          WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
            AND event_name = 'page_view'
            AND (
              event_params[SAFE.OFFSET(0)].value.string_value = '/'
              OR event_params[SAFE.OFFSET(0)].value.string_value LIKE '/index%'
            )
        ),
        
        portfolio_visitors AS (
          SELECT COUNT(DISTINCT user_pseudo_id) as count
          FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
          WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
            AND event_name = 'page_view'
            AND event_params[SAFE.OFFSET(0)].value.string_value LIKE '%portfolio%'
        ),
        
        contact_visitors AS (
          SELECT COUNT(DISTINCT user_pseudo_id) as count
          FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
          WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
            AND event_name = 'page_view'
            AND event_params[SAFE.OFFSET(0)].value.string_value LIKE '%contact%'
        )
        
        SELECT
          'Step 1: Homepage' as step,
          (SELECT count FROM homepage_visitors) as visitors,
          100.0 as conversion_pct
        UNION ALL
        SELECT
          'Step 2: Portfolio',
          (SELECT count FROM portfolio_visitors),
          ROUND(100.0 * (SELECT count FROM portfolio_visitors) / (SELECT count FROM homepage_visitors), 1)
        UNION ALL
        SELECT
          'Step 3: Contact',
          (SELECT count FROM contact_visitors),
          ROUND(100.0 * (SELECT count FROM contact_visitors) / (SELECT count FROM homepage_visitors), 1)
        """
        
        results = client.query(query).result()
        return results.to_dataframe()
    except Exception as e:
        print(f"Error fetching conversion funnel: {e}")
        return pd.DataFrame()

def get_traffic_source_quality(days_back=7):
    """Rank traffic sources by quality metrics"""
    client = get_bq_client()
    if not client:
        return pd.DataFrame()
    
    try:
        query = f"""
        SELECT
          traffic_source.source as source,
          COUNT(*) as sessions,
          COUNT(DISTINCT user_pseudo_id) as unique_users,
          ROUND(AVG(engagement_time_msec) / 1000, 1) as avg_engagement_seconds,
          ROUND(100 * SUM(CASE WHEN engagement_time_msec < 1000 THEN 1 ELSE 0 END) / COUNT(*), 1) as bounce_rate_pct,
          
          -- Quality score
          ROUND((AVG(engagement_time_msec / 1000) / 100) * (1 - (SUM(CASE WHEN engagement_time_msec < 1000 THEN 1 ELSE 0 END) / COUNT(*))) * 10, 1) as quality_score
          
        FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
        WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY))
        GROUP BY source
        ORDER BY quality_score DESC
        LIMIT 10
        """
        
        results = client.query(query).result()
        return results.to_dataframe()
    except Exception as e:
        print(f"Error fetching traffic source quality: {e}")
        return pd.DataFrame()

def test_bigquery_connection():
    """Test if BigQuery is connected and has data"""
    client = get_bq_client()
    if not client:
        return False
    
    try:
        query = f"""
        SELECT COUNT(*) as event_count
        FROM `{PROJECT_ID}.{DATASET_ID}.events_*`
        WHERE _TABLE_SUFFIX = FORMAT_DATE('%Y%m%d', CURRENT_DATE())
        LIMIT 1
        """
        
        results = client.query(query).result()
        for row in results:
            return row.event_count > 0
        return False
    except Exception as e:
        print(f"BigQuery connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("BigQuery Analysis - ReillyDesignStudio\n")
    print("=" * 70)
    
    # Test connection
    if not test_bigquery_connection():
        print("⚠️  BigQuery not yet receiving GA4 data")
        print("Wait 24 hours after linking GA4 property, then try again.")
        exit(1)
    
    print("\n📊 Top Pages by Engagement (7-day):")
    print(get_top_pages_by_engagement(7))
    
    print("\n👥 Visitor Cohorts (7-day):")
    print(get_visitor_cohorts(7))
    
    print("\n🔄 Conversion Funnel (7-day):")
    print(get_conversion_funnel(7))
    
    print("\n🎯 Traffic Source Quality (7-day):")
    print(get_traffic_source_quality(7))
