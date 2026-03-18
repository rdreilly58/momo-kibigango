#!/bin/bash

# Test speculative decoding with sample queries
# Compares vLLM response vs. expected behavior

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$( dirname "$SCRIPT_DIR" )"

PORT=${1:-8000}
API_URL="http://localhost:$PORT/v1"

echo "=========================================="
echo "🧪 Testing Speculative Decoding"
echo "=========================================="
echo "API URL: $API_URL"
echo ""

# Check if server is running
if ! curl -s "$API_URL/models" > /dev/null 2>&1; then
  echo "❌ Error: vLLM server not responding at $API_URL"
  echo ""
  echo "Start the server with:"
  echo "  ./scripts/start-vlm-server.sh"
  exit 1
fi

echo "✅ Server is running"
echo ""

# Test cases
test_count=0
pass_count=0

# Function to run a test
run_test() {
  local name="$1"
  local prompt="$2"
  local expected_tokens="$3"
  
  test_count=$((test_count + 1))
  
  echo "Test $test_count: $name"
  echo "Prompt: $prompt"
  echo ""
  
  # Make API request
  start_time=$(date +%s%N)
  
  response=$(curl -s -X POST "$API_URL/completions" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"meta-llama/Llama-2-7b-hf\",
      \"prompt\": \"$prompt\",
      \"max_tokens\": $expected_tokens,
      \"temperature\": 0.7,
      \"top_p\": 0.9
    }")
  
  end_time=$(date +%s%N)
  latency_ms=$(( (end_time - start_time) / 1000000 ))
  
  # Extract text and token count
  text=$(echo "$response" | jq -r '.choices[0].text // empty')
  tokens=$(echo "$response" | jq -r '.usage.completion_tokens // 0')
  
  if [ -n "$text" ]; then
    pass_count=$((pass_count + 1))
    echo "✅ PASS"
    echo "Response: ${text:0:100}..."
    echo "Tokens: $tokens, Latency: ${latency_ms}ms"
  else
    echo "❌ FAIL"
    echo "Error: $response"
  fi
  
  echo ""
}

# Run test cases
run_test "Simple greeting" "Hello, how are you?" 50
run_test "Factual question" "What is the capital of France?" 50
run_test "List generation" "List 5 types of fruits:" 100
run_test "Short story" "Once upon a time, there was a" 150

echo "=========================================="
echo "📊 Test Results: $pass_count/$test_count passed"
echo "=========================================="
echo ""

if [ "$pass_count" -eq "$test_count" ]; then
  echo "✅ All tests passed!"
  echo ""
  echo "Next steps:"
  echo "  1. Measure performance (latency, throughput)"
  echo "  2. Compare with Claude API baseline"
  echo "  3. Evaluate quality with longer responses"
  echo "  4. Document findings"
else
  echo "⚠️  Some tests failed"
  echo "Troubleshooting:"
  echo "  - Check vLLM logs: tail -f logs/vlm-server.log"
  echo "  - Verify models are downloaded"
  echo "  - Check GPU memory: nvidia-smi"
fi
