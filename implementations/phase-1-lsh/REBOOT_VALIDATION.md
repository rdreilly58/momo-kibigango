# Post-Reboot Validation Guide

**Purpose:** Verify LSH and Speculative Decoding survive M4 Mac reboot  
**Date Created:** March 29, 2026 - 4:26 AM EDT  
**Status:** Ready for testing after reboot

---

## Pre-Reboot Checklist

✅ Phase 1 LSH implementation: COMPLETE
✅ Segfault fix deployed: COMPLETE
✅ Test suites created: COMPLETE
✅ Git commits saved: COMPLETE

---

## Post-Reboot Validation Tests

### Test 1: LSH Health Check (Quick - 30 seconds)

**Purpose:** Verify LSH still works and reaches HEALTHY status

**Command:**
```bash
cd ~/.openclaw/workspace/implementations/phase-1-lsh
source venv/bin/activate
python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from openclaw_integration import create_openclaw_lsh
import numpy as np

print("\n" + "="*60)
print("🍑 POST-REBOOT: LSH HEALTH CHECK")
print("="*60)

lsh = create_openclaw_lsh()
if not lsh or not lsh.initialized:
    print("❌ LSH initialization FAILED")
    sys.exit(1)

print(f"✅ LSH initialized")

# Quick 5-query test
embeddings = np.load(Path.home() / ".openclaw/workspace/.lsh_cache/embeddings.npy")
import time

for i in range(5):
    query_emb = embeddings[i % len(embeddings)]
    start = time.time()
    results = lsh.search(query_emb, top_k=5)
    t = (time.time() - start) * 1000
    print(f"  Query {i+1}: {t:.2f}ms")

health = lsh.health_check()
metrics = lsh.get_metrics()

print(f"\n✅ LSH Status: {health.get('status', 'UNKNOWN')}")
print(f"   Total queries: {metrics.get('total_queries', 0)}")
print(f"   Avg latency: {metrics.get('avg_latency_ms', 0):.2f}ms")
print(f"   LSH hit rate: {metrics.get('lsh_hit_rate', 0)*100:.1f}%")

if health.get('status') == 'HEALTHY':
    print("\n✅ LSH HEALTHY - REBOOT SURVIVAL: PASS")
    sys.exit(0)
else:
    print(f"\n⚠️  LSH Status: {health.get('status', 'UNKNOWN')}")
    sys.exit(1)
EOF
```

**Expected Output:**
- 5 queries executed successfully
- Status: HEALTHY
- Latencies: 0.1-0.3ms range

---

### Test 2: CPU-Only Test Suite (Medium - 2 minutes)

**Purpose:** Full validation with CPU-only mode (no GPU issues)

**Command:**
```bash
cd ~/.openclaw/workspace/implementations/phase-1-lsh
source venv/bin/activate
python test_robust_cpu_only.py
```

**Expected Output:**
- 20 queries completed
- Zero segfaults
- Health status: HEALTHY
- Mean latency: 0.15-0.20ms

**What to look for:**
- ✅ No SIGSEGV errors
- ✅ No semaphore warnings
- ✅ All queries succeed
- ✅ Performance metrics stable

---

### Test 3: Speculative Decoding Check (Medium - 2 minutes)

**Purpose:** Verify speculative decoding daemon survived reboot

**Command:**
```bash
cd ~/.openclaw/workspace && \
ps aux | grep -i speculative | grep -v grep && \
echo "✅ Speculative decoding daemon running" || \
echo "⚠️  Daemon not running - checking if it needs restart"
```

**If daemon running:**
- ✅ Should see: `python /path/to/speculative_2model_minimal.py`
- Test continues to latency check

**If daemon NOT running:**
```bash
# Check launchctl status
launchctl list | grep speculative

# If not in list, restart it
launchctl start com.momotaro.speculative-decoding-3tier
sleep 5

# Verify
ps aux | grep -i speculative
```

**Then run latency test:**
```bash
cd ~/.openclaw/workspace/momo-kibidango/src && \
python test_speculative_live_3day.sh 2>/dev/null || \
python3 << 'EOF'
import time
import numpy as np

print("\n" + "="*60)
print("🍑 POST-REBOOT: SPECULATIVE DECODING CHECK")
print("="*60)

# Try to connect to Flask daemon on localhost:7779
try:
    import requests
    health_response = requests.get('http://localhost:7779/health', timeout=2)
    if health_response.status_code == 200:
        print("✅ Speculative decoding daemon responding")
        print(f"   Status: {health_response.json()}")
    else:
        print(f"⚠️  Daemon returned status {health_response.status_code}")
except Exception as e:
    print(f"⚠️  Could not connect to daemon: {e}")
    print("   Try: launchctl start com.momotaro.speculative-decoding-3tier")
EOF
```

---

### Test 4: Comprehensive Integration Test (Long - 5 minutes)

**Purpose:** Full end-to-end validation

**Command:**
```bash
cat << 'BASHEOF' > /tmp/post_reboot_validation.sh
#!/bin/bash

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🍑 POST-REBOOT COMPREHENSIVE VALIDATION"
echo "════════════════════════════════════════════════════════════"

# Test 1: LSH
echo ""
echo "TEST 1: LSH Health Check..."
cd ~/.openclaw/workspace/implementations/phase-1-lsh
source venv/bin/activate
python3 test_robust_cpu_only.py 2>&1 | tail -30 | grep -E "(HEALTHY|EXCELLENT|PASS|ERROR)"

if [ $? -eq 0 ]; then
    echo "✅ Test 1: PASS"
else
    echo "❌ Test 1: FAIL"
fi

# Test 2: Speculative Decoding
echo ""
echo "TEST 2: Speculative Decoding Daemon..."
ps aux | grep speculative_2model | grep -v grep > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Daemon running"
    curl -s http://localhost:7779/health > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Test 2: PASS"
    else
        echo "⚠️  Daemon running but not responding"
    fi
else
    echo "⚠️  Daemon not running - attempt restart..."
    launchctl start com.momotaro.speculative-decoding-3tier
    sleep 3
    ps aux | grep speculative_2model | grep -v grep > /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Daemon restarted"
        echo "✅ Test 2: PASS (after restart)"
    else
        echo "❌ Test 2: FAIL (daemon won't start)"
    fi
fi

# Test 3: File Integrity
echo ""
echo "TEST 3: File Integrity..."
if [ -f ~/.openclaw/workspace/.lsh_cache/embeddings.npy ]; then
    echo "✅ LSH cache files intact"
    echo "✅ Test 3: PASS"
else
    echo "❌ LSH cache files missing"
    echo "❌ Test 3: FAIL"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ POST-REBOOT VALIDATION COMPLETE"
echo "════════════════════════════════════════════════════════════"
BASHEOF

chmod +x /tmp/post_reboot_validation.sh
/tmp/post_reboot_validation.sh
```

---

## What to Check After Reboot

### Critical Files (must exist)

✅ LSH Implementation:
```
~/.openclaw/workspace/implementations/phase-1-lsh/
  ├── lsh_memory_search.py (350 lines)
  ├── openclaw_integration.py (200 lines)
  ├── test_robust_cpu_only.py (7 KB)
  ├── .lsh_cache/
  │   ├── embeddings.npy (17 embeddings)
  │   ├── chunk_ids.json
  │   └── chunk_contents.json
  └── venv/ (virtual environment)
```

✅ Speculative Decoding:
```
~/.openclaw/workspace/momo-kibidango/src/
  ├── speculative_2model_minimal.py
  ├── speculative_3model.py
  └── test files
```

✅ LaunchAgents:
```
~/Library/LaunchAgents/
  ├── com.momotaro.speculative-decoding.plist
  └── com.momotaro.speculative-decoding-3tier.plist
```

### Environment Check

```bash
# Verify Python/venv
~/.openclaw/workspace/implementations/phase-1-lsh/venv/bin/python --version
# Expected: Python 3.14.3 (or similar)

# Verify packages
source ~/.openclaw/workspace/implementations/phase-1-lsh/venv/bin/activate
python -c "import faiss; import numpy; print('✅ Packages OK')"

# Verify git history
cd ~/.openclaw/workspace/implementations/phase-1-lsh
git log --oneline -5
# Expected: Recent commits including segfault fix
```

---

## Success Criteria

### LSH Survival
- [ ] LSH initializes without errors
- [ ] Cache files load correctly
- [ ] 5 test queries execute in <1ms each
- [ ] Health status: HEALTHY
- [ ] No segfaults

### Speculative Decoding Survival
- [ ] Daemon process still running (or restarts cleanly)
- [ ] Responds to health checks
- [ ] Flask server on localhost:7779
- [ ] Can generate tokens

### File Integrity
- [ ] All implementation files present
- [ ] Cache files uncorrupted
- [ ] Git history intact
- [ ] LaunchAgent plists valid

---

## Failure Troubleshooting

### If LSH fails:
```bash
# Rebuild venv
cd ~/.openclaw/workspace/implementations/phase-1-lsh
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install faiss-cpu numpy sentence-transformers

# Re-cache embeddings
cd ~/.openclaw/workspace && python3 << 'EOF'
import json, numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['OMP_NUM_THREADS'] = '1'

model = SentenceTransformer('all-MiniLM-L6-v2').to('cpu').eval()
with open(Path.home() / ".openclaw/workspace/MEMORY.md") as f:
    content = f.read()

sections = content.split('\n## ')[:17]
embeddings = model.encode([s[:1000] for s in sections])
np.save('.lsh_cache/embeddings.npy', embeddings.astype(np.float32))
print("✅ Cache rebuilt")
EOF
```

### If Speculative Decoding fails:
```bash
# Check daemon status
launchctl list | grep speculative

# Restart
launchctl stop com.momotaro.speculative-decoding-3tier
sleep 2
launchctl start com.momotaro.speculative-decoding-3tier
sleep 3

# Verify
ps aux | grep speculative
curl http://localhost:7779/health
```

### If cache files missing:
```bash
# Restore from MEMORY.md
cd ~/.openclaw/workspace/implementations/phase-1-lsh
source venv/bin/activate
python deploy_to_openclaw.sh
```

---

## What to Report Back

After reboot, please provide:

1. **LSH Health Check**
   - Command executed: `python3 test_robust_cpu_only.py`
   - Output: Last 30 lines
   - Status: PASS/FAIL

2. **Speculative Decoding Status**
   - Daemon running: YES/NO
   - Health check response: (curl output)
   - Status: PASS/FAIL

3. **File Integrity**
   - All files present: YES/NO
   - Cache valid: YES/NO
   - Status: PASS/FAIL

4. **Any errors or warnings:**
   - Segfaults: YES/NO
   - Resource warnings: YES/NO
   - Startup issues: YES/NO

---

## Expected Results

✅ **All should PASS:**
- LSH: HEALTHY status, 0.15-0.20ms latency
- Speculative Decoding: Daemon running, responding
- Files: All intact, no corruption
- No segfaults or warnings

---

**Ready for reboot validation!** 🍑

After reboot, run the tests and report results. I'll help troubleshoot any issues.
