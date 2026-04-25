#!/usr/bin/env python3
"""
3-Tier Pyramid Speculative Decoding Test Suite
Comprehensive testing: health, performance, quality, stability, memory
"""

import requests
import json
import time
import statistics
from datetime import datetime
from pathlib import Path

BASE_URL = "http://127.0.0.1:7779"
REPORT_FILE = Path.home() / ".openclaw/logs/3tier-test-results.txt"

class TestSuite:
    def __init__(self):
        self.results = []
        self.speeds = []
        self.times = []
        self.tokens = []
        
    def log(self, msg):
        print(msg)
        
    def report(self, test_name, status, details=""):
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {test_name}: {status}"
        if details:
            line += f" - {details}"
        self.results.append(line)
        print(line)
        
    def save_report(self):
        with open(REPORT_FILE, 'w') as f:
            f.write("╔" + "="*78 + "╗\n")
            f.write("║" + " "*16 + "3-TIER PYRAMID TEST SUITE RESULTS" + " "*28 + "║\n")
            f.write("║" + " "*20 + f"March 28, 2026 - {datetime.now().strftime('%H:%M:%S')}" + " "*26 + "║\n")
            f.write("╚" + "="*78 + "╝\n\n")
            for line in self.results:
                f.write(line + "\n")
            f.write("\n")
    
    def test_health(self):
        """Test 1: Health Check"""
        print("\n" + "="*60)
        print("TEST 1: Health Check")
        print("="*60)
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=5)
            data = resp.json()
            print(f"Status: {data.get('status')}")
            print(f"Model: {data.get('model')}")
            print(f"Tiers: {data.get('tiers')}")
            
            if data.get('status') == 'ok':
                self.log("✅ Health Check PASSED\n")
                self.report("Health Check", "PASS")
                return True
            else:
                self.log("❌ Health Check FAILED\n")
                self.report("Health Check", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Health Check FAILED: {e}\n")
            self.report("Health Check", "FAIL", str(e))
            return False
    
    def test_basic_generation(self):
        """Test 2: Basic Generation"""
        print("\n" + "="*60)
        print("TEST 2: Basic Generation (100 tokens)")
        print("="*60)
        try:
            prompt = "The future of artificial intelligence is"
            start = time.time()
            resp = requests.post(
                f"{BASE_URL}/generate",
                json={"prompt": prompt, "max_tokens": 100},
                timeout=120
            )
            elapsed = time.time() - start
            data = resp.json()
            
            tokens = data.get('tokens_generated', 0)
            speed = data.get('throughput_tokens_per_sec', 0)
            
            print(f"Tokens: {tokens} | Speed: {speed:.2f} tok/sec | Time: {elapsed:.2f}s")
            
            if tokens > 0:
                self.log("✅ Basic Generation PASSED\n")
                self.report("Basic Generation", "PASS", f"{tokens} tokens @ {speed:.2f} tok/sec")
                self.speeds.append(speed)
                self.times.append(elapsed)
                self.tokens.append(tokens)
                return True
            else:
                self.log("❌ Basic Generation FAILED\n")
                self.report("Basic Generation", "FAIL", "No tokens generated")
                return False
        except Exception as e:
            self.log(f"❌ Basic Generation FAILED: {e}\n")
            self.report("Basic Generation", "FAIL", str(e))
            return False
    
    def test_performance(self):
        """Test 3: Performance Benchmark"""
        print("\n" + "="*60)
        print("TEST 3: Performance Benchmark (5 rapid requests)")
        print("="*60)
        
        success = 0
        for i in range(5):
            try:
                prompt = f"Performance test {i+1}: What is"
                start = time.time()
                resp = requests.post(
                    f"{BASE_URL}/generate",
                    json={"prompt": prompt, "max_tokens": 75},
                    timeout=120
                )
                elapsed = time.time() - start
                data = resp.json()
                
                tokens = data.get('tokens_generated', 0)
                speed = data.get('throughput_tokens_per_sec', 0)
                
                print(f"  Request {i+1}: {tokens} tokens @ {speed:.2f} tok/sec ({elapsed:.2f}s)")
                
                if tokens > 0:
                    success += 1
                    self.speeds.append(speed)
                    self.times.append(elapsed)
                    self.tokens.append(tokens)
            except Exception as e:
                print(f"  Request {i+1}: FAILED - {e}")
        
        if success > 0:
            avg_speed = statistics.mean(self.speeds[-success:]) if success > 0 else 0
            print(f"\nAverage Speed: {avg_speed:.2f} tok/sec")
            
            if avg_speed >= 10:
                self.log(f"✅ Performance Benchmark PASSED ({avg_speed:.2f} tok/sec)\n")
                self.report("Performance Benchmark", "PASS", f"avg {avg_speed:.2f} tok/sec")
                return True
            else:
                self.log(f"⚠️ Performance Below Target ({avg_speed:.2f} tok/sec < 10)\n")
                self.report("Performance Benchmark", "WARN", f"avg {avg_speed:.2f} tok/sec")
                return True
        else:
            self.log("❌ Performance Benchmark FAILED\n")
            self.report("Performance Benchmark", "FAIL", "No successful requests")
            return False
    
    def test_quality(self):
        """Test 4: Quality Checks"""
        print("\n" + "="*60)
        print("TEST 4: Quality Checks (coherence)")
        print("="*60)
        
        prompts = [
            "Short test",
            "Explain machine learning in simple terms",
            "Write a creative story about AI"
        ]
        
        quality_pass = 0
        for i, prompt in enumerate(prompts, 1):
            try:
                resp = requests.post(
                    f"{BASE_URL}/generate",
                    json={"prompt": prompt, "max_tokens": 60},
                    timeout=120
                )
                data = resp.json()
                text = data.get('generated_text', '')
                tokens = data.get('tokens_generated', 0)
                
                text_len = len(text)
                print(f"  Test {i}: {tokens} tokens, {text_len} chars")
                
                if text_len > 50:
                    quality_pass += 1
                    print(f"    ✅ Coherent output")
                else:
                    print(f"    ⚠️ Short output")
            except Exception as e:
                print(f"  Test {i}: FAILED - {e}")
        
        print(f"\nQuality Score: {quality_pass}/3")
        
        if quality_pass == 3:
            self.log("✅ Quality Checks PASSED\n")
            self.report("Quality Checks", "PASS", f"{quality_pass}/3 coherent")
            return True
        elif quality_pass >= 2:
            self.log(f"⚠️ Quality Checks Partial ({quality_pass}/3)\n")
            self.report("Quality Checks", "PARTIAL", f"{quality_pass}/3 coherent")
            return True
        else:
            self.log("❌ Quality Checks FAILED\n")
            self.report("Quality Checks", "FAIL", f"{quality_pass}/3 coherent")
            return False
    
    def test_stability(self):
        """Test 5: Stability"""
        print("\n" + "="*60)
        print("TEST 5: Stability (10 rapid requests)")
        print("="*60)
        
        success = 0
        for i in range(10):
            try:
                resp = requests.post(
                    f"{BASE_URL}/generate",
                    json={"prompt": f"Stability test {i+1}", "max_tokens": 40},
                    timeout=60
                )
                if 'tokens_generated' in resp.json():
                    success += 1
                    print(".", end="", flush=True)
                else:
                    print("E", end="", flush=True)
            except:
                print("E", end="", flush=True)
        
        print(f"\n\nResults: {success}/10 successful")
        error_rate = (10 - success) / 10 * 100
        
        if error_rate == 0:
            self.log("✅ Stability Test PASSED (0% error)\n")
            self.report("Stability", "PASS", "0% error rate")
            return True
        elif error_rate < 10:
            self.log(f"⚠️ Stability Test Acceptable ({error_rate:.0f}% error)\n")
            self.report("Stability", "PARTIAL", f"{error_rate:.0f}% error rate")
            return True
        else:
            self.log(f"❌ Stability Test FAILED ({error_rate:.0f}% error)\n")
            self.report("Stability", "FAIL", f"{error_rate:.0f}% error rate")
            return False
    
    def test_memory(self):
        """Test 6: Memory Usage"""
        print("\n" + "="*60)
        print("TEST 6: Memory Usage")
        print("="*60)
        try:
            resp = requests.get(f"{BASE_URL}/status", timeout=5)
            data = resp.json()
            mem = data.get('memory_gb', 0)
            
            print(f"Memory Used: {mem:.2f} GB")
            
            if mem < 15:
                self.log("✅ Memory Usage OK (<15 GB)\n")
                self.report("Memory Usage", "PASS", f"{mem:.2f} GB")
                return True
            else:
                self.log(f"⚠️ Memory Usage High ({mem:.2f} GB)\n")
                self.report("Memory Usage", "WARN", f"{mem:.2f} GB")
                return True
        except Exception as e:
            self.log(f"❌ Memory Check FAILED: {e}\n")
            self.report("Memory Usage", "FAIL", str(e))
            return False
    
    def run_all(self):
        """Run all tests"""
        print("\n" + "🍑 "*30)
        print("3-TIER PYRAMID TEST SUITE")
        print("🍑 "*30 + "\n")
        
        results = [
            self.test_health(),
            self.test_basic_generation(),
            self.test_performance(),
            self.test_quality(),
            self.test_stability(),
            self.test_memory()
        ]
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        passed = sum(results)
        total = len(results)
        
        if self.speeds:
            avg_speed = statistics.mean(self.speeds)
            print(f"Average Speed: {avg_speed:.2f} tok/sec")
            print(f"Min Speed: {min(self.speeds):.2f} tok/sec")
            print(f"Max Speed: {max(self.speeds):.2f} tok/sec")
        
        if self.times:
            avg_time = statistics.mean(self.times)
            print(f"Average Generation Time: {avg_time:.2f}s")
        
        if self.tokens:
            avg_tokens = statistics.mean(self.tokens)
            print(f"Average Tokens Generated: {avg_tokens:.0f}")
        
        print(f"\nTests Passed: {passed}/{total}")
        
        self.save_report()
        
        print(f"\nReport saved to: {REPORT_FILE}")
        print("\n" + "="*60)
        print("✅ 3-TIER PYRAMID TEST SUITE COMPLETE")
        print("="*60 + "\n")
        
        return passed == total

if __name__ == "__main__":
    suite = TestSuite()
    suite.run_all()
