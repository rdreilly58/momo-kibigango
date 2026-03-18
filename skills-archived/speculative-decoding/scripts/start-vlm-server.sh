#!/bin/bash

# Start vLLM server with speculative decoding configuration
# Usage: ./start-vlm-server.sh [--docker] [--port 8000] [--model llama-7b-13b]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$( dirname "$SCRIPT_DIR" )"
CONFIG_FILE="$SKILL_DIR/references/vlm-config.json"
LOG_DIR="$SKILL_DIR/logs"

# Defaults
USE_DOCKER=false
PORT=8000
MODEL_PAIR="llama-7b-13b"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --docker) USE_DOCKER=true; shift ;;
    --port) PORT="$2"; shift 2 ;;
    --model) MODEL_PAIR="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Create log directory
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "🚀 Starting vLLM Speculative Decoding"
echo "=========================================="
echo "Config file: $CONFIG_FILE"
echo "Port: $PORT"
echo "Model pair: $MODEL_PAIR"
echo "Docker: $USE_DOCKER"
echo "Logs: $LOG_DIR/vlm-server.log"
echo ""

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Error: Config file not found at $CONFIG_FILE"
  exit 1
fi

if [ "$USE_DOCKER" = true ]; then
  echo "📦 Starting vLLM in Docker..."
  echo ""
  
  # Check Docker is running
  if ! docker ps > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    exit 1
  fi
  
  # Build Docker image (simplified)
  docker run -d \
    --name vlm-speculative \
    --gpus all \
    -p "$PORT:$PORT" \
    -v "$CONFIG_FILE:/app/vlm-config.json" \
    -v "$LOG_DIR:/app/logs" \
    vllm/vllm:latest \
    python -m vllm.entrypoints.openai.api_server \
      --model meta-llama/Llama-2-7b-hf \
      --speculative-model meta-llama/Llama-2-13b-hf \
      --port "$PORT" \
      --dtype float16 \
      --gpu-memory-utilization 0.9
  
  echo "✅ Docker container started"
  echo "Container name: vlm-speculative"
  echo ""
  echo "To view logs:"
  echo "  docker logs -f vlm-speculative"
  echo ""
  echo "To stop:"
  echo "  docker stop vlm-speculative"
  
else
  echo "💻 Starting vLLM locally..."
  echo ""
  
  # Activate venv if it exists
  VENV_DIR="$SKILL_DIR/venv"
  if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    echo "✅ Virtual environment activated"
  fi
  
  # Check if vLLM is installed
  if ! python3 -c "import vllm" 2>/dev/null; then
    echo "❌ Error: vLLM not installed"
    echo "Run: ./install-dependencies.sh"
    exit 1
  fi
  
  # Start vLLM with speculative decoding
  python3 -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-hf \
    --speculative-model meta-llama/Llama-2-13b-hf \
    --port "$PORT" \
    --dtype float16 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 4096 \
    2>&1 | tee "$LOG_DIR/vlm-server.log"
fi

echo ""
echo "=========================================="
echo "✅ vLLM server started successfully!"
echo "=========================================="
echo ""
echo "Test the server:"
echo "  curl http://localhost:$PORT/health"
echo ""
echo "Or run:"
echo "  ./scripts/test-speculative.sh"
