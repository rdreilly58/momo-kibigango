#!/usr/bin/env python3
"""Debug 3-tier with Flask - pinpoint the hang"""

import sys
import os
import time

# Add paths
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/momo-kibidango/src'))

print("Step 1: Importing modules...")
from speculative_3model import PyramidSpeculativeDecoder, ModelConfig
from flask import Flask, jsonify
print("  ✅ Imports complete")

print("Step 2: Loading models...")
start = time.time()
config = ModelConfig()
decoder = PyramidSpeculativeDecoder(config)
print(f"  ✅ Models loaded ({time.time()-start:.1f}s)")

print("Step 3: Creating Flask app...")
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"model": "3tier", "status": "ok"})

@app.route('/test', methods=['GET'])
def test():
    result = decoder.generate("test", max_length=20)
    return jsonify(result)

print("  ✅ Flask app created")

print("Step 4: Starting Flask server on 127.0.0.1:7780...")
print("  (Press Ctrl+C to stop)")
app.run(host='127.0.0.1', port=7780, debug=False, use_reloader=False, threaded=True)
