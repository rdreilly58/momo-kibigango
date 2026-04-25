#!/bin/bash
# Integrate Config 4 Hybrid Decoder into 3-Day Test (March 28-30)

set -e

echo "🍑 Integrating Config 4 into 3-Day Speculative Decoding Test"
echo "=========================================================="
echo ""
echo "Timeline: March 28-30, 2026"
echo "Test: 2-tier baseline → Config 4 hybrid comparison"
echo ""

# Directories
WORKSPACE="$HOME/.openclaw/workspace"
LOGS="$WORKSPACE/.openclaw/logs"
TEST_DIR="$WORKSPACE/3day-test-results"

# Create test directory
mkdir -p "$TEST_DIR"
mkdir -p "$LOGS"

echo "Step 1: Backup current 2-tier metrics"
if [ -f "$LOGS/speculative-metrics.jsonl" ]; then
  cp "$LOGS/speculative-metrics.jsonl" "$TEST_DIR/2tier-metrics-backup.jsonl"
  echo "  ✅ Backed up 2-tier metrics"
else
  echo "  ⚠️ No existing metrics found"
fi

echo ""
echo "Step 2: Prepare Config 4 integration"
echo "  • Hybrid decoder: $WORKSPACE/hybrid_pyramid_decoder.py"
echo "  • Configuration: $WORKSPACE/hybrid_config.json"
echo "  • Tests: $WORKSPACE/test_hybrid_local_only.py"

echo ""
echo "Step 3: Initialize Config 4 logging"
CONFIG4_LOG="$LOGS/config4-metrics.jsonl"
touch "$CONFIG4_LOG"
echo "  ✅ Created: $CONFIG4_LOG"

echo ""
echo "Step 4: Test harness configuration"
cat > "$TEST_DIR/config4-test-plan.json" << 'EOF'
{
  "test_id": "config4-hybrid-3tier",
  "duration_days": 3,
  "start_date": "2026-03-28",
  "end_date": "2026-03-30",
  
  "baseline": {
    "type": "2tier",
    "draft": "Qwen2.5-0.5B",
    "target": "Qwen2.5-3B (equivalent)",
    "startup_seconds": 5,
    "expected_throughput_tokpers": 15.55,
    "expected_quality_pct": 85
  },
  
  "candidate": {
    "type": "3tier-hybrid",
    "draft": "Qwen2.5-0.5B",
    "qualifier": "Phi-2-2.7B",
    "target_api": "Claude-Opus",
    "startup_seconds": 6,
    "expected_throughput_tokpers": 12,
    "expected_quality_pct": 92,
    "expected_acceptance_rate_pct": 70,
    "expected_cost_per_1000": 6
  },
  
  "success_criteria": {
    "startup_acceptable": true,
    "acceptance_rate_pct_min": 65,
    "quality_pct_min": 88,
    "cost_per_1000_max": 10
  },
  
  "metrics_tracked": [
    "startup_time",
    "requests_total",
    "local_accepted_count",
    "api_fallback_count",
    "acceptance_rate_pct",
    "average_latency_ms",
    "quality_score",
    "total_cost_usd"
  ]
}
EOF
echo "  ✅ Created: $TEST_DIR/config4-test-plan.json"

echo ""
echo "Step 5: Integration commands (run separately)"
echo ""
echo "To start Config 4 test:"
echo "  source ~/.openclaw/speculative-env/bin/activate"
echo "  cd $WORKSPACE"
echo "  python3 hybrid_pyramid_decoder.py 2>&1 | tee $CONFIG4_LOG &"
echo ""
echo "To run test suite:"
echo "  python3 test_hybrid_local_only.py"
echo ""
echo "To monitor 3-day test:"
echo "  tail -f $CONFIG4_LOG"
echo ""

echo "Step 6: Integration summary"
echo "=========================================================="
echo ""
echo "Config 4 Hybrid (3-Tier with Opus Fallback) Ready for:"
echo "  ✅ 3-day test integration (March 28-30)"
echo "  ✅ Performance comparison vs 2-tier baseline"
echo "  ✅ Cost tracking ($5-10/month expected)"
echo "  ✅ Quality assessment (92% target)"
echo "  ✅ Metrics collection (logging active)"
echo ""
echo "Test artifacts:"
echo "  • Baseline: $TEST_DIR/2tier-metrics-backup.jsonl"
echo "  • Config 4: $CONFIG4_LOG"
echo "  • Plan: $TEST_DIR/config4-test-plan.json"
echo ""
echo "Expected Results (by March 30):"
echo "  • Local acceptance rate: ~70%"
echo "  • API fallback rate: ~30%"
echo "  • Average quality: 92%"
echo "  • Cost: $5-10 (3-day estimate: $0.15-0.30)"
echo ""
echo "✅ Integration Complete - Ready to start Config 4 test"
echo ""
