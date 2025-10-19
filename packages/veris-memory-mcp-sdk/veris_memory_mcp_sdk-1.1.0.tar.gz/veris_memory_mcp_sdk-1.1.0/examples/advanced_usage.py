"""
Advanced usage example for Veris Memory MCP SDK.

This example demonstrates:
- Custom configuration and transport policies
- Distributed tracing and monitoring
- Circuit breaker and retry logic
- Comprehensive error handling
- Performance monitoring
"""

import asyncio
import logging

from veris_memory_sdk import MCPClient, MCPConfig
from veris_memory_sdk.monitoring import get_tracer, start_trace
from veris_memory_sdk.transport import CircuitBreakerPolicy, RetryPolicy, TransportPolicy

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def advanced_example():
    """Advanced example with comprehensive configuration and monitoring."""

    # Configure custom retry policy
    retry_policy = RetryPolicy(
        max_attempts=5,
        base_delay_ms=1000,
        max_delay_ms=30000,
        exponential_backoff=True,
        jitter=True,
    )

    # Configure circuit breaker
    circuit_breaker_policy = CircuitBreakerPolicy(
        enabled=True, failure_threshold=3, recovery_timeout_ms=60000, half_open_max_calls=2
    )

    # Create transport policy
    transport_policy = TransportPolicy(
        retry_policy=retry_policy, circuit_breaker_policy=circuit_breaker_policy
    )

    # Configure client with advanced settings
    config = MCPConfig(
        server_url="http://localhost:8000",
        user_id="advanced-user-456",
        timeout_ms=45000,
        retry_attempts=5,
        enable_tracing=True,
        enable_compression=True,
    )

    # Create client with custom transport policy
    client = MCPClient(config, transport_policy=transport_policy)

    # Start distributed trace
    tracer = get_tracer()
    trace = start_trace(
        operation="advanced_context_workflow",
        user_id=config.user_id,
        workflow_type="batch_processing",
    )

    try:
        # Connect with tracing
        with tracer.span("connect_to_veris", trace_id=trace.trace_id) as span:
            await client.connect()
            span.add_tag("server_url", config.server_url)
            span.add_log("info", "Connected successfully")

        # Batch store multiple contexts
        contexts_to_store = [
            {
                "type": "design",
                "content": {
                    "title": "API Design Document",
                    "version": "1.0",
                    "components": ["authentication", "storage", "retrieval"],
                },
                "metadata": {"team": "backend", "status": "draft"},
            },
            {
                "type": "decision",
                "content": {
                    "title": "Database Choice",
                    "decision": "PostgreSQL with vector extensions",
                    "alternatives": ["MongoDB", "Redis", "Elasticsearch"],
                },
                "metadata": {"team": "backend", "status": "approved"},
            },
            {
                "type": "task",
                "content": {
                    "title": "Implement MCP client",
                    "description": "Build production-ready MCP client with retry logic",
                    "assignee": "engineering-team",
                },
                "metadata": {"sprint": "Q1-2024", "priority": "high"},
            },
        ]

        stored_contexts = []

        with tracer.span("batch_store_contexts", count=len(contexts_to_store)):
            for i, context_data in enumerate(contexts_to_store):
                with tracer.span(f"store_context_{i}", context_type=context_data["type"]) as span:
                    try:
                        result = await client.store_context(
                            context_type=context_data["type"],
                            content=context_data["content"],
                            metadata=context_data["metadata"],
                        )

                        stored_contexts.append(result)
                        span.add_tag("context_id", result.get("context_id"))
                        span.add_tag("success", True)
                        span.add_log("info", f"Stored {context_data['type']} context")

                    except Exception as e:
                        span.add_tag("success", False)
                        span.add_log("error", f"Failed to store context: {e}")
                        logger.error(f"Failed to store context {i}: {e}")
                        raise

        logger.info(f"Successfully stored {len(stored_contexts)} contexts")

        # Perform complex retrieval with different queries
        queries = [
            {"query": "API design components", "expected_type": "design"},
            {"query": "database decision PostgreSQL", "expected_type": "decision"},
            {"query": "MCP client implementation", "expected_type": "task"},
        ]

        with tracer.span("batch_retrieve_contexts", query_count=len(queries)):
            all_results = []

            for query_data in queries:
                with tracer.span("retrieve_context", query=query_data["query"]) as span:
                    try:
                        results = await client.retrieve_context(
                            query=query_data["query"],
                            limit=10,
                            context_types=[query_data["expected_type"]],
                        )

                        all_results.extend(results)
                        span.add_tag("result_count", len(results))
                        span.add_tag("query_type", query_data["expected_type"])
                        span.add_log("info", f"Retrieved {len(results)} contexts")

                    except Exception as e:
                        span.add_log("error", f"Query failed: {e}")
                        logger.error(f"Query failed for '{query_data['query']}': {e}")
                        raise

        logger.info(f"Retrieved total of {len(all_results)} contexts across all queries")

        # Update scratchpad with workflow status
        with tracer.span("update_scratchpad") as span:
            scratchpad_content = f"""
            Advanced Workflow Completed:
            - Stored {len(stored_contexts)} contexts
            - Retrieved {len(all_results)} contexts
            - Used advanced retry and circuit breaker policies
            - Comprehensive tracing enabled

            Transport Status:
            {transport_policy.get_status()}
            """

            await client.update_scratchpad(
                content=scratchpad_content.strip(),
                metadata={
                    "workflow": "advanced_example",
                    "contexts_stored": len(stored_contexts),
                    "contexts_retrieved": len(all_results),
                },
            )

            span.add_log("info", "Updated scratchpad with workflow results")

        # Get trace statistics
        trace_stats = tracer.get_trace_stats()
        logger.info(f"Trace statistics: {trace_stats}")

        # Get transport policy status
        transport_status = transport_policy.get_status()
        logger.info(f"Transport policy status: {transport_status}")

    except Exception as e:
        logger.error(f"Error in advanced example: {e}")
        raise

    finally:
        # Finish trace and disconnect
        tracer.finish_trace(trace.trace_id)
        await client.disconnect()
        logger.info("Advanced example completed")


async def demonstrate_error_handling():
    """Demonstrate comprehensive error handling."""

    config = MCPConfig(
        server_url="http://invalid-url:9999",  # Intentionally invalid
        user_id="error-demo-user",
        timeout_ms=5000,
        retry_attempts=2,
    )

    client = MCPClient(config)

    try:
        await client.connect()
    except Exception as e:
        logger.info(f"Expected connection error: {type(e).__name__}: {e}")

    # Try with valid URL but demonstrate other error types
    config.server_url = "http://localhost:8000"
    client = MCPClient(config)

    try:
        await client.connect()

        # Demonstrate validation error
        try:
            await client.store_context(
                context_type="", content={}, metadata={}  # Invalid empty type
            )
        except Exception as e:
            logger.info(f"Expected validation error: {type(e).__name__}: {e}")

    except Exception as e:
        logger.info(f"Connection error (server may not be running): {e}")

    finally:
        await client.disconnect()


if __name__ == "__main__":
    print("Running advanced Veris Memory MCP SDK example...")

    # Run advanced example
    asyncio.run(advanced_example())

    print("\nDemonstrating error handling...")

    # Demonstrate error handling
    asyncio.run(demonstrate_error_handling())
