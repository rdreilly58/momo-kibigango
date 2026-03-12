#!/usr/bin/env python3
"""
Professional Morning Briefing Generator
Sends a daily morning briefing with calendar, email, GA4 analytics, and priorities.
Converts to PDF and emails as attachment.
"""

import subprocess
import json
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Configuration
GA4_PROPERTY_ID = "526836321"  # ReillyDesignStudio
GA4_CREDS = os.path.expanduser("~/.openclaw/workspace/secrets/ga4-service-account.json")
EMAIL = "rdreilly2010@gmail.com"
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")

def run_command(cmd, timeout=15):
    """Run shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() if result.returncode == 0 else None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f"Command error: {e}", file=sys.stderr)
        return None

def get_calendar_events():
    """Fetch calendar events for next 48h."""
    today = datetime.now()
    from_date = today.isoformat()
    to_date = (today + timedelta(days=2)).isoformat()
    
    cmd = f'gog calendar events primary --from {from_date} --to {to_date} --json 2>/dev/null'
    output = run_command(cmd)
    
    if not output:
        return []
    
    try:
        events = json.loads(output)
        event_list = []
        for event in events[:5]:
            title = event.get('summary', 'Untitled')
            start = event.get('start', {})
            start_time = start.get('dateTime', start.get('date', '')).split('T')[0]
            event_list.append((title, start_time))
        return event_list
    except:
        return []

def get_unread_count():
    """Get unread email count."""
    cmd = "gog gmail search 'is:unread' --json 2>/dev/null | jq 'length' 2>/dev/null || echo '0'"
    output = run_command(cmd, timeout=10)
    return output if output else "0"

def get_ga4_data():
    """Fetch GA4 analytics with detailed breakdowns (last 7 days)."""
    try:
        import google.analytics.data_v1beta as analytics
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest, OrderBy
        from google.oauth2 import service_account
        
        # Load service account
        credentials = service_account.Credentials.from_service_account_file(GA4_CREDS)
        client = analytics.BetaAnalyticsDataClient(credentials=credentials)
        
        # 1. Get overall metrics (7 days)
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
            "bounce_rate": "0%",
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
            data["avg_duration"] = f"{duration_val:.0f}s"
        
        # 2. Get traffic sources (7 days, ordered by sessions)
        try:
            request = RunReportRequest(
                property=f"properties/{GA4_PROPERTY_ID}",
                date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
                dimensions=[
                    analytics.types.Dimension(name="sessionSource"),
                ],
                metrics=[
                    analytics.types.Metric(name="sessions"),
                    analytics.types.Metric(name="activeUsers"),
                ],
                order_bys=[
                    OrderBy(metric={"metric_name": "sessions"}, desc=True)
                ],
                limit=10
            )
            
            response = client.run_report(request)
            for row in response.rows[:5]:  # Top 5
                source = row.dimension_values[0].value
                sessions = row.metric_values[0].value
                data["traffic_sources"].append((source, sessions))
        except:
            pass
        
        # 3. Get top pages (7 days)
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
            for row in response.rows[:5]:  # Top 5
                page = row.dimension_values[0].value
                views = row.metric_values[0].value
                data["top_pages"].append((page, views))
        except:
            pass
        
        return data
        
    except Exception as e:
        if "403" in str(e) or "permission" in str(e).lower():
            print(f"GA4 Permissions: Service account needs Viewer+ role on property", file=sys.stderr)
        else:
            print(f"GA4 Error: {e}", file=sys.stderr)
    
    return None

def generate_html():
    """Generate professional HTML briefing."""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p %Z")
    
    calendar_events = get_calendar_events()
    unread = get_unread_count()
    ga4_data = get_ga4_data()
    
    # Calendar HTML
    calendar_html = ""
    if calendar_events:
        for title, date in calendar_events:
            calendar_html += f"<tr><td style='padding: 8px; border-bottom: 1px solid #eee;'>{title}</td><td style='padding: 8px; border-bottom: 1px solid #eee; text-align: right; color: #666;'>{date}</td></tr>"
    else:
        calendar_html = "<tr><td colspan='2' style='padding: 8px; color: #999;'>No events scheduled</td></tr>"
    
    # GA4 HTML with traffic sources and top pages
    ga4_html = ""
    if ga4_data:
        # Key metrics
        metrics_html = f"""<table style='width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 15px;'>
    <tr style='background: #f9f9f9;'>
        <td style='padding: 10px; font-weight: bold;'>Sessions</td>
        <td style='padding: 10px; font-weight: bold;'>Users</td>
        <td style='padding: 10px; font-weight: bold;'>Bounce Rate</td>
        <td style='padding: 10px; font-weight: bold;'>Avg Duration</td>
    </tr>
    <tr>
        <td style='padding: 10px;'>{ga4_data['sessions']}</td>
        <td style='padding: 10px;'>{ga4_data['users']}</td>
        <td style='padding: 10px;'>{ga4_data['bounce_rate']}</td>
        <td style='padding: 10px;'>{ga4_data['avg_duration']}</td>
    </tr>
</table>"""
        
        # Traffic sources
        sources_html = ""
        if ga4_data['traffic_sources']:
            sources_html = "<h3 style='margin-top: 10px; margin-bottom: 5px; font-size: 12px; color: #2c5aa0;'>Traffic Sources</h3>"
            for source, sessions in ga4_data['traffic_sources']:
                sources_html += f"<p style='margin: 3px 0; font-size: 11px;'>• {source}: {sessions} sessions</p>"
        
        # Top pages
        pages_html = ""
        if ga4_data['top_pages']:
            pages_html = "<h3 style='margin-top: 10px; margin-bottom: 5px; font-size: 12px; color: #2c5aa0;'>Top Pages (7 days)</h3>"
            for page, views in ga4_data['top_pages']:
                pages_html += f"<p style='margin: 3px 0; font-size: 11px;'>• {page}: {views} views</p>"
        
        ga4_html = metrics_html + sources_html + pages_html
    else:
        ga4_html = "<p style='color: #999; font-size: 12px;'>Analytics data unavailable</p>"
    
    html = f"""<div class="header">
<h1>Morning Briefing</h1>
<p>{date_str} at {time_str}</p>
</div>

<div class="section">
<h2>Email Status</h2>
<p>You have <span class="badge">{unread} unread</span> messages.</p>
</div>

<div class="section">
<h2>Next 48 Hours</h2>
<table border="1" cellpadding="8">
{calendar_html}
</table>
</div>

<div class="section">
<h2>Website Analytics (Today)</h2>
{ga4_html}
<p style="font-size: 11px; color: #999; margin-top: 10px;">ReillyDesignStudio</p>
</div>

<div class="section">
<h2>Priorities for Today</h2>
<div class="priority">
<strong>1. iOS Development</strong><br/>
<span>Continue WebSocket integration for Momotaro</span>
</div>
<div class="priority">
<strong>2. Stripe Setup</strong><br/>
<span>Configure environment variables in AWS Amplify</span>
</div>
<div class="priority">
<strong>3. ReillyDesignStudio</strong><br/>
<span>Monitor deployment and test payment flows</span>
</div>
</div>

<div class="footer">
Generated by Momotaro | Have a productive day!
</div>"""
    
    return html

def html_to_pdf(html_content, filename):
    """Convert HTML to PDF using our converter script."""
    # Save HTML temporarily
    html_path = f"{WORKSPACE}/temp_{filename}.html"
    pdf_path = f"{WORKSPACE}/{filename}.pdf"
    
    try:
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        # Use our Python converter with morning briefing type
        cmd = f"python3 {WORKSPACE}/scripts/html_to_pdf.py '{html_path}' '{pdf_path}' morning 2>/dev/null"
        result = run_command(cmd, timeout=30)
        
        # Clean up temp HTML
        try:
            os.remove(html_path)
        except:
            pass
        
        if os.path.exists(pdf_path):
            return pdf_path
    except Exception as e:
        print(f"PDF conversion error: {e}", file=sys.stderr)
    
    return None

def send_email_with_attachment(pdf_path):
    """Send briefing PDF via email."""
    subject = f"☀️ Morning Briefing - {datetime.now().strftime('%A, %B %d')}"
    body = "Your daily morning briefing is attached."
    
    # Use gog to send with attachment
    cmd = f'gog gmail send --to {EMAIL} --subject "{subject}" --body "{body}" --attach "{pdf_path}" --account {EMAIL} 2>/dev/null'
    output = run_command(cmd, timeout=30)
    
    if output and 'message_id' in output:
        return True
    return False

def main():
    try:
        print("Generating morning briefing...", file=sys.stderr)
        
        # Generate HTML
        html = generate_html()
        
        # Convert to PDF
        print("Converting to PDF...", file=sys.stderr)
        pdf_filename = f"Morning_Briefing_{datetime.now().strftime('%Y%m%d')}"
        pdf_path = html_to_pdf(html, pdf_filename)
        
        if not pdf_path:
            print("❌ PDF conversion failed", file=sys.stderr)
            return 1
        
        # Send email with PDF attachment
        print(f"Sending PDF: {pdf_path}", file=sys.stderr)
        if send_email_with_attachment(pdf_path):
            print(f"✅ Morning briefing sent: {pdf_path}", file=sys.stderr)
            return 0
        else:
            print("❌ Failed to send briefing email", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
