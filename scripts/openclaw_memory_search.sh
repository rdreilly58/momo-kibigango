#!/bin/bash
# Wrapper script for OpenClaw memory_search integration
# Usage: openclaw_memory_search.sh "search query"

# Check if query provided
if [ -z "$1" ]; then
    echo "Usage: $0 \"search query\""
    exit 1
fi

# Navigate to workspace and activate venv
cd ~/.openclaw/workspace || exit 1
source venv/bin/activate 2>/dev/null || {
    echo "Error: Virtual environment not found. Run setup first."
    exit 1
}

# Run memory search
python scripts/memory_search.py "$1" --top-k 5 --json 2>/dev/null || {
    echo "[]"  # Return empty array on error
    exit 1
}