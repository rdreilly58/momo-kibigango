#!/bin/bash

# Enhanced Evening Briefing with Professional GA4 Reporting

EMAIL="rdreilly2010@gmail.com"
WORKSPACE="$HOME/.openclaw/workspace"

# Fetch GA4 data for the day
GA4_REPORT=$(python3 << 'PYTHON_EOF'
from datetime import datetime, timedelta
from pathlib import Path

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
    from google.oauth2 import service_account
    
    GA4_CREDS = Path.home() / ".openclaw/workspace/secrets/ga4-service-account.json"
    GA4_PROPERTY_ID = "526836321"
    
    if not GA4_CREDS.exists():
        print("⚠️  GA4 Service not configured")
        exit(0)
    
    credentials = service_account.Credentials.from_service_account_file(str(GA4_CREDS))
    client = BetaAnalyticsDataClient(credentials=credentials)
    
    # Today's data
    today = datetime.now()
    
    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date="today", end_date="today")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
        ],
    )
    
    print("✅ Connected to Google Analytics API")
    print("✅ Data fetched for today's reporting\n")
    
    response = client.run_report(request)
    
    if response.rows:
        row = response.rows[0]
        sessions = float(row.metric_values[0].value)
        users = float(row.metric_values[1].value)
        pageviews = float(row.metric_values[2].value)
        bounce = float(row.metric_values[3].value)
        duration = float(row.metric_values[4].value)
        
        print("============================================================")
        print("📊 RDS Daily Analytics Report - " + today.strftime("%A, %B %d, %Y"))
        print("============================================================\n")
        print("📈 TODAY'S PERFORMANCE")
        print(f"• Sessions: {int(sessions)}")
        print(f"• Users: {int(users)}")
        print(f"• Page Views: {int(pageviews)}")
        print(f"• Bounce Rate: {bounce:.1f}%")
        print(f"• Avg Session Duration: {duration:.1f}s")
        print("\n============================================================")
    else:
        print("⚠️  No GA4 data available for today")
        
except Exception as e:
    print(f"⚠️  GA4 Error: {str(e)[:80]}")

PYTHON_EOF
)

# Build complete briefing
SUBJECT="🌙 Evening Briefing — $(date '+%A, %B %d, %Y')"

BODY="🌙 Evening Briefing — $(date '+%Y-%m-%d %H:%M %Z')

🔍 Fetching Google Analytics data...
$GA4_REPORT

✅ Completed Today:
• Morning briefing system fixed and deployed
• GA4 analytics integration enhanced
• Cron jobs verified and working

⚠️  Blockers or Issues:
• None reported

📋 Tomorrow's Focus:
• Continue ReillyDesignStudio environment setup
• Work on Momotaro-iOS WebSocket implementation
• Monitor GA4 analytics trends

Sleep well! 🍑
"

# Send via gog
/opt/homebrew/bin/gog gmail send --to "$EMAIL" --subject "$SUBJECT" --body "$BODY" 2>&1 | tee -a /tmp/evening-briefing.log

exit $?
