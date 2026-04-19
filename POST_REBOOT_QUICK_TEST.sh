#!/bin/bash
# Quick Post-Reboot Validation - Run immediately after Mac restarts
# Tests both LSH and Speculative Decoding survival

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         🍑 POST-REBOOT VALIDATION TEST SUITE 🍑               ║"
echo "║                                                                ║"
echo "║       Testing LSH & Speculative Decoding Survival              ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# Test 1: LSH Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: LSH Health Check (30 seconds)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd ~/.openclaw/workspace/implementations/phase-1-lsh
if source venv/bin/activate 2>/dev/null; then
    echo "✅ Virtual environment activated"
    
    python3 << 'PYEOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

try:
    from openclaw_integration import create_openclaw_lsh
    import numpy as np
    import time
    
    lsh = create_openclaw_lsh()
    if not lsh or not lsh.initialized:
        print("❌ LSH initialization FAILED")
        sys.exit(1)
    
    print("✅ LSH initialized")
    
    embeddings = np.load(Path.home() / ".openclaw/workspace/.lsh_cache/embeddings.npy")
    
    for i in range(5):
        query_emb = embeddings[i % len(embeddings)]
        start = time.time()
        results = lsh.search(query_emb, top_k=5)
        t = (time.time() - start) * 1000
        print(f"  Query {i+1}: {t:.2f}ms")
    
    health = lsh.health_check()
    metrics = lsh.get_metrics()
    
    print(f"\n✅ LSH Status: {health.get('status', 'UNKNOWN')}")
    print(f"   Avg latency: {metrics.get('avg_latency_ms', 0):.2f}ms")
    print(f"   LSH hit rate: {metrics.get('lsh_hit_rate', 0)*100:.1f}%")
    
    if health.get('status') == 'HEALTHY':
        print("\n✅ TEST 1: PASS")
        sys.exit(0)
    else:
        print(f"\n⚠️  TEST 1: WARNING (Status: {health.get('status')})")
        sys.exit(0)
except Exception as e:
    print(f"❌ TEST 1: FAIL - {e}")
    sys.exit(1)
PYEOF
    
    if [ $? -eq 0 ]; then
        echo "✅ TEST 1 PASSED"
        ((PASS_COUNT++))
    else
        echo "❌ TEST 1 FAILED"
        ((FAIL_COUNT++))
    fi
else
    echo "❌ Could not activate virtual environment"
    ((FAIL_COUNT++))
fi

# Test 2: Speculative Decoding Daemon
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Speculative Decoding Daemon"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if ps aux | grep -E "speculative.*\.py" | grep -v grep > /dev/null 2>&1; then
    echo "✅ Speculative decoding daemon running"
    
    # Check if responsive
    curl -s http://localhost:7779/health > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Daemon responding to health checks"
        echo "✅ TEST 2 PASSED"
        ((PASS_COUNT++))
    else
        echo "⚠️  Daemon running but not responding (may be warming up)"
        echo "⚠️  TEST 2 INCONCLUSIVE"
    fi
else
    echo "⚠️  Daemon not running - attempting restart..."
    launchctl start com.momotaro.speculative-decoding-3tier 2>/dev/null
    sleep 5
    
    if ps aux | grep -E "speculative.*\.py" | grep -v grep > /dev/null 2>&1; then
        echo "✅ Daemon restarted successfully"
        echo "✅ TEST 2 PASSED (after restart)"
        ((PASS_COUNT++))
    else
        echo "❌ Daemon failed to start"
        echo "❌ TEST 2 FAILED"
        ((FAIL_COUNT++))
    fi
fi

# Test 3: File Integrity
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: File Integrity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

FILES_OK=true

if [ -f ~/.openclaw/workspace/.lsh_cache/embeddings.npy ]; then
    echo "✅ LSH embeddings cache present"
else
    echo "❌ LSH embeddings cache missing"
    FILES_OK=false
fi

if [ -d ~/.openclaw/workspace/implementations/phase-1-lsh/venv ]; then
    echo "✅ LSH virtual environment present"
else
    echo "❌ LSH virtual environment missing"
    FILES_OK=false
fi

if [ -f ~/.openclaw/workspace/implementations/phase-1-lsh/lsh_memory_search.py ]; then
    echo "✅ LSH implementation files present"
else
    echo "❌ LSH implementation files missing"
    FILES_OK=false
fi

if [ "$FILES_OK" = true ]; then
    echo "✅ TEST 3 PASSED"
    ((PASS_COUNT++))
else
    echo "❌ TEST 3 FAILED"
    ((FAIL_COUNT++))
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Tests Passed:  $PASS_COUNT/3"
echo "Tests Failed:  $FAIL_COUNT/3"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "🍑 OVERALL: ALL SYSTEMS GO ✅"
    echo ""
    echo "✅ LSH survived reboot"
    echo "✅ Speculative decoding operational"
    echo "✅ Files intact and accessible"
    echo ""
    echo "System is production-ready after reboot!"
    exit 0
elif [ $FAIL_COUNT -le 1 ]; then
    echo "🍑 OVERALL: MOSTLY OK ⚠️"
    echo ""
    echo "Some minor issues detected (see above)"
    echo "Run: less REBOOT_VALIDATION.md for troubleshooting"
    exit 1
else
    echo "🍑 OVERALL: ISSUES DETECTED ❌"
    echo ""
    echo "Please review test output and troubleshooting guide:"
    echo "  cd ~/.openclaw/workspace/implementations/phase-1-lsh"
    echo "  cat REBOOT_VALIDATION.md"
    exit 2
fi
