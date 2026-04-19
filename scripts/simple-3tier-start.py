#!/usr/bin/env python3
"""Simple 3-tier Speculative Decoding Flask Server"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/momo-kibidango/src'))
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/scripts'))

from speculative_3model import PyramidSpeculativeDecoder, ModelConfig
from flask import Flask, request, jsonify
import logging
import time
import traceback
import psutil

# Set up logging
logging.basicConfig(
    filename=os.path.expanduser('~/.openclaw/logs/speculative-3tier.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
decoder = None
request_count = 0
total_tokens = 0

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "model": "speculative-3tier-pyramid",
        "status": "ok",
        "tiers": 3,
        "draft": "Qwen2.5-0.5B",
        "qualifier": "Phi-2-2.7B",
        "target": "Qwen2.5-7B"
    })

@app.route('/generate', methods=['POST'])
def generate():
    global decoder, request_count, total_tokens
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 100)
        
        if not decoder:
            return jsonify({"error": "Models not loaded"}), 500
        
        request_count += 1
        
        # Generate with 3-tier pyramid
        start_time = time.time()
        result = decoder.generate(prompt, max_length=max_tokens)
        elapsed = time.time() - start_time
        
        # Calculate metrics
        generated_text = result.get('generated_text', '')
        tokens_generated = len(decoder.target_tokenizer.encode(generated_text))
        total_tokens += tokens_generated
        throughput = tokens_generated / elapsed if elapsed > 0 else 0
        
        # Memory usage
        process = psutil.Process()
        memory_gb = process.memory_info().rss / 1e9
        
        return jsonify({
            "prompt": prompt,
            "generated_text": generated_text,
            "tokens_generated": tokens_generated,
            "time_taken_seconds": round(elapsed, 3),
            "throughput_tokens_per_sec": round(throughput, 2),
            "memory_gb": round(memory_gb, 3),
            "tier_mode": "3-model-pyramid"
        })
    
    except Exception as e:
        logging.error(f"Generation error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    if not decoder:
        return jsonify({"status": "loading"})
    
    process = psutil.Process()
    memory_gb = process.memory_info().rss / 1e9
    
    return jsonify({
        "status": "ready",
        "mode": "3-tier-pyramid",
        "memory_gb": round(memory_gb, 3),
        "requests_served": request_count,
        "total_tokens_generated": total_tokens
    })

if __name__ == '__main__':
    try:
        logging.info("Loading 3-tier pyramid speculative decoding...")
        print("🚀 Loading 3-tier pyramid models...", flush=True)
        
        # Load decoder
        config = ModelConfig()
        decoder = PyramidSpeculativeDecoder(config)
        
        logging.info("3-tier pyramid models loaded successfully")
        print("✅ 3-tier pyramid ready on 127.0.0.1:7779", flush=True)
        
        # Start Flask server
        app.run(host='127.0.0.1', port=7779, debug=False, use_reloader=False, threaded=True)
    
    except Exception as e:
        logging.error(f"Startup error: {e}\n{traceback.format_exc()}")
        print(f"❌ Error: {e}", flush=True)
        sys.exit(1)
