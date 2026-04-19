#!/usr/bin/env python3
"""
Flask REST API for Hybrid Pyramid Decoder
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
import time
import os
import argparse
from datetime import datetime
from hybrid_pyramid_decoder import HybridPyramidDecoder

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hybrid_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global decoder instance
decoder = None
config = None
startup_time = None


def load_config(config_path='hybrid_config.json'):
    """Load configuration"""
    global config
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def initialize_decoder():
    """Initialize the decoder with timing"""
    global decoder, startup_time
    
    logger.info("Initializing Hybrid Pyramid Decoder...")
    start = time.time()
    
    # Get API key from environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("No ANTHROPIC_API_KEY found. Opus fallback will be disabled.")
    
    # Create decoder
    decoder = HybridPyramidDecoder(
        draft_model_id=config['models']['draft']['id'],
        qualifier_model_id=config['models']['qualifier']['id'],
        similarity_model_id=config['models']['similarity']['id'],
        anthropic_api_key=api_key
    )
    
    startup_time = time.time() - start
    logger.info(f"Decoder initialized in {startup_time:.2f} seconds")
    
    # Validate startup time
    target_startup = config['targets']['startup_time']
    if startup_time <= target_startup:
        logger.info(f"✅ Startup time {startup_time:.2f}s <= target {target_startup}s")
    else:
        logger.warning(f"❌ Startup time {startup_time:.2f}s > target {target_startup}s")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    if decoder is None:
        return jsonify({
            'status': 'initializing',
            'message': 'Decoder not yet initialized'
        }), 503
    
    metrics = decoder.get_metrics()
    
    # Check if we're meeting targets
    targets_met = {
        'acceptance_rate': metrics.get('acceptance_rate', 0) >= config['targets']['acceptance_rate'],
        'average_latency': metrics.get('average_latency', float('inf')) <= config['targets']['average_latency']
    }
    
    return jsonify({
        'status': 'healthy',
        'uptime': time.time() - startup_time if startup_time else 0,
        'startup_time': startup_time,
        'metrics': metrics,
        'targets_met': targets_met,
        'config': config
    })


@app.route('/generate', methods=['POST'])
def generate():
    """Main generation endpoint"""
    if decoder is None:
        return jsonify({
            'error': 'Decoder not initialized'
        }), 503
    
    # Parse request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    max_tokens = data.get('max_tokens', 100)
    
    # Log request
    logger.info(f"Generate request: prompt_length={len(prompt)}, max_tokens={max_tokens}")
    
    try:
        # Generate
        result = decoder.generate(prompt, max_tokens)
        
        # Log result
        logger.info(f"Generation complete: source={result['source']}, latency={result['latency']:.2f}s, cost=${result['cost']:.4f}")
        
        # Check if meeting latency target
        if result['latency'] <= config['targets']['average_latency']:
            logger.info(f"✅ Latency {result['latency']:.2f}s <= target {config['targets']['average_latency']}s")
        else:
            logger.warning(f"❌ Latency {result['latency']:.2f}s > target {config['targets']['average_latency']}s")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/metrics', methods=['GET'])
def metrics():
    """Get current metrics"""
    if decoder is None:
        return jsonify({'error': 'Decoder not initialized'}), 503
    
    return jsonify(decoder.get_metrics())


@app.route('/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify(config)


@app.route('/config/thresholds', methods=['PUT'])
def update_thresholds():
    """Update confidence thresholds"""
    if decoder is None:
        return jsonify({'error': 'Decoder not initialized'}), 503
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    # Update thresholds
    for task_type, threshold in data.items():
        if task_type in decoder.thresholds:
            old_value = decoder.thresholds[task_type]
            decoder.thresholds[task_type] = threshold
            logger.info(f"Updated threshold for {task_type}: {old_value} -> {threshold}")
    
    return jsonify({
        'thresholds': decoder.thresholds,
        'message': 'Thresholds updated'
    })


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Hybrid Pyramid Decoder API')
    parser.add_argument('--config', default='hybrid_config.json', help='Config file path')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=7779, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Load config
    load_config(args.config)
    
    # Override config with command line args
    if args.host:
        config['api']['host'] = args.host
    if args.port:
        config['api']['port'] = args.port
    if args.debug:
        config['api']['debug'] = args.debug
    
    # Initialize decoder
    initialize_decoder()
    
    # Run Flask app
    logger.info(f"Starting API server on {config['api']['host']}:{config['api']['port']}")
    app.run(
        host=config['api']['host'],
        port=config['api']['port'],
        debug=config['api']['debug']
    )


if __name__ == '__main__':
    main()