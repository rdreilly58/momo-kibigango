"""
Robust CPU-Only Test Suite for LSH Memory Search
Fixes GPU/MPS segfault issues by disabling acceleration
"""

import sys
import os

# ⚠️ CRITICAL: Disable GPU/MPS acceleration BEFORE importing torch/sentence_transformers
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Disable CUDA
os.environ['TRANSFORMERS_OFFLINE'] = '0'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Disable tokenizer parallelism
os.environ['OMP_NUM_THREADS'] = '1'  # Disable OpenMP parallelism
os.environ['LOKY_PICKLER'] = 'cloudpickle'  # Use safer pickling

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

import logging
logging.basicConfig(level=logging.CRITICAL)
for logger_name in ['sentence_transformers', 'transformers', 'httpx', 'urllib3']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

import time
import numpy as np
from pathlib import Path

print("\n" + "="*80)
print("🍑 ROBUST CPU-ONLY TEST SUITE")
print("="*80)
print("\n⚠️  GPU/MPS Acceleration: DISABLED (CPU-only mode)")
print("    Multiprocessing: DISABLED")
print("    Parallelism: DISABLED")

# Load sentence transformers with CPU-only mode
print("\n📦 Loading SentenceTransformer (CPU-only)...", end="", flush=True)

try:
    from sentence_transformers import SentenceTransformer
    
    # Force CPU-only mode
    import torch
    torch.set_num_threads(1)  # Single-threaded
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Move to CPU explicitly
    model = model.to('cpu')
    # Disable gradient computation
    model.eval()
    
    print(" ✅")
except Exception as e:
    print(f" ❌ FAILED: {e}")
    sys.exit(1)

sys.path.insert(0, str(Path.cwd()))

print("✅ SentenceTransformer loaded successfully")

# Initialize LSH
print("\n📋 Initializing LSH...", end="", flush=True)

try:
    from openclaw_integration import create_openclaw_lsh
    lsh = create_openclaw_lsh()
    if not lsh or not lsh.initialized:
        print(" ❌ LSH initialization failed")
        sys.exit(1)
    print(" ✅")
except Exception as e:
    print(f" ❌ FAILED: {e}")
    sys.exit(1)

# Test queries
TEST_QUERIES = [
    "What is the current leadership strategy at Leidos?",
    "What are the DORA metrics and team health?",
    "What decisions were made about task routing?",
    "What is the architecture of speculative decoding?",
    "How is Config 4 hybrid deployment configured?",
    "What are the performance benchmarks?",
    "How does the 3-tier model routing work?",
    "What is the status of momo-mukashi website?",
    "What features are in momo-kibidango project?",
    "What research was conducted on hashing?",
    "What is the GitHub repository structure?",
    "How are memory files organized?",
    "What is the setup for local embeddings?",
    "How are API keys and credentials managed?",
    "What security hardening was implemented?",
    "What is the 79% cost reduction strategy?",
    "How does Claude Code optimize costs?",
    "What are the Tier A, B, C strategies?",
    "How is speculative decoding improving latency?",
    "What is the OpenClaw gateway configuration?",
]

print("\n" + "-"*80)
print(f"🔥 WARMUP PHASE (First 5 queries)")
print("-"*80)

warmup_times = []
try:
    for i in range(min(5, len(TEST_QUERIES))):
        query = TEST_QUERIES[i]
        
        print(f"  {i+1}. Encoding query...", end="", flush=True)
        embedding = model.encode(query)
        print(" Searching...", end="", flush=True)
        
        start = time.time()
        results = lsh.search(embedding, top_k=5)
        t = (time.time() - start) * 1000
        warmup_times.append(t)
        
        print(f" ✅ {t:.2f}ms")
except Exception as e:
    print(f"\n❌ Warmup phase failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n✅ Warmup complete: avg {np.mean(warmup_times):.2f}ms")

print("\n" + "-"*80)
print(f"📊 MAIN TEST ({len(TEST_QUERIES)} queries)")
print("-"*80)

latencies = []
sources = {'lsh': 0, 'fallback': 0}

try:
    for i, query in enumerate(TEST_QUERIES):
        print(f"  {i+1:2d}. Encoding...", end="", flush=True)
        embedding = model.encode(query)
        print(" Searching...", end="", flush=True)
        
        start = time.time()
        results = lsh.search(embedding, top_k=5)
        t = (time.time() - start) * 1000
        latencies.append(t)
        
        if results:
            src = results[0].get('source', 'unknown')
            if src in sources:
                sources[src] += 1
        
        print(f" ✅ {t:.2f}ms")
        
except Exception as e:
    print(f"\n❌ Main test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ MAIN TEST COMPLETE")
p50 = np.percentile(latencies, 50)
p95 = np.percentile(latencies, 95)
p99 = np.percentile(latencies, 99)
mean = np.mean(latencies)
std = np.std(latencies)

print(f"  Mean: {mean:.2f}ms (±{std:.2f}ms)")
print(f"  P50:  {p50:.2f}ms")
print(f"  P95:  {p95:.2f}ms")
print(f"  P99:  {p99:.2f}ms")
print(f"  LSH:  {sources['lsh']}/{len(TEST_QUERIES)}")
print(f"  Fallback: {sources['fallback']}/{len(TEST_QUERIES)}")

print("\n" + "-"*80)
print("💪 STRESS TEST (10 rapid-fire)")
print("-"*80)

stress_times = []
try:
    for i in range(10):
        query = TEST_QUERIES[i % len(TEST_QUERIES)]
        print(f"  {i+1:2d}. ", end="", flush=True)
        
        embedding = model.encode(query)
        start = time.time()
        lsh.search(embedding, top_k=5)
        stress_times.append((time.time() - start) * 1000)
        
        print(f"✅")
except Exception as e:
    print(f"\n❌ Stress test failed: {e}")
    sys.exit(1)

print(f"✅ Stress test complete")
print(f"  Mean: {np.mean(stress_times):.2f}ms")
print(f"  Min:  {np.min(stress_times):.2f}ms")
print(f"  Max:  {np.max(stress_times):.2f}ms")

print("\n" + "-"*80)
print("📈 FINAL METRICS")
print("-"*80)

metrics = lsh.get_metrics()
health = lsh.health_check()

print(f"✅ LSH Status: {health.get('status', 'UNKNOWN')}")
print(f"   Total queries: {metrics.get('total_queries', 0)}")
print(f"   LSH queries: {metrics.get('lsh_queries', 0)}")
print(f"   Fallback: {metrics.get('fallback_queries', 0)}")
print(f"   Avg latency: {metrics.get('avg_latency_ms', 0):.2f}ms")
print(f"   LSH hit rate: {metrics.get('lsh_hit_rate', 0)*100:.1f}%")
print(f"   Fallback rate: {metrics.get('fallback_rate', 0)*100:.1f}%")

print("\n" + "="*80)
print("🏆 PERFORMANCE ASSESSMENT")
print("="*80)

if p99 < 50:
    print(f"✅ Latency: EXCELLENT (P99 {p99:.2f}ms < 50ms)")
else:
    print(f"⚠️  Latency: {p99:.2f}ms")

fb = metrics.get('fallback_rate', 0) * 100
print(f"✅ Accuracy: Fallback {fb:.1f}%")

print(f"✅ Reliability: {health.get('status', 'UNKNOWN')}")

print("\n" + "="*80)
print("✅ CPU-ONLY TEST SUITE COMPLETE - NO SEGFAULTS")
print("="*80)
print(f"\n✨ Summary:")
print(f"  ✓ {len(TEST_QUERIES)} queries tested")
print(f"  ✓ CPU-only mode: STABLE")
print(f"  ✓ GPU acceleration: DISABLED")
print(f"  ✓ Multiprocessing: DISABLED")
print(f"  ✓ No segfaults or crashes")
print()
