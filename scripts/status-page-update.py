#!/usr/bin/env python3
"""
status-page-update.py — Update the persistent OpenClaw Telegraph status page.

Creates the page on first run, then edits it in-place every subsequent run.
Page path is stored in ~/.openclaw/workspace/config/status-page-path.txt.

Usage:
  python3 status-page-update.py
  python3 status-page-update.py --reset    # force new page creation

Cron: 7,37 * * * *  (every 30 min, off :00/:30 marks)
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/scripts"))
from telegraph_publisher import TelegraphPublisher

# ── Config ────────────────────────────────────────────────────────────────────
PAGE_PATH_FILE  = Path.home() / ".openclaw/workspace/config/status-page-path.txt"
LOG_DIR         = Path.home() / ".openclaw/logs"
WORKSPACE       = Path.home() / ".openclaw/workspace"
LOGS_TO_SCAN    = [
    ("Watchdog",      LOG_DIR / "session-watchdog.log",       50),
    ("Health",        LOG_DIR / "health-check.log",           80),
    ("Quota",         LOG_DIR / "quota-monitor.log",          80),
    ("Auto-flush",    LOG_DIR / "session-context-flush.log",  30),
    ("Evening brief", Path("/tmp/evening-briefing.log"),       30),
]

FORCE_RESET = "--reset" in sys.argv

# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd: list[str], timeout: int = 10) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def recent_errors(log_path: Path, tail_lines: int) -> list[str]:
    """Return ERROR/FAIL/❌ lines from the last `tail_lines` of a log."""
    if not log_path.exists():
        return []
    try:
        lines = log_path.read_text(errors="replace").splitlines()[-tail_lines:]
        hits = [l.strip() for l in lines if re.search(r"ERROR|FAIL|❌|STALE|stale", l, re.I)]
        # Deduplicate while preserving order
        seen, out = set(), []
        for h in hits:
            key = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '', h)[:120]
            if key not in seen:
                seen.add(key); out.append(h[:150])
        return out[:5]
    except Exception:
        return []


def get_telegram_credentials():
    try:
        c = json.loads(Path.home().joinpath(".openclaw/config.json").read_text())
        return c.get("telegram", {}).get("botToken", ""), c.get("telegram", {}).get("chatId", "")
    except Exception:
        return "", ""


def send_telegram(text: str):
    token, chat_id = get_telegram_credentials()
    if not token or not chat_id:
        return
    subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{token}/sendMessage",
        "-d", f"chat_id={chat_id}",
        "-d", f"text={text}",
        "-d", "parse_mode=HTML",
        "-d", "disable_web_page_preview=true",
    ], capture_output=True, timeout=10)


# ── Build content ─────────────────────────────────────────────────────────────

def build_status_content() -> str:
    now = datetime.now()
    ts  = now.strftime("%Y-%m-%d %H:%M %Z")

    # Session health
    session_age_min = "unknown"
    try:
        sessions = json.loads(
            (Path.home() / ".openclaw/agents/main/sessions/sessions.json").read_text()
        )
        updated_ms = sessions.get("agent:main:main", {}).get("updatedAt", 0)
        if updated_ms:
            session_age_min = f"{int((time.time() - updated_ms/1000) / 60)}m"
    except Exception:
        pass

    # System uptime
    uptime = run(["uptime"]).split("up")[-1].split(",")[0].strip() if run(["uptime"]) else "unknown"

    # Things Today
    things_raw = run(["things", "today", "--json"])
    things_lines = []
    if things_raw:
        try:
            for t in json.loads(things_raw)[:6]:
                things_lines.append(f"- {t.get('title','?')}")
        except Exception:
            pass
    things_section = "\n".join(things_lines) if things_lines else "- (nothing scheduled)"

    # Cron health: last line of key logs
    cron_rows = []
    for label, path, _ in LOGS_TO_SCAN:
        if path.exists():
            last = path.read_text(errors="replace").splitlines()
            last = [l for l in last if l.strip()][-1][:120] if last else "(empty)"
            cron_rows.append(f"**{label}:** {last}")

    # Errors in last 24h across all logs
    all_errors = []
    for label, path, tail in LOGS_TO_SCAN:
        errs = recent_errors(path, tail)
        for e in errs:
            all_errors.append(f"[{label}] {e}")

    errors_section = "\n".join(f"- {e}" for e in all_errors[:10]) if all_errors else "- No errors detected"

    # Recent git commits
    git_log = run(["git", "-C", str(WORKSPACE), "log", "--oneline", "-5"])
    git_lines = "\n".join(f"- {l}" for l in git_log.splitlines()) if git_log else "- (no commits)"

    return f"""## OpenClaw Status

**Updated:** {ts}
**Session age:** {session_age_min} ago
**System uptime:** {uptime}

---

## Today's Tasks

{things_section}

---

## Recent Errors (24h)

{errors_section}

---

## Cron Job Last Output

{chr(10).join(cron_rows) if cron_rows else '- (no logs found)'}

---

## Recent Commits

{git_lines}

---

*Auto-updated every 30 min by OpenClaw status-page-update.py*
"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    pub = TelegraphPublisher()
    content = build_status_content()
    title   = f"OpenClaw Status — {datetime.now().strftime('%b %d')}"

    stored_path = None
    if not FORCE_RESET and PAGE_PATH_FILE.exists():
        stored_path = PAGE_PATH_FILE.read_text().strip()

    if stored_path:
        # Update existing page
        result = pub.edit_page(stored_path, title, content)
        if not result["success"]:
            print(f"editPage failed ({result.get('error')}) — creating new page")
            stored_path = None

    if not stored_path:
        # First run or reset — create page and save path
        result = pub.publish_markdown(title, content)
        if result["success"]:
            PAGE_PATH_FILE.parent.mkdir(parents=True, exist_ok=True)
            PAGE_PATH_FILE.write_text(result["path"])
            print(f"Created status page: {result['url']}")
            send_telegram(
                f"📊 <b>OpenClaw Status Page created</b>\n{result['url']}\n"
                "(auto-updates every 30 min)"
            )
        else:
            print(f"ERROR: {result.get('error')}", file=sys.stderr)
            sys.exit(1)
        return

    print(f"Updated: {result['url']}")


if __name__ == "__main__":
    main()
