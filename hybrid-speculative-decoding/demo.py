#!/usr/bin/env python3
"""
Quick demo of Hybrid Pyramid Decoder
Shows the system making intelligent routing decisions
"""

import requests
import time
import json
from typing import Dict, List

# API endpoint
API_URL = "http://localhost:7779"

# Demo prompts showing different difficulty levels
DEMO_PROMPTS = [
    # Easy - should use local
    {
        "prompt": "What is 2 + 2?",
        "expected": "local",
        "category": "math-easy"
    },
    {
        "prompt": "What color is the sky?",
        "expected": "local", 
        "category": "general-easy"
    },
    {
        "prompt": "Write a Python print statement",
        "expected": "local",
        "category": "code-easy"
    },
    
    # Hard - should use Opus
    {
        "prompt": "Explain the P vs NP problem and its implications for computer science",
        "expected": "opus",
        "category": "general-hard"
    },
    {
        "prompt": "Derive the Black-Scholes equation from first principles",
        "expected": "opus",
        "category": "math-hard"
    },
    {
        "prompt": "Implement a red-black tree with full balancing logic in Python",
        "expected": "opus",
        "category": "code-hard"
    }
]


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return True
        return False
    except:
        return False


def run_demo_prompt(prompt_data: Dict) -> Dict:
    """Run a single demo prompt"""
    prompt = prompt_data["prompt"]
    
    print(f"\n{'='*70}")
    print(f"📝 PROMPT: {prompt[:60]}...")
    print(f"   Category: {prompt_data['category']}")
    print(f"   Expected: {prompt_data['expected']}")
    
    # Make request
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json={"prompt": prompt, "max_tokens": 100},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            latency = time.time() - start_time
            
            # Display results
            print(f"\n📊 RESULTS:")
            print(f"   Source: {result['source']} {'✅' if result['source'] == prompt_data['expected'] else '❌'}")
            print(f"   Confidence: {result['confidence']:.3f}")
            print(f"   Task Type: {result['task_type']}")
            print(f"   Latency: {latency:.2f}s")
            print(f"   Cost: ${result['cost']:.4f}")
            print(f"\n💬 Response: {result['text'][:150]}...")
            
            return {
                "success": True,
                "source": result['source'],
                "expected": prompt_data['expected'],
                "correct": result['source'] == prompt_data['expected'],
                "latency": latency,
                "cost": result['cost']
            }
        else:
            print(f"❌ API Error: {response.status_code}")
            return {"success": False}
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return {"success": False}


def print_summary(results: List[Dict]):
    """Print demo summary"""
    print(f"\n{'='*70}")
    print("📊 DEMO SUMMARY")
    print("="*70)
    
    total = len(results)
    successful = sum(1 for r in results if r.get("success", False))
    correct = sum(1 for r in results if r.get("correct", False))
    
    local_count = sum(1 for r in results if r.get("source") == "local")
    opus_count = sum(1 for r in results if r.get("source") == "opus")
    
    total_cost = sum(r.get("cost", 0) for r in results)
    avg_latency = sum(r.get("latency", 0) for r in results if r.get("latency")) / max(successful, 1)
    
    print(f"\n✅ Success Rate: {successful}/{total} ({successful/total*100:.0f}%)")
    print(f"🎯 Routing Accuracy: {correct}/{successful} ({correct/successful*100:.0f}%)")
    print(f"\n📈 Source Distribution:")
    print(f"   - Local: {local_count} ({local_count/successful*100:.0f}%)")
    print(f"   - Opus: {opus_count} ({opus_count/successful*100:.0f}%)")
    print(f"\n⏱️  Average Latency: {avg_latency:.2f}s")
    print(f"💰 Total Cost: ${total_cost:.4f}")
    print(f"💵 Average Cost: ${total_cost/successful:.4f}")


def main():
    """Run the demo"""
    print("🚀 HYBRID PYRAMID DECODER DEMO")
    print("="*70)
    
    # Check API health
    print("\n🔍 Checking API status...")
    if not check_api_health():
        print("❌ API is not running!")
        print("\nPlease start the server first:")
        print("  ./start_hybrid_server.sh")
        return
    
    print("✅ API is healthy!")
    
    # Get current metrics
    try:
        metrics = requests.get(f"{API_URL}/metrics").json()
        print(f"\n📊 Current Metrics:")
        print(f"   - Total requests: {metrics.get('total_requests', 0)}")
        print(f"   - Acceptance rate: {metrics.get('acceptance_rate', 0):.1%}")
        print(f"   - Average latency: {metrics.get('average_latency', 0):.2f}s")
    except:
        pass
    
    # Run demo prompts
    print(f"\n🎯 Running {len(DEMO_PROMPTS)} demo prompts...")
    input("Press Enter to start...\n")
    
    results = []
    for prompt_data in DEMO_PROMPTS:
        result = run_demo_prompt(prompt_data)
        results.append(result)
        time.sleep(0.5)  # Small pause between requests
    
    # Print summary
    print_summary(results)
    
    # Final metrics
    try:
        final_metrics = requests.get(f"{API_URL}/metrics").json()
        print(f"\n📊 Final System Metrics:")
        print(f"   - Total requests: {final_metrics.get('total_requests', 0)}")
        print(f"   - Acceptance rate: {final_metrics.get('acceptance_rate', 0):.1%}")
        print(f"   - Average latency: {final_metrics.get('average_latency', 0):.2f}s")
        print(f"   - Total cost: ${final_metrics.get('total_cost', 0):.4f}")
    except:
        pass
    
    print(f"\n✅ Demo complete!")


if __name__ == "__main__":
    main()