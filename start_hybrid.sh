#!/bin/bash
# Start the hybrid pyramid decoder test

set -e  # Exit on error

echo "Starting Hybrid Pyramid Decoder Test..."
echo "======================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages if not already installed
echo "Installing dependencies..."
pip install -q torch transformers anthropic scikit-learn numpy

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY environment variable not set"
    echo "Please set: export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

# Run the test
echo ""
echo "Running tests..."
python3 test_hybrid.py

echo ""
echo "Test complete!"