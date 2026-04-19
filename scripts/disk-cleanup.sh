#!/bin/bash
# OpenClaw Disk Cleanup
# Removes unnecessary files to free disk space
# Usage: disk-cleanup.sh [--dry-run] [--aggressive]

set -e

WORKSPACE="$HOME/.openclaw/workspace"
LOG_DIR="$HOME/.openclaw/logs"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Options
DRY_RUN=0
AGGRESSIVE=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=1 ;;
    --aggressive) AGGRESSIVE=1 ;;
  esac
  shift
done

mkdir -p "$LOG_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              OpenClaw Disk Cleanup                            ║"
echo "║              $TIMESTAMP                         ║"
[ $DRY_RUN -eq 1 ] && echo "║              [DRY RUN MODE]                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

total_freed=0

# 1. Remove node_modules (can be reinstalled with npm install)
cleanup_node_modules() {
  echo -e "${YELLOW}→ Checking node_modules...${NC}"
  
  local size_before=$(du -sh "$WORKSPACE" 2>/dev/null | awk '{print $1}')
  local modules=$(find "$WORKSPACE" -name "node_modules" -type d 2>/dev/null | wc -l)
  
  if [ "$modules" -gt 0 ]; then
    echo "Found $modules node_modules directories (~2 GB)"
    
    if [ $DRY_RUN -eq 0 ]; then
      find "$WORKSPACE" -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
      echo -e "${GREEN}✅ Deleted node_modules${NC}"
      local size_after=$(du -sh "$WORKSPACE" 2>/dev/null | awk '{print $1}')
      echo "   Before: $size_before → After: $size_after"
    else
      echo "   Would delete: ~2 GB (node_modules)"
    fi
  fi
}

# 2. Remove screenshot files
cleanup_screenshots() {
  echo -e "${YELLOW}→ Checking screenshots...${NC}"
  
  local count=$(find "$WORKSPACE" -name "*.png" -o -name "*.jpg" 2>/dev/null | wc -l)
  
  if [ "$count" -gt 0 ]; then
    local size=$(find "$WORKSPACE" \( -name "*.png" -o -name "*.jpg" \) -exec du -ch {} + 2>/dev/null | tail -1 | awk '{print $1}')
    echo "Found $count screenshots (~$size)"
    
    if [ $DRY_RUN -eq 0 ]; then
      find "$WORKSPACE" \( -name "*.png" -o -name "*.jpg" \) -delete 2>/dev/null || true
      echo -e "${GREEN}✅ Deleted screenshots${NC}"
    else
      echo "   Would delete: ~$size (screenshots)"
    fi
  fi
}

# 3. Remove .DS_Store files
cleanup_ds_store() {
  echo -e "${YELLOW}→ Checking .DS_Store files...${NC}"
  
  local count=$(find "$WORKSPACE" -name ".DS_Store" 2>/dev/null | wc -l)
  
  if [ "$count" -gt 0 ]; then
    echo "Found $count .DS_Store files"
    
    if [ $DRY_RUN -eq 0 ]; then
      find "$WORKSPACE" -name ".DS_Store" -delete 2>/dev/null || true
      echo -e "${GREEN}✅ Deleted .DS_Store files${NC}"
    else
      echo "   Would delete: $count .DS_Store files"
    fi
  fi
}

# 4. Clean old logs (if aggressive)
cleanup_old_logs() {
  if [ $AGGRESSIVE -eq 0 ]; then
    return
  fi
  
  echo -e "${YELLOW}→ Checking old logs (aggressive mode)...${NC}"
  
  local count=$(find "$LOG_DIR" -name "*.log.*" 2>/dev/null | wc -l)
  
  if [ "$count" -gt 0 ]; then
    echo "Found $count archived log files"
    
    if [ $DRY_RUN -eq 0 ]; then
      find "$LOG_DIR" -name "*.log.*" -delete 2>/dev/null || true
      echo -e "${GREEN}✅ Deleted archived logs${NC}"
    else
      echo "   Would delete: $count archived logs"
    fi
  fi
}

# 5. Clean git objects (if aggressive)
cleanup_git_objects() {
  if [ $AGGRESSIVE -eq 0 ]; then
    return
  fi
  
  echo -e "${YELLOW}→ Cleaning git objects (aggressive mode)...${NC}"
  
  if [ $DRY_RUN -eq 0 ]; then
    cd "$WORKSPACE"
    git gc --aggressive 2>/dev/null || true
    echo -e "${GREEN}✅ Git garbage collection complete${NC}"
  else
    echo "   Would run: git gc --aggressive"
  fi
}

# Main execution
main() {
  cleanup_node_modules
  echo ""
  
  cleanup_screenshots
  echo ""
  
  cleanup_ds_store
  echo ""
  
  if [ $AGGRESSIVE -eq 1 ]; then
    cleanup_old_logs
    echo ""
    
    cleanup_git_objects
    echo ""
  fi
  
  # Final status
  local final=$(df "$WORKSPACE" | awk 'NR==2 {print $5}' | sed 's/%//')
  
  echo -e "${GREEN}✅ Disk cleanup complete${NC}"
  echo "Disk usage: ${final}%"
  
  if [ "$final" -lt 75 ]; then
    echo -e "${GREEN}✅ Disk space healthy${NC}"
  elif [ "$final" -lt 90 ]; then
    echo -e "${YELLOW}⚠️  Still over 75%, consider --aggressive mode${NC}"
  else
    echo -e "${RED}❌ Still critical, run with --aggressive${NC}"
  fi
}

main "$@"
