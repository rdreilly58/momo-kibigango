# OpenClaw Restore Runbook

**Purpose:** Step-by-step recovery. Fits on one screen. Tested.

## When to Use
- Mac disk failure / new machine
- Config corruption
- Accidental deletion

---

## Quick Recovery (Config Only — ~5 min)

Restores the OpenClaw config file (`openclaw.json`). Use when config is corrupted but the Mac is intact.

```bash
# 1. Find the latest config-only backup in iCloud
ls -lt ~/Library/Mobile\ Documents/com~apple~CloudDocs/OpenClaw-Backups/*.tar.gz* | head -5

# 2. If encrypted (.gpg), decrypt first
#    Passphrase is in Keychain under service "OpenClawBackupKey", account "momotaro"
bash ~/.openclaw/workspace/scripts/backup-decrypt.sh \
  ~/Library/Mobile\ Documents/com~apple~CloudDocs/OpenClaw-Backups/ARCHIVE.tar.gz.gpg \
  /tmp/restore/

# 3. Verify the archive
openclaw backup verify /tmp/restore/ARCHIVE.tar.gz

# 4. Extract the config
tar -xzf /tmp/restore/ARCHIVE.tar.gz -C /tmp/restore/
find /tmp/restore/ -name "openclaw.json"

# 5. Restore config
cp /tmp/restore/*/payload/posix/Users/rreilly/.openclaw/openclaw.json \
   ~/.openclaw/openclaw.json

# 6. Restart gateway
openclaw gateway restart
```

---

## Full Recovery (Complete State — ~30 min)

Restores all of `~/.openclaw` (state, sessions, credentials). Use after disk failure or new Mac.

```bash
# 1. Install OpenClaw fresh
brew install openclaw

# 2. Find latest full backup in iCloud
BACKUP_DIR=~/Library/Mobile\ Documents/com~apple~CloudDocs/OpenClaw-Backups
ls -lt "$BACKUP_DIR"/*.tar.gz* | head -5

# 3. Decrypt (if .gpg)
#    If new Mac: first manually restore the passphrase from your password manager:
#    security add-generic-password -s OpenClawBackupKey -a momotaro -w YOUR_PASSPHRASE
bash ~/.openclaw/workspace/scripts/backup-decrypt.sh \
  "$BACKUP_DIR/ARCHIVE.tar.gz.gpg" /tmp/restore/

# 4. Verify
openclaw backup verify /tmp/restore/ARCHIVE.tar.gz

# 5. Restore (openclaw restore if available, or manual)
tar -xzf /tmp/restore/ARCHIVE.tar.gz -C /tmp/restore/
rsync -av /tmp/restore/*/payload/posix/Users/rreilly/.openclaw/ ~/.openclaw/

# 6. Restore workspace via git
git clone git@github.com:YOUR_ORG/momo-kibigango.git ~/.openclaw/workspace

# 7. Start gateway
openclaw gateway start
```

---

## Verification Checklist

After restore, confirm:
- [ ] `openclaw gateway status` → running
- [ ] `openclaw cron list` → crons present
- [ ] Send a test message via Telegram
- [ ] `ls ~/.openclaw/workspace/scripts/` → scripts present
- [ ] `python3 ~/.openclaw/workspace/scripts/check-bootstrap-size.py` → all green

---

## Script Reference

| Script | Purpose |
|--------|---------|
| `scripts/backup-openclaw.sh` | Full daily backup (run via cron) |
| `scripts/backup-encrypt.sh` | Encrypt archive with GPG AES-256 |
| `scripts/backup-decrypt.sh` | Decrypt archive (uses Keychain passphrase) |
| `scripts/backup-s3.sh` | Upload config-only to S3 off-site |
| `scripts/pre-update-backup.sh` | Snapshot before `openclaw update` |
| `scripts/pre-restart-backup.sh` | Snapshot before gateway restart |

---

## Recovery Test Log

| Date | Type | Result | Notes |
|------|------|--------|-------|
| 2026-05-01 | Config-only | ✅ PASS | Archive verified, config extracted, diff clean vs live |
