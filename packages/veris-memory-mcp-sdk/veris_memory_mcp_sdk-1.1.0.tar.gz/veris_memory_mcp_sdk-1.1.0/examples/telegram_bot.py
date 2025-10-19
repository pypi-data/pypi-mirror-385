#!/usr/bin/env python3
"""
Telegram Bot Example using Veris Memory MCP SDK.

This example demonstrates how to build a Telegram bot that integrates with
Veris Memory to store and retrieve conversation context.

Installation:
    pip install veris-memory-mcp-sdk python-telegram-bot

Usage:
    1. Create a bot with @BotFather on Telegram
    2. Set environment variables:
       export TELEGRAM_BOT_TOKEN="your-bot-token"
       export VERIS_MEMORY_SERVER_URL="https://your-veris-instance.com"
       export VERIS_MEMORY_API_KEY="your-api-key"  # Optional
    3. Run: python telegram_bot.py
"""

import asyncio
import logging
import os
from typing import Optional

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
except ImportError:
    print("❌ python-telegram-bot not installed. Run: pip install python-telegram-bot")
    exit(1)

from veris_memory_sdk import MCPClient, MCPConfig, MCPError

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class VerisMemoryBot:
    """Telegram bot with Veris Memory integration."""

    def __init__(self, telegram_token: str, veris_config: MCPConfig):
        """Initialize bot with Telegram token and Veris Memory configuration."""
        self.telegram_token = telegram_token
        self.veris_config = veris_config
        self.mcp_client: Optional[MCPClient] = None
        self.app = Application.builder().token(telegram_token).build()

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register Telegram command and message handlers."""
        # Commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("remember", self.remember_command))
        self.app.add_handler(CommandHandler("recall", self.recall_command))
        self.app.add_handler(CommandHandler("status", self.status_command))

        # Messages (auto-store conversations)
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_bot(self):
        """Start the bot and connect to Veris Memory."""
        logger.info("Starting Telegram bot with Veris Memory integration...")

        # Initialize Veris Memory connection
        self.mcp_client = MCPClient(self.veris_config)
        try:
            await self.mcp_client.connect()
            logger.info("✅ Connected to Veris Memory")
        except MCPError as e:
            logger.error(f"❌ Failed to connect to Veris Memory: {e}")
            return

        # Start Telegram bot
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

        logger.info("🤖 Bot is running! Send /help for commands.")

        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
        finally:
            await self.stop_bot()

    async def stop_bot(self):
        """Stop the bot and disconnect from Veris Memory."""
        if self.app.updater.running:
            await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

        if self.mcp_client:
            await self.mcp_client.disconnect()

        logger.info("Bot stopped.")

    async def start_command(self, update: Update, context):
        """Handle /start command."""
        welcome_text = """
🤖 **Veris Memory Bot**

I can help you store and recall conversations using Veris Memory!

**Commands:**
/remember <text> - Store specific text in memory
/recall <query> - Search and recall stored memories
/status - Check Veris Memory connection
/help - Show this help message

I also automatically store our conversations for future reference.
        """
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

        # Store the welcome interaction
        await self._store_interaction(
            user_id=str(update.effective_user.id),
            user_message="/start",
            bot_response=welcome_text,
            context_type="system",
        )

    async def help_command(self, update: Update, context):
        """Handle /help command."""
        help_text = """
🔍 **How to use Veris Memory Bot:**

**Basic Commands:**
• `/remember <text>` - Store important information
• `/recall <search terms>` - Find stored memories
• `/status` - Check if Veris Memory is connected

**Examples:**
• `/remember Meeting with John scheduled for next Tuesday at 3 PM`
• `/recall meeting John`
• `/recall appointments this week`

**Auto-storage:**
All our conversations are automatically stored with your user ID for privacy and easy retrieval.

**Privacy:**
Your data is stored securely and only accessible to you using your Telegram user ID.
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def remember_command(self, update: Update, context):
        """Handle /remember command to store specific text."""
        if not context.args:
            await update.message.reply_text(
                "Please provide text to remember. Example: `/remember Important meeting tomorrow`",
                parse_mode="Markdown",
            )
            return

        text_to_remember = " ".join(context.args)
        user_id = str(update.effective_user.id)

        try:
            result = await self._store_memory(
                user_id=user_id,
                content={
                    "text": text_to_remember,
                    "type": "user_note",
                    "timestamp": update.message.date.isoformat(),
                    "source": "telegram_remember_command",
                },
                context_type="user_note",
            )

            await update.message.reply_text(
                f"✅ Remembered! Stored with ID: `{result.get('id', 'unknown')}`",
                parse_mode="Markdown",
            )

        except MCPError as e:
            logger.error(f"Failed to store memory: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't store that memory. Please try again."
            )

    async def recall_command(self, update: Update, context):
        """Handle /recall command to search stored memories."""
        if not context.args:
            await update.message.reply_text(
                "Please provide search terms. Example: `/recall meeting tomorrow`",
                parse_mode="Markdown",
            )
            return

        query = " ".join(context.args)
        user_id = str(update.effective_user.id)

        try:
            results = await self._search_memories(user_id=user_id, query=query, limit=5)

            if not results.get("results"):
                await update.message.reply_text(
                    f"🤔 No memories found for: *{query}*", parse_mode="Markdown"
                )
                return

            # Format results
            response_parts = [f"🧠 **Memories for:** {query}\n"]

            for i, memory in enumerate(results["results"][:5], 1):
                content = memory.get("payload", {}).get("content", {})
                memory_text = content.get("text", str(content))
                timestamp = content.get("timestamp", "unknown time")
                score = memory.get("score", 0)

                # Truncate long memories
                if len(memory_text) > 200:
                    memory_text = memory_text[:200] + "..."

                response_parts.append(f"{i}. **{timestamp}** (score: {score:.2f})\n{memory_text}\n")

            response = "\n".join(response_parts)

            # Telegram has message length limits
            if len(response) > 4000:
                response = response[:4000] + "\n\n... (truncated)"

            await update.message.reply_text(response, parse_mode="Markdown")

        except MCPError as e:
            logger.error(f"Failed to recall memories: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't search memories. Please try again."
            )

    async def status_command(self, update: Update, context):
        """Handle /status command to check Veris Memory connection."""
        if not self.mcp_client or not self.mcp_client.connected:
            await update.message.reply_text("❌ Not connected to Veris Memory")
            return

        try:
            # Test connection with a simple query
            user_id = str(update.effective_user.id)
            results = await self._search_memories(user_id=user_id, query="test", limit=1)

            status_text = f"""
✅ **Veris Memory Status: Connected**

• Server: `{self.veris_config.server_url}`
• User ID: `{user_id}`
• Transport: {'WebSocket' if self.veris_config.use_websocket else 'HTTP'}
• Test query successful: {bool(results)}

Ready to store and recall your memories!
            """
            await update.message.reply_text(status_text, parse_mode="Markdown")

        except Exception as e:
            await update.message.reply_text(f"❌ Connection issue: {str(e)}")

    async def handle_message(self, update: Update, context):
        """Handle regular messages (auto-store conversations)."""
        user_message = update.message.text
        user_id = str(update.effective_user.id)

        # Simple auto-response
        truncated_msg = f"{user_message[:50]}{'...' if len(user_message) > 50 else ''}"
        response = f"Thanks for sharing! I've stored this in your memory: '{truncated_msg}'"

        # Store the conversation
        await self._store_interaction(
            user_id=user_id,
            user_message=user_message,
            bot_response=response,
            context_type="conversation",
        )

        await update.message.reply_text(response)

    async def _store_memory(
        self, user_id: str, content: dict, context_type: str = "user_data"
    ) -> dict:
        """Store content in Veris Memory."""
        if not self.mcp_client:
            raise MCPError("MCP client not connected")

        return await self.mcp_client.call_tool(
            tool_name="store_context",
            arguments={
                "type": context_type,
                "content": content,
                "metadata": {"user_id": user_id, "source": "telegram_bot", "platform": "telegram"},
            },
            user_id=user_id,
        )

    async def _search_memories(self, user_id: str, query: str, limit: int = 10) -> dict:
        """Search memories in Veris Memory."""
        if not self.mcp_client:
            raise MCPError("MCP client not connected")

        return await self.mcp_client.call_tool(
            tool_name="retrieve_context",
            arguments={"query": query, "limit": limit, "metadata_filters": {"user_id": user_id}},
            user_id=user_id,
        )

    async def _store_interaction(
        self, user_id: str, user_message: str, bot_response: str, context_type: str
    ):
        """Store a user-bot interaction."""
        try:
            await self._store_memory(
                user_id=user_id,
                content={
                    "user_message": user_message,
                    "bot_response": bot_response,
                    "timestamp": asyncio.get_event_loop().time(),
                    "type": "telegram_interaction",
                },
                context_type=context_type,
            )
        except Exception as e:
            logger.warning(f"Failed to store interaction: {e}")


async def main():
    """Main bot entry point."""
    # Get configuration from environment
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable required")
        exit(1)

    server_url = os.getenv("VERIS_MEMORY_SERVER_URL", "http://localhost:8000")
    api_key = os.getenv("VERIS_MEMORY_API_KEY")

    # Configure Veris Memory
    veris_config = MCPConfig(
        server_url=server_url,
        api_key=api_key,
        use_websocket=False,  # Use HTTP for simplicity
        max_retries=3,
        request_timeout_ms=30000,
    )

    print(f"🚀 Starting Telegram bot...")
    print(f"📡 Veris Memory Server: {server_url}")
    print(f"🔐 API Key: {'✅ Set' if api_key else '❌ Not set'}")

    # Create and start bot
    bot = VerisMemoryBot(telegram_token, veris_config)
    await bot.start_bot()


if __name__ == "__main__":
    asyncio.run(main())
