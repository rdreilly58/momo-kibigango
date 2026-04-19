#!/usr/bin/env python3
"""
Flask wrapper for Hybrid Pyramid Decoder
Starts daemon server on localhost:7779
"""

import os
import sys
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify

# Disable GPU/MPS for stability
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# Add workspace to path
sys.path.insert(0, str(Path.home() / ".openclaw/workspace"))

from hybrid_pyramid_decoder import HybridPyramidDecoder, HybridConfig

# Configure logging
log_dir = Path.home() / ".openclaw/logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'config4-flask.log')
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Initialize decoder (lazy - load on first request)
_decoder = None
_config = None

def get_decoder():
    global _decoder, _config
    if _decoder is None:
        logger.info("Initializing HybridPyramidDecoder...")
        _config = HybridConfig()
        _decoder = HybridPyramidDecoder(_config)
        logger.info("✅ Decoder initialized and ready")
    return _decoder

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        decoder = get_decoder()
        return jsonify({
            "status": "healthy",
            "service": "hybrid-pyramid-decoder",
            "device": decoder.config.device,
            "models": {
                "draft": "Qwen/Qwen2.5-0.5B-Instruct",
                "qualifier": "microsoft/phi-2",
                "target": "claude-opus-4-1-20250805"
            },
            "stats": {
                "total_requests": decoder.stats.get("total_requests", 0),
                "local_accepted": decoder.stats.get("local_accepted", 0),
                "api_fallbacks": decoder.stats.get("api_fallbacks", 0),
                "total_cost": f"${decoder.stats.get('total_cost', 0):.4f}"
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    """Generate response using hybrid pyramid"""
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt')
        max_tokens = data.get('max_tokens', 100)
        
        if not prompt:
            return jsonify({"error": "prompt is required"}), 400
        
        logger.info(f"Generating for prompt: {prompt[:50]}...")
        decoder = get_decoder()
        result = decoder.generate(prompt, max_tokens)
        
        logger.info(f"Generation complete: source={result.get('source')}, confidence={result.get('confidence'):.2f}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get decoder statistics"""
    try:
        decoder = get_decoder()
        return jsonify({
            "stats": decoder.stats,
            "cost_per_request": f"${decoder.stats.get('total_cost', 0) / max(decoder.stats.get('total_requests', 1), 1):.4f}"
        }), 200
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Welcome endpoint"""
    return jsonify({
        "service": "Hybrid Pyramid Decoder (Config 4)",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "generate": "POST /generate (payload: {prompt, max_tokens})",
            "stats": "GET /stats"
        },
        "documentation": "See https://github.com/rdreilly58/momo-kibidango"
    }), 200

if __name__ == '__main__':
    logger.info("="*80)
    logger.info("🍑 Starting Config 4 Hybrid Pyramid Decoder Server")
    logger.info("="*80)
    logger.info("Listening on http://127.0.0.1:7779")
    logger.info("Health check: curl http://127.0.0.1:7779/health")
    logger.info("Generate: curl -X POST http://127.0.0.1:7779/generate -d '{\"prompt\": \"...\"}'")
    logger.info("="*80)
    
    app.run(
        host='127.0.0.1',
        port=7779,
        debug=False,
        use_reloader=False,
        threaded=True
    )
