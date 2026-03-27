#!/bin/bash
# OpenClaw Integration for Speculative Decoding
# Provides convenient wrappers for using speculative-decoding from OpenClaw

set -euo pipefail

ENDPOINT="http://127.0.0.1:7779"
DEPLOY_SCRIPT=~/.openclaw/workspace/scripts/speculative-decoding-deploy.sh

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Generate text using speculative decoding
generate() {
  local prompt="$1"
  local max_tokens="${2:-150}"
  local draft_len="${3:-4}"
  
  # Check if server is running
  if ! curl -s "$ENDPOINT/health" >/dev/null 2>&1; then
    echo -e "${RED}❌ Speculative decoding server not running${NC}"
    echo "Start it with: bash $DEPLOY_SCRIPT start"
    return 1
  fi
  
  # Generate
  echo -e "${BLUE}🤖 Generating with speculative decoding...${NC}"
  
  response=$(curl -s -X POST "$ENDPOINT/generate" \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": \"$prompt\",
      \"max_tokens\": $max_tokens,
      \"draft_len\": $draft_len
    }")
  
  # Extract generated text
  generated=$(echo "$response" | jq -r '.generated_text // .error')
  tokens=$(echo "$response" | jq -r '.tokens_generated // 0')
  time=$(echo "$response" | jq -r '.time_taken_seconds // 0')
  speed=$(echo "$response" | jq -r '.throughput_tokens_per_sec // 0')
  
  # Display results
  echo ""
  echo -e "${GREEN}✅ Generation complete${NC}"
  echo "─────────────────────────────────────────────"
  echo "Output:"
  echo "$generated"
  echo ""
  echo "Stats:"
  echo "  Tokens: $tokens"
  echo "  Time: ${time}s"
  echo "  Speed: ${speed} tok/sec"
  echo ""
}

# Start server
start_server() {
  echo -e "${BLUE}🚀 Starting speculative decoding server...${NC}"
  bash "$DEPLOY_SCRIPT" start
}

# Stop server
stop_server() {
  echo -e "${BLUE}🛑 Stopping speculative decoding server...${NC}"
  bash "$DEPLOY_SCRIPT" stop
}

# Check status
server_status() {
  bash "$DEPLOY_SCRIPT" status
}

# Run test suite
run_tests() {
  echo -e "${BLUE}🧪 Running test suite...${NC}"
  bash ~/.openclaw/workspace/scripts/test-speculative-decoding.sh
}

# Show usage
usage() {
  cat << 'EOF'
OpenClaw Speculative Decoding Integration

USAGE:
  openclaw-spec generate "<prompt>" [max_tokens] [draft_len]
  openclaw-spec start
  openclaw-spec stop
  openclaw-spec status
  openclaw-spec test

EXAMPLES:
  # Simple generation
  openclaw-spec generate "What is machine learning?"
  
  # Longer generation
  openclaw-spec generate "Explain neural networks" 300
  
  # Custom draft length
  openclaw-spec generate "Compare two algorithms" 200 6
  
  # Server management
  openclaw-spec start
  openclaw-spec status
  openclaw-spec stop
  
  # Testing
  openclaw-spec test

DOCUMENTATION:
  ~/.openclaw/workspace/skills/speculative-decoding/SKILL.md
EOF
}

# Main
case "${1:-help}" in
  generate)
    shift
    if [ $# -lt 1 ]; then
      echo "Usage: openclaw-spec generate \"<prompt>\" [max_tokens] [draft_len]"
      exit 1
    fi
    generate "$@"
    ;;
  start)
    start_server
    ;;
  stop)
    stop_server
    ;;
  status)
    server_status
    ;;
  test)
    run_tests
    ;;
  *)
    usage
    exit 1
    ;;
esac
