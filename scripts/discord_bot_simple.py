#!/usr/bin/env python3
"""
Minimal Discord bot for testing message events
"""

import discord
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
config_path = Path.home() / ".openclaw/config/discord.json"
with open(config_path) as f:
    config = json.load(f)

TOKEN = config['bot']['token']

# Create bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f"✓ Bot logged in as {client.user}")

@client.event
async def on_message(message):
    """Simple message handler"""
    if message.author == client.user:
        return
    
    logger.info(f"Message from {message.author} in #{message.channel.name}: {message.content}")
    
    # Simple response
    if message.channel.name == 'general':
        try:
            await message.reply(f"Momotaro got: {message.content}")
            logger.info(f"Replied to {message.author}")
        except Exception as e:
            logger.error(f"Error sending reply: {e}")

# Run
logger.info("Starting bot...")
client.run(TOKEN)
