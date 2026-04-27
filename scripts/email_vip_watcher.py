#!/usr/bin/env python3
"""
email-vip-watcher.py — Poll email for VIP senders/keywords, send Telegram alerts.

Runs every 5 min via cron. Features:
  - VIP sender / domain / keyword matching
  - Per-account cooldown (avoid alert storms)
  - max_age_minutes filter (skip old messages)
  - Dedup via persisted state file
  - enabled flag for config-level kill switch

Cron entry:
  */5 * * * * /Users/rreilly/.openclaw/workspace/venv/bin/python3 \
    /Users/rreilly/.openclaw/workspace/scripts/email-vip-watcher.py \
    >> /Users/rreilly/.openclaw/logs/email-vip-watcher.log 2>&1
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure Homebrew bin is on PATH (cron environments are often stripped)
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", "")

WORKSPACE = Path(__file__).parent.parent
CONFIG_FILE = WORKSPACE / "config" / "email-vip-config.json"
STATE_FILE = WORKSPACE / ".email-vip-state.json"
MAX_STATE_IDS = 500

DEFAULT_CONFIG = {
    "enabled": True,
    "vip_senders": [],
    "vip_emails": [],
    "vip_sender_domains": [],
    "subject_keywords": ["urgent", "action required", "deadline", "emergency", "invoice", "payment"],
    "accounts": ["rdreilly2010@gmail.com", "robert@reillydesignstudio.com"],
    "max_age_minutes": 10,
    "cooldown_minutes": 60,
    "check_interval_minutes": 5,
    "telegram_channel": "8755120444",
}


def load_config() -> dict:
    """Load config from file, falling back to safe defaults on any error."""
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            # Merge with defaults so missing keys are always present
            merged = dict(DEFAULT_CONFIG)
            merged.update(data)
            return merged
    except Exception as exc:
        print(f"[vip-watcher] Config load error: {exc} — using defaults", file=sys.stderr)
    return dict(DEFAULT_CONFIG)


def load_state() -> dict:
    """Load dedup state, creating empty state if missing or corrupt."""
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[vip-watcher] State load error: {exc} — starting fresh", file=sys.stderr)
    return {"notified_ids": [], "cooldowns": {}, "last_run": ""}


def save_state(state: dict) -> None:
    """Persist state, keeping only the last MAX_STATE_IDS entries."""
    try:
        state["notified_ids"] = state["notified_ids"][-MAX_STATE_IDS:]
        state["last_run"] = datetime.now().isoformat(timespec="seconds")
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"[vip-watcher] State save error: {exc}", file=sys.stderr)


def fetch_unread(account: str) -> list[dict]:
    """
    Fetch unread messages for one account via gog.

    Returns a list of message dicts (may be empty on error or auth failure).
    Each dict has at minimum: id, from, subject, date.
    """
    try:
        r = subprocess.run(
            ["gog", "gmail", "search", "is:unread", "-a", account, "--json"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if r.returncode != 0:
            stderr = r.stderr.strip()
            if any(k in stderr for k in ("No auth", "OAuth", "auth", "token", "credential")):
                print(f"[vip-watcher] Auth error for {account}: {stderr}", file=sys.stderr)
            else:
                print(f"[vip-watcher] gog error for {account}: {stderr}", file=sys.stderr)
            return []

        data = json.loads(r.stdout.strip())
        return data.get("messages", data.get("threads", []))

    except subprocess.TimeoutExpired:
        print(f"[vip-watcher] gog timed out for {account}", file=sys.stderr)
        return []
    except json.JSONDecodeError as exc:
        print(f"[vip-watcher] JSON parse error for {account}: {exc}", file=sys.stderr)
        return []
    except Exception as exc:
        print(f"[vip-watcher] Unexpected error for {account}: {exc}", file=sys.stderr)
        return []


def is_message_recent(msg: dict, max_age_minutes: int) -> bool:
    """Return True if the message date is within max_age_minutes, or if date is unparseable."""
    date_str = msg.get("date", "")
    if not date_str:
        return True  # no date — include conservatively
    try:
        msg_dt = datetime.fromisoformat(date_str)
        if msg_dt.tzinfo is None:
            msg_dt = msg_dt.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - msg_dt).total_seconds() / 60
        return age <= max_age_minutes + 0.1  # 6s tolerance for clock skew / test timing
    except (ValueError, Exception):
        return True  # unparseable date — include conservatively


def is_account_on_cooldown(account: str, state: dict, cooldown_minutes: int) -> bool:
    """Return True if we alerted for this account within cooldown_minutes."""
    last_str = state.get("cooldowns", {}).get(account, "")
    if not last_str:
        return False
    try:
        last_dt = datetime.fromisoformat(last_str)
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds() / 60
        return elapsed < cooldown_minutes
    except Exception:
        return False


def is_vip_match(msg: dict, config: dict) -> tuple[bool, str]:
    """
    Return (True, reason) if msg matches a VIP rule, else (False, '').

    Rules:
      1. sender contains a vip_email entry (case-insensitive substring)
      2. sender contains a vip_senders entry
      3. sender domain matches vip_sender_domains
      4. subject contains a subject_keyword
    """
    sender = (msg.get("from", "") or "").lower()
    subject = (msg.get("subject", "") or "").lower()

    for ve in config.get("vip_emails", []):
        if ve.lower() in sender:
            return True, f"VIP email: {ve}"

    for vs in config.get("vip_senders", []):
        if vs.lower() in sender:
            return True, f"VIP sender: {vs}"

    for domain in config.get("vip_sender_domains", []):
        if f"@{domain.lower()}" in sender:
            return True, f"VIP domain: {domain}"

    for kw in config.get("subject_keywords", []):
        if kw.lower() in subject:
            return True, f"keyword: '{kw}'"

    return False, ""


def send_telegram(msg_text: str, channel: str) -> bool:
    """
    Send a Telegram notification via the openclaw CLI.

    Returns True on success, False on any failure (does not raise).
    """
    try:
        r = subprocess.run(
            ["openclaw", "message", "send", "--channel", channel, "--text", msg_text],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if r.returncode != 0:
            print(f"[vip-watcher] Telegram error (rc={r.returncode}): {r.stderr.strip()}", file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print("[vip-watcher] Telegram notification timed out", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"[vip-watcher] Notification error: {exc}", file=sys.stderr)
        return False


def main() -> None:
    config = load_config()

    if not config.get("enabled", True):
        print("[vip-watcher] Disabled in config — exiting.")
        return

    channel = config.get("telegram_channel", "8755120444")
    accounts = config.get("accounts", ["rdreilly2010@gmail.com"])
    max_age = config.get("max_age_minutes", 10)
    cooldown_min = config.get("cooldown_minutes", 60)

    state = load_state()
    notified_ids: set = set(state.get("notified_ids", []))
    new_ids: list = []
    alerts_sent = 0

    for account in accounts:
        if is_account_on_cooldown(account, state, cooldown_min):
            print(f"[vip-watcher] [{account}] on cooldown — skipping")
            continue

        messages = fetch_unread(account)
        account_label = account.split("@")[0]

        for msg in messages:
            msg_id = msg.get("id", "")
            if not msg_id:
                continue

            if msg_id in notified_ids:
                continue

            if not is_message_recent(msg, max_age):
                continue

            matched, reason = is_vip_match(msg, config)
            if not matched:
                continue

            sender = msg.get("from", "Unknown")
            sender_short = sender.split("<")[0].strip().strip('"') or sender
            subject = msg.get("subject", "(no subject)")
            now_str = datetime.now().strftime("%I:%M %p").lstrip("0")

            notification = (
                f"\U0001f4e7 VIP Email Alert ({now_str})\n"
                f"From: {sender_short}\n"
                f"Subject: {subject}\n"
                f"Account: {account_label}\n"
                f"Reason: {reason}"
            )
            sent = send_telegram(notification, channel)

            # Always mark as notified to prevent retry spam on send failure
            new_ids.append(msg_id)
            notified_ids.add(msg_id)
            state.setdefault("cooldowns", {})[account] = datetime.now(timezone.utc).isoformat()

            if sent:
                alerts_sent += 1
                print(f"[vip-watcher] Alerted: {subject!r} from {sender_short!r} [{reason}]")
            else:
                print(f"[vip-watcher] Send failed (marked to suppress retry): {subject!r}")

    state["notified_ids"] = list(notified_ids)
    save_state(state)
    print(f"[vip-watcher] Done. {alerts_sent} alert(s) sent, {len(new_ids)} message(s) marked.")


if __name__ == "__main__":
    main()
