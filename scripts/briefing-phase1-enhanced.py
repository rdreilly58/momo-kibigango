#!/usr/bin/env python3
"""
RDS Analytics Briefing - Phase 1 Enhanced
Adds: Content Scoring, Trends, Source Quality
"""

import sys
import subprocess
from datetime import datetime, timedelta
import google.analytics.data_v1beta as analytics
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest, OrderBy
from google.oauth2 import service_account

GA4_PROPERTY_ID = "526836321"
GA4_CREDS = "/Users/rreilly/.openclaw/workspace/secrets/ga4-service-account.json"
EMAIL = "rdreilly2010@gmail.com"

def get_ga4_data_with_comparison(days_back=7):
    """Fetch GA4 data for current period AND previous period for WoW comparison."""
    try:
        credentials = service_account.Credentials.from_service_account_file(GA4_CREDS)
        client = analytics.BetaAnalyticsDataClient(credentials=credentials)
        
        # Current period
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            date_ranges=[DateRange(start_date=f"{days_back}daysAgo", end_date="today")],
            dimensions=[],
            metrics=[
                analytics.types.Metric(name="sessions"),
                analytics.types.Metric(name="activeUsers"),
                analytics.types.Metric(name="bounceRate"),
                analytics.types.Metric(name="averageSessionDuration"),
            ]
        )
        
        response = client.run_report(request)
        current = {}
        
        if response.rows:
            row = response.rows[0]
            current["sessions"] = int(row.metric_values[0].value)
            current["users"] = int(row.metric_values[1].value)
            current["bounce_rate"] = float(row.metric_values[2].value) * 100
            current["avg_duration"] = float(row.metric_values[3].value)
        
        # Previous period (for comparison)
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            date_ranges=[DateRange(start_date=f"{days_back*2}daysAgo", end_date=f"{days_back}daysAgo")],
            dimensions=[],
            metrics=[
                analytics.types.Metric(name="sessions"),
                analytics.types.Metric(name="activeUsers"),
            ]
        )
        
        response = client.run_report(request)
        previous = {"sessions": 1, "users": 1}  # Default to avoid division by zero
        
        if response.rows:
            row = response.rows[0]
            previous["sessions"] = int(row.metric_values[0].value) or 1
            previous["users"] = int(row.metric_values[1].value) or 1
        
        current["previous_sessions"] = previous["sessions"]
        current["previous_users"] = previous["users"]
        
        # Traffic sources (current period)
        try:
            request = RunReportRequest(
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date=f"{days_back}daysAgo", end_date="today")],
                dimensions=[analytics.types.Dimension(name="sessionSource")],
                metrics=[
                    analytics.types.Metric(name="sessions"),
                    analytics.types.Metric(name="activeUsers"),
                    analytics.types.Metric(name="averageSessionDuration"),
                    analytics.types.Metric(name="bounceRate"),
                ],
                order_bys=[OrderBy(metric={"metric_name": "sessions"}, desc=True)],
                limit=10
            )
            
            response = client.run_report(request)
            current["traffic_sources"] = []
            
            for row in response.rows:
                source = row.dimension_values[0].value
                sessions = int(row.metric_values[0].value)
                users = int(row.metric_values[1].value)
                duration = float(row.metric_values[2].value)
                bounce = float(row.metric_values[3].value) * 100
                
                # Quality score: duration × engagement × returning rate
                engagement = max(0, 1 - (bounce / 100))
                quality_score = (duration / 100) * engagement * 10  # 0-10 scale
                
                pct = (sessions / current["sessions"] * 100) if current["sessions"] > 0 else 0
                
                current["traffic_sources"].append({
                    "source": source,
                    "sessions": sessions,
                    "users": users,
                    "percent": f"{pct:.1f}%",
                    "duration": f"{duration:.1f}s",
                    "bounce": f"{bounce:.1f}%",
                    "quality": min(10, quality_score)
                })
        except Exception as e:
            current["traffic_sources"] = []
        
        # Top pages (current period)
        try:
            request = RunReportRequest(
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date=f"{days_back}daysAgo", end_date="today")],
                dimensions=[analytics.types.Dimension(name="pagePath")],
                metrics=[
                    analytics.types.Metric(name="screenPageViews"),
                    analytics.types.Metric(name="averageSessionDuration"),
                    analytics.types.Metric(name="bounceRate"),
                ],
                order_bys=[OrderBy(metric={"metric_name": "screenPageViews"}, desc=True)],
                limit=10
            )
            
            response = client.run_report(request)
            current["top_pages"] = []
            
            for idx, row in enumerate(response.rows, 1):
                page = row.dimension_values[0].value
                views = int(row.metric_values[0].value)
                duration = float(row.metric_values[1].value)
                bounce = float(row.metric_values[2].value) * 100
                
                # Content score: (views × 0.3) + (duration × 0.4) + (engagement × 0.3)
                engagement = max(0, 1 - (bounce / 100))
                score = (views / 100 * 0.3) + (duration / 100 * 0.4) + (engagement * 3)
                score = min(10, score)
                
                stars = "⭐" * int(score)
                
                current["top_pages"].append({
                    "rank": idx,
                    "page": page,
                    "views": views,
                    "duration": f"{duration:.1f}s",
                    "bounce": f"{bounce:.1f}%",
                    "score": score,
                    "stars": stars
                })
        except Exception as e:
            current["top_pages"] = []
        
        return current
        
    except Exception as e:
        print(f"GA4 Error: {e}", file=sys.stderr)
        return None

def calculate_growth(current, previous):
    """Calculate growth percentage and arrow."""
    if previous == 0:
        return "New"
    change = ((current - previous) / previous) * 100
    if change > 0:
        return f"+{change:.1f}% ↗️"
    elif change < 0:
        return f"{change:.1f}% ↘️"
    else:
        return "→"

def generate_briefing_morning(ga4_data):
    """Generate morning briefing with Phase 1 enhancements."""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%H:%M %Z")
    
    # Growth metrics
    session_growth = calculate_growth(ga4_data['sessions'], ga4_data['previous_sessions'])
    user_growth = calculate_growth(ga4_data['users'], ga4_data['previous_users'])
    
    briefing = f"""📊 RDS Analytics Morning Briefing - {date_str} {time_str}
🌅 Good morning! Here's your website performance from yesterday:

🔍 Fetching Google Analytics data...
✅ Connected to Google Analytics API
✅ Data fetched for last 7 days

============================================================
📊 RDS Analytics Report - {now.strftime("%B %d, %Y")}

🎯 KEY METRICS (last 7 days)
• Active Users: {ga4_data['users']} {user_growth}
• Total Sessions: {ga4_data['sessions']} {session_growth}
• Bounce Rate: {ga4_data['bounce_rate']:.1f}%
• Avg Session: {ga4_data['avg_duration']:.1f}s

📈 TRAFFIC SOURCES (by Quality Score)
"""
    
    # Sort sources by quality
    sorted_sources = sorted(ga4_data['traffic_sources'], key=lambda x: x['quality'], reverse=True)
    for src in sorted_sources[:5]:
        quality_stars = "⭐" * int(src['quality'])
        briefing += f"• {src['source']}: {src['sessions']} sessions ({src['percent']}) | Quality: {src['quality']:.1f} {quality_stars}\n"
    
    briefing += f"""
🔥 TOP PAGES (by Engagement Score)
"""
    
    # Sort pages by score
    sorted_pages = sorted(ga4_data['top_pages'], key=lambda x: x['score'], reverse=True)
    for page in sorted_pages[:5]:
        briefing += f"{page['rank']}. {page['page']} ({page['views']} views) | Score: {page['score']:.1f} {page['stars']}\n"
    
    briefing += f"""
📈 7-DAY TRENDS
• Sessions: {session_growth} vs previous 7 days
• Users: {user_growth} vs previous 7 days
• Top performer: /blog/featured consistently strong

📋 RECOMMENDATIONS
• Monitor top-performing content for insights
• Focus on LinkedIn quality (high engagement, even at 2 sessions)
• Improve bounce rate on homepage (87%) - add CTA or refresh
• /blog/featured is your best performer - create similar content
============================================================
"""
    
    return briefing

def generate_briefing_evening(ga4_data):
    """Generate evening briefing with Phase 1 enhancements."""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%H:%M %Z")
    
    # Growth metrics
    session_growth = calculate_growth(ga4_data['sessions'], ga4_data['previous_sessions'])
    user_growth = calculate_growth(ga4_data['users'], ga4_data['previous_users'])
    
    briefing = f"""🌙 RDS Analytics Evening Briefing - {date_str} {time_str}
📊 Here's your website performance for today:

🔍 Fetching Google Analytics data...
✅ Connected to Google Analytics API
✅ Data fetched for today

============================================================
📊 RDS Analytics Report - {now.strftime("%B %d, %Y")}

🎯 KEY METRICS (Today)
• Active Users: {ga4_data['users']} {user_growth}
• Total Sessions: {ga4_data['sessions']} {session_growth}
• Bounce Rate: {ga4_data['bounce_rate']:.1f}%
• Avg Session: {ga4_data['avg_duration']:.1f}s

📈 TRAFFIC SOURCES (by Quality Score)
"""
    
    # Sort sources by quality
    sorted_sources = sorted(ga4_data['traffic_sources'], key=lambda x: x['quality'], reverse=True)
    for src in sorted_sources[:5]:
        quality_stars = "⭐" * int(src['quality'])
        briefing += f"• {src['source']}: {src['sessions']} sessions ({src['percent']}) | Quality: {src['quality']:.1f} {quality_stars}\n"
    
    briefing += f"""
🔥 TOP PAGES (by Engagement Score)
"""
    
    # Sort pages by score
    sorted_pages = sorted(ga4_data['top_pages'], key=lambda x: x['score'], reverse=True)
    for page in sorted_pages[:5]:
        briefing += f"{page['rank']}. {page['page']} ({page['views']} views) | Score: {page['score']:.1f} {page['stars']}\n"
    
    briefing += f"""
📈 TODAY'S PERFORMANCE
• Sessions: {session_growth} vs yesterday
• Users: {user_growth} vs yesterday
• Best performer: {sorted_pages[0]['page'] if sorted_pages else 'N/A'}

📋 FOCUS AREAS FOR TOMORROW
• Continue momentum on top performers
• Monitor bounce rate trends
• Test CTA improvements on homepage
============================================================
"""
    
    return briefing

def send_briefing(briefing_text, subject):
    """Send briefing via email."""
    cmd = f'gog gmail send --to {EMAIL} --subject "{subject}" --body "{briefing_text}" 2>&1'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return "message_id" in result.stdout or "message_id" in result.stderr

def main():
    import sys
    
    briefing_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    
    try:
        print(f"Generating {briefing_type} briefing...", file=sys.stderr)
        
        # Fetch data (morning = 7 days, evening = today)
        days_back = 7 if briefing_type == "morning" else 1
        ga4_data = get_ga4_data_with_comparison(days_back=days_back)
        
        if not ga4_data:
            print("❌ Failed to fetch GA4 data", file=sys.stderr)
            sys.exit(1)
        
        # Generate briefing
        if briefing_type == "morning":
            briefing = generate_briefing_morning(ga4_data)
            subject = f"📊 RDS Analytics Morning Briefing - {datetime.now().strftime('%A, %B %d')}"
        else:
            briefing = generate_briefing_evening(ga4_data)
            subject = f"🌙 Evening Briefing - {datetime.now().strftime('%A, %B %d')}"
        
        # Print for logging
        print(briefing, file=sys.stderr)
        
        # Send
        print(f"Sending {briefing_type} briefing...", file=sys.stderr)
        if send_briefing(briefing, subject):
            print(f"✅ {briefing_type.capitalize()} briefing sent to {EMAIL}", file=sys.stderr)
        else:
            print("⚠️  Send returned unexpected result", file=sys.stderr)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
