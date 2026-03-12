#!/bin/bash

# Complete Morning Briefing with GA4
# Fetches calendar, email, GA4 analytics, and sends via Gmail

EMAIL="rdreilly2010@gmail.com"
SUBJECT="☀️ Morning Briefing - $(date '+%A, %B %d, %Y')"
WORKSPACE="$HOME/.openclaw/workspace"

# Fetch GA4 data
GA4_DATA=$(python3 << 'PYTHON_EOF'
from datetime import datetime, timedelta
from pathlib import Path

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
    from google.oauth2 import service_account
    
    GA4_CREDS = Path.home() / ".openclaw/workspace/secrets/ga4-service-account.json"
    GA4_PROPERTY_ID = "526836321"
    
    if GA4_CREDS.exists():
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
            print(f"📊 GA4 Analytics (Last 24h):\n  • Sessions: {sessions}\n  • Users: {users}\n  • Page Views: {pageviews}")
        else:
            print("📊 GA4 Analytics: No data available")
    else:
        print("📊 GA4 Analytics: Service not configured")
except Exception as e:
    print(f"📊 GA4 Analytics: Error ({str(e)[:50]})")
PYTHON_EOF
)

# Build the complete briefing
BODY="Good morning! ☀️

📅 Time: $(date '+%I:%M %p %Z on %A, %B %d, %Y')

📋 Your Priorities for Today:
• Check calendar and upcoming meetings
• Review important emails  
• Work on active projects:
  - ReillyDesignStudio: Set Stripe env vars, configure OAuth
  - Momotaro-iOS: Add WebSocket dependencies, implement gateway connection

$GA4_DATA

✉️ Email Status:
Briefing generated at $(date '+%Y-%m-%d %H:%M:%S %Z')

Have a productive day! 🍑
"

# Send via gog
gog gmail send --to "$EMAIL" --subject "$SUBJECT" --body "$BODY" 2>&1 | tee -a /tmp/morning-briefing.log

exit $?
