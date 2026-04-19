#!/bin/bash
# Start script for Hybrid Pyramid Decoder API server

echo "========================================"
echo "Hybrid Pyramid Decoder Server"
echo "========================================"

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: ANTHROPIC_API_KEY not set!"
    echo "The system will run in local-only mode (no Opus fallback)."
    echo ""
    echo "To enable Opus fallback, set your API key:"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for Python dependencies
echo "Checking dependencies..."
python3 -c "import torch, transformers, sentence_transformers, anthropic, flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Missing dependencies. Please install:"
    echo "  pip install torch transformers sentence-transformers anthropic flask flask-cors"
    exit 1
fi

# Default config
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-7779}
CONFIG=${CONFIG:-hybrid_config.json}
DEBUG=${DEBUG:-false}

echo ""
echo "Starting server with:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Config: $CONFIG"
echo "  Debug: $DEBUG"
echo ""

# Create logs directory
mkdir -p logs

# Start server with unbuffered output
export PYTHONUNBUFFERED=1
python3 hybrid_flask_api.py \
    --host "$HOST" \
    --port "$PORT" \
    --config "$CONFIG" \
    $([ "$DEBUG" = "true" ] && echo "--debug")