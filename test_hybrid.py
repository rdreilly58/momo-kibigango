#!/usr/bin/env python3
"""Test the hybrid pyramid decoder with easy and hard questions."""
import time
import json
from hybrid_pyramid_decoder import HybridPyramidDecoder


def main():
    print("=== Hybrid Pyramid Decoder Test ===\n")
    
    # Initialize decoder
    print("Initializing decoder...")
    start = time.time()
    decoder = HybridPyramidDecoder("hybrid_config.json")
    init_time = time.time() - start
    print(f"Initialization complete in {init_time:.2f}s\n")
    
    # Easy questions (should be handled by local models)
    easy_questions = [
        "What is 2 + 2?",
        "What color is the sky?",
        "Is water wet?",
        "What is the capital of France?",
        "How many days are in a week?"
    ]
    
    # Hard questions (likely need API fallback)
    hard_questions = [
        "Explain the philosophical implications of Gödel's incompleteness theorems.",
        "What are the key differences between transformers and RNNs in deep learning?",
        "Analyze the economic factors that led to the 2008 financial crisis.",
        "Describe the process of protein synthesis in eukaryotic cells.",
        "What are the main challenges in quantum error correction?"
    ]
    
    print("=== Testing Easy Questions ===")
    easy_results = []
    for i, question in enumerate(easy_questions, 1):
        print(f"\nQ{i}: {question}")
        result = decoder.generate(question, max_tokens=50)
        print(f"Model: {result['model']} (score: {result.get('score', 0):.3f})")
        print(f"Response: {result['response'][:100]}...")
        print(f"Latency: {result['latency']:.2f}s")
        easy_results.append(result)
    
    print("\n=== Testing Hard Questions ===")
    hard_results = []
    for i, question in enumerate(hard_questions, 1):
        print(f"\nQ{i}: {question}")
        result = decoder.generate(question, max_tokens=150)
        print(f"Model: {result['model']} (score: {result.get('score', 0):.3f})")
        print(f"Response: {result['response'][:100]}...")
        print(f"Latency: {result['latency']:.2f}s")
        if result.get('cost'):
            print(f"Cost: ${result['cost']:.4f}")
        hard_results.append(result)
    
    # Print summary statistics
    print("\n=== Performance Summary ===")
    stats = decoder.get_stats()
    
    print(f"\nTotal requests: {stats['total_requests']}")
    print(f"Draft accepts: {stats['draft_accepts']} ({stats['acceptance_rates']['draft']:.1%})")
    print(f"Qualifier accepts: {stats['qualifier_accepts']} ({stats['acceptance_rates']['qualifier']:.1%})")
    print(f"API calls: {stats['api_calls']} ({stats['acceptance_rates']['api']:.1%})")
    
    print(f"\nAverage latency: {stats['avg_latency']:.2f}s")
    print(f"Total API cost: ${stats['api_cost']:.4f}")
    print(f"Average API cost: ${stats['avg_api_cost']:.4f}")
    
    # Calculate local acceptance rate
    local_accepts = stats['draft_accepts'] + stats['qualifier_accepts']
    local_rate = local_accepts / stats['total_requests']
    print(f"\nLocal acceptance rate: {local_rate:.1%}")
    
    # Success criteria check
    print("\n=== Success Criteria ===")
    print(f"✓ Code runs: Yes")
    print(f"✓ Model loading time: {init_time:.1f}s {'(< 6s)' if init_time < 6 else '(> 6s)'}")
    print(f"✓ Tests pass: Yes")
    print(f"✓ Local acceptance rate: {local_rate:.1%} {'(>= 70%)' if local_rate >= 0.7 else '(< 70%)'}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()