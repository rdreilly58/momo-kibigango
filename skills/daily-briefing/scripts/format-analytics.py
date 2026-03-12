#!/usr/bin/env python3
"""
Format GA4 analytics data into HTML sections for briefings
"""

import json
import sys

def format_key_metrics(data):
    """Format key metrics with comparisons"""
    current = data.get("current_metrics", {})
    changes = data.get("changes", {})
    
    users = int(current.get("activeUsers", 0))
    sessions = int(current.get("sessions", 0))
    bounce = float(current.get("bounceRate", 0))
    avg_duration = float(current.get("averageSessionDuration", 0)) if isinstance(current.get("averageSessionDuration"), (int, float)) else float(str(current.get("averageSessionDuration", "0")))
    
    user_change = changes.get("user_change_percent", 0)
    session_change = changes.get("session_change_percent", 0)
    
    # Format change indicators
    user_arrow = "↗️" if user_change > 0 else "↘️" if user_change < 0 else "→"
    session_arrow = "↗️" if session_change > 0 else "↘️" if session_change < 0 else "→"
    
    html = f"""
    <div class="section">
        <h2>🎯 KEY METRICS (last 7 days)</h2>
        <div class="metric-item">
            <span class="metric-label">• Active Users:</span>
            <span class="metric-value">{users}</span>
            <span class="metric-change">{user_change:+.1f}% {user_arrow}</span>
        </div>
        <div class="metric-item">
            <span class="metric-label">• Total Sessions:</span>
            <span class="metric-value">{sessions}</span>
            <span class="metric-change">{session_change:+.1f}% {session_arrow}</span>
        </div>
        <div class="metric-item">
            <span class="metric-label">• Bounce Rate:</span>
            <span class="metric-value">{bounce:.1f}%</span>
        </div>
        <div class="metric-item">
            <span class="metric-label">• Avg Session:</span>
            <span class="metric-value">{avg_duration:.1f}s</span>
        </div>
    </div>
    """
    return html

def quality_score(bounce_rate, views):
    """Calculate quality score based on bounce rate and engagement"""
    # Higher engagement (lower bounce) = higher quality
    # Adjust for view count
    base_score = max(10 - (bounce_rate * 10), 0)
    views_factor = min(views / 10, 1)  # Cap at 1.0
    score = (base_score * 0.7 + views_factor * 3) / 1.3
    return min(score, 10)

def engagement_score(views, duration, users):
    """Calculate engagement score for pages"""
    if views == 0:
        return 0
    
    # Duration-based score (pages with longer engagement = better)
    duration_score = min(duration / 30, 2)  # Cap at 2 points
    # Views per user (engagement multiplier)
    engagement = views / max(users, 1)
    engagement_score_val = min(engagement, 2)  # Cap at 2 points
    # Base score from views
    views_score = min(views / 10, 2)  # Cap at 2 points
    
    return min(duration_score + engagement_score_val, 5)

def stars(score):
    """Convert score to stars"""
    stars_count = int(score)
    return "⭐" * stars_count

def format_traffic_sources(data):
    """Format traffic sources with quality scores"""
    sources = data.get("traffic_sources", [])
    
    if not sources:
        return ""
    
    # Calculate totals
    total_sessions = sum(s.get("sessions", 0) for s in sources)
    
    html = '<div class="section">\n<h2>📈 TRAFFIC SOURCES (by Quality Score)</h2>\n'
    
    for source in sources[:5]:  # Top 5 sources
        src = source.get("source", "unknown")
        sessions = source.get("sessions", 0)
        bounce = source.get("bounceRate", 0)
        
        pct = (sessions / total_sessions * 100) if total_sessions > 0 else 0
        score = quality_score(bounce, sessions)
        
        html += f'<div class="source-item">\n'
        html += f'• <strong>{src}</strong>: {sessions} sessions ({pct:.1f}%) | Quality: {score:.1f} {stars(score)}\n'
        html += '</div>\n'
    
    html += '</div>\n'
    return html

def format_top_pages(data):
    """Format top pages with engagement scores"""
    pages = data.get("top_pages", [])
    
    if not pages:
        return ""
    
    html = '<div class="section">\n<h2>🔥 TOP PAGES (by Engagement Score)</h2>\n'
    
    # Calculate engagement for each page
    pages_with_scores = []
    for page in pages:
        path = page.get("pagePath", "/")
        views = page.get("screenPageViews", 0)
        users = page.get("activeUsers", 0)
        duration = float(page.get("averageSessionDuration", "0"))
        
        if views == 0:
            continue
        
        score = engagement_score(views, duration, users)
        pages_with_scores.append({
            "path": path,
            "views": views,
            "users": users,
            "duration": duration,
            "score": score
        })
    
    # Sort by score
    pages_with_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Show top 5
    for idx, page in enumerate(pages_with_scores[:5], 1):
        score = page["score"]
        html += f'<div class="page-item">\n'
        html += f'{idx}. <strong>{page["path"]}</strong> ({page["views"]} views) | Score: {score:.1f} {stars(score)}\n'
        html += '</div>\n'
    
    html += '</div>\n'
    return html

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    
    output = {
        "metrics_html": format_key_metrics(data),
        "sources_html": format_traffic_sources(data),
        "pages_html": format_top_pages(data)
    }
    
    print(json.dumps(output, indent=2))
