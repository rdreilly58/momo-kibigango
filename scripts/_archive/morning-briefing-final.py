#!/usr/bin/env python3
"""
RDS Analytics Morning Briefing - Text Format with Detailed GA4
Sends daily at 6:00 AM EDT
"""

import sys
import subprocess
from datetime import datetime
import google.analytics.data_v1beta as analytics
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest, OrderBy
from google.oauth2 import service_account

GA4_PROPERTY_ID = "526836321"
GA4_CREDS = "/Users/rreilly/.openclaw/workspace/secrets/ga4-service-account.json"
EMAIL = "rdreilly2010@gmail.com"

def get_ga4_data_detailed():
    """Fetch GA4 analytics with full detail (7 days)."""
    try:
        credentials = service_account.Credentials.from_service_account_file(GA4_CREDS)
        client = analytics.BetaAnalyticsDataClient(credentials=credentials)
        
        # 1. Overall metrics (7 days)
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimensions=[],
            metrics=[
                analytics.types.Metric(name="sessions"),
                analytics.types.Metric(name="activeUsers"),
                analytics.types.Metric(name="bounceRate"),
                analytics.types.Metric(name="averageSessionDuration"),
            ]
        )
        
        response = client.run_report(request)
        
        data = {
            "sessions": "0",
            "users": "0",
            "bounce_rate": "0.0%",
            "avg_duration": "0s",
            "traffic_sources": [],
            "top_pages": [],
        }
        
        if response.rows:
            row = response.rows[0]
            data["sessions"] = row.metric_values[0].value
            data["users"] = row.metric_values[1].value
            bounce_val = float(row.metric_values[2].value) * 100
            data["bounce_rate"] = f"{bounce_val:.1f}%"
            duration_val = float(row.metric_values[3].value)
            data["avg_duration"] = f"{duration_val:.1f}s"
        
        # 2. Traffic sources (7 days)
        try:
            request = RunReportRequest(
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
                dimensions=[
                    analytics.types.Dimension(name="sessionSource"),
                ],
                metrics=[
                    analytics.types.Metric(name="sessions"),
                ],
                order_bys=[
                    OrderBy(metric={"metric_name": "sessions"}, desc=True)
                ],
                limit=10
            )
            
            response = client.run_report(request)
            total_sessions = int(data["sessions"]) if data["sessions"] != "0" else 1
            
            for row in response.rows:
                source = row.dimension_values[0].value
                sessions = row.metric_values[0].value
                pct = (int(sessions) / total_sessions * 100) if total_sessions > 0 else 0
                
                data["traffic_sources"].append({
                    "source": source,
                    "sessions": sessions,
                    "percent": f"{pct:.1f}%"
                })
        except Exception as e:
            pass
        
        # 3. Top pages (7 days)
        try:
            request = RunReportRequest(
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
                dimensions=[
                    analytics.types.Dimension(name="pagePath"),
                ],
                metrics=[
                    analytics.types.Metric(name="screenPageViews"),
                ],
                order_bys=[
                    OrderBy(metric={"metric_name": "screenPageViews"}, desc=True)
                ],
                limit=10
            )
            
            response = client.run_report(request)
            for idx, row in enumerate(response.rows, 1):
                page = row.dimension_values[0].value
                views = row.metric_values[0].value
                data["top_pages"].append({
                    "rank": idx,
                    "page": page,
                    "views": views
                })
        except Exception as e:
            pass
        
        return data
        
    except Exception as e:
        return None

def generate_briefing():
    """Generate morning briefing in March 8 format."""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%H:%M %Z")
    
    ga4_data = get_ga4_data_detailed()
    
    if not ga4_data:
        return None
    
    briefing = f"""📊 RDS Analytics Morning Briefing - {date_str} {time_str}
🌅 Good morning! Here's your website performance from yesterday:

🔍 Fetching Google Analytics data...
✅ Connected to Google Analytics API
✅ Data fetched for last 7 days

============================================================
📊 RDS Analytics Report - {now.strftime("%B %d, %Y")}

🎯 KEY METRICS (last 7 days)
• Active Users: {ga4_data['users']}
• Total Sessions: {ga4_data['sessions']}
• Bounce Rate: {ga4_data['bounce_rate']}
• Avg Session: {ga4_data['avg_duration']}

📈 TRAFFIC SOURCES
"""
    
    # Add traffic sources
    for src in ga4_data['traffic_sources'][:5]:
        briefing += f"• {src['source']}: {src['sessions']} sessions ({src['percent']})\n"
    
    briefing += f"""
🔥 TOP PAGES (last 7 days)
"""
    
    # Add top pages
    for page in ga4_data['top_pages'][:5]:
        briefing += f"{page['rank']}. {page['page']} ({page['views']} views)\n"
    
    briefing += f"""
📈 7-DAY TRENDS
• Weekly visitors trend analysis (coming soon)
• Goal progress tracking (coming soon)

📋 RECOMMENDATIONS
• Monitor top-performing content for insights
• Track traffic source performance over time
• Consider A/B testing high-traffic pages
============================================================
"""
    
    return briefing

def send_briefing(briefing_text):
    """Send briefing via email."""
    now = datetime.now()
    subject = f"📊 RDS Analytics Morning Briefing - {now.strftime('%A, %B %d')}"
    
    # Escape quotes in body
    body = briefing_text.replace('"', '\\"').replace('\n', '\\n')
    
    cmd = f'gog gmail send --to {EMAIL} --subject "{subject}" --body "{briefing_text}" 2>&1'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    return "message_id" in result.stdout or "message_id" in result.stderr

def main():
    try:
        print("Generating morning briefing...", file=sys.stderr)
        
        briefing = generate_briefing()
        if not briefing:
            print("❌ Failed to generate briefing", file=sys.stderr)
            sys.exit(1)
        
        # Print to console for logging
        print(briefing, file=sys.stderr)
        
        print("Sending briefing...", file=sys.stderr)
        if send_briefing(briefing):
            print(f"✅ Morning briefing sent to {EMAIL}", file=sys.stderr)
        else:
            print("⚠️  Briefing send returned unexpected result", file=sys.stderr)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
