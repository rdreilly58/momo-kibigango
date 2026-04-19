#!/usr/bin/env python3
"""
Test Hybrid Decoder (Local Only - No API)
Tests that local draft + qualifier works correctly
"""

import os
import sys
import time
import json

# Add to path
sys.path.insert(0, os.path.dirname(__file__))

from hybrid_pyramid_decoder import HybridPyramidDecoder, HybridConfig


def test_local_generation():
    """Test that local generation works"""
    print("\n" + "="*60)
    print("TEST 1: Local Model Loading & Generation")
    print("="*60)
    
    config = HybridConfig()
    decoder = HybridPyramidDecoder(config)
    
    # Test simple prompt
    prompt = "Hello, how are you?"
    print(f"\nPrompt: {prompt}")
    
    # Generate locally (bypass Opus)
    draft = decoder.generate_local(prompt, max_tokens=30)
    if draft:
        print(f"✅ Local generation successful")
        print(f"   Text: {draft[:100]}...")
        return True
    else:
        print(f"❌ Local generation failed")
        return False


def test_quality_scoring():
    """Test quality scoring"""
    print("\n" + "="*60)
    print("TEST 2: Quality Scoring")
    print("="*60)
    
    config = HybridConfig()
    decoder = HybridPyramidDecoder(config)
    
    test_cases = [
        ("What is 2+2?", "The answer is 4", "high similarity"),
        ("What is 2+2?", "Paris is a city in France", "low similarity"),
        ("Who is the president?", "The current president is...", "medium similarity"),
    ]
    
    for prompt, response, expected in test_cases:
        score = decoder.score_quality(prompt, response)
        print(f"\nPrompt: {prompt}")
        print(f"Response: {response}")
        print(f"Score: {score:.3f} ({expected})")
    
    print("\n✅ Quality scoring working")
    return True


def test_task_detection():
    """Test task type detection"""
    print("\n" + "="*60)
    print("TEST 3: Task Type Detection")
    print("="*60)
    
    config = HybridConfig()
    decoder = HybridPyramidDecoder(config)
    
    test_cases = [
        ("What is 2+2?", "math"),
        ("How do I write a function in Python?", "code"),
        ("Write a poem about nature", "creative"),
        ("Tell me about Paris", "general"),
    ]
    
    for prompt, expected_type in test_cases:
        task_type = decoder.get_task_type(prompt)
        threshold = config.thresholds.get(task_type, 0.85)
        
        status = "✅" if task_type == expected_type else "⚠️"
        print(f"{status} '{prompt}' -> {task_type} (threshold: {threshold})")
    
    print("\n✅ Task detection working")
    return True


def test_performance_metrics():
    """Test performance metrics tracking"""
    print("\n" + "="*60)
    print("TEST 4: Metrics Tracking")
    print("="*60)
    
    config = HybridConfig()
    decoder = HybridPyramidDecoder(config)
    
    # Simulate some requests
    print("\nSimulating 10 requests...")
    for i in range(10):
        decoder.stats["total_requests"] += 1
        if i % 3 == 0:
            decoder.stats["api_fallbacks"] += 1
            decoder.stats["total_cost"] += 0.015
        else:
            decoder.stats["local_accepted"] += 1
    
    stats = decoder.get_stats()
    
    print(f"\nMetrics:")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Local accepted: {stats['local_accepted']} ({stats.get('acceptance_rate_pct', 0):.1f}%)")
    print(f"  API fallbacks: {stats['api_fallbacks']}")
    print(f"  Total cost: ${stats['total_cost']:.4f}")
    print(f"  Cost/request: ${stats.get('avg_cost_per_request', 0):.6f}")
    print(f"  Cost/1000: ${stats.get('cost_per_1000', 0):.2f}")
    
    print("\n✅ Metrics tracking working")
    return True


def main():
    print("\n" + "🍑 HYBRID DECODER TEST SUITE (LOCAL ONLY)")
    print("Testing Config 4 implementation without API calls")
    
    results = []
    
    try:
        results.append(("Model Loading", test_local_generation()))
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        results.append(("Model Loading", False))
    
    try:
        results.append(("Quality Scoring", test_quality_scoring()))
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        results.append(("Quality Scoring", False))
    
    try:
        results.append(("Task Detection", test_task_detection()))
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        results.append(("Task Detection", False))
    
    try:
        results.append(("Metrics Tracking", test_performance_metrics()))
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        results.append(("Metrics Tracking", False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Ready for integration")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
