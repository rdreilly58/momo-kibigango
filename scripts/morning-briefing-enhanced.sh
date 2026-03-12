#!/bin/bash

# Enhanced Morning Briefing with Professional GA4 Reporting
# Matches the format from March 8 briefing

EMAIL="rdreilly2010@gmail.com"
WORKSPACE="$HOME/.openclaw/workspace"

# Fetch GA4 data with detailed reporting
GA4_REPORT=$(python3 << 'PYTHON_EOF'
from datetime import datetime, timedelta
from pathlib import Path
import json

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest, OrderBy
    from google.oauth2 import service_account
    
    GA4_CREDS = Path.home() / ".openclaw/workspace/secrets/ga4-service-account.json"
    GA4_PROPERTY_ID = "526836321"
    
    if not GA4_CREDS.exists():
        print("⚠️  GA4 Service not configured")
        exit(0)
    
    credentials = service_account.Credentials.from_service_account_file(str(GA4_CREDS))
    client = BetaAnalyticsDataClient(credentials=credentials)
    
    # Current period (last 24h)
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    current_request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date="yesterday", end_date="today")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
        ],
        dimensions=[Dimension(name="date")],
    )
    
    # Previous period for comparison (day before yesterday)
    previous_request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date="2daysAgo", end_date="yesterday")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="bounceRate"),
        ],
    )
    
    print("✅ Connected to Google Analytics API")
    print("✅ Data fetched for reporting\n")
    
    current_response = client.run_report(current_request)
    previous_response = client.run_report(previous_request)
    
    if current_response.rows:
        curr_row = current_response.rows[0]
        curr_sessions = float(curr_row.metric_values[0].value)
        curr_users = float(curr_row.metric_values[1].value)
        curr_pageviews = float(curr_row.metric_values[2].value)
        curr_bounce = float(curr_row.metric_values[3].value)
        curr_duration = float(curr_row.metric_values[4].value)
        
        if previous_response.rows:
            prev_row = previous_response.rows[0]
            prev_sessions = float(prev_row.metric_values[0].value)
            prev_users = float(prev_row.metric_values[1].value)
            prev_pageviews = float(prev_row.metric_values[2].value)
            prev_bounce = float(prev_row.metric_values[3].value)
            
            # Calculate % changes
            sessions_pct = ((curr_sessions - prev_sessions) / prev_sessions * 100) if prev_sessions > 0 else 0
            users_pct = ((curr_users - prev_users) / prev_users * 100) if prev_users > 0 else 0
            pageviews_pct = ((curr_pageviews - prev_pageviews) / prev_pageviews * 100) if prev_pageviews > 0 else 0
            bounce_pct = ((curr_bounce - prev_bounce) / prev_bounce * 100) if prev_bounce > 0 else 0
            
            sessions_arrow = "📈" if sessions_pct > 0 else "📉" if sessions_pct < 0 else "➡️"
            users_arrow = "📈" if users_pct > 0 else "📉" if users_pct < 0 else "➡️"
            pageviews_arrow = "📈" if pageviews_pct > 0 else "📉" if pageviews_pct < 0 else "➡️"
            bounce_arrow = "📉" if bounce_pct < 0 else "📈" if bounce_pct > 0 else "➡️"
            
            print("============================================================")
            print("📊 RDS Analytics Report - " + today.strftime("%B %d, %Y"))
            print("============================================================\n")
            print("🎯 KEY METRICS (last 24h)")
            print(f"• Sessions: {int(curr_sessions)} {sessions_arrow} ({sessions_pct:+.1f}% vs yesterday)")
            print(f"• Users: {int(curr_users)} {users_arrow} ({users_pct:+.1f}% vs yesterday)")
            print(f"• Page Views: {int(curr_pageviews)} {pageviews_arrow} ({pageviews_pct:+.1f}% vs yesterday)")
            print(f"• Bounce Rate: {curr_bounce:.1f}% {bounce_arrow} ({bounce_pct:+.1f}% vs yesterday)")
            print(f"• Avg Session Duration: {curr_duration:.1f}s")
            print("\n============================================================")
        else:
            print("📊 RDS Analytics Report - " + today.strftime("%B %d, %Y"))
            print("============================================================\n")
            print("🎯 KEY METRICS (last 24h)")
            print(f"• Sessions: {int(curr_sessions)}")
            print(f"• Users: {int(curr_users)}")
            print(f"• Page Views: {int(curr_pageviews)}")
            print(f"• Bounce Rate: {curr_bounce:.1f}%")
            print(f"• Avg Session Duration: {curr_duration:.1f}s")
            print("\n============================================================")
    else:
        print("⚠️  No GA4 data available")
        
except Exception as e:
    print(f"⚠️  GA4 Error: {str(e)[:80]}")

PYTHON_EOF
)

# Build complete briefing
SUBJECT="📊 RDS Analytics Morning Briefing - $(date '+%A, %B %d, %Y')"

BODY="📊 RDS Analytics Morning Briefing - $(date '+%A, %Y-%m-%d %H:%M %Z')
🌅 Good morning! Here's your website performance from yesterday:

🔍 Fetching Google Analytics data...
$GA4_REPORT

📋 Your Priorities for Today:
• Check calendar and upcoming meetings
• Review important emails  
• Work on active projects:
  - ReillyDesignStudio: Set Stripe env vars, configure OAuth
  - Momotaro-iOS: Add WebSocket dependencies, implement gateway connection

Have a productive day! 🍑
"

# Send via gog
/opt/homebrew/bin/gog gmail send --to "$EMAIL" --subject "$SUBJECT" --body "$BODY" 2>&1 | tee -a /tmp/morning-briefing.log

exit $?
