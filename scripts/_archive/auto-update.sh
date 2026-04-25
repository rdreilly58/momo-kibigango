#!/bin/bash
# OpenClaw Auto-Update Manager
# Safely updates: macOS, Homebrew packages, security patches
# Usage: auto-update.sh [--dry-run] [--approve-all]

set -e

WORKSPACE="$HOME/.openclaw/workspace"
LOG_DIR="$HOME/.openclaw/logs"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Options
DRY_RUN=0
APPROVE_ALL=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=1 ;;
    --approve-all) APPROVE_ALL=1 ;;
  esac
  shift
done

mkdir -p "$LOG_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_update() {
  local status=$1
  local component=$2
  local details=$3
  
  echo "[$TIMESTAMP] $status: $component — $details" >> "$LOG_DIR/updates.log"
}

# Check for macOS updates
check_macos_updates() {
  echo -e "${BLUE}→ Checking macOS updates...${NC}"
  
  local updates=$(softwareupdate -l 2>/dev/null | grep -c "^[[:space:]]*\*" || echo "0")
  
  if [ "$updates" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $updates macOS update(s) available${NC}"
    log_update "AVAILABLE" "macOS" "$updates updates"
    
    if [ $DRY_RUN -eq 0 ]; then
      if [ $APPROVE_ALL -eq 1 ]; then
        echo "Installing macOS updates..."
        sudo softwareupdate -i -a
        log_update "INSTALLED" "macOS" "Updates installed"
      else
        echo -e "${YELLOW}⚠️  Manual approval required. Run: sudo softwareupdate -i -a${NC}"
      fi
    fi
  else
    echo -e "${GREEN}✅ macOS up to date${NC}"
    log_update "OK" "macOS" "No updates"
  fi
}

# Check Homebrew updates
check_brew_updates() {
  echo -e "${BLUE}→ Checking Homebrew updates...${NC}"
  
  if ! command -v brew &> /dev/null; then
    echo "Homebrew not installed"
    return
  fi
  
  # Get outdated packages
  local outdated=$(brew outdated --quiet 2>/dev/null || echo "")
  
  if [ -z "$outdated" ]; then
    echo -e "${GREEN}✅ All Homebrew packages up to date${NC}"
    log_update "OK" "Homebrew" "No updates"
    return
  fi
  
  local count=$(echo "$outdated" | wc -l)
  echo -e "${YELLOW}⚠️  $count Homebrew update(s) available:${NC}"
  echo "$outdated" | head -10
  
  log_update "AVAILABLE" "Homebrew" "$count packages outdated"
  
  if [ $DRY_RUN -eq 0 ]; then
    if [ $APPROVE_ALL -eq 1 ]; then
      echo -e "${BLUE}Updating Homebrew packages...${NC}"
      brew upgrade
      log_update "INSTALLED" "Homebrew" "Packages updated"
      echo -e "${GREEN}✅ Homebrew packages updated${NC}"
    else
      echo -e "${YELLOW}⚠️  Manual approval required. Run: brew upgrade${NC}"
    fi
  fi
}

# Check security patches
check_security_patches() {
  echo -e "${BLUE}→ Checking security patches...${NC}"
  
  # Check for critical security updates
  # macOS includes these in softwareupdate output
  local security=$(softwareupdate -l 2>/dev/null | grep -i "security" | wc -l || echo "0")
  
  if [ "$security" -gt 0 ]; then
    echo -e "${RED}⚠️  $security security update(s) available${NC}"
    log_update "CRITICAL" "Security" "$security critical patches"
    
    if [ $DRY_RUN -eq 0 ] && [ $APPROVE_ALL -eq 1 ]; then
      echo "Installing security patches..."
      sudo softwareupdate -i -a
      log_update "INSTALLED" "Security" "Critical patches installed"
    fi
  else
    echo -e "${GREEN}✅ No critical security patches needed${NC}"
    log_update "OK" "Security" "Current"
  fi
}

# Check OpenClaw updates
check_openclaw_updates() {
  echo -e "${BLUE}→ Checking OpenClaw updates...${NC}"
  
  if ! command -v openclaw &> /dev/null; then
    echo "OpenClaw not installed"
    return
  fi
  
  # Try to get current version
  local current=$(openclaw --version 2>/dev/null | head -1 || echo "unknown")
  echo "OpenClaw version: $current"
  log_update "OK" "OpenClaw" "Version: $current"
  
  # Note: Homebrew auto-updates OpenClaw when `brew upgrade` runs
  echo -e "${BLUE}(Will be updated with Homebrew packages)${NC}"
}

# Verification after updates
verify_updates() {
  echo -e "${BLUE}→ Verifying system health after updates...${NC}"
  
  if [ -f "$WORKSPACE/scripts/system-health-check.sh" ]; then
    bash "$WORKSPACE/scripts/system-health-check.sh" --verbose
    log_update "OK" "Verification" "System health check passed"
  fi
}

# Main execution
main() {
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║              OpenClaw Auto-Update Manager                      ║"
  echo "║              $TIMESTAMP                         ║"
  [ $DRY_RUN -eq 1 ] && echo "║              [DRY RUN MODE]                                     ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  
  if [ $DRY_RUN -eq 1 ]; then
    echo -e "${YELLOW}DRY RUN: No changes will be made${NC}"
    echo ""
  fi
  
  check_macos_updates
  echo ""
  
  check_brew_updates
  echo ""
  
  check_security_patches
  echo ""
  
  check_openclaw_updates
  echo ""
  
  if [ $DRY_RUN -eq 0 ]; then
    verify_updates
    echo ""
  fi
  
  echo -e "${GREEN}✅ Update check complete${NC}"
  echo "Log: $LOG_DIR/updates.log"
}

main "$@"
