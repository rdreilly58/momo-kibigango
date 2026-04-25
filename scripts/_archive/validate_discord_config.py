#!/usr/bin/env python3
"""Validate Discord configuration."""

import json
import os
import sys
from pathlib import Path

def validate_discord_config():
    """Validate Discord config file."""
    config_path = Path.home() / ".openclaw/workspace/config/discord.json"
    
    if not config_path.exists():
        print("❌ Config file not found:", config_path)
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    
    # Validate required fields
    required = {
        "bot": ["token", "command_prefix", "status"],
        "server": ["id", "channels"],
        "features": ["auto_threading"]
    }
    
    for section, fields in required.items():
        if section not in config:
            print(f"❌ Missing section: {section}")
            return False
        for field in fields:
            if field not in config[section]:
                print(f"❌ Missing field: {section}.{field}")
                return False
    
    # Validate channel IDs
    channels = config.get("server", {}).get("channels", {})
    if len(channels) != 7:
        print(f"⚠️  Expected 7 channels, got {len(channels)}")
    
    for name, ch_id in channels.items():
        if not str(ch_id).isdigit() or len(str(ch_id)) < 10:
            print(f"❌ Invalid channel ID for {name}: {ch_id}")
            return False
    
    # Validate bot token
    token = config["bot"]["token"]
    if not token or len(token) < 20:
        print(f"❌ Invalid bot token (too short)")
        return False
    
    print("✅ Discord config is valid!")
    print(f"\n📋 Configuration Summary:")
    print(f"  Server ID: {config['server']['id']}")
    print(f"  Bot Token: {token[:20]}...***")
    print(f"  Channels: {len(channels)}")
    print(f"  Features: {', '.join(k for k, v in config['features'].items() if v)}")
    
    return True

if __name__ == "__main__":
    if validate_discord_config():
        sys.exit(0)
    else:
        sys.exit(1)
