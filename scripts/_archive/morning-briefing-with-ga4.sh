#!/bin/bash

# Morning Briefing with GA4 Analytics
# Uses Python to fetch GA4 data, then sends via gog

EMAIL="rdreilly2010@gmail.com"
SUBJECT="☀️ Morning Briefing - $(date '+%A, %B %d, %Y')"
WORKSPACE="$HOME/.openclaw/workspace"
GA4_CREDS="$WORKSPACE/secrets/ga4-service-account.json"
GA4_PROPERTY_ID="526836321"

# Python script to fetch GA4 data
python3 << 'PYTHON_EOF'
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Try to import GA4 client
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
    from google.oauth2 import service_account
    HAS_GA4 = True
except ImportError:
    HAS_GA4 = False

GA4_CREDS = Path.home() / ".openclaw/workspace/secrets/ga4-service-account.json"
GA4_PROPERTY_ID = "526836321"

if HAS_GA4 and GA4_CREDS.exists():
    try:
        credentials = service_account.Credentials.from_service_account_file(str(GA4_CREDS))
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            date_ranges=[DateRange(start_date="yesterday", end_date="today")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="screenPageViews"),
            ],
        )
        
        response = client.run_report(request)
        
        if response.rows:
            sessions = response.rows[0].metric_values[0].value
            users = response.rows[0].metric_values[1].value
            pageviews = response.rows[0].metric_values[2].value
            print(f"📊 GA4 Analytics (Last 24h):")
            print(f"  • Sessions: {sessions}")
            print(f"  • Users: {users}")
            print(f"  • Page Views: {pageviews}")
        else:
            print("📊 GA4 Analytics: No data available")
    except Exception as e:
        print(f"📊 GA4 Analytics: Error fetching data ({str(e)[:50]})")
else:
    print("📊 GA4 Analytics: Service not configured")

PYTHON_EOF

exit 0
