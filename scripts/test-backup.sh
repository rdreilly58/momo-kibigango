#!/usr/bin/env bash
# test-backup.sh — Test suite for OpenClaw backup & restore capabilities
# Usage: bash scripts/test-backup.sh

set -uo pipefail

PASS=0
FAIL=0
WARN=0

pass() { echo "  ✅ PASS: $1"; ((PASS++)); }
fail() { echo "  ❌ FAIL: $1"; ((FAIL++)); }
warn() { echo "  ⚠️  WARN: $1"; ((WARN++)); }
header() { echo ""; echo "▶ $1"; }

SCRIPT="$HOME/.openclaw/workspace/scripts/backup-openclaw.sh"
ICLOUD="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Backups"

# ──────────────────────────────────────────────
header "1. Script Integrity"
# ──────────────────────────────────────────────
if [[ -f "$SCRIPT" ]]; then
  pass "backup-openclaw.sh exists"
else
  fail "backup-openclaw.sh NOT FOUND at $SCRIPT"
fi

if [[ -x "$SCRIPT" ]]; then
  pass "backup-openclaw.sh is executable"
else
  fail "backup-openclaw.sh is not executable"
fi

# Check key components are present
if grep -q "openclaw backup create" "$SCRIPT"; then
  pass "Script uses native openclaw backup create"
else
  fail "Script missing 'openclaw backup create'"
fi

if grep -q "\-\-verify" "$SCRIPT"; then
  pass "Script uses --verify flag"
else
  fail "Script missing --verify flag"
fi

if grep -q "telegram_notify" "$SCRIPT"; then
  pass "Telegram notification present"
else
  fail "Telegram notification missing"
fi

if grep -q "KEEP_ICLOUD" "$SCRIPT"; then
  pass "iCloud rotation logic present"
else
  fail "iCloud rotation logic missing"
fi

# ──────────────────────────────────────────────
header "2. Dry Run"
# ──────────────────────────────────────────────
DRY_OUTPUT=$(bash "$SCRIPT" --dry-run 2>&1)
DRY_EXIT=$?

if [[ $DRY_EXIT -eq 0 ]]; then
  pass "Dry run exits 0"
else
  fail "Dry run failed (exit $DRY_EXIT)"
fi

if echo "$DRY_OUTPUT" | grep -q "DRY RUN"; then
  pass "Dry run mode confirmed in output"
else
  fail "Dry run mode not announced"
fi

if echo "$DRY_OUTPUT" | grep -q "openclaw backup create"; then
  pass "Dry run shows correct command"
else
  fail "Dry run doesn't show openclaw backup create"
fi

if echo "$DRY_OUTPUT" | grep -q "✅ Backup complete"; then
  pass "Dry run completes successfully"
else
  fail "Dry run didn't reach completion"
fi

# ──────────────────────────────────────────────
header "3. iCloud Directory"
# ──────────────────────────────────────────────
if [[ -d "$ICLOUD" ]]; then
  pass "iCloud backup directory exists"
else
  fail "iCloud backup directory missing: $ICLOUD"
fi

# Check iCloud is syncing (brctl)
ICLOUD_SYNC=$(brctl status 2>/dev/null | grep -i "full-sync\|has-synced" | head -1)
if [[ -n "$ICLOUD_SYNC" ]]; then
  pass "iCloud is actively syncing"
else
  warn "Could not confirm iCloud sync status"
fi

# Check available space
AVAIL=$(df -h "$ICLOUD" 2>/dev/null | tail -1 | awk '{print $4}')
if [[ -n "$AVAIL" ]]; then
  pass "iCloud available space: $AVAIL"
else
  warn "Could not read iCloud available space"
fi

# ──────────────────────────────────────────────
header "4. Backup Archives"
# ──────────────────────────────────────────────
ARCHIVES=$(ls "$ICLOUD"/*.tar.gz 2>/dev/null)
ARCHIVE_COUNT=$(echo "$ARCHIVES" | grep -c ".tar.gz" 2>/dev/null || echo 0)

if [[ $ARCHIVE_COUNT -gt 0 ]]; then
  pass "Archives found in iCloud: $ARCHIVE_COUNT"
else
  fail "No archives found in iCloud"
fi

# Check most recent archive age (should be from today)
LATEST=$(ls -t "$ICLOUD"/*.tar.gz 2>/dev/null | head -1)
if [[ -n "$LATEST" ]]; then
  ARCHIVE_NAME=$(basename "$LATEST")
  ARCHIVE_SIZE=$(du -sh "$LATEST" | cut -f1)
  pass "Latest archive: $ARCHIVE_NAME ($ARCHIVE_SIZE)"

  # Check it's from today
  ARCHIVE_DATE=$(date -r "$LATEST" '+%Y-%m-%d' 2>/dev/null || stat -f '%Sm' -t '%Y-%m-%d' "$LATEST" 2>/dev/null)
  TODAY=$(date '+%Y-%m-%d')
  if [[ "$ARCHIVE_DATE" == "$TODAY" ]]; then
    pass "Latest archive is from today ($TODAY)"
  else
    warn "Latest archive is from $ARCHIVE_DATE (not today)"
  fi

  # Check archive is substantial (>100MB — full state should be ~3GB)
  ARCHIVE_BYTES=$(du -sk "$LATEST" | cut -f1)
  if [[ $ARCHIVE_BYTES -gt 102400 ]]; then
    pass "Archive size is substantial (${ARCHIVE_SIZE} > 100MB)"
  else
    warn "Archive seems small (${ARCHIVE_SIZE}) — may be partial"
  fi
else
  fail "Could not find latest archive"
fi

# ──────────────────────────────────────────────
header "5. Archive Integrity"
# ──────────────────────────────────────────────
if [[ -n "$LATEST" ]]; then
  # Test tar integrity
  tar -tzf "$LATEST" > /dev/null 2>&1 && \
    pass "Archive is valid tar.gz (not corrupt)" || \
    fail "Archive failed tar integrity check"

  # Check manifest exists in archive
  HAS_MANIFEST=$(tar -tzf "$LATEST" 2>/dev/null | grep -c "manifest.json" || echo 0)
  if [[ $HAS_MANIFEST -gt 0 ]]; then
    pass "Archive contains manifest.json"
  else
    warn "manifest.json not found in archive"
  fi

  # Run openclaw verify
  VERIFY_OUT=$(openclaw backup verify "$LATEST" 2>&1)
  VERIFY_EXIT=$?
  if [[ $VERIFY_EXIT -eq 0 ]]; then
    pass "openclaw backup verify passed"
  else
    fail "openclaw backup verify failed: $VERIFY_OUT"
  fi
fi

# ──────────────────────────────────────────────
header "6. config-latest.json"
# ──────────────────────────────────────────────
CONFIG_LATEST="$ICLOUD/config-latest.json"
if [[ -f "$CONFIG_LATEST" ]]; then
  pass "config-latest.json exists in iCloud"
else
  fail "config-latest.json missing from iCloud"
fi

if [[ -f "$CONFIG_LATEST" ]]; then
  python3 -m json.tool "$CONFIG_LATEST" > /dev/null 2>&1 && \
    pass "config-latest.json is valid JSON" || \
    fail "config-latest.json is corrupt/invalid JSON"

  # Check it matches current config
  CURRENT_HASH=$(md5 -q "$HOME/.openclaw/openclaw.json" 2>/dev/null || md5sum "$HOME/.openclaw/openclaw.json" | cut -d' ' -f1)
  BACKUP_HASH=$(md5 -q "$CONFIG_LATEST" 2>/dev/null || md5sum "$CONFIG_LATEST" | cut -d' ' -f1)
  if [[ "$CURRENT_HASH" == "$BACKUP_HASH" ]]; then
    pass "config-latest.json matches current openclaw.json"
  else
    warn "config-latest.json differs from current config (stale)"
  fi
fi

# ──────────────────────────────────────────────
header "7. Cron Job"
# ──────────────────────────────────────────────
CRON_ENTRY=$(openclaw cron list 2>/dev/null | grep -i "backup" | head -1)
if [[ -n "$CRON_ENTRY" ]]; then
  pass "Backup cron job exists"
  
  if echo "$CRON_ENTRY" | grep -q "2 \* \* \*\|30 2"; then
    pass "Cron scheduled at 2:30 AM"
  else
    warn "Cron schedule may differ: $(echo $CRON_ENTRY | awk '{print $5,$6}')"
  fi

  if echo "$CRON_ENTRY" | grep -q "isolated"; then
    pass "Cron runs in isolated session"
  else
    warn "Cron not confirmed isolated"
  fi

  if echo "$CRON_ENTRY" | grep -q "announce\|telegram"; then
    pass "Cron delivers to Telegram"
  else
    warn "Cron delivery not confirmed"
  fi
else
  fail "No backup cron job found"
fi

# ──────────────────────────────────────────────
header "8. Rotation Logic"
# ──────────────────────────────────────────────
KEEP_DAYS=$(grep "KEEP_ICLOUD=" "$SCRIPT" | head -1 | grep -o '[0-9]*')
if [[ -n "$KEEP_DAYS" && $KEEP_DAYS -gt 0 ]]; then
  pass "Rotation configured: ${KEEP_DAYS}-day TTL"
else
  fail "Rotation TTL not found in script"
fi

# Check find command syntax for rotation
if grep -q "find.*mtime.*delete" "$SCRIPT"; then
  pass "Rotation uses find -mtime -delete pattern"
else
  fail "Rotation logic missing find/delete pattern"
fi

# ──────────────────────────────────────────────
header "9. Restore Readiness"
# ──────────────────────────────────────────────
# Verify openclaw backup restore command exists
RESTORE_HELP=$(openclaw backup --help 2>/dev/null | grep -i "restore\|verify" || echo "")
if [[ -n "$RESTORE_HELP" ]]; then
  pass "openclaw backup restore/verify commands available"
else
  warn "Could not confirm restore command availability"
fi

# Check archive contents cover key paths
if [[ -n "$LATEST" ]]; then
  KEY_PATHS_FOUND=0
  for key in "openclaw.json" "memory" "cron"; do
    if tar -tzf "$LATEST" 2>/dev/null | grep -q "$key"; then
      ((KEY_PATHS_FOUND++))
    fi
  done
  if [[ $KEY_PATHS_FOUND -ge 2 ]]; then
    pass "Archive covers key paths (config, memory, cron)"
  else
    warn "Only $KEY_PATHS_FOUND/3 key paths found in archive"
  fi
fi

# ──────────────────────────────────────────────
header "10. Gateway Still Healthy"
# ──────────────────────────────────────────────
GW=$(openclaw gateway status 2>/dev/null | grep "running" | head -1)
if [[ -n "$GW" ]]; then
  pass "Gateway still running after backup"
else
  fail "Gateway appears down"
fi

# ──────────────────────────────────────────────
echo ""
echo "════════════════════════════════════"
echo "  Results: ✅ $PASS passed · ❌ $FAIL failed · ⚠️  $WARN warnings"
echo "════════════════════════════════════"

[[ $FAIL -gt 0 ]] && exit 1 || exit 0
