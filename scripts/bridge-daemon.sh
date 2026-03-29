#!/bin/bash
# Wrapper script to run bridge with proper Python environment

source /Users/rreilly/.openclaw/workspace/venv/bin/activate
cd /Users/rreilly/.openclaw/workspace
python3 /Users/rreilly/.openclaw/workspace/scripts/rocketchat-mistral-bridge.py
