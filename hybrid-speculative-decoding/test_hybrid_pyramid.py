#!/usr/bin/env python3
"""
Comprehensive test suite for Hybrid Pyramid Decoder
"""

import time
import json
import requests
import numpy as np
from typing import List, Dict, Tuple
import subprocess
import os
import sys
import signal
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
EASY_PROMPTS = [
    "What is 2 + 2?",
    "What color is the sky?",
    "Complete this sentence: The cat sat on the",
    "What is the capital of France?",
    "How many days are in a week?",
]

HARD_PROMPTS = [
    "Explain the halting problem in theoretical computer science",
    "Derive the quadratic formula step by step", 
    "Write a recursive function to solve the Tower of Hanoi problem",
    "Explain the philosophical implications of Gödel's incompleteness theorems",
    "Analyze the time complexity of quicksort in the worst, average, and best cases",
]

MIXED_PROMPTS = [
    ("What is the weather like today?", "general", "easy"),
    ("Calculate the derivative of x^3 + 2x^2 - 5x + 7", "math", "medium"),
    ("Write a Python function to check if a string is a palindrome", "code", "medium"),
    ("Compose a haiku about artificial intelligence", "creative", "easy"),
    ("Explain quantum entanglement to a 10-year-old", "general", "hard"),
    ("Solve the integral of sin(x)*cos(x) dx", "math", "hard"),
    ("Implement a binary search tree in Python with insert and search methods", "code", "hard"),
    ("Write a short story about a robot learning to paint", "creative", "medium"),
    ("What is machine learning?", "general", "easy"),
    ("Prove that the square root of 2 is irrational", "math", "hard"),
]


class TestHybridPyramid:
    """Test suite for Hybrid Pyramid Decoder"""
    
    def __init__(self, api_url="http://127.0.0.1:7779"):
        self.api_url = api_url
        self.api_process = None
        self.results = {
            'startup': {},
            'easy_tests': [],
            'hard_tests': [],
            'mixed_tests': [],
            'latency_tests': [],
            'metrics': {},
            'summary': {}
        }
    
    def start_api_server(self):
        """Start the API server as a subprocess"""
        logger.info("Starting API server...")
        
        # Set environment variable for API key if available
        env = os.environ.copy()
        if 'ANTHROPIC_API_KEY' not in env:
            logger.warning("No ANTHROPIC_API_KEY set. Tests will run in local-only mode.")
        
        # Start server
        self.api_process = subprocess.Popen(
            [sys.executable, 'hybrid_flask_api.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to be ready
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 second timeout
            try:
                response = requests.get(f"{self.api_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    self.results['startup']['time'] = data.get('startup_time', 0)
                    self.results['startup']['status'] = 'success'
                    logger.info(f"API server ready in {data.get('startup_time', 0):.2f} seconds")
                    return True
            except:
                pass
            time.sleep(0.5)
        
        self.results['startup']['status'] = 'timeout'
        return False
    
    def stop_api_server(self):
        """Stop the API server"""
        if self.api_process:
            logger.info("Stopping API server...")
            self.api_process.terminate()
            self.api_process.wait()
    
    def test_endpoint(self, prompt: str, max_tokens: int = 100) -> Dict:
        """Test a single prompt via API"""
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json={'prompt': prompt, 'max_tokens': max_tokens}
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f"Status {response.status_code}: {response.text}"}
        except Exception as e:
            return {'error': str(e)}
    
    def run_easy_tests(self):
        """Test easy prompts (should use local)"""
        logger.info("\n" + "="*60)
        logger.info("TESTING EASY PROMPTS (expect local)")
        logger.info("="*60)
        
        for prompt in EASY_PROMPTS:
            result = self.test_endpoint(prompt)
            self.results['easy_tests'].append({
                'prompt': prompt,
                'source': result.get('source', 'error'),
                'confidence': result.get('confidence', 0),
                'latency': result.get('latency', 0),
                'cost': result.get('cost', 0),
                'text': result.get('text', '')[:100] + '...' if result.get('text') else 'ERROR'
            })
            
            logger.info(f"\nPrompt: {prompt}")
            logger.info(f"Source: {result.get('source', 'error')}")
            logger.info(f"Confidence: {result.get('confidence', 0):.3f}")
            logger.info(f"Latency: {result.get('latency', 0):.2f}s")
    
    def run_hard_tests(self):
        """Test hard prompts (should fallback to Opus)"""
        logger.info("\n" + "="*60)
        logger.info("TESTING HARD PROMPTS (expect Opus fallback)")
        logger.info("="*60)
        
        for prompt in HARD_PROMPTS:
            result = self.test_endpoint(prompt)
            self.results['hard_tests'].append({
                'prompt': prompt,
                'source': result.get('source', 'error'),
                'confidence': result.get('confidence', 0),
                'latency': result.get('latency', 0),
                'cost': result.get('cost', 0),
                'text': result.get('text', '')[:100] + '...' if result.get('text') else 'ERROR'
            })
            
            logger.info(f"\nPrompt: {prompt[:50]}...")
            logger.info(f"Source: {result.get('source', 'error')}")
            logger.info(f"Confidence: {result.get('confidence', 0):.3f}")
            logger.info(f"Latency: {result.get('latency', 0):.2f}s")
    
    def run_mixed_tests(self):
        """Test mixed prompts with known types and difficulties"""
        logger.info("\n" + "="*60)
        logger.info("TESTING MIXED PROMPTS")
        logger.info("="*60)
        
        for prompt, task_type, difficulty in MIXED_PROMPTS:
            result = self.test_endpoint(prompt)
            self.results['mixed_tests'].append({
                'prompt': prompt,
                'expected_type': task_type,
                'difficulty': difficulty,
                'actual_type': result.get('task_type', 'error'),
                'source': result.get('source', 'error'),
                'confidence': result.get('confidence', 0),
                'latency': result.get('latency', 0),
                'cost': result.get('cost', 0)
            })
            
            logger.info(f"\nPrompt: {prompt[:50]}...")
            logger.info(f"Type: {result.get('task_type', 'error')} (expected: {task_type})")
            logger.info(f"Difficulty: {difficulty}")
            logger.info(f"Source: {result.get('source', 'error')}")
            logger.info(f"Confidence: {result.get('confidence', 0):.3f}")
    
    def run_latency_tests(self):
        """Test latency for both paths"""
        logger.info("\n" + "="*60)
        logger.info("TESTING LATENCY")
        logger.info("="*60)
        
        # Test 5 easy and 5 hard prompts
        test_prompts = [
            ("What is 1 + 1?", "easy"),
            ("Name a color", "easy"),
            ("What day comes after Monday?", "easy"),
            ("Is water wet?", "easy"),
            ("Count to 5", "easy"),
            ("Explain P vs NP problem", "hard"),
            ("Derive Euler's identity", "hard"),
            ("Implement a red-black tree", "hard"),
            ("Analyze Bitcoin's consensus mechanism", "hard"),
            ("Prove Fermat's Last Theorem", "hard"),
        ]
        
        latencies = {'easy': [], 'hard': []}
        
        for prompt, difficulty in test_prompts:
            result = self.test_endpoint(prompt, max_tokens=50)
            if 'latency' in result:
                latencies[difficulty].append(result['latency'])
                logger.info(f"{difficulty.upper()}: {result['latency']:.2f}s - {prompt[:30]}...")
        
        # Calculate statistics
        for difficulty in ['easy', 'hard']:
            if latencies[difficulty]:
                self.results['latency_tests'].append({
                    'type': difficulty,
                    'count': len(latencies[difficulty]),
                    'mean': np.mean(latencies[difficulty]),
                    'std': np.std(latencies[difficulty]),
                    'min': np.min(latencies[difficulty]),
                    'max': np.max(latencies[difficulty])
                })
    
    def get_final_metrics(self):
        """Get final metrics from API"""
        try:
            response = requests.get(f"{self.api_url}/metrics")
            if response.status_code == 200:
                self.results['metrics'] = response.json()
        except:
            pass
    
    def generate_summary(self):
        """Generate test summary"""
        # Count sources
        all_results = self.results['easy_tests'] + self.results['hard_tests'] + self.results['mixed_tests']
        source_counts = {}
        total_cost = 0
        total_latency = 0
        
        for result in all_results:
            source = result.get('source', 'error')
            source_counts[source] = source_counts.get(source, 0) + 1
            total_cost += result.get('cost', 0)
            total_latency += result.get('latency', 0)
        
        total_tests = len(all_results)
        local_count = source_counts.get('local', 0) + source_counts.get('local-forced', 0)
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'local_accepts': local_count,
            'opus_fallbacks': source_counts.get('opus', 0),
            'errors': source_counts.get('error', 0),
            'acceptance_rate': local_count / total_tests if total_tests > 0 else 0,
            'total_cost': total_cost,
            'average_latency': total_latency / total_tests if total_tests > 0 else 0,
            'startup_time': self.results['startup'].get('time', 0)
        }
    
    def print_summary(self):
        """Print test summary"""
        summary = self.results['summary']
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"- Total tests: {summary['total_tests']}")
        print(f"- Local accepts: {summary['local_accepts']} ({summary['acceptance_rate']:.1%})")
        print(f"- Opus fallbacks: {summary['opus_fallbacks']}")
        print(f"- Errors: {summary['errors']}")
        print(f"- Average latency: {summary['average_latency']:.2f}s")
        print(f"- Total cost: ${summary['total_cost']:.4f}")
        print(f"- Startup time: {summary['startup_time']:.2f}s")
        
        # Check success criteria
        print(f"\n✅ SUCCESS CRITERIA:")
        criteria = {
            'Startup ≤ 6s': summary['startup_time'] <= 6.0,
            'Acceptance ≥ 70%': summary['acceptance_rate'] >= 0.70,
            'Avg latency < 1s': summary['average_latency'] < 1.0,
            'All tests passed': summary['errors'] == 0
        }
        
        for criterion, passed in criteria.items():
            print(f"- {criterion}: {'✅ PASS' if passed else '❌ FAIL'}")
        
        overall_pass = all(criteria.values())
        print(f"\n{'🎉 ALL CRITERIA PASSED!' if overall_pass else '❌ Some criteria failed'}")
    
    def save_results(self):
        """Save test results to file"""
        with open('test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info("\nResults saved to test_results.json")
    
    def run_all_tests(self):
        """Run complete test suite"""
        logger.info("Starting Hybrid Pyramid Decoder test suite...")
        
        # Start API server
        if not self.start_api_server():
            logger.error("Failed to start API server")
            return
        
        try:
            # Run tests
            self.run_easy_tests()
            self.run_hard_tests()
            self.run_mixed_tests()
            self.run_latency_tests()
            
            # Get final metrics
            self.get_final_metrics()
            
            # Generate summary
            self.generate_summary()
            
            # Print summary
            self.print_summary()
            
            # Save results
            self.save_results()
            
        finally:
            # Stop server
            self.stop_api_server()


if __name__ == "__main__":
    # Check if API key is set
    if 'ANTHROPIC_API_KEY' not in os.environ:
        print("\n⚠️  WARNING: ANTHROPIC_API_KEY not set!")
        print("The system will run in local-only mode (no Opus fallback).")
        print("To enable Opus fallback, set your API key:")
        print("  export ANTHROPIC_API_KEY='your-key-here'\n")
        
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Run tests
    tester = TestHybridPyramid()
    tester.run_all_tests()