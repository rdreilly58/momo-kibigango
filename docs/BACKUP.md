# OpenClaw Backup & Restore

**Version:** 1.0 · **Added:** April 26, 2026 · **Author:** Momotaro (AI Agent)

---

## Overview

OpenClaw Backup provides automated, verified, offsite backup of the full OpenClaw agent state — including memory, configuration, cron jobs, session history, skills, and workspace — to iCloud Drive. A daily cron job runs at 2:30 AM EDT and delivers a Telegram notification on completion or failure.

---

## Structure

```
~/.openclaw/workspace/
├── scripts/
│   ├── backup-openclaw.sh     # Main backup script
│   └── test-backup.sh         # 32-test validation suite
└── docs/
    └── BACKUP.md              # This file

~/Documents/
└── OpenClaw-Backups/          # Local staging (legacy — not used in full-state mode)

~/Library/Mobile Documents/com~apple~CloudDocs/
└── OpenClaw-Backups/          # Primary offsite backup location (iCloud Drive)
    ├── YYYY-MM-DDTHH-MM-SSZ-openclaw-backup.tar.gz   # Full state archives
    └── config-latest.json     # Quick-restore config reference (always current)
```

### What Gets Backed Up

The backup uses `openclaw backup create` — OpenClaw's native backup command — which captures:

| Component | Path | Size |
|-----------|------|------|
| Configuration | `~/.openclaw/openclaw.json` | ~5KB |
| Memory (SQLite + vector index) | `~/.openclaw/memory/` | ~53MB |
| Cron jobs | `~/.openclaw/cron/` | ~1.5MB |
| Agent sessions | `~/.openclaw/agents/` | ~46MB |
| Skills library | `~/.openclaw/skills/` | ~2GB |
| Extensions (plugins) | `~/.openclaw/extensions/` | ~1.3GB |
| Workspace (agent files) | `~/.openclaw/workspace/` | ~5.3GB |
| Telegram state | `~/.openclaw/telegram/` | ~12KB |
| Flows | `~/.openclaw/flows/` | ~96KB |
| **Total** | | **~3GB compressed** |

> **Note:** The workspace (`~/.openclaw/workspace/`) is also independently backed up via Git on GitHub (`rdreilly58/momo-kibigango`). The archive is a complete redundant copy.

### What Is NOT Backed Up

- `~/.openclaw/logs/` — ephemeral, not needed for restore
- `~/.openclaw/plugin-runtime-deps/` — auto-regenerated on gateway start
- `~/.openclaw/browser/` — browser cache, reproducible
- `~/.openclaw/speculative-env/` — Python venv, reproducible
- `~/.openclaw/ga4-env/` — Python venv, reproducible

---

## Theory of Operations

```
┌─────────────────────────────────────────────────────┐
│                  Daily at 2:30 AM EDT                │
│                  (openclaw cron job)                 │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│            backup-openclaw.sh                        │
│                                                      │
│  1. openclaw backup create                           │
│     └── Captures full ~/.openclaw state              │
│     └── Writes timestamped .tar.gz to iCloud         │
│     └── Verifies archive integrity (--verify)        │
│                                                      │
│  2. Updates config-latest.json in iCloud             │
│     └── Fast reference for config-only restores      │
│                                                      │
│  3. Rotates archives older than 7 days               │
│                                                      │
│  4. Sends Telegram notification (success or failure) │
└──────────────────────┬──────────────────────────────┘
                       │
           ┌───────────┴────────────┐
           ▼                        ▼
  ☁️ iCloud Drive              📱 Telegram
  OpenClaw-Backups/            Backup complete ✅
  (syncs to all devices)       or FAILED ⚠️
```

### Archive Format

Archives are created by OpenClaw's native backup system and include:

- A `manifest.json` at the archive root describing all included paths
- All content from `~/.openclaw/` (state directory)
- Workspace directories discovered from the active config
- Timestamped filename: `YYYY-MM-DDTHH-MM-SSZ-openclaw-backup.tar.gz`
- Verified with `openclaw backup verify` immediately after creation

### iCloud Sync

iCloud Drive handles offsite replication automatically. The `OpenClaw-Backups/` folder syncs to:
- Bob's iPhone (via iCloud)
- Bob's iPad Pro (via iCloud)
- Any other Apple devices on the same iCloud account

No additional configuration is needed — iCloud handles sync, versioning, and availability.

---

## Usage

### Run a Manual Backup

```bash
# Full backup (recommended)
bash ~/.openclaw/workspace/scripts/backup-openclaw.sh

# With Telegram notification
bash ~/.openclaw/workspace/scripts/backup-openclaw.sh --notify

# Dry run (see what would happen, no files written)
bash ~/.openclaw/workspace/scripts/backup-openclaw.sh --dry-run
```

### Verify an Archive

```bash
# Verify the latest iCloud archive
ICLOUD="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Backups"
LATEST=$(ls -t "$ICLOUD"/*.tar.gz | head -1)
openclaw backup verify "$LATEST"
```

### List Available Backups

```bash
ICLOUD="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Backups"
ls -lh "$ICLOUD"/*.tar.gz | sort -r
```

### Restore from Backup

```bash
# Step 1: Stop the gateway
openclaw gateway stop

# Step 2: Verify archive integrity
ARCHIVE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Backups/YYYY-MM-DDTHH-MM-SSZ-openclaw-backup.tar.gz"
openclaw backup verify "$ARCHIVE"

# Step 3: Extract to a staging directory
mkdir -p ~/openclaw-restore-staging
tar -xzf "$ARCHIVE" -C ~/openclaw-restore-staging

# Step 4: Review and restore selectively (or full restore)
# WARNING: Full restore overwrites current state
rsync -av ~/openclaw-restore-staging/.openclaw/ ~/.openclaw/

# Step 5: Restart the gateway
openclaw gateway start

# Step 6: Verify
openclaw status
```

> ⚠️ **Always verify the archive before restoring.** Use `openclaw backup verify` first.

### Config-Only Restore (Fast)

When only the configuration needs restoring (e.g., after accidental config corruption):

```bash
ICLOUD="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Backups"
cp "$ICLOUD/config-latest.json" ~/.openclaw/openclaw.json
openclaw gateway restart
```

---

## Cron Schedule

| Property | Value |
|----------|-------|
| Job name | `daily-backup` |
| Schedule | `30 2 * * *` (2:30 AM EDT daily) |
| Timezone | `America/New_York` |
| Session | Isolated (no main session context loaded) |
| Delivery | Telegram announcement on completion |
| Model | `anthropic/claude-haiku-4-5` |

**View cron status:**
```bash
openclaw cron list | grep backup
```

---

## Rotation Policy

| Location | Retention |
|----------|-----------|
| iCloud Drive | 7 days |

Archives older than 7 days are automatically deleted from iCloud during each backup run. At 3GB per archive and 7 archives retained, maximum iCloud usage is ~21GB (of 271GB available).

---

## Test Suite

A 32-test validation suite is included:

```bash
bash ~/.openclaw/workspace/scripts/test-backup.sh
```

**Test coverage:**

| Section | Tests |
|---------|-------|
| Script integrity (exists, executable, key patterns) | 6 |
| Dry run (exits 0, correct output) | 4 |
| iCloud directory + active sync confirmation | 3 |
| Archive existence, age, size validation | 4 |
| Archive integrity (tar + openclaw verify) | 3 |
| config-latest.json validity + freshness | 3 |
| Cron schedule, isolation, delivery | 4 |
| Rotation TTL + find/delete pattern | 2 |
| Restore readiness (commands + key paths) | 2 |
| Gateway health post-backup | 1 |
| **Total** | **32** |

**Last run:** April 26, 2026 — 32/32 passing ✅

---

## Monitoring & Alerts

**Success:** Telegram message — `✅ OpenClaw Full Backup Complete` with archive name, size, and iCloud copy count.

**Failure:** Telegram message — `⚠️ OpenClaw Backup FAILED` with error detail. Gateway continues running — backup failure does not affect agent operation.

**Manual health check:**
```bash
# Check recent backup logs
cat /tmp/openclaw-backup-last.log

# Check iCloud contents
ls -lh "$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Backups/"
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/backup-openclaw.sh` | Main backup script |
| `scripts/test-backup.sh` | 32-test validation suite |
| `docs/BACKUP.md` | This documentation |
| `iCloud/OpenClaw-Backups/*.tar.gz` | Full state archives |
| `iCloud/OpenClaw-Backups/config-latest.json` | Quick restore config reference |

---

## Limitations & Known Issues

- **Archive size ~3GB** — backup takes ~6 minutes. Plan for this in cron window.
- **iCloud only** — no secondary offsite (S3, Backblaze). Acceptable given iCloud's 99.9% uptime.
- **No incremental backup** — each run is a full snapshot. Deduplication handled by iCloud's block-level storage.
- **Secrets in archive** — the archive contains API keys and tokens (stored in `openclaw.json` and agent profiles). The archive is protected by iCloud encryption and macOS file permissions (`chmod 600`).

---

## Future Improvements

- [ ] Add S3 as secondary offsite destination
- [ ] Incremental/delta backups for faster daily runs
- [ ] Add `test-backup.sh` to CI pipeline
- [ ] Restore dry-run mode (`--dry-run` for restore)
- [ ] Encrypt archive with GPG before upload

---

*Documentation maintained by Momotaro 🍑 · Last updated April 26, 2026*
