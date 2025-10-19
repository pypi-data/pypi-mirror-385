"""
Basic usage example for Veris Memory MCP SDK.

This example demonstrates the fundamental operations:
- Connecting to Veris Memory
- Storing context data
- Retrieving context data
- Using proper error handling
"""

import asyncio
import logging

from veris_memory_sdk import MCPClient, MCPConfig

# Configure logging to see SDK operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_example():
    """Basic example of using Veris Memory MCP SDK."""

    # Configure the client
    config = MCPConfig(
        server_url="http://localhost:8000",
        user_id="example-user-123",
        timeout_ms=30000,
        retry_attempts=3,
    )

    # Create client
    client = MCPClient(config)

    try:
        # Connect to Veris Memory
        await client.connect()
        logger.info("Connected to Veris Memory")

        # Store some context
        context_data = {
            "title": "Project Planning Meeting",
            "type": "decision",
            "content": {
                "decision": "Use MCP protocol for context management",
                "reasoning": "Better integration and standardization",
                "stakeholders": ["engineering", "product"],
                "timeline": "Q1 2024",
            },
        }

        result = await client.store_context(
            context_type="decision",
            content=context_data,
            metadata={"project": "context-store", "priority": "high"},
        )

        logger.info(f"Stored context with ID: {result.get('context_id')}")

        # Retrieve contexts
        contexts = await client.retrieve_context(query="MCP protocol decision", limit=5)

        logger.info(f"Retrieved {len(contexts)} contexts")
        for ctx in contexts:
            logger.info(f"- {ctx.get('content', {}).get('title', 'Untitled')}")

        # Update scratchpad
        await client.update_scratchpad(
            content="Working on MCP integration examples", metadata={"session": "example-session"}
        )

        logger.info("Updated scratchpad")

    except Exception as e:
        logger.error(f"Error in basic example: {e}")
        raise

    finally:
        # Always disconnect
        await client.disconnect()
        logger.info("Disconnected from Veris Memory")


if __name__ == "__main__":
    asyncio.run(basic_example())
