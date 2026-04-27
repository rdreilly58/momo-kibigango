"""
Extensive Warmup & Test Suite for LSH Memory Search
Tests with 25+ diverse queries to warm up metrics and validate performance
"""

import sys
import time
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import json
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))
from openclaw_integration import create_openclaw_lsh

# Test queries covering diverse topics
TEST_QUERIES = [
    # Leadership & Strategy
    "What is the current leadership strategy at Leidos?",
    "What are the DORA metrics and team health observations?",
    "What decisions were made about task routing and model selection?",
    "What is the sprint completion status and blockers?",
    
    # Technical Implementation
    "What is the architecture of the speculative decoding system?",
    "How is Config 4 hybrid deployment configured?",
    "What are the performance benchmarks for different models?",
    "How does the 3-tier model routing system work?",
    
    # Projects & Deliverables
    "What is the status of momo-mukashi website deployment?",
    "What features are included in the momo-kibidango project?",
    "What research was conducted on hashing methods?",
    "What is the GitHub repository structure for momo-mukashi?",
    
    # Memory & Infrastructure
    "How are memory files organized and consolidated?",
    "What is the setup for local embeddings and memory search?",
    "How are API keys and credentials managed?",
    "What security hardening was implemented?",
    
    # Cost & Optimization
    "What is the 79% cost reduction strategy?",
    "How does Claude Code model selection optimize costs?",
    "What are the Tier A, B, C optimization strategies?",
    "How is speculative decoding improving latency?",
    
    # Integration & Deployment
    "What is the OpenClaw gateway configuration?",
    "How are cron jobs configured with timeouts?",
    "What is the health check and monitoring setup?",
    "How is Telegraph integration configured?",
    
    # User Context
    "Who is Bob Reilly and what is his work?",
    "What are the current projects and goals?",
    "What is the timeline for major initiatives?",
    "What are the next steps for Phase 2 and Phase 3?",
]

# Additional variations for robustness testing
VARIATIONS = [
    "OpenClaw memory search optimization",
    "Performance metrics and latency",
    "Fallback mechanisms and accuracy",
    "Cost reduction and efficiency",
    "Team leadership and strategy",
]

# Combine all queries
ALL_QUERIES = TEST_QUERIES + VARIATIONS

print(f"Total test queries: {len(ALL_QUERIES)}")


class ExtensiveWarmupTest:
    """Comprehensive warmup and performance test suite"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.lsh = None
        self.results = {
            "metadata": {},
            "warmup_phase": {},
            "per_query_results": [],
            "summary": {},
        }
        self.query_times = []
    
    def setup(self):
        """Set up LSH integration"""
        print("\n" + "="*80)
        print("🍑 EXTENSIVE WARMUP & TEST SUITE")
        print("="*80)
        print("\n📋 Setup phase...")
        
        self.lsh = create_openclaw_lsh()
        if not self.lsh or not self.lsh.initialized:
            print("❌ Failed to initialize LSH")
            return False
        
        print("✅ LSH initialized successfully")
        print(f"   Chunks indexed: {len(self.lsh.chunk_ids)}")
        
        return True
    
    def run_warmup_phase(self):
        """Run warmup queries (not counted in metrics)"""
        print("\n" + "-"*80)
        print("🔥 WARMUP PHASE (5 queries)")
        print("-"*80)
        
        warmup_queries = ALL_QUERIES[:5]
        warmup_times = []
        
        for i, query in enumerate(warmup_queries, 1):
            embedding = self.model.encode(query)
            
            start = time.time()
            results = self.lsh.search(embedding, top_k=5)
            elapsed = (time.time() - start) * 1000
            
            warmup_times.append(elapsed)
            
            print(f"  {i}. '{query[:50]}...' → {elapsed:.2f}ms")
        
        avg_warmup = np.mean(warmup_times)
        print(f"\n✅ Warmup complete")
        print(f"   Average warmup latency: {avg_warmup:.2f}ms")
        
        self.results["warmup_phase"] = {
            "queries_run": len(warmup_queries),
            "latencies_ms": warmup_times,
            "average_ms": avg_warmup,
        }
    
    def run_main_test_phase(self):
        """Run main test queries (counted in metrics)"""
        print("\n" + "-"*80)
        print(f"📊 MAIN TEST PHASE ({len(TEST_QUERIES)} diverse queries)")
        print("-"*80)
        
        latencies = []
        sources = {"lsh": 0, "fallback": 0}
        
        for i, query in enumerate(TEST_QUERIES, 1):
            embedding = self.model.encode(query)
            
            start = time.time()
            results = self.lsh.search(embedding, top_k=5)
            elapsed = (time.time() - start) * 1000
            
            latencies.append(elapsed)
            self.query_times.append(elapsed)
            
            # Track source
            if results:
                source = results[0].get("source", "unknown")
                if source in sources:
                    sources[source] += 1
            
            # Print progress every 5 queries
            if i % 5 == 0 or i == len(TEST_QUERIES):
                print(f"  {i:2d}. '{query[:50]}...' → {elapsed:.2f}ms ({source})")
        
        # Calculate statistics
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        mean = np.mean(latencies)
        std = np.std(latencies)
        
        print(f"\n✅ Main test phase complete ({len(TEST_QUERIES)} queries)")
        print(f"   Mean latency: {mean:.2f}ms (±{std:.2f}ms)")
        print(f"   P50: {p50:.2f}ms")
        print(f"   P95: {p95:.2f}ms")
        print(f"   P99: {p99:.2f}ms")
        print(f"   LSH hits: {sources['lsh']}")
        print(f"   Fallbacks: {sources['fallback']}")
        
        return {
            "latencies_ms": latencies,
            "mean_ms": mean,
            "std_ms": std,
            "p50_ms": p50,
            "p95_ms": p95,
            "p99_ms": p99,
            "sources": sources,
        }
    
    def run_stress_test(self):
        """Run rapid-fire queries to stress test"""
        print("\n" + "-"*80)
        print("💪 STRESS TEST (20 rapid queries)")
        print("-"*80)
        
        stress_queries = ALL_QUERIES[-20:]  # Last 20 queries
        stress_times = []
        
        print("  Running rapid-fire queries...", end="", flush=True)
        
        for query in stress_queries:
            embedding = self.model.encode(query)
            
            start = time.time()
            results = self.lsh.search(embedding, top_k=5)
            elapsed = (time.time() - start) * 1000
            
            stress_times.append(elapsed)
        
        print(" ✅")
        
        mean_stress = np.mean(stress_times)
        max_stress = np.max(stress_times)
        min_stress = np.min(stress_times)
        
        print(f"✅ Stress test complete (20 queries in {sum(stress_times):.0f}ms)")
        print(f"   Mean: {mean_stress:.2f}ms")
        print(f"   Min: {min_stress:.2f}ms")
        print(f"   Max: {max_stress:.2f}ms")
        
        return {
            "queries_run": 20,
            "latencies_ms": stress_times,
            "mean_ms": mean_stress,
            "min_ms": min_stress,
            "max_ms": max_stress,
        }
    
    def get_final_metrics(self):
        """Get final metrics from LSH"""
        print("\n" + "-"*80)
        print("📈 FINAL METRICS")
        print("-"*80)
        
        metrics = self.lsh.get_metrics()
        health = self.lsh.health_check()
        
        print(f"✅ LSH Status: {health.get('status', 'UNKNOWN')}")
        print(f"   Total queries: {metrics.get('total_queries', 0)}")
        print(f"   LSH queries: {metrics.get('lsh_queries', 0)}")
        print(f"   Fallback queries: {metrics.get('fallback_queries', 0)}")
        print(f"   Average latency: {metrics.get('avg_latency_ms', 0):.2f}ms")
        print(f"   LSH hit rate: {metrics.get('lsh_hit_rate', 0)*100:.1f}%")
        print(f"   Fallback rate: {metrics.get('fallback_rate', 0)*100:.1f}%")
        
        return metrics, health
    
    def generate_report(self, main_test_results, stress_test_results, metrics, health):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Build report
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_configuration": {
                "warmup_queries": len(self.results["warmup_phase"].get("latencies_ms", [])),
                "main_test_queries": len(TEST_QUERIES),
                "stress_test_queries": stress_test_results.get("queries_run", 0),
                "total_test_queries": len(self.results["warmup_phase"].get("latencies_ms", [])) + len(TEST_QUERIES) + stress_test_results.get("queries_run", 0),
            },
            "warmup_phase": self.results["warmup_phase"],
            "main_test_phase": main_test_results,
            "stress_test_phase": stress_test_results,
            "lsh_metrics": {
                "total_queries": metrics.get("total_queries", 0),
                "lsh_queries": metrics.get("lsh_queries", 0),
                "fallback_queries": metrics.get("fallback_queries", 0),
                "avg_latency_ms": metrics.get("avg_latency_ms", 0),
                "lsh_hit_rate": metrics.get("lsh_hit_rate", 0),
                "fallback_rate": metrics.get("fallback_rate", 0),
            },
            "health_status": health,
            "performance_assessment": self._assess_performance(main_test_results, metrics, health),
        }
        
        # Print report
        self._print_report(report)
        
        return report
    
    def _assess_performance(self, main_test, metrics, health):
        """Assess performance against targets"""
        assessment = {
            "latency": {},
            "accuracy": {},
            "reliability": {},
            "overall": "PASS",
        }
        
        # Latency assessment
        p99 = main_test.get("p99_ms", 0)
        if p99 < 50:
            assessment["latency"]["status"] = "EXCELLENT"
            assessment["latency"]["message"] = f"P99 {p99:.2f}ms (target <50ms)"
        elif p99 < 100:
            assessment["latency"]["status"] = "GOOD"
            assessment["latency"]["message"] = f"P99 {p99:.2f}ms (acceptable)"
        else:
            assessment["latency"]["status"] = "WARNING"
            assessment["latency"]["message"] = f"P99 {p99:.2f}ms (above target)"
            assessment["overall"] = "WARNING"
        
        # Accuracy assessment
        fallback_rate = metrics.get("fallback_rate", 0)
        if fallback_rate < 0.05:
            assessment["accuracy"]["status"] = "EXCELLENT"
            assessment["accuracy"]["message"] = f"Fallback rate {fallback_rate*100:.1f}% (target <5%)"
        elif fallback_rate < 0.10:
            assessment["accuracy"]["status"] = "GOOD"
            assessment["accuracy"]["message"] = f"Fallback rate {fallback_rate*100:.1f}% (acceptable)"
        else:
            assessment["accuracy"]["status"] = "WARNING"
            assessment["accuracy"]["message"] = f"Fallback rate {fallback_rate*100:.1f}% (above target)"
            assessment["overall"] = "WARNING"
        
        # Reliability assessment
        health_status = health.get("status", "UNKNOWN")
        if health_status == "HEALTHY":
            assessment["reliability"]["status"] = "EXCELLENT"
            assessment["reliability"]["message"] = "LSH health check HEALTHY"
        elif health_status == "WARNING":
            assessment["reliability"]["status"] = "WARNING"
            assessment["reliability"]["message"] = "LSH health check WARNING"
            assessment["overall"] = "WARNING"
        else:
            assessment["reliability"]["status"] = "INFO"
            assessment["reliability"]["message"] = f"LSH health check {health_status}"
        
        return assessment
    
    def _print_report(self, report):
        """Pretty print the report"""
        config = report["test_configuration"]
        main_test = report["main_test_phase"]
        stress_test = report["stress_test_phase"]
        assessment = report["performance_assessment"]
        
        print(f"\n📋 TEST CONFIGURATION")
        print(f"   Warmup queries: {config['warmup_queries']}")
        print(f"   Main test queries: {config['main_test_queries']}")
        print(f"   Stress test queries: {config['stress_test_queries']}")
        print(f"   Total test queries: {config['total_test_queries']}")
        
        print(f"\n⏱️  LATENCY RESULTS")
        print(f"   Mean: {main_test['mean_ms']:.2f}ms")
        print(f"   P50:  {main_test['p50_ms']:.2f}ms")
        print(f"   P95:  {main_test['p95_ms']:.2f}ms")
        print(f"   P99:  {main_test['p99_ms']:.2f}ms")
        print(f"   Std:  {main_test['std_ms']:.2f}ms")
        
        print(f"\n🎯 SOURCE BREAKDOWN")
        sources = main_test['sources']
        total = sources['lsh'] + sources['fallback']
        print(f"   LSH hits: {sources['lsh']}/{total} ({sources['lsh']/total*100:.1f}%)")
        print(f"   Fallbacks: {sources['fallback']}/{total} ({sources['fallback']/total*100:.1f}%)")
        
        print(f"\n💪 STRESS TEST")
        print(f"   Queries: {stress_test['queries_run']}")
        print(f"   Mean: {stress_test['mean_ms']:.2f}ms")
        print(f"   Min: {stress_test['min_ms']:.2f}ms")
        print(f"   Max: {stress_test['max_ms']:.2f}ms")
        
        print(f"\n🏥 PERFORMANCE ASSESSMENT")
        print(f"   Latency:    {assessment['latency']['status']:10s} - {assessment['latency']['message']}")
        print(f"   Accuracy:   {assessment['accuracy']['status']:10s} - {assessment['accuracy']['message']}")
        print(f"   Reliability:{assessment['reliability']['status']:10s} - {assessment['reliability']['message']}")
        print(f"\n   Overall: {assessment['overall']} ✅" if assessment['overall'] == 'PASS' else f"\n   Overall: {assessment['overall']} ⚠️")
        
        # Save report to file
        report_path = Path(__file__).parent / "test_report_extensive.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {report_path}")
    
    def run(self):
        """Run the complete test suite"""
        try:
            if not self.setup():
                return False
            
            self.run_warmup_phase()
            main_test_results = self.run_main_test_phase()
            stress_test_results = self.run_stress_test()
            metrics, health = self.get_final_metrics()
            
            report = self.generate_report(main_test_results, stress_test_results, metrics, health)
            
            print("\n" + "="*80)
            print("✅ EXTENSIVE TEST SUITE COMPLETE")
            print("="*80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    test = ExtensiveWarmupTest()
    success = test.run()
    sys.exit(0 if success else 1)
