#!/usr/bin/env python3
"""
Mock demo showing how the system would work
(without requiring actual model downloads)
"""

import time
import random
import json

class MockHybridDecoder:
    """Mock version for demonstration"""
    
    def __init__(self):
        self.thresholds = {
            'math': 0.90,
            'code': 0.88,
            'creative': 0.80,
            'general': 0.85
        }
        self.metrics = {
            'total_requests': 0,
            'local_accepts': 0,
            'opus_fallbacks': 0,
            'total_latency': 0,
            'total_cost': 0
        }
    
    def classify_task(self, prompt):
        """Simple task classification"""
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ['calculate', 'solve', 'equation']):
            return 'math'
        elif any(w in prompt_lower for w in ['code', 'function', 'implement']):
            return 'code'
        elif any(w in prompt_lower for w in ['story', 'poem', 'creative']):
            return 'creative'
        return 'general'
    
    def mock_confidence(self, prompt, task_type):
        """Mock confidence scoring"""
        # Easy questions get high confidence
        easy_indicators = ['2 + 2', 'color', 'capital of france', 'days in week']
        if any(ind in prompt.lower() for ind in easy_indicators):
            return 0.92 + random.uniform(0, 0.05)
        
        # Hard questions get low confidence
        hard_indicators = ['halting problem', 'gödel', 'black-scholes', 'red-black tree', 'quantum']
        if any(ind in prompt.lower() for ind in hard_indicators):
            return 0.65 + random.uniform(0, 0.15)
        
        # Medium gets mixed
        return 0.82 + random.uniform(-0.1, 0.1)
    
    def generate(self, prompt, max_tokens=100):
        """Mock generation with routing decision"""
        start_time = time.time()
        
        # Classify task
        task_type = self.classify_task(prompt)
        
        # Calculate confidence
        confidence = self.mock_confidence(prompt, task_type)
        threshold = self.thresholds[task_type]
        
        # Make routing decision
        if confidence > threshold:
            # Local path
            source = 'local'
            latency = 0.2 + random.uniform(0, 0.3)  # 0.2-0.5s
            cost = 0.0
            text = f"[Local response] This is a quick answer to: {prompt[:50]}..."
            self.metrics['local_accepts'] += 1
        else:
            # Opus fallback
            source = 'opus'
            latency = 0.8 + random.uniform(0, 0.4)  # 0.8-1.2s
            cost = 0.01 + random.uniform(0, 0.02)  # $0.01-0.03
            text = f"[Opus response] This is a detailed, high-quality answer to: {prompt[:50]}..."
            self.metrics['opus_fallbacks'] += 1
        
        # Simulate processing time
        time.sleep(latency)
        
        # Update metrics
        self.metrics['total_requests'] += 1
        self.metrics['total_latency'] += latency
        self.metrics['total_cost'] += cost
        
        return {
            'text': text,
            'source': source,
            'confidence': confidence,
            'task_type': task_type,
            'latency': latency,
            'cost': cost,
            'threshold': threshold
        }

def run_mock_demo():
    """Run the mock demonstration"""
    print("🚀 HYBRID PYRAMID DECODER - MOCK DEMO")
    print("="*70)
    print("(This is a simulation showing how the system would work)")
    print("="*70)
    
    decoder = MockHybridDecoder()
    
    # Test prompts
    test_prompts = [
        # Easy (should use local)
        ("What is 2 + 2?", "easy"),
        ("What color is the sky?", "easy"),
        ("What's the capital of France?", "easy"),
        
        # Hard (should use Opus)
        ("Explain the halting problem in theoretical computer science", "hard"),
        ("Derive the Black-Scholes equation step by step", "hard"),
        ("Implement a red-black tree with full balancing", "hard"),
        
        # Mixed
        ("Write a simple Python function", "medium"),
        ("Explain photosynthesis", "medium"),
    ]
    
    print(f"\n📊 Configuration:")
    print(f"   Thresholds: {json.dumps(decoder.thresholds, indent=6)}")
    
    print(f"\n🎯 Running {len(test_prompts)} test prompts...\n")
    
    results = []
    for prompt, difficulty in test_prompts:
        print(f"{'='*70}")
        print(f"📝 Prompt ({difficulty}): {prompt[:60]}...")
        
        result = decoder.generate(prompt)
        results.append(result)
        
        # Display results with visual indicators
        confidence_bar = '█' * int(result['confidence'] * 20)
        threshold_pos = int(result['threshold'] * 20)
        
        print(f"\n📊 Analysis:")
        print(f"   Task Type: {result['task_type']}")
        print(f"   Confidence: {result['confidence']:.3f} |{confidence_bar:<20}|")
        print(f"   Threshold:  {result['threshold']:.3f} |{' ' * threshold_pos}^")
        print(f"   Decision: {result['source'].upper()} {'✅' if result['source'] == 'local' else '💰'}")
        print(f"   Latency: {result['latency']:.2f}s")
        if result['cost'] > 0:
            print(f"   Cost: ${result['cost']:.3f}")
        
        print(f"\n💬 Response: {result['text'][:80]}...")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 SUMMARY")
    print("="*70)
    
    total = decoder.metrics['total_requests']
    acceptance_rate = decoder.metrics['local_accepts'] / total * 100
    avg_latency = decoder.metrics['total_latency'] / total
    total_cost = decoder.metrics['total_cost']
    
    print(f"\n✅ Results:")
    print(f"   Total Requests: {total}")
    print(f"   Local Accepts: {decoder.metrics['local_accepts']} ({acceptance_rate:.0f}%)")
    print(f"   Opus Fallbacks: {decoder.metrics['opus_fallbacks']}")
    print(f"   Average Latency: {avg_latency:.2f}s")
    print(f"   Total Cost: ${total_cost:.3f}")
    print(f"   Cost per Request: ${total_cost/total:.3f}")
    
    # Visual acceptance rate
    local_bar = '🟢' * decoder.metrics['local_accepts']
    opus_bar = '🔵' * decoder.metrics['opus_fallbacks']
    print(f"\n📊 Routing Distribution:")
    print(f"   {local_bar}{opus_bar}")
    print(f"   {'Local':<{decoder.metrics['local_accepts']}}{'Opus'}")
    
    # Success criteria
    print(f"\n✅ Success Criteria:")
    criteria = [
        (f"Acceptance ≥ 70%", acceptance_rate >= 70),
        (f"Avg latency < 1s", avg_latency < 1.0),
    ]
    
    for criterion, met in criteria:
        print(f"   {criterion}: {'✅ PASS' if met else '❌ FAIL'}")
    
    print(f"\n{'🎉 Demo Complete!' if all(m for _, m in criteria) else '⚠️  Some criteria not met'}")

if __name__ == "__main__":
    run_mock_demo()