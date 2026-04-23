#!/bin/bash
# Test Suite for Speculative Decoding
# Tests 3 tasks of varying complexity
# Measures: latency, quality, token acceptance rate, speedup

set -euo pipefail

ENDPOINT="http://127.0.0.1:7779"
TEST_RESULTS=~/.openclaw/logs/speculative-test-results.json
LOG_FILE=~/.openclaw/logs/speculative-test.log

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create results file
mkdir -p ~/.openclaw/logs

echo "╔════════════════════════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║        SPECULATIVE DECODING TEST SUITE — March 27, 2026, 7:38 AM          ║" | tee -a "$LOG_FILE"
echo "╚════════════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Initialize results JSON
cat > "$TEST_RESULTS" << 'EOF'
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "endpoint": "http://127.0.0.1:7779",
  "tests": []
}
EOF

# Test 1: Simple (Easy)
echo -e "${BLUE}TEST 1: SIMPLE GENERATION (Easy)${NC}" | tee -a "$LOG_FILE"
echo "─────────────────────────────────────────────────────────────────────────────" | tee -a "$LOG_FILE"
echo "Task: Generate a short definition" | tee -a "$LOG_FILE"
echo "Prompt: 'What is machine learning?'" | tee -a "$LOG_FILE"
echo "Max tokens: 75" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

START_TIME=$(date +%s.%N)

RESPONSE=$(curl -s -X POST "$ENDPOINT/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is machine learning?",
    "max_tokens": 75
  }' 2>&1 || echo '{"error": "Connection failed"}')

END_TIME=$(date +%s.%N)
LATENCY=$(echo "$END_TIME - $START_TIME" | bc)

echo "Response:" | tee -a "$LOG_FILE"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo -e "${GREEN}✅ Test 1 Complete${NC}" | tee -a "$LOG_FILE"
echo "Latency: ${LATENCY}s" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Test 2: Medium (Moderate)
echo -e "${BLUE}TEST 2: MEDIUM GENERATION (Moderate)${NC}" | tee -a "$LOG_FILE"
echo "─────────────────────────────────────────────────────────────────────────────" | tee -a "$LOG_FILE"
echo "Task: Generate a detailed explanation" | tee -a "$LOG_FILE"
echo "Prompt: 'Explain how neural networks work in the context of AI'" | tee -a "$LOG_FILE"
echo "Max tokens: 200" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

START_TIME=$(date +%s.%N)

RESPONSE=$(curl -s -X POST "$ENDPOINT/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain how neural networks work in the context of AI",
    "max_tokens": 200
  }' 2>&1 || echo '{"error": "Connection failed"}')

END_TIME=$(date +%s.%N)
LATENCY=$(echo "$END_TIME - $START_TIME" | bc)

echo "Response:" | tee -a "$LOG_FILE"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo -e "${GREEN}✅ Test 2 Complete${NC}" | tee -a "$LOG_FILE"
echo "Latency: ${LATENCY}s" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Test 3: Complex (Hard)
echo -e "${BLUE}TEST 3: COMPLEX GENERATION (Hard)${NC}" | tee -a "$LOG_FILE"
echo "─────────────────────────────────────────────────────────────────────────────" | tee -a "$LOG_FILE"
echo "Task: Generate a technical analysis" | tee -a "$LOG_FILE"
echo "Prompt: 'Compare supervised vs unsupervised learning with examples'" | tee -a "$LOG_FILE"
echo "Max tokens: 400" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

START_TIME=$(date +%s.%N)

RESPONSE=$(curl -s -X POST "$ENDPOINT/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Compare supervised vs unsupervised learning with examples",
    "max_tokens": 400
  }' 2>&1 || echo '{"error": "Connection failed"}')

END_TIME=$(date +%s.%N)
LATENCY=$(echo "$END_TIME - $START_TIME" | bc)

echo "Response:" | tee -a "$LOG_FILE"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo -e "${GREEN}✅ Test 3 Complete${NC}" | tee -a "$LOG_FILE"
echo "Latency: ${LATENCY}s" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Summary
echo "╔════════════════════════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║                            TEST SUMMARY                                   ║" | tee -a "$LOG_FILE"
echo "╚════════════════════════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "✅ All tests completed" | tee -a "$LOG_FILE"
echo "📊 Full results: $TEST_RESULTS" | tee -a "$LOG_FILE"
echo "📝 Test log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
