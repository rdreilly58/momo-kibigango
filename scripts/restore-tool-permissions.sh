#!/bin/bash
# Restore Tool Permissions After Update
# Recovers tool allowlist from backup or manual configuration
# Usage: bash restore-tool-permissions.sh [--dry-run]

set -e

DRY_RUN=0
if [ "$1" = "--dry-run" ]; then
  DRY_RUN=1
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       Restore Tool Permissions After OpenClaw Update          ║"
echo "║       Recovers critical tool allowlist from backup             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ $DRY_RUN -eq 1 ]; then
  echo "DRY RUN MODE - No changes will be made"
  echo ""
fi

# Function to restore from backup
restore_from_backup() {
  local backup_dir=$1
  
  if [ ! -d "$backup_dir" ]; then
    return 1
  fi
  
  echo "📂 Found backup: $backup_dir"
  
  if [ ! -f "$backup_dir/config/config.json" ]; then
    echo "  ⚠️  config.json not in backup"
    return 1
  fi
  
  echo "  Restoring from backup..."
  
  if [ $DRY_RUN -eq 0 ]; then
    cp "$backup_dir/config/config.json" ~/.openclaw/config.json
    echo "  ✅ config.json restored"
  else
    echo "  [DRY RUN] Would restore config.json"
  fi
  
  if [ -f "$backup_dir/config/openclaw.json" ]; then
    if [ $DRY_RUN -eq 0 ]; then
      cp "$backup_dir/config/openclaw.json" ~/.openclaw/openclaw.json
      echo "  ✅ openclaw.json restored"
    else
      echo "  [DRY RUN] Would restore openclaw.json"
    fi
  fi
  
  return 0
}

# Step 1: Try to restore from latest backup
echo "Step 1: Looking for recent backups..."
echo ""

BACKUP_DIR=$(ls -td ~/.openclaw/backups/pre-update-* 2>/dev/null | head -1)

if [ -n "$BACKUP_DIR" ]; then
  echo "Found latest backup: $BACKUP_DIR"
  echo ""
  
  if restore_from_backup "$BACKUP_DIR"; then
    echo ""
    echo "Step 2: Restarting gateway..."
    
    if [ $DRY_RUN -eq 0 ]; then
      openclaw gateway restart
      sleep 2
      echo "  ✅ Gateway restarted"
    else
      echo "  [DRY RUN] Would restart gateway"
    fi
    
    echo ""
    echo "Step 3: Verifying tools..."
    
    if [ $DRY_RUN -eq 0 ]; then
      bash ~/.openclaw/workspace/scripts/verify-tools-post-update.sh
    else
      echo "  [DRY RUN] Would verify tools"
    fi
    
    exit 0
  fi
fi

# Step 2: Manual restoration if no backup available
echo "⚠️  No backup found or restore failed"
echo ""
echo "Attempting manual restoration..."
echo ""

if [ $DRY_RUN -eq 0 ]; then
  # Create/restore tool configuration
  echo "Creating tool allowlist in config.json..."
  
  # Check if config.json exists
  if [ ! -f ~/.openclaw/config.json ]; then
    echo "  ❌ ~/.openclaw/config.json not found"
    echo "     Cannot restore without existing config file"
    exit 1
  fi
  
  # Backup current config
  cp ~/.openclaw/config.json ~/.openclaw/config.json.broken-$(date +%s)
  
  # Read current file and restore tools section
  python3 << 'PYTHON_SCRIPT'
import json

config_file = "/Users/rreilly/.openclaw/config.json"

try:
  with open(config_file, 'r') as f:
    config = json.load(f)
  
  # Ensure tools section exists
  if 'tools' not in config:
    config['tools'] = {}
  
  # Restore allowed tools
  config['tools']['profile'] = 'full'
  config['tools']['allow'] = [
    'exec',
    'read',
    'write',
    'edit',
    'process',
    'web_search',
    'web_fetch',
    'image',
    'cron',
    'sessions_spawn',
    'sessions_yield',
    'sessions_send',
    'sessions_history',
    'sessions_list',
    'memory_search',
    'memory_get'
  ]
  
  # Write back
  with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)
  
  print("  ✅ Tool allowlist restored in config.json")
  
except Exception as e:
  print(f"  ❌ Error: {e}")
  exit(1)
PYTHON_SCRIPT
  
  echo ""
  echo "Restoring gateway.nodes.denyCommands..."
  
  # Update denied commands in openclaw.json
  python3 << 'PYTHON_SCRIPT'
import json

gw_file = "/Users/rreilly/.openclaw/openclaw.json"

try:
  with open(gw_file, 'r') as f:
    config = json.load(f)
  
  # Ensure gateway.nodes exists
  if 'gateway' not in config:
    config['gateway'] = {}
  if 'nodes' not in config['gateway']:
    config['gateway']['nodes'] = {}
  
  # Restore denied commands
  config['gateway']['nodes']['denyCommands'] = [
    'camera.snap',
    'camera.clip',
    'screen.record',
    'contacts.add',
    'calendar.add',
    'reminders.add',
    'sms.send'
  ]
  
  # Write back
  with open(gw_file, 'w') as f:
    json.dump(config, f, indent=2)
  
  print("  ✅ Security denyCommands restored in openclaw.json")
  
except Exception as e:
  print(f"  ❌ Error: {e}")
  exit(1)
PYTHON_SCRIPT
  
  echo ""
  echo "Restarting gateway..."
  openclaw gateway restart
  sleep 2
  echo "  ✅ Gateway restarted"
  
  echo ""
  echo "Verifying tools..."
  bash ~/.openclaw/workspace/scripts/verify-tools-post-update.sh
  
else
  echo "[DRY RUN] Would restore tool configurations manually"
fi
