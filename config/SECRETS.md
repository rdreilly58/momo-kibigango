# OpenClaw Secret Storage

One-page inventory of where every credential lives, plus rotation playbooks.

## Single source of truth: `~/.openclaw/.env`

All secrets live in `~/.openclaw/.env` (mode `600`, gitignored, outside the
workspace). Scripts source this file at startup. Avoid putting plaintext
credentials anywhere else — committed YAML, Python defaults, or in-repo
`.env` files.

```bash
# At the top of any cron / shell script that needs secrets:
set -a; source "$HOME/.openclaw/.env"; set +a
```

## Inventory

| Secret | Source | Used by | Rotation procedure |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | `~/.openclaw/.env` | Claude Code, agent SDK calls | Anthropic Console → API Keys → revoke + create new |
| `OPENROUTER_API_KEY` | `~/.openclaw/.env` | Fallback model calls | openrouter.ai → keys |
| `BRAVE_API_KEY` + macOS Keychain `OpenclawBrave` | `~/.openclaw/.env` (canonical) | Web-search MCP | Brave Developer Dashboard → keys |
| `GEMINI_API_KEY` | `~/.openclaw/.env` | Gemini CLI skill | aistudio.google.com → keys |
| `HF_TOKEN` | `~/.openclaw/.env` | Hugging Face skills | huggingface.co/settings/tokens |
| `CLOUDFLARE_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` | `~/.openclaw/.env` | DNS automation | dash.cloudflare.com → API Tokens |
| `LLM_API_KEY` | `~/.openclaw/.env` | Generic LLM proxy | depends on backing provider |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | `~/.openclaw/.env` + `launchctl setenv` | Telegram bot, Grafana alerts, `lib/notify.sh` | BotFather: send `/revoke`, then `/token` to mint a new one |
| `NTFY_TOPIC_URL` | `~/.openclaw/.env` | ntfy alerts, `lib/notify.sh` | Generate new topic with `openssl rand -hex 6` and update both env + Grafana yaml |
| `SLACK_WEBHOOK_URL` | `~/.openclaw/.env` (placeholder) | Slack alerts (pending) | api.slack.com/apps → app → Incoming Webhooks |
| Gmail app password | `~/.gmail_app_password` (mode 600) | `gmail-send` skill | myaccount.google.com → Security → App passwords |
| Gmail OAuth (`gog` CLI) | gog token store, per-account | gog mail/calendar | `gog auth refresh <account>` |

## Grafana exception (env-var interpolation)

Grafana provisioning files (`config/grafana/provisioning/alerting/*.yaml`)
support `$VAR` interpolation but read env vars from the **Grafana process
environment**, not from `~/.openclaw/.env`. To make secrets available to
Grafana on macOS:

```bash
# Once per token, and again after rotation:
set -a; source ~/.openclaw/.env; set +a
launchctl setenv TELEGRAM_BOT_TOKEN "$TELEGRAM_BOT_TOKEN"
launchctl setenv TELEGRAM_CHAT_ID "$TELEGRAM_CHAT_ID"
brew services restart grafana
```

`launchctl setenv` does not persist across reboots. For permanence, edit
`~/Library/LaunchAgents/homebrew.mxcl.grafana.plist` and add an
`EnvironmentVariables` dict — but the `launchctl setenv` approach is fine
when paired with a Mac that auto-runs `brew services start grafana` at
login.

## Rotation playbooks

### Telegram bot token (P0 — currently in git history)

The bot token `8716932495:…` is visible in past commits of
`openclaw-contact-points.yaml`. Even though current HEAD references a
placeholder, the historic value remains discoverable via `git log -p`.
Rotate as a precaution.

```bash
# 1. In Telegram, message @BotFather:
#      /revoke         → pick the bot, confirm
#      /token          → pick the bot, copy new token
# 2. Update ~/.openclaw/.env in place (replace the line):
sed -i '' "s|^TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=NEW_TOKEN_HERE|" \
  ~/.openclaw/.env
# 3. Re-export for Grafana and restart:
set -a; source ~/.openclaw/.env; set +a
launchctl setenv TELEGRAM_BOT_TOKEN "$TELEGRAM_BOT_TOKEN"
brew services restart grafana
# 4. Smoke-test:
scripts/notify.sh --channel telegram "Telegram rotation test"
```

### Anthropic API key (P0 — was plaintext on local disk only)

The key was duplicated in `config/briefing.env` (gitignored) and
`~/.openclaw/.env`. The briefing.env copy has been removed from HEAD; the
canonical copy in `~/.openclaw/.env` is unchanged. Rotation is **optional**
unless you suspect external exposure (sold/lost Mac, leaked backup,
unexpected Anthropic invoice anomalies).

```bash
# Optional rotation:
# 1. https://console.anthropic.com/settings/keys → revoke old → create new
# 2. Update ~/.openclaw/.env:
sed -i '' "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=sk-ant-NEW|" \
  ~/.openclaw/.env
# 3. Re-source any open shells; cron picks it up on next run.
```

### Brave API key

Stored in **two** places by historical decision: `~/.openclaw/.env` and
the macOS Keychain item `OpenclawBrave`. Both must be updated together.

```bash
# 1. Brave Developer Dashboard → roll the key.
# 2. ~/.openclaw/.env:
sed -i '' "s|^BRAVE_API_KEY=.*|BRAVE_API_KEY=NEW|" ~/.openclaw/.env
# 3. Keychain:
security delete-generic-password -s OpenclawBrave -a openclaw
security add-generic-password   -s OpenclawBrave -a openclaw -w "NEW"
```

## Pre-commit defense

`scripts/secret-scan-hook.sh` (PreToolUse hook on Bash|Write|Edit) blocks
commits that contain Anthropic/Slack/AWS/etc. secret patterns. This is the
last line of defense — primary discipline is to never paste secrets into
files outside `~/.openclaw/.env`. If the hook ever fires on a real
credential, treat it as if the secret has leaked: rotate first, fix the
file second.
