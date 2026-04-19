#!/usr/bin/env python3
"""
Discord bot integration for OpenClaw/Momotaro
Handles message routing, Telegraph integration, and subagent updates

USAGE:
  source ~/.openclaw/workspace/discord-env/bin/activate
  python3 ~/.openclaw/workspace/scripts/discord_bot.py
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Ensure we're using the venv
venv_path = Path.home() / ".openclaw/workspace/discord-env/bin/python3"
if str(sys.executable) != str(venv_path):
    print(f"⚠️  Not using venv. Activate with:")
    print(f"   source ~/.openclaw/workspace/discord-env/bin/activate")
    print(f"Then run this script again.")
    sys.exit(1)

import discord
from discord.ext import commands, tasks

# Configure logging
log_path = Path.home() / ".openclaw" / "logs" / "discord_bot.log"
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MomotaroBot(commands.Cog):
    """Discord bot for Momotaro/OpenClaw integration"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = self._load_config()
        self.message_archive = []
        
    def _load_config(self) -> Dict:
        """Load Discord configuration from ~/.openclaw/config/discord.json"""
        config_path = Path.home() / ".openclaw" / "config" / "discord.json"
        
        if not config_path.exists():
            logger.error(f"Discord config not found: {config_path}")
            return {}
            
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info("Discord config loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to load Discord config: {e}")
            return {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Bot is ready and connected"""
        logger.info(f"✓ Bot logged in as {self.bot.user}")
        logger.info(f"✓ Connected to server: {self.config.get('server', {}).get('id')}")
        
        # Start background tasks
        self.archive_cleanup.start()
        
        # Set bot status
        status = self.config.get('bot', {}).get('status', 'Playing with Momotaro')
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=status
        ))
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        
        # Ignore bot's own messages
        if message.author == self.bot.user:
            return
        
        # DEBUG: Log all messages
        channel_name = message.channel.name if message.channel else "unknown"
        logger.info(f"Message received in #{channel_name} from {message.author}: {message.content[:50]}")
        
        # Log message to archive
        self._archive_message(message)
        
        # Respond to mentions OR messages in #general
        is_mention = self.bot.user in message.mentions
        is_general = message.channel.name == 'general' if message.channel else False
        
        logger.info(f"  is_mention={is_mention}, is_general={is_general}")
        
        if is_mention:
            logger.info("  → Handling as mention")
            await self._handle_mention(message)
        elif is_general:
            logger.info("  → Handling as general message")
            # Respond to all messages in #general
            await self._handle_general_message(message)
        
        # Handle commands
        await self.bot.process_commands(message)
    
    async def _handle_mention(self, message: discord.Message):
        """Handle @Momotaro mentions"""
        
        # Extract message text (remove bot mention)
        content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
        
        if not content:
            await message.reply("👋 Hi! How can I help?")
            return
        
        logger.info(f"[{message.channel.name}] {message.author} (mention): {content}")
        
        # Show typing indicator
        async with message.channel.typing():
            # Route to Momotaro (main agent)
            response = await self._route_to_momotaro(content, message.author.name)
        
        # Send response (split if too long)
        await self._send_response(message, response)
    
    async def _handle_general_message(self, message: discord.Message):
        """Handle messages in #general channel"""
        
        content = message.content.strip()
        
        if not content or len(content) < 2:
            return
        
        logger.info(f"[{message.channel.name}] {message.author}: {content}")
        
        # Show typing indicator
        async with message.channel.typing():
            # Route to Momotaro (main agent)
            response = await self._route_to_momotaro(content, message.author.name)
        
        # Send response (split if too long)
        await self._send_response(message, response)
    
    async def _route_to_momotaro(self, content: str, author: str) -> str:
        """Route message to Momotaro (main agent)"""
        
        # This would normally call the main agent via IPC/API
        # For now, return a placeholder response
        logger.info(f"Routing to Momotaro: {content[:50]}...")
        
        # TODO: Implement actual routing to main agent
        return f"Received message from {author}: {content[:100]}..."
    
    async def _send_response(self, message: discord.Message, response: str):
        """Send response, splitting if necessary"""
        
        # Discord max message length
        MAX_LENGTH = 2000
        
        if len(response) <= MAX_LENGTH:
            await message.reply(response)
            logger.info(f"Response sent to {message.author}")
        else:
            # Split into multiple messages or use threads
            if self.config.get('features', {}).get('auto_threading'):
                await self._send_as_thread(message, response)
            else:
                # Split into chunks
                for i in range(0, len(response), MAX_LENGTH):
                    chunk = response[i:i+MAX_LENGTH]
                    await message.reply(chunk)
                logger.info(f"Response sent as {len(response) // MAX_LENGTH + 1} messages")
    
    async def _send_as_thread(self, message: discord.Message, content: str):
        """Send response as thread to keep chat clean"""
        
        try:
            thread = await message.create_thread(
                name="Momotaro Response",
                auto_archive_duration=1440  # 24 hours
            )
            
            # Send long response in thread
            MAX_LENGTH = 2000
            for i in range(0, len(content), MAX_LENGTH):
                chunk = content[i:i+MAX_LENGTH]
                await thread.send(chunk)
            
            logger.info(f"Response sent as thread: {thread.id}")
            
        except Exception as e:
            logger.error(f"Failed to create thread: {e}")
            # Fallback to chunks
            await self._send_response(message, content[:500] + "...(truncated)")
    
    def _archive_message(self, message: discord.Message):
        """Archive message for searchability"""
        
        archive_entry = {
            "timestamp": datetime.now().isoformat(),
            "author": message.author.name,
            "channel": message.channel.name,
            "content": message.content,
            "message_id": message.id,
            "attachments": [a.filename for a in message.attachments]
        }
        
        self.message_archive.append(archive_entry)
        
        # Periodically save to disk (every 100 messages)
        if len(self.message_archive) >= 100:
            self._save_archive()
    
    def _save_archive(self):
        """Save message archive to disk"""
        
        archive_dir = Path.home() / ".openclaw" / "workspace" / "discord_archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        archive_file = archive_dir / f"archive_{today}.jsonl"
        
        try:
            with open(archive_file, 'a') as f:
                for entry in self.message_archive:
                    f.write(json.dumps(entry) + "\n")
            
            logger.info(f"Archived {len(self.message_archive)} messages to {archive_file}")
            self.message_archive.clear()
            
        except Exception as e:
            logger.error(f"Failed to save archive: {e}")
    
    @tasks.loop(hours=1)
    async def archive_cleanup(self):
        """Periodic cleanup of old archives"""
        
        archive_dir = Path.home() / ".openclaw" / "workspace" / "discord_archive"
        
        if not archive_dir.exists():
            return
        
        # Save current archive
        self._save_archive()
        
        logger.info("Archive cleanup complete")
    
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Check bot status"""
        
        embed = discord.Embed(
            title="🍑 Momotaro Status",
            color=discord.Color.orange()
        )
        
        embed.add_field(name="Bot", value=self.bot.user, inline=True)
        embed.add_field(name="Server", value=ctx.guild, inline=True)
        embed.add_field(name="Uptime", value="N/A", inline=True)
        embed.add_field(name="Messages Archived", value=len(self.message_archive), inline=True)
        
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command(name='search')
    async def search_archive(self, ctx, *, query: str):
        """Search message archive"""
        
        archive_dir = Path.home() / ".openclaw" / "workspace" / "discord_archive"
        
        if not archive_dir.exists():
            await ctx.send("Archive is empty")
            return
        
        results = []
        query_lower = query.lower()
        
        # Search archived files
        for archive_file in archive_dir.glob("archive_*.jsonl"):
            try:
                with open(archive_file, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        if query_lower in entry.get('content', '').lower():
                            results.append(entry)
            except Exception as e:
                logger.error(f"Error searching {archive_file}: {e}")
        
        if not results:
            await ctx.send(f"No results found for: {query}")
            return
        
        # Format results
        embed = discord.Embed(
            title=f"📚 Search Results: {query}",
            color=discord.Color.blue(),
            description=f"Found {len(results)} matches"
        )
        
        for result in results[:5]:  # Show first 5 results
            embed.add_field(
                name=f"{result['author']} in #{result['channel']}",
                value=result['content'][:100] + "...",
                inline=False
            )
        
        await ctx.send(embed=embed)


async def main():
    """Run the Discord bot"""
    
    # Load config
    config_path = Path.home() / ".openclaw" / "config" / "discord.json"
    
    if not config_path.exists():
        logger.error(f"Discord config not found: {config_path}")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    bot_token = config.get('bot', {}).get('token')
    
    if not bot_token:
        logger.error("Bot token not found in config")
        return
    
    # Create bot with required intents
    # Note: message_content and members are PRIVILEGED intents
    # They MUST be enabled in Discord Developer Portal
    intents = discord.Intents.default()
    intents.message_content = True  # Read message content
    intents.members = True  # Track server members
    
    bot = commands.Bot(
        command_prefix=config.get('bot', {}).get('command_prefix', '!'),
        intents=intents
    )
    
    # Add cog
    cog = MomotaroBot(bot)
    await bot.add_cog(cog)
    
    # Also add direct event listener as backup
    @bot.event
    async def on_message(message: discord.Message):
        """Direct message handler (backup to Cog)"""
        logger.info(f"[Direct] Message from {message.author} in #{message.channel.name}: {message.content[:50]}")
        await cog.on_message(message)
    
    # Start bot
    logger.info("Starting Momotaro Discord bot...")
    await bot.start(bot_token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
