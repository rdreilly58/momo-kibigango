#!/usr/bin/env python3
"""
Metrics tracking and monitoring for Hybrid Pyramid Decoder
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import pandas as pd


class MetricsTracker:
    """Track and analyze metrics for the hybrid decoder"""
    
    def __init__(self, log_file: str = "hybrid_metrics.log"):
        self.log_file = log_file
        self.metrics_data = []
        self.load_existing_metrics()
    
    def load_existing_metrics(self):
        """Load existing metrics from log file"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        self.metrics_data.append(json.loads(line))
                    except:
                        pass
    
    def log_request(self, request_data: Dict):
        """Log a single request"""
        # Add timestamp if not present
        if 'timestamp' not in request_data:
            request_data['timestamp'] = datetime.now().isoformat()
        
        # Append to memory
        self.metrics_data.append(request_data)
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(request_data) + '\n')
    
    def get_metrics_summary(self, time_window: Optional[timedelta] = None) -> Dict:
        """Get summary metrics for a time window"""
        # Filter by time window if specified
        data = self.metrics_data
        if time_window:
            cutoff = datetime.now() - time_window
            data = [m for m in data if datetime.fromisoformat(m['timestamp']) > cutoff]
        
        if not data:
            return {}
        
        # Calculate metrics
        total_requests = len(data)
        local_accepts = sum(1 for m in data if m.get('source') == 'local')
        opus_fallbacks = sum(1 for m in data if m.get('source') == 'opus')
        
        latencies = [m['latency'] for m in data if 'latency' in m]
        costs = [m['cost'] for m in data if 'cost' in m]
        
        # Group by task type
        by_type = defaultdict(lambda: {'total': 0, 'accepted': 0, 'latencies': []})
        for m in data:
            task_type = m.get('task_type', 'unknown')
            by_type[task_type]['total'] += 1
            if m.get('source') == 'local':
                by_type[task_type]['accepted'] += 1
            if 'latency' in m:
                by_type[task_type]['latencies'].append(m['latency'])
        
        # Calculate acceptance rates by type
        acceptance_by_type = {}
        avg_latency_by_type = {}
        for task_type, stats in by_type.items():
            if stats['total'] > 0:
                acceptance_by_type[task_type] = stats['accepted'] / stats['total']
            if stats['latencies']:
                avg_latency_by_type[task_type] = np.mean(stats['latencies'])
        
        return {
            'total_requests': total_requests,
            'acceptance_rate': local_accepts / total_requests if total_requests > 0 else 0,
            'fallback_rate': opus_fallbacks / total_requests if total_requests > 0 else 0,
            'average_latency': np.mean(latencies) if latencies else 0,
            'p95_latency': np.percentile(latencies, 95) if latencies else 0,
            'p99_latency': np.percentile(latencies, 99) if latencies else 0,
            'total_cost': sum(costs),
            'average_cost': np.mean(costs) if costs else 0,
            'acceptance_by_type': acceptance_by_type,
            'avg_latency_by_type': avg_latency_by_type,
            'time_window': str(time_window) if time_window else 'all'
        }
    
    def plot_metrics(self, output_dir: str = "metrics_plots"):
        """Generate visualization plots"""
        os.makedirs(output_dir, exist_ok=True)
        
        if not self.metrics_data:
            print("No data to plot")
            return
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(self.metrics_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # 1. Acceptance rate over time (hourly bins)
        fig, ax = plt.subplots(figsize=(10, 6))
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly = df.groupby('hour').agg({
            'source': lambda x: (x == 'local').sum() / len(x)
        })
        hourly.plot(ax=ax, marker='o')
        ax.set_title('Acceptance Rate Over Time (Hourly)')
        ax.set_ylabel('Local Acceptance Rate')
        ax.axhline(y=0.7, color='r', linestyle='--', label='Target (70%)')
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'acceptance_rate_time.png'))
        plt.close()
        
        # 2. Latency distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        local_latencies = df[df['source'] == 'local']['latency']
        opus_latencies = df[df['source'] == 'opus']['latency']
        
        bins = np.linspace(0, max(df['latency'].max(), 2), 50)
        ax.hist(local_latencies, bins=bins, alpha=0.5, label=f'Local (n={len(local_latencies)})')
        if len(opus_latencies) > 0:
            ax.hist(opus_latencies, bins=bins, alpha=0.5, label=f'Opus (n={len(opus_latencies)})')
        ax.axvline(x=1.0, color='r', linestyle='--', label='Target (<1s)')
        ax.set_xlabel('Latency (seconds)')
        ax.set_ylabel('Count')
        ax.set_title('Latency Distribution by Source')
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'latency_distribution.png'))
        plt.close()
        
        # 3. Task type breakdown
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Acceptance rate by task type
        task_stats = df.groupby('task_type').agg({
            'source': lambda x: (x == 'local').sum() / len(x)
        })
        task_stats.plot(kind='bar', ax=ax1)
        ax1.set_title('Acceptance Rate by Task Type')
        ax1.set_ylabel('Local Acceptance Rate')
        ax1.axhline(y=0.7, color='r', linestyle='--')
        ax1.set_ylim(0, 1)
        
        # Average latency by task type
        task_latency = df.groupby('task_type')['latency'].mean()
        task_latency.plot(kind='bar', ax=ax2)
        ax2.set_title('Average Latency by Task Type')
        ax2.set_ylabel('Latency (seconds)')
        ax2.axhline(y=1.0, color='r', linestyle='--')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'task_type_breakdown.png'))
        plt.close()
        
        # 4. Cost analysis
        fig, ax = plt.subplots(figsize=(10, 6))
        df['cumulative_cost'] = df['cost'].cumsum()
        ax.plot(df['timestamp'], df['cumulative_cost'], marker='o', markersize=3)
        ax.set_title('Cumulative Cost Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Cumulative Cost ($)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'cost_analysis.png'))
        plt.close()
        
        print(f"Plots saved to {output_dir}/")
    
    def generate_report(self) -> str:
        """Generate a comprehensive metrics report"""
        report = []
        report.append("="*80)
        report.append("HYBRID PYRAMID DECODER - METRICS REPORT")
        report.append("="*80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Data points: {len(self.metrics_data)}")
        
        # Overall metrics
        overall = self.get_metrics_summary()
        report.append("\n📊 OVERALL METRICS:")
        report.append(f"- Total requests: {overall['total_requests']}")
        report.append(f"- Acceptance rate: {overall['acceptance_rate']:.1%}")
        report.append(f"- Fallback rate: {overall['fallback_rate']:.1%}")
        report.append(f"- Average latency: {overall['average_latency']:.3f}s")
        report.append(f"- P95 latency: {overall['p95_latency']:.3f}s")
        report.append(f"- P99 latency: {overall['p99_latency']:.3f}s")
        report.append(f"- Total cost: ${overall['total_cost']:.4f}")
        report.append(f"- Average cost per request: ${overall['average_cost']:.4f}")
        
        # By task type
        report.append("\n📈 METRICS BY TASK TYPE:")
        for task_type in ['general', 'math', 'code', 'creative']:
            if task_type in overall['acceptance_by_type']:
                acc_rate = overall['acceptance_by_type'][task_type]
                avg_latency = overall['avg_latency_by_type'].get(task_type, 0)
                report.append(f"\n{task_type.upper()}:")
                report.append(f"  - Acceptance rate: {acc_rate:.1%}")
                report.append(f"  - Average latency: {avg_latency:.3f}s")
        
        # Last hour metrics
        last_hour = self.get_metrics_summary(timedelta(hours=1))
        if last_hour.get('total_requests', 0) > 0:
            report.append("\n⏰ LAST HOUR:")
            report.append(f"- Requests: {last_hour['total_requests']}")
            report.append(f"- Acceptance rate: {last_hour['acceptance_rate']:.1%}")
            report.append(f"- Average latency: {last_hour['average_latency']:.3f}s")
        
        # Performance targets
        report.append("\n✅ TARGET ACHIEVEMENT:")
        targets_met = {
            'Acceptance ≥ 70%': overall['acceptance_rate'] >= 0.70,
            'Average latency < 1s': overall['average_latency'] < 1.0,
            'P95 latency < 2s': overall['p95_latency'] < 2.0,
        }
        
        for target, met in targets_met.items():
            report.append(f"- {target}: {'✅ MET' if met else '❌ NOT MET'}")
        
        return '\n'.join(report)
    
    def monitor_live(self, api_url: str = "http://127.0.0.1:7779", interval: int = 5):
        """Monitor live metrics from API"""
        import requests
        
        print("Starting live monitoring (Ctrl+C to stop)...")
        print(f"Polling {api_url}/metrics every {interval} seconds")
        print("="*80)
        
        try:
            while True:
                try:
                    response = requests.get(f"{api_url}/metrics")
                    if response.status_code == 200:
                        metrics = response.json()
                        
                        # Clear screen
                        os.system('clear' if os.name == 'posix' else 'cls')
                        
                        # Display metrics
                        print("LIVE METRICS DASHBOARD")
                        print("="*80)
                        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"\nTotal requests: {metrics.get('total_requests', 0)}")
                        print(f"Acceptance rate: {metrics.get('acceptance_rate', 0):.1%}")
                        print(f"Average latency: {metrics.get('average_latency', 0):.3f}s")
                        print(f"Total cost: ${metrics.get('total_cost', 0):.4f}")
                        
                        print("\nBy Task Type:")
                        for task_type, rate in metrics.get('acceptance_rates_by_type', {}).items():
                            print(f"  {task_type}: {rate:.1%}")
                        
                except Exception as e:
                    print(f"Error: {e}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


def main():
    """CLI interface for metrics"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hybrid Pyramid Decoder Metrics')
    parser.add_argument('command', choices=['report', 'plot', 'monitor'], 
                       help='Command to run')
    parser.add_argument('--log-file', default='hybrid_metrics.log',
                       help='Metrics log file')
    parser.add_argument('--api-url', default='http://127.0.0.1:7779',
                       help='API URL for monitoring')
    parser.add_argument('--interval', type=int, default=5,
                       help='Monitoring interval in seconds')
    
    args = parser.parse_args()
    
    tracker = MetricsTracker(args.log_file)
    
    if args.command == 'report':
        print(tracker.generate_report())
    elif args.command == 'plot':
        tracker.plot_metrics()
    elif args.command == 'monitor':
        tracker.monitor_live(args.api_url, args.interval)


if __name__ == "__main__":
    main()