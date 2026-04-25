#!/bin/bash
# Start 3-Tier Speculative Decoding Daemon
# Pyramid: Qwen2.5-0.5B (draft) → Phi-2 2.7B (qualifier) → Qwen2.5-7B (target)

set -e

WORKSPACE="$HOME/.openclaw/workspace"
MOMO_KIBIDANGO="$WORKSPACE/momo-kibidango"
LOG_DIR="$HOME/.openclaw/logs"
VENV="$HOME/.openclaw/speculative-env"

echo "🚀 Starting 3-Tier Speculative Decoding Daemon"
echo ""

# Activate virtual environment
if [ ! -d "$VENV" ]; then
    echo "❌ Virtual environment not found at $VENV"
    exit 1
fi

source "$VENV/bin/activate"

# Create Flask wrapper
cd "$MOMO_KIBIDANGO"

python3 << 'PYTHON_SERVER'
import sys
sys.path.insert(0, '/Users/rreilly/.openclaw/workspace/momo-kibidango/src')

from speculative_3model import PyramidSpeculativeDecoder, ModelConfig
from speculative_logging import init_logger, get_logger
from flask import Flask, request, jsonify
import logging
import time
import traceback

# Set up logging
logging.basicConfig(
    filename='/Users/rreilly/.openclaw/logs/speculative-3tier.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
decoder = None
logger = None

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
    global decoder, logger
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 100)
        draft_len = data.get('draft_len', 6)
        
        if not decoder:
            return jsonify({"error": "Models not loaded"}), 500
        
        # Log request
        logger.log_request(len(prompt), max_tokens, draft_len)
        
        # Generate with 3-tier pyramid
        start_time = time.time()
        result = decoder.generate_pyramid(prompt, max_tokens=max_tokens)
        elapsed = time.time() - start_time
        
        # Calculate metrics
        tokens_generated = len(decoder.target_tokenizer.encode(result['generated_text']))
        throughput = tokens_generated / elapsed if elapsed > 0 else 0
        
        # Get memory usage
        try:
            import psutil
            process = psutil.Process()
            memory_gb = process.memory_info().rss / 1e9
        except:
            memory_gb = 0
        
        # Log result
        logger.log_generation(tokens_generated, elapsed, throughput, memory_gb)
        
        return jsonify({
            "prompt": prompt,
            "generated_text": result.get("generated_text", ""),
            "tokens_generated": tokens_generated,
            "time_taken_seconds": round(elapsed, 3),
            "throughput_tokens_per_sec": round(throughput, 2),
            "memory_gb": round(memory_gb, 3),
            "draft_acceptance_rate": result.get("draft_acceptance_rate", 0),
            "qualifier_acceptance_rate": result.get("qualifier_acceptance_rate", 0),
            "tier_mode": "3-model-pyramid"
        })
    
    except Exception as e:
        logger.log_error(str(e))
        logging.error(f"Generation error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    if not decoder:
        return jsonify({"status": "loading"})
    
    try:
        import psutil
        process = psutil.Process()
        memory_gb = process.memory_info().rss / 1e9
    except:
        memory_gb = 0
    
    stats = logger.get_stats() if logger else {}
    
    return jsonify({
        "status": "ready",
        "mode": "3-tier-pyramid",
        "memory_gb": round(memory_gb, 3),
        "test_stats": stats
    })

if __name__ == '__main__':
    try:
        logging.info("Loading 3-tier pyramid speculative decoding...")
        print("🚀 Loading 3-tier pyramid models...", flush=True)
        
        # Initialize logger
        logger = init_logger()
        logger.log_server_start()
        
        # Load decoder
        config = ModelConfig()
        decoder = PyramidSpeculativeDecoder(config)
        
        logging.info("3-tier pyramid models loaded successfully")
        print("✅ 3-tier pyramid ready on 127.0.0.1:7779", flush=True)
        
        # Start Flask server
        app.run(host='127.0.0.1', port=7779, debug=False, use_reloader=False)
    
    except Exception as e:
        logging.error(f"Startup error: {e}\n{traceback.format_exc()}")
        print(f"❌ Error: {e}", flush=True)
        sys.exit(1)
    
    finally:
        if logger:
            logger.flush()
            logger.log_server_stop()
PYTHON_SERVER

