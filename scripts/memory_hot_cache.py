#!/usr/bin/env python3
"""
memory_hot_cache.py — LRU in-process hot tier for the tiered memory system.

Max 50 entries. TTL=30min using time.monotonic(). Thread-safe with threading.Lock.
Stores full Memory objects as dicts.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Dict, Optional

_MAX_SIZE = 50
_TTL_SECONDS = 30 * 60  # 30 minutes


class HotCache:
    """
    LRU in-process cache with TTL expiry.

    Entries are stored as (timestamp, memory_dict) tuples in an OrderedDict.
    The oldest entry (front of OrderedDict) is evicted when the cache is full.
    """

    def __init__(self, max_size: int = _MAX_SIZE, ttl_seconds: float = _TTL_SECONDS):
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._cache: OrderedDict[int, tuple[float, dict]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, memory_id: int) -> Optional[dict]:
        """Return cached memory dict or None if absent/expired."""
        with self._lock:
            if memory_id not in self._cache:
                self._misses += 1
                return None
            ts, mem = self._cache[memory_id]
            if time.monotonic() - ts > self._ttl:
                # Expired — evict
                del self._cache[memory_id]
                self._misses += 1
                return None
            # LRU: move to end (most recently used)
            self._cache.move_to_end(memory_id)
            self._hits += 1
            return mem

    def put(self, memory_dict: dict) -> None:
        """Insert or update a memory dict keyed by its 'id' field."""
        memory_id = memory_dict.get("id")
        if memory_id is None:
            return
        # Keep id as-is (string UUIDs and string keys must match get() calls)
        with self._lock:
            if memory_id in self._cache:
                self._cache.move_to_end(memory_id)
            self._cache[memory_id] = (time.monotonic(), memory_dict)
            # Evict oldest if over capacity
            while len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

    def invalidate(self, memory_id: int) -> None:
        """Remove a specific entry from the cache."""
        with self._lock:
            self._cache.pop(memory_id, None)

    def stats(self) -> dict:
        """Return hit_rate, size, oldest_entry (seconds ago)."""
        with self._lock:
            size = len(self._cache)
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0
            if size > 0:
                now = time.monotonic()
                oldest_ts = next(iter(self._cache.values()))[0]
                oldest_seconds_ago = now - oldest_ts
            else:
                oldest_seconds_ago = None
            return {
                "hit_rate": round(hit_rate, 4),
                "size": size,
                "oldest_entry": oldest_seconds_ago,
                "hits": self._hits,
                "misses": self._misses,
            }

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0


_singleton: Optional["HotCache"] = None


def get_hot_cache() -> "HotCache":
    """Return the process-wide HotCache singleton."""
    global _singleton
    if _singleton is None:
        _singleton = HotCache()
    return _singleton


if __name__ == "__main__":
    # Smoke test
    cache = HotCache(max_size=3, ttl_seconds=60)
    for i in range(4):
        cache.put({"id": i, "title": f"Memory {i}", "content": f"Content {i}"})

    # Oldest (0) should be evicted
    assert cache.get(0) is None, "Oldest entry should have been evicted"
    assert cache.get(1) is not None, "Entry 1 should be present"
    assert cache.get(3) is not None, "Entry 3 should be present"

    s = cache.stats()
    print("Stats:", s)
    assert s["size"] == 2  # 1 and 3, since we moved 1 to end then retrieved 3
    print("HotCache smoke test PASSED")
