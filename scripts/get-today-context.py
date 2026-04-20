#!/usr/bin/env python3
"""
get-today-context.py — Fetch today's calendar + email and write TODAY.md

Runs every 2h via observer-agent.sh. Produces ~/.openclaw/workspace/TODAY.md
for agent context awareness.

Accounts:
  - rdreilly2010@gmail.com   (gog — authenticated)
  - reillyrd25@gmail.com     (gog — needs: gog auth add reillyrd25@gmail.com --services gmail,calendar)
  - robert@reillydesignstudio.com (gog — needs: gog auth add robert@reillydesignstudio.com --services gmail,calendar)

Calendar: today's remaining events + tomorrow morning (before noon)
Email:    unread + important/starred, subject + sender, up to 8 per account
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

WORKSPACE   = Path.home() / ".openclaw" / "workspace"
TODAY_FILE  = WORKSPACE / "TODAY.md"
TZ          = ZoneInfo("America/New_York")

EMAIL_ACCOUNTS = [
    {"email": "rdreilly2010@gmail.com",           "label": "rdreilly2010",      "tool": "gog"},
    {"email": "reillyrd25@gmail.com",             "label": "reillyrd25",        "tool": "gog"},
    {"email": "robert@reillydesignstudio.com",    "label": "reillydesignstudio","tool": "gog"},
]

CALENDAR_ACCOUNT = "rdreilly2010@gmail.com"


def run(cmd: str, timeout: int = 12) -> tuple[int, str]:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout.strip()


def fmt_time(dt_field) -> str:
    """Format a calendar start/end dict into a readable string."""
    if not dt_field:
        return ""
    if "date" in dt_field:
        return "All day"
    if "dateTime" in dt_field:
        try:
            dt = datetime.fromisoformat(dt_field["dateTime"])
            local = dt.astimezone(TZ)
            return local.strftime("%-I:%M %p")
        except Exception:
            return dt_field["dateTime"][:16]
    return str(dt_field)


def get_calendar() -> dict:
    """Fetch today's remaining events + tomorrow morning from Google Calendar."""
    now       = datetime.now(TZ)
    today     = now.date()
    tomorrow  = today + timedelta(days=1)

    code, out = run(f"gog calendar list -a {CALENDAR_ACCOUNT} --json 2>/dev/null")
    if code != 0 or not out:
        return {"today": [], "tomorrow": [], "error": "gog calendar unavailable"}

    try:
        data   = json.loads(out)
        events = data.get("events", data.get("items", []))
    except json.JSONDecodeError:
        return {"today": [], "tomorrow": [], "error": "JSON parse error"}

    today_events, tomorrow_events = [], []

    for ev in events:
        start = ev.get("start", {})
        summary = ev.get("summary", "Untitled")
        location = ev.get("location", "")

        # Determine event date
        if "dateTime" in start:
            try:
                dt = datetime.fromisoformat(start["dateTime"]).astimezone(TZ)
                ev_date = dt.date()
                # Skip today's events that already ended
                if ev_date == today and dt < now:
                    continue
            except Exception:
                ev_date = None
        elif "date" in start:
            try:
                from datetime import date as _date
                ev_date = _date.fromisoformat(start["date"])
            except Exception:
                ev_date = None
        else:
            ev_date = None

        if ev_date is None:
            continue

        entry = {
            "title":    summary,
            "time":     fmt_time(start),
            "location": location,
        }

        if ev_date == today:
            today_events.append(entry)
        elif ev_date == tomorrow:
            # Only include tomorrow morning events (before noon)
            if entry["time"] == "All day" or _is_before_noon(start):
                tomorrow_events.append(entry)

    return {
        "today":    today_events[:8],
        "tomorrow": tomorrow_events[:5],
    }


def _is_before_noon(start_field: dict) -> bool:
    if "dateTime" not in start_field:
        return True
    try:
        dt = datetime.fromisoformat(start_field["dateTime"]).astimezone(TZ)
        return dt.hour < 12
    except Exception:
        return True


def get_email_for_account(account: dict) -> dict:
    """Fetch unread + important email for one account."""
    email = account["email"]
    label = account["label"]

    # Check auth by doing a quick search
    code, out = run(f"gog gmail search 'is:unread' -a {email} --json 2>/dev/null")

    if code != 0:
        # Check if it's an auth error
        _, err = run(f"gog gmail search 'is:unread' -a {email} --json 2>&1 | head -1")
        if "No auth" in err or "OAuth" in err:
            return {
                "label":   label,
                "status":  "needs_auth",
                "fix":     f"gog auth add {email} --services gmail,calendar",
                "messages": [],
            }
        return {"label": label, "status": "error", "messages": []}

    messages = []
    try:
        data     = json.loads(out)
        raw_msgs = data.get("messages", data.get("threads", []))

        for m in raw_msgs[:8]:
            sender  = m.get("from", "")
            subject = m.get("subject", "(no subject)")
            date    = m.get("date", "")
            labels  = m.get("labels", [])

            # Short preview = subject truncated (gog doesn't expose body snippet)
            preview = subject[:80] + ("…" if len(subject) > 80 else "")

            # Tag important/starred/flagged
            flags = []
            if "IMPORTANT" in labels:  flags.append("important")
            if "STARRED"   in labels:  flags.append("starred")

            messages.append({
                "from":    sender,
                "subject": subject,
                "preview": preview,
                "date":    date,
                "flags":   flags,
            })
    except (json.JSONDecodeError, Exception):
        pass

    # Also fetch starred (may not overlap with unread)
    code2, out2 = run(f"gog gmail search 'is:starred is:read' -a {email} --json 2>/dev/null")
    if code2 == 0 and out2:
        try:
            data2    = json.loads(out2)
            raw2     = data2.get("messages", data2.get("threads", []))
            seen_ids = {m.get("id") for m in json.loads(out).get("messages", [])}
            for m in raw2[:3]:
                if m.get("id") not in seen_ids:
                    messages.append({
                        "from":    m.get("from", ""),
                        "subject": m.get("subject", "(no subject)"),
                        "preview": m.get("subject", "")[:80],
                        "date":    m.get("date", ""),
                        "flags":   ["starred"],
                    })
        except Exception:
            pass

    return {
        "label":    label,
        "status":   "ok",
        "count":    len(messages),
        "messages": messages,
    }


def render_today_md(calendar: dict, email_results: list) -> str:
    now_str = datetime.now(TZ).strftime("%A %B %-d, %Y  %-I:%M %p %Z")
    lines   = [f"# TODAY  —  {now_str}", ""]

    # ── Calendar ──────────────────────────────────────────────────────────────
    lines.append("## 📅 Calendar")

    if calendar.get("error"):
        lines.append(f"_Calendar unavailable: {calendar['error']}_")
    else:
        today_ev = calendar.get("today", [])
        if today_ev:
            lines.append("**Today (remaining):**")
            for ev in today_ev:
                loc  = f"  📍 {ev['location']}" if ev["location"] else ""
                lines.append(f"- {ev['time']}  {ev['title']}{loc}")
        else:
            lines.append("**Today:** _No remaining events_")

        lines.append("")
        tomorrow_ev = calendar.get("tomorrow", [])
        if tomorrow_ev:
            lines.append("**Tomorrow morning:**")
            for ev in tomorrow_ev:
                loc  = f"  📍 {ev['location']}" if ev["location"] else ""
                lines.append(f"- {ev['time']}  {ev['title']}{loc}")
        else:
            lines.append("**Tomorrow morning:** _Nothing scheduled_")

    lines.append("")

    # ── Email ─────────────────────────────────────────────────────────────────
    lines.append("## 📧 Email")
    lines.append("")

    for acct in email_results:
        label = acct["label"]
        status = acct.get("status", "error")

        if status == "needs_auth":
            lines.append(f"### {label}  ⚠️  Not authenticated")
            lines.append(f"_Run: `{acct['fix']}`_")
            lines.append("")
            continue

        if status == "error":
            lines.append(f"### {label}  ❌  Error fetching email")
            lines.append("")
            continue

        msgs = acct.get("messages", [])
        lines.append(f"### {label}  ({len(msgs)} unread/important)")

        if not msgs:
            lines.append("_Inbox clear_")
        else:
            for m in msgs:
                flag_str = ""
                if "starred"   in m["flags"]: flag_str += " ⭐"
                if "important" in m["flags"]: flag_str += " 🔔"
                # Shorten sender to display name only
                sender = m["from"].split("<")[0].strip().strip('"') or m["from"]
                lines.append(f"- **{sender}**{flag_str}  —  {m['subject']}")

        lines.append("")

    lines.append("---")
    lines.append(f"_Refreshed by observer-agent.sh · Next refresh in ~2h_")
    return "\n".join(lines)


def main():
    calendar      = get_calendar()
    email_results = [get_email_for_account(a) for a in EMAIL_ACCOUNTS]
    md            = render_today_md(calendar, email_results)
    TODAY_FILE.write_text(md)
    print(f"[today-context] Written: {TODAY_FILE}")
    # Summary for caller
    today_count    = len(calendar.get("today", []))
    tomorrow_count = len(calendar.get("tomorrow", []))
    email_counts   = {a["label"]: a.get("count", "?") for a in email_results if a.get("status") == "ok"}
    print(f"[today-context] Calendar: {today_count} today, {tomorrow_count} tomorrow AM | Email: {email_counts}")


if __name__ == "__main__":
    main()
