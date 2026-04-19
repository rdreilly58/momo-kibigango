#!/bin/bash
# Convenience script to run Discord bot with proper venv

VENV_PATH="$HOME/.openclaw/workspace/discord-env"
SCRIPT_PATH="$HOME/.openclaw/workspace/scripts/discord_bot.py"

echo "🤖 Starting Momotaro Discord bot..."
echo ""

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
  echo "❌ Virtual environment not found at: $VENV_PATH"
  echo ""
  echo "Creating venv..."
  python3 -m venv "$VENV_PATH"
  
  echo "Installing dependencies..."
  source "$VENV_PATH/bin/activate"
  pip install -q discord.py
  
  echo "✅ Venv created and dependencies installed"
  echo ""
fi

# Activate venv
source "$VENV_PATH/bin/activate"

# Run bot
echo "🟢 Bot starting... (Press Ctrl+C to stop)"
echo ""
python3 "$SCRIPT_PATH"
