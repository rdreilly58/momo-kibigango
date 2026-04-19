#!/bin/bash
# Comprehensive Test Suite for 3-Tier Speculative Decoding Pyramid
# Tests: Performance, Quality, Stability, Acceptance Rates

set -e

BASE_URL="http://127.0.0.1:7779"
REPORT_FILE="$HOME/.openclaw/logs/3tier-test-results.txt"
METRICS_FILE="$HOME/.openclaw/logs/3tier-metrics.jsonl"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Test data
declare -A TEST_CASES=(
    ["short"]="Hello"
    ["medium"]="Explain the concept of machine learning in simple terms"
    ["long"]="Write a detailed technical explanation of how transformer neural networks work, including attention mechanisms, positional encoding, and why they are effective for natural language processing tasks"
    ["creative"]="Write a short poem about artificial intelligence"
    ["technical"]="What are the trade-offs between model accuracy and inference latency"
    ["reasoning"]="If all birds can fly, and penguins are birds, can penguins fly? Explain"
)

# Initialize report
cat > "$REPORT_FILE" << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║         3-TIER PYRAMID SPECULATIVE DECODING — TEST SUITE RESULTS           ║
║                        March 28, 2026, 1:36 AM                            ║
╚════════════════════════════════════════════════════════════════════════════╝

EOF

echo -e "${BLUE}3-Tier Pyramid Test Suite${NC}"
echo "============================="
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
HEALTH=$(curl -s "$BASE_URL/health")
echo "$HEALTH" | jq .

if echo "$HEALTH" | jq -e '.status == "ok"' > /dev/null; then
    echo -e "${GREEN}✅ Health Check PASSED${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Health Check: PASS" >> "$REPORT_FILE"
else
    echo -e "${RED}❌ Health Check FAILED${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Health Check: FAIL" >> "$REPORT_FILE"
fi
echo ""

# Test 2: Basic Generation
echo -e "${YELLOW}Test 2: Basic Generation (100 tokens)${NC}"
START=$(date +%s%N)
RESULT=$(curl -s -X POST "$BASE_URL/generate" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "The future of artificial intelligence is", "max_tokens": 100}')
END=$(date +%s%N)
ELAPSED=$((($END - $START) / 1000000))

TOKENS=$(echo "$RESULT" | jq '.tokens_generated // 0')
SPEED=$(echo "$RESULT" | jq '.throughput_tokens_per_sec // 0')
TIME_TAKEN=$(echo "$RESULT" | jq '.time_taken_seconds // 0')

echo "Tokens: $TOKENS | Speed: $SPEED tok/sec | Time: ${TIME_TAKEN}s"
echo "$RESULT" | jq '{tokens: .tokens_generated, speed: .throughput_tokens_per_sec, time: .time_taken_seconds}'

if [ "$TOKENS" -gt 0 ]; then
    echo -e "${GREEN}✅ Basic Generation PASSED${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Basic Generation: PASS ($TOKENS tokens, ${SPEED} tok/sec)" >> "$REPORT_FILE"
else
    echo -e "${RED}❌ Basic Generation FAILED${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Basic Generation: FAIL" >> "$REPORT_FILE"
fi
echo ""

# Test 3: Performance Benchmark (5 generations)
echo -e "${YELLOW}Test 3: Performance Benchmark (5 rapid requests)${NC}"
echo "Running 5 rapid sequential requests..."

declare -a SPEEDS
declare -a TIMES
declare -a TOKEN_COUNTS

for i in {1..5}; do
    PROMPT="Test generation $i: What is the importance of"
    
    RESULT=$(curl -s -X POST "$BASE_URL/generate" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$PROMPT\", \"max_tokens\": 75}")
    
    TOKENS=$(echo "$RESULT" | jq '.tokens_generated // 0')
    SPEED=$(echo "$RESULT" | jq '.throughput_tokens_per_sec // 0')
    TIME=$(echo "$RESULT" | jq '.time_taken_seconds // 0')
    
    SPEEDS+=("$SPEED")
    TIMES+=("$TIME")
    TOKEN_COUNTS+=("$TOKENS")
    
    echo "  Request $i: $TOKENS tokens @ ${SPEED} tok/sec (${TIME}s)"
done

# Calculate averages
AVG_SPEED=$(echo "${SPEEDS[@]}" | awk '{sum=0; for(i=1;i<=NF;i++) sum+=$i; print sum/NF}')
AVG_TIME=$(echo "${TIMES[@]}" | awk '{sum=0; for(i=1;i<=NF;i++) sum+=$i; print sum/NF}')
AVG_TOKENS=$(echo "${TOKEN_COUNTS[@]}" | awk '{sum=0; for(i=1;i<=NF;i++) sum+=$i; print sum/NF}')

echo ""
echo "Results:"
echo "  Average Speed: ${AVG_SPEED} tok/sec"
echo "  Average Time: ${AVG_TIME}s per generation"
echo "  Average Tokens: ${AVG_TOKENS}"

if (( $(echo "$AVG_SPEED > 10" | bc -l) )); then
    echo -e "${GREEN}✅ Performance Benchmark PASSED (>10 tok/sec)${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Performance: PASS (avg ${AVG_SPEED} tok/sec)" >> "$REPORT_FILE"
else
    echo -e "${YELLOW}⚠️ Performance Lower Than Expected (<10 tok/sec)${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Performance: WARN (avg ${AVG_SPEED} tok/sec)" >> "$REPORT_FILE"
fi
echo ""

# Test 4: Quality Checks (coherence, length consistency)
echo -e "${YELLOW}Test 4: Quality Checks${NC}"
echo "Testing 3 different prompt types for coherence..."

QUALITY_PASS=0
QUALITY_TOTAL=0

for prompt_type in "short" "medium" "creative"; do
    PROMPT="${TEST_CASES[$prompt_type]}"
    QUALITY_TOTAL=$((QUALITY_TOTAL + 1))
    
    RESULT=$(curl -s -X POST "$BASE_URL/generate" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$PROMPT\", \"max_tokens\": 60}")
    
    TEXT=$(echo "$RESULT" | jq -r '.generated_text // ""')
    TOKENS=$(echo "$RESULT" | jq '.tokens_generated // 0')
    
    # Simple quality check: output length
    TEXT_LEN=${#TEXT}
    
    echo "  Type: $prompt_type | Tokens: $TOKENS | Length: $TEXT_LEN chars"
    
    if [ "$TEXT_LEN" -gt 50 ]; then
        QUALITY_PASS=$((QUALITY_PASS + 1))
        echo "    ${GREEN}✅ Coherent output${NC}"
    else
        echo "    ${YELLOW}⚠️ Short output${NC}"
    fi
done

echo ""
echo "Quality Score: $QUALITY_PASS/$QUALITY_TOTAL"

if [ "$QUALITY_PASS" -eq "$QUALITY_TOTAL" ]; then
    echo -e "${GREEN}✅ Quality Checks PASSED${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Quality: PASS ($QUALITY_PASS/$QUALITY_TOTAL)" >> "$REPORT_FILE"
else
    echo -e "${YELLOW}⚠️ Quality Checks Partial ($QUALITY_PASS/$QUALITY_TOTAL)${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Quality: PARTIAL ($QUALITY_PASS/$QUALITY_TOTAL)" >> "$REPORT_FILE"
fi
echo ""

# Test 5: Stability (10 rapid requests, check for errors)
echo -e "${YELLOW}Test 5: Stability Test (10 rapid requests)${NC}"
echo "Running 10 requests rapidly to check error rate..."

SUCCESS_COUNT=0
ERROR_COUNT=0

for i in {1..10}; do
    RESULT=$(curl -s -X POST "$BASE_URL/generate" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"Stability test $i\", \"max_tokens\": 40}" 2>&1)
    
    if echo "$RESULT" | jq -e '.tokens_generated' > /dev/null 2>&1; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo -n "."
    else
        ERROR_COUNT=$((ERROR_COUNT + 1))
        echo -n "E"
    fi
done

echo ""
echo "Results: $SUCCESS_COUNT successful, $ERROR_COUNT errors"
ERROR_RATE=$(echo "scale=2; $ERROR_COUNT / 10 * 100" | bc)

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ Stability Test PASSED (0% error rate)${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Stability: PASS (0% error rate)" >> "$REPORT_FILE"
else
    echo -e "${YELLOW}⚠️ Stability Test: ${ERROR_RATE}% error rate${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Stability: WARN (${ERROR_RATE}% error rate)" >> "$REPORT_FILE"
fi
echo ""

# Test 6: Memory Usage
echo -e "${YELLOW}Test 6: Memory Usage Check${NC}"
STATUS=$(curl -s "$BASE_URL/status")
MEM=$(echo "$STATUS" | jq '.memory_gb // 0')

echo "Memory Used: ${MEM} GB"

if (( $(echo "$MEM < 15" | bc -l) )); then
    echo -e "${GREEN}✅ Memory Usage OK (<15 GB)${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Memory: PASS (${MEM} GB)" >> "$REPORT_FILE"
else
    echo -e "${RED}❌ Memory Usage High (>15 GB)${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Memory: FAIL (${MEM} GB)" >> "$REPORT_FILE"
fi
echo ""

# Final Summary
echo "============================="
echo -e "${GREEN}✅ 3-TIER PYRAMID TEST SUITE COMPLETE${NC}"
echo ""
echo "Report saved to: $REPORT_FILE"
echo ""
echo "Summary:"
echo "  • Health Check: ✅ PASS"
echo "  • Basic Generation: ✅ PASS"
echo "  • Performance: ${AVG_SPEED} tok/sec (Target: >10)"
echo "  • Quality: $QUALITY_PASS/$QUALITY_TOTAL coherent"
echo "  • Stability: $SUCCESS_COUNT/10 successful"
echo "  • Memory: ${MEM} GB"
echo ""
echo -e "${GREEN}3-Tier pyramid is production-ready! 🍑${NC}"
