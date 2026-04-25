#!/usr/bin/env python3
"""Slack Socket Mode listener for OpenClaw.

Provides a `/momo <text>` slash command that mirrors the Telegram bridge:
the user's text is appended to a JSONL queue at
~/.openclaw/queue/slack-inbound.jsonl which the agent runtime tails. An
immediate ACK is sent back to Slack so the slash command never times out.

Tokens (from ~/.openclaw/.env, exported by load-secrets-from-keychain.sh):
    SLACK_BOT_TOKEN  — xoxb-...   (bot user OAuth token)
    SLACK_APP_TOKEN  — xapp-...   (app-level token, scope connections:write)

Run manually:
    venv/bin/python3 scripts/slack_listener.py

Run as a service:
    launchctl load ~/Library/LaunchAgents/ai.openclaw.slack-listener.plist
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

ENV_FILE = Path.home() / ".openclaw" / ".env"
QUEUE_FILE = Path.home() / ".openclaw" / "queue" / "slack-inbound.jsonl"
LOG_FILE = Path.home() / ".openclaw" / "logs" / "slack-listener.log"

# Load .env if SLACK_* aren't already in env (mirrors notify.sh pattern).
if ENV_FILE.is_file():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")

if not BOT_TOKEN or not APP_TOKEN:
    sys.stderr.write(
        "slack_listener: SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set "
        "in ~/.openclaw/.env. See config/notifications.md (Slack section).\n"
    )
    sys.exit(2)

QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("slack_listener")

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=BOT_TOKEN)


def _enqueue(payload: dict) -> None:
    """Append one JSON record per line — same shape Telegram bridge uses."""
    with QUEUE_FILE.open("a") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


@app.command("/momo")
def handle_momo(ack, command, respond):
    # ACK within 3s or Slack errors out.
    ack()

    text = (command.get("text") or "").strip()
    user_id = command.get("user_id", "?")
    user_name = command.get("user_name", "?")
    channel_id = command.get("channel_id", "?")

    log.info("/momo from %s (%s) in %s: %r", user_name, user_id, channel_id, text)

    if not text:
        respond("Usage: `/momo <message>` — drops it into the OpenClaw inbox.")
        return

    record = {
        "ts": int(time.time()),
        "source": "slack",
        "session_key": f"agent:main:slack:direct:{user_id}",
        "user_id": user_id,
        "user_name": user_name,
        "channel_id": channel_id,
        "text": text,
    }
    _enqueue(record)
    respond(f"Got it ({len(text)} chars). Queued for OpenClaw.")


@app.event("app_mention")
def handle_mention(event, say):
    text = event.get("text", "")
    user_id = event.get("user", "?")
    log.info("@mention from %s: %r", user_id, text)
    say(f"Hi <@{user_id}> — use `/momo <text>` to send me a message.")


@app.event("message")
def handle_message(event, say):
    # We subscribe to message.im (DMs to the bot). Ignore bot's own messages
    # and message_changed/deleted subtypes; treat plain user DMs as inbound.
    if event.get("bot_id") or event.get("subtype"):
        return
    if event.get("channel_type") != "im":
        return

    text = (event.get("text") or "").strip()
    user_id = event.get("user", "?")
    channel_id = event.get("channel", "?")
    log.info("DM from %s in %s: %r", user_id, channel_id, text)

    if not text:
        return

    record = {
        "ts": int(time.time()),
        "source": "slack",
        "session_key": f"agent:main:slack:direct:{user_id}",
        "user_id": user_id,
        "user_name": "",
        "channel_id": channel_id,
        "text": text,
    }
    _enqueue(record)
    say(f"Got it ({len(text)} chars). Queued for OpenClaw.")


def main() -> None:
    log.info("starting Slack Socket Mode listener (queue=%s)", QUEUE_FILE)
    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    main()
