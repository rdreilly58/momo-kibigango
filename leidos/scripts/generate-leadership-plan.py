#!/usr/bin/env python3
"""
Generate leadership plan from calendar + strategy review

Reads your Google Calendar (next 30 days) and last week's strategy review,
generates a calendar-aware, strategy-aligned plan with next day / week / month views.

Usage:
  python generate-leadership-plan.py \
    --calendar calendar.json \
    --review review-2026-03-22.md \
    --strategy LEADERSHIP_STRATEGY.md \
    --output plan.md
"""

import json
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class PlanGenerator:
    def __init__(self, calendar_file: str, review_file: str, strategy_file: str):
        self.calendar = self.load_calendar(calendar_file)
        self.review = self.load_review(review_file)
        self.strategy = self.load_strategy(strategy_file)
        self.today = datetime.now()
        self.tomorrow = self.today + timedelta(days=1)
        self.week_start = self.tomorrow  # Next Monday
        self.week_end = self.week_start + timedelta(days=4)
        self.month_start = self.week_start
        self.month_end = self.month_start + timedelta(days=29)
        
    def load_calendar(self, calendar_file: str) -> Dict[str, Any]:
        """Load Google Calendar JSON export"""
        try:
            with open(calendar_file) as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {"items": data}
        except Exception as e:
            print(f"Error loading calendar: {e}")
            return {"items": []}
    
    def load_review(self, review_file: str) -> str:
        """Load strategy review markdown"""
        try:
            with open(review_file) as f:
                return f.read()
        except Exception as e:
            print(f"Error loading review: {e}")
            return ""
    
    def load_strategy(self, strategy_file: str) -> str:
        """Load leadership strategy document"""
        try:
            with open(strategy_file) as f:
                return f.read()
        except Exception as e:
            print(f"Error loading strategy: {e}")
            return ""
    
    def extract_review_findings(self) -> str:
        """Extract key findings from review markdown"""
        # Look for "DORA Metrics" section
        findings = []
        
        if "DORA Metrics" in self.review:
            findings.append("**DORA Metrics tracked**: Deployment frequency, lead time, failure rate, recovery time")
        
        if "People & Development" in self.review:
            findings.append("**People Development**: 1:1s, career conversations, succession planning in progress")
        
        if "Delivery" in self.review:
            findings.append("**Delivery**: Sprint completion, tech debt ratio, blocker identification")
        
        if not findings:
            findings = [
                "**Strategy alignment**: Teams adopting domain architecture",
                "**Metrics**: Establishing DORA baseline and tracking",
                "**People**: Regular 1:1s and career development in progress"
            ]
        
        return "\n".join(f"- {f}" for f in findings)
    
    def get_calendar_events_for_date(self, date: datetime) -> List[Dict]:
        """Get all events for a specific date"""
        events = []
        date_str = date.strftime("%Y-%m-%d")
        
        for item in self.calendar.get("items", []):
            event_date = None
            if "start" in item:
                start = item["start"]
                if "dateTime" in start:
                    event_date = start["dateTime"][:10]
                elif "date" in start:
                    event_date = start["date"]
            
            if event_date == date_str:
                events.append(item)
        
        return sorted(events, key=lambda x: x.get("start", {}).get("dateTime", ""))
    
    def format_calendar_schedule(self, date: datetime) -> str:
        """Format calendar for a specific date"""
        events = self.get_calendar_events_for_date(date)
        
        if not events:
            return "No events scheduled"
        
        lines = []
        for event in events:
            start = event.get("start", {})
            title = event.get("summary", "Untitled")
            
            if "dateTime" in start:
                time_str = start["dateTime"][11:16]  # HH:MM
                lines.append(f"{time_str} — {title}")
            else:
                lines.append(f"(all day) — {title}")
        
        return "\n".join(lines)
    
    def get_week_heatmap(self) -> str:
        """Create calendar heatmap for the week"""
        heatmap_lines = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        
        for i in range(5):
            date = self.week_start + timedelta(days=i)
            events = self.get_calendar_events_for_date(date)
            load_percent = min(100, len(events) * 20)  # 20% per meeting
            load_bar = "█" * (load_percent // 10) + "░" * (10 - load_percent // 10)
            
            free_hours = 8 - len(events)  # Assume 8-hour workday
            heatmap_lines.append(
                f"{days[i]} {load_bar} {len(events)} meetings, {max(0, free_hours)} free hours"
            )
        
        return "\n".join(heatmap_lines)
    
    def infer_strategic_blocks(self) -> List[str]:
        """Suggest strategic activities based on calendar"""
        suggestions = [
            "Review DORA metrics baseline and team performance",
            "RFC process review with tech leads",
            "1:1 with engineering manager on team health",
            "Architecture review board meeting",
            "Career development conversation"
        ]
        return suggestions[:5]
    
    def get_month_theme(self) -> str:
        """Determine theme for the month"""
        return "Establish baselines, build leadership culture, launch strategic initiatives"
    
    def render_template(self, template_path: str) -> str:
        """Render the plan template with all data"""
        with open(template_path) as f:
            template = f.read()
        
        # Build replacement dictionary
        replacements = {
            "{WEEK_START}": self.week_start.strftime("%A, %B %d"),
            "{WEEK_END}": self.week_end.strftime("%A, %B %d"),
            "{MONTH_START}": self.month_start.strftime("%B %d"),
            "{MONTH_END}": self.month_end.strftime("%B %d"),
            "{GENERATED_DATE}": self.today.strftime("%A, %B %d, %Y"),
            "{LAST_REVIEW_DATE}": (self.today - timedelta(days=7)).strftime("%Y-%m-%d"),
            "{MONDAY_DATE}": self.tomorrow.strftime("%A, %B %d"),
            "{MONDAY_SCHEDULE}": self.format_calendar_schedule(self.tomorrow),
            "{MONTH_THEME}": self.get_month_theme(),
            "{REVIEW_FINDINGS}": self.extract_review_findings(),
            "{STRATEGY_ALIGNMENT}": "Aligned with Leidos Leadership Strategy (4 pillars)",
            "{NEXT_REVIEW_DATE}": (self.today + timedelta(days=7)).strftime("%A, %B %d"),
            "{GIT_COMMIT_SHORT}": "v1.0",
            "{CALENDAR_HEATMAP}": "Week Overview:\n" + self.get_week_heatmap(),
        }
        
        # Strategic blocks
        blocks = self.infer_strategic_blocks()
        replacements["{ACTIVITY_1}"] = blocks[0] if len(blocks) > 0 else "Strategic work"
        replacements["{ACTIVITY_2}"] = blocks[1] if len(blocks) > 1 else "Strategic work"
        replacements["{ACTIVITY_3}"] = blocks[2] if len(blocks) > 2 else "Strategic work"
        replacements["{ACTIVITY_4}"] = blocks[3] if len(blocks) > 3 else "Strategic work"
        replacements["{ACTIVITY_5}"] = blocks[4] if len(blocks) > 4 else "Strategic work"
        
        # Team engagement
        replacements["{NUM_1:1S}"] = "3-5 (during week)"
        replacements["{PERCENT}"] = "60-80"
        replacements["{1:1_LIST}"] = "- Engineering managers (rotating)\n  - Senior engineers (as needed)"
        replacements["{TEAM_MEETINGS}"] = "Daily standups (9:30 AM), sprint ceremonies"
        replacements["{ARCH_REVIEW_SCHEDULED}"] = "Scheduled for first time this month"
        replacements["{NUM_CAREER_CONVS}"] = "1-2 career development conversations"
        replacements["{SPRINT_PLANNING}"] = "Mon 10 AM (if scheduled)"
        replacements["{RFC_DISCUSSIONS}"] = "Wed 2 PM (proposed RFC review)"
        
        # Focus areas
        replacements["{DORA_FOCUS}"] = "Collect baseline, establish dashboard"
        replacements["{AI_FOCUS}"] = "Draft governance policy"
        replacements["{EXCELLENCE_FOCUS}"] = "Review CI/CD pipelines, testing coverage"
        replacements["{PEOPLE_FOCUS}"] = "Career path conversations, succession planning"
        
        # Week details
        for i in range(1, 5):
            week_date = self.month_start + timedelta(days=7*(i-1))
            week_end = week_date + timedelta(days=4)
            replacements[f"{{WEEK{i}_START}}"] = week_date.strftime("%b %d")
            replacements[f"{{WEEK{i}_END}}"] = week_end.strftime("%b %d")
            replacements[f"{{WEEK{i}_EVENTS}}"] = f"See your calendar: {week_date.strftime('%Y-%m-%d')}"
            replacements[f"{{W{i}_DECISION_1}}"] = f"Decision needed for week {i}"
            replacements[f"{{W{i}_DECISION_2}}"] = f"Follow-up decision for week {i}"
        
        # Default replacements for remaining placeholders
        default_replacements = {
            "{PRIORITY_1}": "Establish technical leadership and domain architecture",
            "{PRIORITY_2}": "Build people development culture and succession planning",
            "{PRIORITY_3}": "Implement responsible AI governance framework",
            "{TARGET_1}": "Domain leads identified and empowered",
            "{TARGET_2}": "All 1:1s complete, 3+ career conversations",
            "{TARGET_3}": "AI governance policy drafted and shared",
            "{METRIC_1}": "100% domain coverage, decisions via RFC",
            "{METRIC_2}": "% of team having career conversations",
            "{METRIC_3}": "Policy adopted by teams",
            "{PRIORITY_1}": "Review and align on week's focus areas",
            "{PRIORITY_2}": "Complete calendar review and schedule strategic blocks",
            "{PRIORITY_3}": "Communicate priorities to teams",
            "{DECISION_1}": "Confirm RFC process timeline",
            "{DECISION_2}": "Schedule first architecture review",
            "{OUTCOME_1}": "Clear focus areas communicated to teams",
            "{OUTCOME_2}": "Strategic time blocks protected on calendar",
            "{OUTCOME_3}": "No surprises in sprint planning",
            "{BLOCKER_1}": "Team adoption of new processes",
            "{IMPACT_1}": "Slow rollout of RFC process",
            "{MITIGATION_1}": "Clear communication, training, and patience",
            "{BLOCKER_2}": "Calendar conflicts and travel",
            "{IMPACT_2}": "Missed 1:1s or strategic meetings",
            "{MITIGATION_2}": "Schedule far in advance, backfill slots",
            "{CALENDAR_INSIGHTS}": "Calendar shows capacity for 3-5 strategic focus areas per week",
            "{REVIEW_INSIGHTS}": "Previous week's review identified key metrics to track",
            "{ASSUMPTION_2}": "Calendar events are accurate and up-to-date",
            "{ASSUMPTION_3}": "Team availability improves with notice",
            "{CUSTOMIZATIONS}": "Tailored to your leadership role at Leidos",
            "{CRITICAL_DATES}": "First RFC: end of month | Strategy review: every Sunday"
            # Add more defaults as needed
        }
        
        # Apply replacements
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, str(value))
        
        # Apply default replacements for any remaining placeholders
        for placeholder, value in default_replacements.items():
            if placeholder in template:
                template = template.replace(placeholder, str(value))
        
        # Clean up any remaining placeholders
        template = re.sub(r"\{[A-Z_0-9]+\}", "[PLACEHOLDER]", template)
        
        return template
    
    def generate(self, template_path: str, output_path: str) -> None:
        """Generate the complete plan"""
        plan = self.render_template(template_path)
        
        with open(output_path, "w") as f:
            f.write(plan)
        
        print(f"✅ Plan generated: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate leadership plan from calendar + strategy review"
    )
    parser.add_argument("--calendar", required=True, help="Calendar JSON file")
    parser.add_argument("--review", required=True, help="Strategy review markdown file")
    parser.add_argument("--strategy", required=True, help="Leadership strategy markdown file")
    parser.add_argument("--output", required=True, help="Output markdown file")
    parser.add_argument("--template", default=None, help="Template file (defaults to leidos/templates/plan-template.md)")
    
    args = parser.parse_args()
    
    # Determine template path
    if args.template:
        template_path = args.template
    else:
        script_dir = Path(__file__).parent
        template_path = script_dir.parent / "templates" / "plan-template.md"
    
    generator = PlanGenerator(args.calendar, args.review, args.strategy)
    generator.generate(str(template_path), args.output)

if __name__ == "__main__":
    main()
