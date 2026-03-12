#!/bin/bash

# Enhanced Morning Briefing with Full GA4 Reporting
# Includes: Key Metrics, Traffic Sources, Top Pages, 7-Day Trends

EMAIL="rdreilly2010@gmail.com"
WORKSPACE="$HOME/.openclaw/workspace"

# Fetch comprehensive GA4 data
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
    
    today = datetime.now()
    
    # ===== 1. KEY METRICS (7 days) =====
    print("✅ Connected to Google Analytics API")
    print("✅ Fetching comprehensive GA4 data\n")
    
    current_7d_request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date="6daysAgo", end_date="today")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
        ],
    )
    
    previous_7d_request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date="13daysAgo", end_date="7daysAgo")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="bounceRate"),
        ],
    )
    
    current_7d = client.run_report(current_7d_request)
    previous_7d = client.run_report(previous_7d_request)
    
    print("============================================================")
    print("📊 RDS Analytics Report - " + today.strftime("%B %d, %Y"))
    print("============================================================\n")
    
    if current_7d.rows:
        curr_row = current_7d.rows[0]
        curr_active = float(curr_row.metric_values[0].value)
        curr_total = float(curr_row.metric_values[1].value)
        curr_pageviews = float(curr_row.metric_values[2].value)
        curr_bounce = float(curr_row.metric_values[3].value)
        curr_duration = float(curr_row.metric_values[4].value)
        
        # Calculate comparisons
        if previous_7d.rows:
            prev_row = previous_7d.rows[0]
            prev_active = float(prev_row.metric_values[0].value)
            prev_total = float(prev_row.metric_values[1].value)
            prev_pageviews = float(prev_row.metric_values[2].value)
            prev_bounce = float(prev_row.metric_values[3].value)
            
            active_pct = ((curr_active - prev_active) / prev_active * 100) if prev_active > 0 else 0
            total_pct = ((curr_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
            pageviews_pct = ((curr_pageviews - prev_pageviews) / prev_pageviews * 100) if prev_pageviews > 0 else 0
            bounce_pct = ((curr_bounce - prev_bounce) / prev_bounce * 100) if prev_bounce > 0 else 0
            
            active_arrow = "📈" if active_pct > 0 else "📉" if active_pct < 0 else "➡️"
            total_arrow = "📈" if total_pct > 0 else "📉" if total_pct < 0 else "➡️"
            pageviews_arrow = "📈" if pageviews_pct > 0 else "📉" if pageviews_pct < 0 else "➡️"
            bounce_arrow = "📉" if bounce_pct < 0 else "📈" if bounce_pct > 0 else "➡️"
            
            print("🎯 KEY METRICS (last 7 days)")
            print(f"• Active Users: {int(curr_active)} {active_arrow} ({active_pct:+.1f}% vs prev week)")
            print(f"• Total Users: {int(curr_total)} {total_arrow} ({total_pct:+.1f}% vs prev week)")
            print(f"• Page Views: {int(curr_pageviews)} {pageviews_arrow} ({pageviews_pct:+.1f}% vs prev week)")
            print(f"• Bounce Rate: {curr_bounce:.1f}% {bounce_arrow} ({bounce_pct:+.1f}% vs prev week)")
            print(f"• Avg Session: {curr_duration:.1f} seconds")
        else:
            print("🎯 KEY METRICS (last 7 days)")
            print(f"• Active Users: {int(curr_active)}")
            print(f"• Total Users: {int(curr_total)}")
            print(f"• Page Views: {int(curr_pageviews)}")
            print(f"• Bounce Rate: {curr_bounce:.1f}%")
            print(f"• Avg Session: {curr_duration:.1f} seconds")
    
    # ===== 2. TRAFFIC SOURCES (7 days) =====
    print("\n📈 TRAFFIC SOURCES")
    
    traffic_request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date="6daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
        ],
        metrics=[Metric(name="totalUsers")],
    )
    
    try:
        traffic_response = client.run_report(traffic_request)
        
        if traffic_response.rows:
            total_traffic = sum(float(row.metric_values[0].value) for row in traffic_response.rows)
            
            for i, row in enumerate(traffic_response.rows[:5], 1):
                try:
                    source = row.dimension_values[0].value if len(row.dimension_values) > 0 else "(not set)"
                    medium = row.dimension_values[1].value if len(row.dimension_values) > 1 else "(not set)"
                    users = float(row.metric_values[0].value)
                    pct = (users / total_traffic * 100) if total_traffic > 0 else 0
                    
                    source_display = source if source and source != "(not set)" else "(data not available)"
                    medium_display = f": {medium}" if medium and medium != "(not set)" else ""
                    
                    print(f"• {source_display}{medium_display}: {int(users)} visitors ({pct:.1f}%)")
                except:
                    pass
        else:
            print("• No traffic source data available")
    except Exception as e:
        print(f"• Error fetching traffic sources: {str(e)[:50]}")
    
    # ===== 3. TOP PAGES (7 days) =====
    print("\n🔥 TOP PAGES (last 7 days)")
    
    pages_request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date="6daysAgo", end_date="today")],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")],
    )
    
    try:
        pages_response = client.run_report(pages_request)
        
        if pages_response.rows:
            # Sort by views
            sorted_rows = sorted(pages_response.rows, key=lambda x: float(x.metric_values[0].value), reverse=True)
            
            for i, row in enumerate(sorted_rows[:5], 1):
                try:
                    page = row.dimension_values[0].value if len(row.dimension_values) > 0 else "/"
                    views = int(float(row.metric_values[0].value))
                    page_label = f"{i}. {page} (homepage)" if page == "/" else f"{i}. {page}"
                    print(f"{page_label} ({views} views)")
                except:
                    pass
        else:
            print("• No page data available")
    except Exception as e:
        print(f"• Error fetching top pages: {str(e)[:50]}")
    
    # ===== 4. 7-DAY TRENDS =====
    print("\n📈 7-DAY TRENDS")
    print("• Weekly visitors trend analysis (available in dashboard)")
    print("• Goal progress tracking (available in dashboard)")
    
    print("\n============================================================")
    
except Exception as e:
    print(f"⚠️  GA4 Error: {str(e)[:100]}")

PYTHON_EOF
)

# Fetch email statistics
EMAIL_STATS=$(/bin/bash /Users/rreilly/.openclaw/workspace/scripts/email-stats.sh)

# Fetch calendar events (today in EDT)
CALENDAR_EVENTS=$(/opt/homebrew/bin/gog calendar events primary --json 2>/dev/null | jq -r '.events[] | select(.start.dateTime | startswith("'$(date +%Y-%m-%d)'")) | "\(.start.dateTime[11:16]) - \(.summary)"' 2>/dev/null | head -10 || echo "")

# Fetch tasks statistics
TASKS_STATS=$(/bin/bash /Users/rreilly/.openclaw/workspace/scripts/tasks-stats.sh)

# Fetch top pending tasks
TOP_TASKS=$(/bin/bash /Users/rreilly/.openclaw/workspace/scripts/tasks-stats.sh top)

# Build complete briefing
SUBJECT="📊 RDS Analytics Morning Briefing - $(date '+%A, %B %d, %Y')"

BODY="📊 RDS Analytics Morning Briefing - $(date '+%A, %Y-%m-%d %H:%M %Z')
🌅 Good morning! Here's your website performance from the last 7 days:

🔍 Fetching Google Analytics data...
$GA4_REPORT

✉️ EMAIL STATUS
$EMAIL_STATS

📅 TODAY'S CALENDAR
$(if [ -n "$CALENDAR_EVENTS" ]; then echo "$CALENDAR_EVENTS"; else echo "No scheduled events"; fi)

✅ GOOGLE TASKS
Tasks: $TASKS_STATS

Top Pending:
$(if [ -n "$TOP_TASKS" ]; then echo "$TOP_TASKS" | sed 's/^/  • /'; else echo "  No pending tasks"; fi)

📋 Your Priorities for Today:
• Check calendar and upcoming meetings
• Review important emails  
• Work on active projects:
  - ReillyDesignStudio: Set Stripe env vars, configure OAuth
  - Momotaro-iOS: Add WebSocket dependencies, implement gateway connection

Have a productive day! 🍑
"

# Send via gog with full path and account
/opt/homebrew/bin/gog gmail send --account "$EMAIL" --to "$EMAIL" --subject "$SUBJECT" --body "$BODY" 2>&1 | tee -a /tmp/morning-briefing.log

exit $?
