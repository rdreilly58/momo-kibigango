# OpenClaw Notification Channels

OpenClaw can deliver alerts and proactive messages over three channels in
parallel. Telegram remains the primary chat channel; ntfy.sh is the
notification firehose; Slack is the new production-grade chat option.

| Channel  | Direction          | Status      | Setup needed |
|----------|--------------------|-------------|--------------|
| Telegram | bidirectional      | live        | already configured |
| ntfy.sh  | push only          | live        | install iOS app, subscribe to topic |
| Slack    | push only (pilot)  | scaffolded  | create Slack app + paste webhook URL |

## ntfy.sh

**Topic URL:** `https://ntfy.sh/openclaw-bob-e6453b5d6b02`

Topic names on public ntfy.sh act as the only secret — anyone who knows the
URL can subscribe to or publish messages on it. The suffix above was
generated with `openssl rand -hex 6`. Rotate it by editing
`NTFY_TOPIC_URL` in `~/.openclaw/.env` and the contact-point URL in
`config/grafana/provisioning/alerting/openclaw-contact-points.yaml`.

### Subscribe on iPhone

1. Install **ntfy** from the App Store (`io.heckel.ntfy`).
2. Tap `+`, choose *Subscribe to topic*, leave server as `ntfy.sh`.
3. Paste topic name: `openclaw-bob-e6453b5d6b02`.
4. Allow notifications when prompted.

### Subscribe on Mac

- Web: open `https://ntfy.sh/openclaw-bob-e6453b5d6b02` in Safari/Chrome.
- Native: install via Homebrew (`brew install ntfy`) and run
  `ntfy subscribe openclaw-bob-e6453b5d6b02` in a terminal, or use the menu
  bar app at https://github.com/binwiederhier/ntfy.

### Test

```bash
scripts/notify.sh --channel ntfy --priority high --tags rotating_light \
  "ntfy live test"
```

## Slack

Slack delivery is scaffolded but inactive until you provide an incoming
webhook URL.

### One-time setup

1. Visit <https://api.slack.com/apps> → *Create New App* → *From scratch*.
2. Name it `OpenClaw`, pick your workspace.
3. Side menu → *Incoming Webhooks* → toggle *Activate* on.
4. Click *Add New Webhook to Workspace*, choose the channel (e.g.
   `#openclaw-alerts`), authorize.
5. Copy the webhook URL (starts with `https://hooks.slack.com/services/...`).

### Wire the URL in two places

```bash
# 1. CLI / cron-script delivery (lib/notify.sh reads this)
echo 'SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ' \
  >> ~/.openclaw/.env

# Or in-place edit if the placeholder is already there:
sed -i '' \
  's|^SLACK_WEBHOOK_URL=$|SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ|' \
  ~/.openclaw/.env
```

```bash
# 2. Grafana alert delivery
sed -i '' \
  's|__REPLACE_WITH_SLACK_WEBHOOK_URL__|https://hooks.slack.com/services/XXX/YYY/ZZZ|' \
  config/grafana/provisioning/alerting/openclaw-contact-points.yaml

# Restart Grafana to pick up the change:
brew services restart grafana
```

### Test

```bash
source ~/.openclaw/.env
scripts/notify.sh --channel slack "Slack live test"
```

## Programmatic use

Any cron script can broadcast to every configured channel by sourcing the
shared library:

```bash
#!/bin/bash
set -Eeuo pipefail
source "$(dirname "$0")/lib/notify.sh"

notify_user "Backup completed in 47s" "Backup" "default" "white_check_mark"
```

`notify_user` is a no-op for any channel whose env var is unset, so missing
Slack credentials never break the cron. Per-channel helpers
(`notify_telegram`, `notify_ntfy`, `notify_slack`) remain available when you
need to target one channel directly.

Opt out per script via `NOTIFY_CHANNELS`:

```bash
NOTIFY_CHANNELS="ntfy,slack" notify_user "Skipping Telegram for this one"
```

## Grafana fan-out

`config/grafana/provisioning/alerting/openclaw-notification-policy.yaml`
fans every `critical|warning` alert to Telegram and ntfy, and routes
`critical` alerts additionally to Slack. Severity is set on each rule in
`openclaw-alerts.yaml`.

To roll back to Telegram-only delivery, set every route except the Telegram
one to `continue: false` and remove the others.
