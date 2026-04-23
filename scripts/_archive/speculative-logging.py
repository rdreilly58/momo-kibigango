#!/usr/bin/env python3
"""
Lightweight Logging for Speculative Decoding
Minimal overhead, maximum insight for 3-day test analysis
"""

import json
import time
from pathlib import Path
from datetime import datetime
from threading import Lock

# Configuration
LOG_DIR = Path.home() / ".openclaw/logs"
METRICS_FILE = LOG_DIR / "speculative-metrics.jsonl"  # JSON Lines format
BATCH_SIZE = 10  # Batch writes for efficiency

class SpeculativeLogger:
    """Lightweight async metrics logger"""
    
    def __init__(self):
        self.log_dir = LOG_DIR
        self.metrics_file = METRICS_FILE
        self.batch = []
        self.lock = Lock()
        self.session_start = time.time()
        
        # Ensure directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def log_request(self, prompt_len, max_tokens, draft_len=4):
        """Log a generation request (lightweight)"""
        with self.lock:
            self.batch.append({
                "type": "request",
                "ts": time.time(),
                "prompt_len": prompt_len,
                "max_tokens": max_tokens,
                "draft_len": draft_len
            })
            self._flush_if_needed()
    
    def log_generation(self, tokens_generated, time_taken, throughput, memory_gb):
        """Log generation result (lightweight)"""
        with self.lock:
            self.batch.append({
                "type": "generation",
                "ts": time.time(),
                "tokens": tokens_generated,
                "time_s": round(time_taken, 3),
                "tok_s": round(throughput, 2),
                "mem_gb": round(memory_gb, 3)
            })
            self._flush_if_needed()
    
    def log_error(self, error_msg):
        """Log an error (important!)"""
        with self.lock:
            self.batch.append({
                "type": "error",
                "ts": time.time(),
                "error": str(error_msg)[:200]  # Truncate to 200 chars
            })
            self._flush_if_needed()
    
    def log_server_start(self):
        """Log server startup"""
        with self.lock:
            self.batch.append({
                "type": "server_start",
                "ts": time.time()
            })
            self._flush()
    
    def log_server_stop(self):
        """Log server shutdown"""
        with self.lock:
            self.batch.append({
                "type": "server_stop",
                "ts": time.time()
            })
            self._flush()
    
    def _flush_if_needed(self):
        """Flush batch if it reaches threshold (non-blocking)"""
        if len(self.batch) >= BATCH_SIZE:
            self._flush()
    
    def _flush(self):
        """Write batch to file (must hold lock)"""
        if not self.batch:
            return
        
        try:
            # Append to JSONL file (very fast, no parsing)
            with open(self.metrics_file, 'a') as f:
                for record in self.batch:
                    f.write(json.dumps(record) + '\n')
            self.batch = []
        except Exception as e:
            # Silently fail to avoid impacting generation
            pass
    
    def flush(self):
        """Explicit flush (call on shutdown)"""
        with self.lock:
            self._flush()
    
    def get_stats(self):
        """Quick stats (for /status endpoint)"""
        try:
            if not self.metrics_file.exists():
                return {"generations": 0, "avg_speed": 0, "errors": 0}
            
            total_gens = 0
            total_time = 0
            total_tokens = 0
            error_count = 0
            
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if record["type"] == "generation":
                        total_gens += 1
                        total_tokens += record.get("tokens", 0)
                        total_time += record.get("time_s", 0)
                    elif record["type"] == "error":
                        error_count += 1
            
            avg_speed = (total_tokens / total_time) if total_time > 0 else 0
            
            return {
                "generations": total_gens,
                "total_tokens": total_tokens,
                "avg_speed": round(avg_speed, 2),
                "total_time_s": round(total_time, 1),
                "errors": error_count
            }
        except:
            return {"error": "stats unavailable"}

# Global logger instance
logger = None

def init_logger():
    """Initialize global logger"""
    global logger
    if logger is None:
        logger = SpeculativeLogger()
        logger.log_server_start()
    return logger

def get_logger():
    """Get or create logger"""
    global logger
    if logger is None:
        init_logger()
    return logger
