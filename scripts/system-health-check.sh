#!/bin/bash
# OpenClaw System Health Check
# Monitors critical systems and alerts on failures
# Usage: system-health-check.sh [--verbose] [--telegram]

set -e

WORKSPACE="$HOME/.openclaw/workspace"
SCRIPT_DIR="$WORKSPACE/scripts"
LOG_DIR="$HOME/.openclaw/logs"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Options
VERBOSE=0
SEND_TELEGRAM=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose) VERBOSE=1 ;;
    --telegram) SEND_TELEGRAM=1 ;;
  esac
  shift
done

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Report function
report() {
  local status=$1
  local service=$2
  local message=$3
  
  local timestamp=$(date '+%H:%M:%S')
  local color=""
  local symbol=""
  
  case $status in
    OK)
      color=$GREEN
      symbol="✅"
      ;;
    WARN)
      color=$YELLOW
      symbol="⚠️"
      ;;
    ERROR)
      color=$RED
      symbol="❌"
      ;;
  esac
  
  if [ $VERBOSE -eq 1 ]; then
    echo -e "${color}${symbol} [$timestamp] $service: $message${NC}"
  fi
  
  echo "[$timestamp] $status: $service — $message" >> "$LOG_DIR/health-check.log"
}

# Check Gateway connectivity
check_gateway() {
  if curl -s http://localhost:8080/health >/dev/null 2>&1; then
    report "OK" "OpenClaw Gateway" "Running (port 8080)"
    return 0
  else
    report "ERROR" "OpenClaw Gateway" "Not responding on port 8080"
    return 1
  fi
}

# Check Git repository
check_git() {
  if [ -d "$WORKSPACE/.git" ]; then
    local status=$(cd "$WORKSPACE" && git status --short 2>/dev/null || echo "unknown")
    if [ -z "$status" ]; then
      report "OK" "Git Repository" "Clean"
    else
      report "WARN" "Git Repository" "Uncommitted changes detected"
    fi
    return 0
  else
    report "ERROR" "Git Repository" "Not initialized"
    return 1
  fi
}

# Check API Keys
check_api_keys() {
  local missing=0
  
  # Check BRAVE_API_KEY
  if [ -z "$BRAVE_API_KEY" ]; then
    report "WARN" "API Keys" "BRAVE_API_KEY not set in environment"
    missing=$((missing + 1))
  else
    report "OK" "API Keys" "BRAVE_API_KEY loaded"
  fi
  
  # Check if ~/.openclaw/config.json exists
  if [ ! -f ~/.openclaw/config.json ]; then
    report "WARN" "Config" "~/.openclaw/config.json not found"
  else
    report "OK" "Config" "~/.openclaw/config.json present"
  fi
  
  return $missing
}

# Check memory files
check_memory_files() {
  local missing=0
  
  for file in SOUL.md USER.md MEMORY.CORE.md; do
    if [ ! -f "$WORKSPACE/$file" ]; then
      report "ERROR" "Memory Files" "$file missing"
      missing=$((missing + 1))
    fi
  done
  
  if [ -d "$WORKSPACE/memory" ]; then
    local count=$(find "$WORKSPACE/memory" -name "*.md" 2>/dev/null | wc -l)
    report "OK" "Memory Files" "$count daily logs"
  else
    report "WARN" "Memory Files" "memory/ directory not found"
  fi
  
  return $missing
}

# Check disk space
check_disk_space() {
  local usage=$(df "$WORKSPACE" | awk 'NR==2 {print $5}' | sed 's/%//')
  
  if [ "$usage" -gt 90 ]; then
    report "ERROR" "Disk Space" "Critical: $usage% used"
    return 1
  elif [ "$usage" -gt 75 ]; then
    report "WARN" "Disk Space" "Warning: $usage% used"
    return 0
  else
    report "OK" "Disk Space" "$usage% used"
    return 0
  fi
}

# Check Python environment
check_python() {
  if [ ! -d "$WORKSPACE/venv" ]; then
    report "WARN" "Python Env" "Virtual environment not found"
    return 1
  fi
  
  if [ -f "$WORKSPACE/venv/bin/python3" ]; then
    local version=$("$WORKSPACE/venv/bin/python3" --version 2>&1)
    report "OK" "Python Env" "$version"
    return 0
  else
    report "ERROR" "Python Env" "python3 not found in venv"
    return 1
  fi
}

# Check cron jobs
check_cron() {
  local count=$(crontab -l 2>/dev/null | grep -c "^[^#]" || echo "0")
  report "OK" "Cron Jobs" "$count active entries"
  return 0
}

# Check launchd services
check_launchd() {
  local count=$(ls -1 ~/Library/LaunchAgents/ 2>/dev/null | wc -l)
  local active=$(launchctl list 2>/dev/null | grep -c "openclaw\|momotaro" || echo "0")
  report "OK" "LaunchD Services" "$count agents, $active active"
  return 0
}

# GPU Health (if configured)
check_gpu() {
  if [ -f "$SCRIPT_DIR/gpu-health-check-quick.sh" ]; then
    if bash "$SCRIPT_DIR/gpu-health-check-quick.sh" >/dev/null 2>&1; then
      report "OK" "GPU Health" "Quick check passed"
    else
      report "WARN" "GPU Health" "Quick check failed (may be unavailable)"
    fi
  fi
  return 0
}

# Send Telegram alert (if enabled and errors found)
send_telegram_alert() {
  if [ $SEND_TELEGRAM -eq 0 ]; then
    return
  fi
  
  # Count errors from log
  local error_count=$(grep -c "ERROR:" "$LOG_DIR/health-check.log" 2>/dev/null || echo "0")
  
  if [ "$error_count" -gt 0 ]; then
    # Implementation would go here to send to Telegram
    # For now, just indicate it would be sent
    echo "Would send Telegram alert: $error_count errors detected"
  fi
}

# Main execution
main() {
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║              OpenClaw System Health Check                      ║"
  echo "║              $TIMESTAMP                         ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  
  local errors=0
  
  # Run all checks
  check_gateway || errors=$((errors + 1))
  check_git || true
  check_api_keys || true
  check_memory_files || errors=$((errors + 1))
  check_disk_space || true
  check_python || true
  check_cron || true
  check_launchd || true
  check_gpu || true
  
  echo ""
  if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ System Health: GOOD${NC}"
  else
    echo -e "${RED}❌ System Health: $errors ERRORS${NC}"
    send_telegram_alert
  fi
  
  echo ""
  echo "Log: $LOG_DIR/health-check.log"
}

main "$@"
