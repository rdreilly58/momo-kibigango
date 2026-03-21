#!/usr/bin/env python3
"""Test search speed with pre-loaded model and index."""

import os
import sys
import time

# Add venv to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/venv/lib/python3.14/site-packages"))

# Suppress warnings
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from memory_search import MemorySearcher

# Create searcher and pre-load everything
print("Pre-loading model and indexing files...")
searcher = MemorySearcher()
searcher.index_memory_files()

# Now test search speed
queries = [
    "password manager",
    "Apple Passwords",
    "1Password",
    "momo-kibidango",
    "Phase 4 production"
]

print("\nTesting search speed (model already loaded):")
print("-" * 50)

total_time = 0
for query in queries:
    start = time.time()
    results = searcher.search(query, top_k=3)
    elapsed = time.time() - start
    total_time += elapsed
    print(f"Query: '{query}' - {elapsed*1000:.1f}ms - Found {len(results)} results")

avg_time = total_time / len(queries)
print("-" * 50)
print(f"Average search time: {avg_time*1000:.1f}ms")
print(f"Total time for {len(queries)} queries: {total_time:.2f}s")

if avg_time < 1.0:
    print("\n✅ Search latency <1 second per query (after initial load)")
else:
    print("\n❌ Search too slow")