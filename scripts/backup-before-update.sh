#!/bin/bash
# Backup Before OpenClaw Update
# Creates complete backup of production system before updating
# Usage: bash backup-before-update.sh [--verify-only]

set -e

BACKUP_BASE="$HOME/.openclaw/backups"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_DIR="$BACKUP_BASE/pre-update-$TIMESTAMP"
VERIFY_ONLY=0

if [ "$1" = "--verify-only" ]; then
  VERIFY_ONLY=1
  echo "VERIFY MODE: Checking backups only (no new backup created)"
  echo ""
fi

mkdir -p "$BACKUP_BASE"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         OpenClaw Pre-Update Backup Procedure                  ║"
echo "║         Creates production snapshot before update             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ $VERIFY_ONLY -eq 0 ]; then
  echo "📂 Creating backup directory: $BACKUP_DIR"
  mkdir -p "$BACKUP_DIR"
  echo ""
  
  # Backup configuration
  echo "💾 Backing up configuration files..."
  mkdir -p "$BACKUP_DIR/config"
  cp ~/.openclaw/openclaw.json "$BACKUP_DIR/config/" 2>/dev/null || true
  cp ~/.openclaw/config.json "$BACKUP_DIR/config/" 2>/dev/null || true
  cp ~/.openclaw/cron/jobs.json "$BACKUP_DIR/config/" 2>/dev/null || true
  cp -r ~/.openclaw/identity "$BACKUP_DIR/config/" 2>/dev/null || true
  echo "  ✅ Configuration backed up"
  echo ""
  
  # Backup workspace
  echo "💾 Backing up workspace (can be large, may take 1-2 min)..."
  mkdir -p "$BACKUP_DIR/workspace"
  # Backup critical files only (not node_modules or large projects)
  cp ~/.openclaw/workspace/SOUL.md "$BACKUP_DIR/workspace/" 2>/dev/null || true
  cp ~/.openclaw/workspace/TOOLS.md "$BACKUP_DIR/workspace/" 2>/dev/null || true
  cp ~/.openclaw/workspace/USER.md "$BACKUP_DIR/workspace/" 2>/dev/null || true
  cp ~/.openclaw/workspace/MEMORY.md "$BACKUP_DIR/workspace/" 2>/dev/null || true
  cp -r ~/.openclaw/workspace/memory "$BACKUP_DIR/workspace/" 2>/dev/null || true
  cp -r ~/.openclaw/workspace/scripts "$BACKUP_DIR/workspace/" 2>/dev/null || true
  cp -r ~/.openclaw/workspace/docs "$BACKUP_DIR/workspace/" 2>/dev/null || true
  echo "  ✅ Workspace backed up"
  echo ""
  
  # Backup cron configuration
  echo "💾 Backing up cron jobs..."
  mkdir -p "$BACKUP_DIR/cron"
  cp ~/.openclaw/cron/jobs.json "$BACKUP_DIR/cron/" 2>/dev/null || true
  echo "  ✅ Cron jobs backed up"
  echo ""
  
  # Create manifest
  echo "📋 Creating backup manifest..."
  cat > "$BACKUP_DIR/MANIFEST.txt" << 'EOF'
OpenClaw Pre-Update Backup
==========================

Contents:
  config/          - OpenClaw configuration files
  config/identity/ - Device identity and auth tokens
  cron/            - Cron job definitions
  workspace/       - Critical workspace files (SOUL.md, TOOLS.md, MEMORY.md, scripts, docs)

To restore after failed update:
  1. Stop gateway: openclaw gateway stop
  2. Restore config: cp -r config/* ~/.openclaw/
  3. Restart: openclaw gateway restart

Location of backups:
  ~/.openclaw/backups/pre-update-YYYYMMDD_HHMMSS/

Size estimation:
  Config: ~5-10 MB
  Workspace: ~50-100 MB  
  Total: ~60-110 MB per backup

Retention policy:
  Keep latest 3 backups
  Delete older than 30 days
  (Can be automated with cleanup script)

Recovery steps in detail:
  1. Identify last good backup: ls -la ~/.openclaw/backups/
  2. Stop current gateway: openclaw gateway stop
  3. Backup current (broken) state: mv ~/.openclaw ~/.openclaw-broken
  4. Restore from good backup: cp -r ~/.openclaw/backups/pre-update-XXX/config/* ~/.openclaw/
  5. Restart gateway: openclaw gateway start
  6. Verify: openclaw gateway status

If full restore needed:
  1. Remove broken: rm -rf ~/.openclaw-broken
  2. Reinstall OpenClaw: brew install openclaw (or specific version)
  3. Restore configuration from backup
  4. Test critical paths (see P2.1_CURRENT_SYSTEM_STATUS.md)
EOF
  
  echo "  ✅ Manifest created"
  echo ""
  
  # Create backup info
  echo "📊 Backup Summary"
  echo "  Directory: $BACKUP_DIR"
  echo "  Timestamp: $TIMESTAMP"
  echo "  Size: $(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
  echo ""
  
  # Verify backup integrity
  echo "✔️  Verifying backup integrity..."
  
  CHECKS=0
  PASSED=0
  
  check_file() {
    local file=$1
    local desc=$2
    ((CHECKS++))
    if [ -f "$file" ]; then
      echo "  ✅ $desc"
      ((PASSED++))
    else
      echo "  ⚠️  $desc (NOT FOUND - optional)"
    fi
  }
  
  check_dir() {
    local dir=$1
    local desc=$2
    ((CHECKS++))
    if [ -d "$dir" ]; then
      echo "  ✅ $desc"
      ((PASSED++))
    else
      echo "  ⚠️  $desc (NOT FOUND - optional)"
    fi
  }
  
  echo ""
  echo "  Critical files:"
  check_file "$BACKUP_DIR/config/openclaw.json" "openclaw.json"
  check_file "$BACKUP_DIR/config/config.json" "config.json"
  check_file "$BACKUP_DIR/cron/jobs.json" "cron/jobs.json"
  
  echo ""
  echo "  Workspace files:"
  check_file "$BACKUP_DIR/workspace/SOUL.md" "SOUL.md"
  check_file "$BACKUP_DIR/workspace/TOOLS.md" "TOOLS.md"
  check_file "$BACKUP_DIR/workspace/MEMORY.md" "MEMORY.md"
  check_dir "$BACKUP_DIR/workspace/scripts" "scripts/"
  
  echo ""
  echo "✅ Backup verification: $PASSED/$CHECKS items present"
  echo ""
  
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║                   BACKUP COMPLETE ✅                          ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Backup ready for update:"
  echo "  Location: $BACKUP_DIR"
  echo "  Size: $(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
  echo ""
  echo "Next: Proceed with 'openclaw update' command"
  echo "If update fails: Use backup with restore procedure (see MANIFEST.txt)"
  echo ""

else
  # Verify mode: check existing backups
  echo "Checking existing backups..."
  echo ""
  
  if [ -d "$BACKUP_BASE" ]; then
    echo "Backups found in $BACKUP_BASE:"
    ls -lh "$BACKUP_BASE" | grep "^d" | tail -5
    echo ""
    
    # Show latest backup
    LATEST=$(ls -t "$BACKUP_BASE" | grep "^pre-update-" | head -1)
    if [ -n "$LATEST" ]; then
      echo "Latest backup:"
      echo "  Directory: $BACKUP_BASE/$LATEST"
      echo "  Size: $(du -sh "$BACKUP_BASE/$LATEST" 2>/dev/null | cut -f1)"
      echo "  Date: $LATEST"
      echo ""
      echo "This backup can be used to restore if needed."
    else
      echo "⚠️  No pre-update backups found!"
      echo "Run: bash backup-before-update.sh"
    fi
  else
    echo "❌ No backups directory found!"
    echo "Run: bash backup-before-update.sh"
  fi
fi
