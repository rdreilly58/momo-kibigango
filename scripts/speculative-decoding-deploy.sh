#!/bin/bash
# Speculative Decoding Deployment Script
# Deploys Phase 2 of the speculative-decoding research project
# Usage: bash speculative-decoding-deploy.sh [start|stop|status|test]

set -euo pipefail

SPEC_ENV=~/.openclaw/speculative-env
SPEC_DIR=~/.openclaw/workspace/momo-kibidango
SPEC_PID_FILE=/tmp/speculative-decoding.pid
SPEC_LOG=~/.openclaw/logs/speculative-decoding.log

# Create log directory
mkdir -p ~/.openclaw/logs

# Activate environment
activate_env() {
  if [ ! -d "$SPEC_ENV" ]; then
    echo "❌ Environment not found. Run setup first."
    exit 1
  fi
  source "$SPEC_ENV/bin/activate"
}

# Start server
start_server() {
  echo "🚀 Starting Speculative Decoding server..."
  
  activate_env
  cd "$SPEC_DIR"
  
  # Start in background
  python3 << 'PYTHON' > "$SPEC_LOG" 2>&1 &
import sys
sys.path.insert(0, '/Users/rreilly/.openclaw/workspace/momo-kibidango/src')

from speculative_2model_minimal import MinimalSpeculativeDecoder
from flask import Flask, request, jsonify
import json

app = Flask(__name__)
decoder = None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "model": "speculative-2model"})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    max_length = data.get('max_length', 100)
    
    if not decoder:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        result = decoder.speculative_generate(prompt, max_length=max_length)
        return jsonify({"prompt": prompt, "output": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    if not decoder:
        return jsonify({"status": "loading"})
    
    memory = decoder.get_memory_usage()
    return jsonify({"status": "ready", "memory": memory})

if __name__ == '__main__':
    print("Loading models...")
    decoder = MinimalSpeculativeDecoder()
    print("✅ Models loaded, server starting...")
    app.run(host='127.0.0.1', port=7779, debug=False)
PYTHON
  
  PID=$!
  echo $PID > "$SPEC_PID_FILE"
  
  # Wait for startup
  sleep 3
  
  # Check if running
  if kill -0 $PID 2>/dev/null; then
    echo "✅ Speculative Decoding server started (PID: $PID)"
    echo "   Endpoint: http://127.0.0.1:7779"
    echo "   Health: /health"
    echo "   Generate: POST /generate"
    echo "   Status: /status"
  else
    echo "❌ Server failed to start"
    cat "$SPEC_LOG"
    exit 1
  fi
}

# Stop server
stop_server() {
  echo "🛑 Stopping Speculative Decoding server..."
  
  if [ -f "$SPEC_PID_FILE" ]; then
    PID=$(cat "$SPEC_PID_FILE")
    if kill -0 $PID 2>/dev/null; then
      kill $PID
      rm "$SPEC_PID_FILE"
      echo "✅ Server stopped (PID: $PID)"
    else
      echo "⚠️ Server not running"
      rm "$SPEC_PID_FILE"
    fi
  else
    echo "⚠️ No PID file found"
  fi
}

# Check status
server_status() {
  echo "📊 Speculative Decoding Status"
  echo "════════════════════════════════════════════════"
  
  if [ -f "$SPEC_PID_FILE" ]; then
    PID=$(cat "$SPEC_PID_FILE")
    if kill -0 $PID 2>/dev/null; then
      echo "Status: ✅ RUNNING (PID: $PID)"
      echo "Endpoint: http://127.0.0.1:7779"
      
      # Test health
      if command -v curl &> /dev/null; then
        HEALTH=$(curl -s http://127.0.0.1:7779/health 2>/dev/null || echo "unreachable")
        echo "Health: $HEALTH"
      fi
    else
      echo "Status: ❌ STOPPED"
      rm "$SPEC_PID_FILE"
    fi
  else
    echo "Status: ❌ NOT RUNNING"
  fi
  
  echo ""
  echo "Log: $SPEC_LOG"
  echo "Environment: $SPEC_ENV"
  echo "Source: $SPEC_DIR"
}

# Test endpoint
test_endpoint() {
  echo "🧪 Testing Speculative Decoding endpoint..."
  echo ""
  
  activate_env
  
  python3 << 'PYTHON'
import requests
import json

endpoint = "http://127.0.0.1:7779"

try:
    # Test health
    resp = requests.get(f"{endpoint}/health", timeout=5)
    print(f"✅ Health check: {resp.status_code}")
    print(f"   Response: {resp.json()}")
    
    # Test status
    resp = requests.get(f"{endpoint}/status", timeout=5)
    print(f"✅ Status check: {resp.status_code}")
    print(f"   Response: {resp.json()}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("   Is the server running? Try: bash speculative-decoding-deploy.sh start")

PYTHON
}

# Main
case "${1:-status}" in
  start)
    start_server
    ;;
  stop)
    stop_server
    ;;
  status)
    server_status
    ;;
  test)
    test_endpoint
    ;;
  *)
    echo "Usage: bash speculative-decoding-deploy.sh [start|stop|status|test]"
    exit 1
    ;;
esac
