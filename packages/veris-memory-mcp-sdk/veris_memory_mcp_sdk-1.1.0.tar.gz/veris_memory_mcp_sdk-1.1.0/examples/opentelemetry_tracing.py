#!/usr/bin/env python3
"""
OpenTelemetry Tracing Example using Veris Memory MCP SDK.

This example demonstrates how to integrate OpenTelemetry distributed tracing
with the Veris Memory SDK for comprehensive observability.

Installation:
    pip install veris-memory-mcp-sdk[monitoring] opentelemetry-api \\
                opentelemetry-sdk opentelemetry-exporter-jaeger

Usage:
    1. Start Jaeger (optional, for visualization):
       docker run -d --name jaeger -p 16686:16686 -p 14268:14268 jaegertracing/all-in-one:latest
    2. Set environment variables:
       export VERIS_MEMORY_SERVER_URL="https://your-veris-instance.com"
       export VERIS_MEMORY_API_KEY="your-api-key"  # Optional
       export JAEGER_ENDPOINT="http://localhost:14268/api/traces"  # Optional
    3. Run: python opentelemetry_tracing.py
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, Optional

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import Status, StatusCode
except ImportError:
    print(
        "❌ OpenTelemetry not installed. Run: pip install opentelemetry-api "
        "opentelemetry-sdk opentelemetry-exporter-jaeger"
    )
    exit(1)

from veris_memory_sdk import MCPClient, MCPConfig, MCPError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TracedMemoryService:
    """Example service with comprehensive OpenTelemetry tracing."""

    def __init__(self, veris_config: MCPConfig, service_name: str = "memory-service"):
        """Initialize service with tracing configuration."""
        self.veris_config = veris_config
        self.service_name = service_name
        self.mcp_client: Optional[MCPClient] = None

        # Initialize OpenTelemetry
        self._setup_tracing()
        self.tracer = trace.get_tracer(__name__)

    def _setup_tracing(self):
        """Configure OpenTelemetry with Jaeger exporter."""
        # Create resource with service information
        resource = Resource.create(
            {
                "service.name": self.service_name,
                "service.version": "1.1.0",
                "service.namespace": "veris-memory",
            }
        )

        # Set tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))

        # Configure Jaeger exporter (optional)
        jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
        if jaeger_endpoint:
            try:
                jaeger_exporter = JaegerExporter(
                    endpoint=jaeger_endpoint,
                    # collector_endpoint=jaeger_endpoint,  # Alternative for gRPC
                )

                span_processor = BatchSpanProcessor(jaeger_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
                logger.info(f"✅ Jaeger tracing configured: {jaeger_endpoint}")

            except Exception as e:
                logger.warning(f"Failed to setup Jaeger exporter: {e}")
        else:
            logger.info("ℹ️  Running without external trace collection")

    async def start(self):
        """Start the service with tracing."""
        with self.tracer.start_as_current_span("service_startup") as span:
            span.set_attribute("service.name", self.service_name)
            span.set_attribute("config.server_url", self.veris_config.server_url)

            try:
                logger.info("Starting traced memory service...")
                self.mcp_client = MCPClient(self.veris_config)
                await self.mcp_client.connect()

                span.set_attribute("startup.success", True)
                span.set_status(Status(StatusCode.OK, "Service started successfully"))
                logger.info("✅ Service started with tracing enabled")

            except Exception as e:
                span.set_attribute("startup.success", False)
                span.set_attribute("error.message", str(e))
                span.set_status(Status(StatusCode.ERROR, f"Startup failed: {e}"))
                logger.error(f"❌ Service startup failed: {e}")
                raise

    async def stop(self):
        """Stop the service with tracing."""
        with self.tracer.start_as_current_span("service_shutdown") as span:
            try:
                if self.mcp_client:
                    await self.mcp_client.disconnect()

                span.set_status(Status(StatusCode.OK, "Service stopped successfully"))
                logger.info("Service stopped")

            except Exception as e:
                span.set_attribute("error.message", str(e))
                span.set_status(Status(StatusCode.ERROR, f"Shutdown failed: {e}"))
                raise

    async def store_with_tracing(
        self,
        context_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "traced_user",
    ) -> Optional[str]:
        """Store context with detailed tracing."""
        with self.tracer.start_as_current_span("store_context_operation") as span:
            # Add span attributes
            span.set_attribute("operation.type", "store_context")
            span.set_attribute("context.type", context_type)
            span.set_attribute("user.id", user_id)
            span.set_attribute("content.size_bytes", len(str(content)))

            if metadata:
                for key, value in metadata.items():
                    span.set_attribute(f"metadata.{key}", str(value))

            try:
                start_time = time.time()

                # Call the SDK
                result = await self.mcp_client.call_tool(
                    tool_name="store_context",
                    arguments={
                        "type": context_type,
                        "content": content,
                        "metadata": metadata or {},
                    },
                    user_id=user_id,
                )

                duration_ms = (time.time() - start_time) * 1000

                # Record success metrics
                context_id = result.get("id", "unknown")
                span.set_attribute("context.id", context_id)
                span.set_attribute("operation.duration_ms", duration_ms)
                span.set_attribute("operation.success", True)
                span.set_status(Status(StatusCode.OK, "Context stored successfully"))

                # Add timing event
                span.add_event(
                    "context_stored", {"context_id": context_id, "duration_ms": duration_ms}
                )

                logger.info(f"✅ Stored context: {context_id} ({duration_ms:.1f}ms)")
                return context_id

            except MCPError as e:
                # Record error details
                span.set_attribute("operation.success", False)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                span.set_attribute("error.code", getattr(e, "code", "unknown"))

                if hasattr(e, "trace_id"):
                    span.set_attribute("error.trace_id", e.trace_id)

                span.set_status(Status(StatusCode.ERROR, f"Store failed: {e}"))
                span.add_event(
                    "error_occurred", {"error.type": type(e).__name__, "error.message": str(e)}
                )

                logger.error(f"❌ Store failed: {e}")
                return None

    async def retrieve_with_tracing(
        self, query: str, limit: int = 10, user_id: str = "traced_user"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve contexts with detailed tracing."""
        with self.tracer.start_as_current_span("retrieve_context_operation") as span:
            # Add span attributes
            span.set_attribute("operation.type", "retrieve_context")
            span.set_attribute("query.text", query)
            span.set_attribute("query.limit", limit)
            span.set_attribute("user.id", user_id)

            try:
                start_time = time.time()

                # Call the SDK
                results = await self.mcp_client.call_tool(
                    tool_name="retrieve_context",
                    arguments={
                        "query": query,
                        "limit": limit,
                        "metadata_filters": {"user_id": user_id},
                    },
                    user_id=user_id,
                )

                duration_ms = (time.time() - start_time) * 1000

                # Record success metrics
                result_count = len(results.get("results", []))
                span.set_attribute("results.count", result_count)
                span.set_attribute("operation.duration_ms", duration_ms)
                span.set_attribute("operation.success", True)
                span.set_status(Status(StatusCode.OK, "Contexts retrieved successfully"))

                # Add timing event
                span.add_event(
                    "contexts_retrieved", {"result_count": result_count, "duration_ms": duration_ms}
                )

                logger.info(f"✅ Retrieved {result_count} contexts ({duration_ms:.1f}ms)")
                return results

            except MCPError as e:
                # Record error details
                span.set_attribute("operation.success", False)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                span.set_attribute("error.code", getattr(e, "code", "unknown"))

                span.set_status(Status(StatusCode.ERROR, f"Retrieve failed: {e}"))
                span.add_event(
                    "error_occurred", {"error.type": type(e).__name__, "error.message": str(e)}
                )

                logger.error(f"❌ Retrieve failed: {e}")
                return None

    async def batch_operations_with_tracing(
        self, operations: list, user_id: str = "traced_user"
    ) -> Dict[str, Any]:
        """Execute batch operations with tracing."""
        with self.tracer.start_as_current_span("batch_operations") as span:
            span.set_attribute("operation.type", "batch_operations")
            span.set_attribute("batch.size", len(operations))
            span.set_attribute("user.id", user_id)

            try:
                start_time = time.time()

                # Prepare tool calls with tracing context
                tool_calls = []
                for i, op in enumerate(operations):
                    tool_calls.append(
                        {
                            "name": "store_context",
                            "arguments": {
                                "type": op.get("context_type", "batch_item"),
                                "content": op.get("content", {}),
                                "metadata": {
                                    **op.get("metadata", {}),
                                    "batch_index": i,
                                    "trace_id": span.get_span_context().trace_id,
                                },
                            },
                            "user_id": user_id,
                            "trace_id": f"batch-{i}-{int(time.time())}",
                        }
                    )

                # Execute batch with controlled concurrency
                results = await self.mcp_client.call_tools(
                    tool_calls=tool_calls, max_concurrency=5, timeout_ms=60000
                )

                duration_ms = (time.time() - start_time) * 1000

                # Analyze results
                successful = sum(1 for r in results if not r.error)
                failed = len(results) - successful

                # Record batch metrics
                span.set_attribute("batch.successful", successful)
                span.set_attribute("batch.failed", failed)
                span.set_attribute("batch.duration_ms", duration_ms)
                span.set_attribute("batch.ops_per_second", len(operations) / (duration_ms / 1000))

                if failed == 0:
                    span.set_status(Status(StatusCode.OK, "Batch completed successfully"))
                else:
                    span.set_status(
                        Status(StatusCode.ERROR, f"Batch partially failed: {failed} errors")
                    )

                # Add batch completion event
                span.add_event(
                    "batch_completed",
                    {"successful": successful, "failed": failed, "duration_ms": duration_ms},
                )

                logger.info(
                    f"✅ Batch completed: {successful} success, {failed} failed "
                    f"({duration_ms:.1f}ms)"
                )

                return {
                    "total": len(operations),
                    "successful": successful,
                    "failed": failed,
                    "duration_ms": duration_ms,
                    "results": results,
                }

            except Exception as e:
                span.set_attribute("batch.success", False)
                span.set_attribute("error.message", str(e))
                span.set_status(Status(StatusCode.ERROR, f"Batch failed: {e}"))
                logger.error(f"❌ Batch operation failed: {e}")
                raise

    async def workflow_example(self, workflow_name: str = "example_workflow"):
        """Example workflow with nested spans."""
        with self.tracer.start_as_current_span(f"workflow_{workflow_name}") as workflow_span:
            workflow_span.set_attribute("workflow.name", workflow_name)
            workflow_span.set_attribute("workflow.version", "1.0")

            try:
                # Step 1: Store initial context
                with self.tracer.start_as_current_span("workflow_step_1") as step1_span:
                    step1_span.set_attribute("step.name", "store_initial_context")

                    context_id = await self.store_with_tracing(
                        context_type="workflow",
                        content={
                            "workflow_name": workflow_name,
                            "step": "initial",
                            "timestamp": time.time(),
                        },
                        metadata={"workflow_id": workflow_name, "step": 1},
                    )

                    step1_span.set_attribute("context.id", context_id or "failed")

                # Step 2: Store additional contexts
                with self.tracer.start_as_current_span("workflow_step_2") as step2_span:
                    step2_span.set_attribute("step.name", "store_batch_contexts")

                    batch_operations = [
                        {
                            "context_type": "workflow_data",
                            "content": {"data": f"item_{i}", "value": i * 10},
                            "metadata": {"workflow_id": workflow_name, "item": i},
                        }
                        for i in range(5)
                    ]

                    batch_result = await self.batch_operations_with_tracing(batch_operations)
                    step2_span.set_attribute("batch.successful", batch_result["successful"])

                # Step 3: Search for stored contexts
                with self.tracer.start_as_current_span("workflow_step_3") as step3_span:
                    step3_span.set_attribute("step.name", "search_contexts")

                    search_results = await self.retrieve_with_tracing(
                        query=f"workflow {workflow_name}", limit=10
                    )

                    if search_results:
                        step3_span.set_attribute(
                            "search.results", len(search_results.get("results", []))
                        )

                workflow_span.set_status(Status(StatusCode.OK, "Workflow completed successfully"))
                logger.info(f"✅ Workflow '{workflow_name}' completed successfully")

            except Exception as e:
                workflow_span.set_attribute("workflow.error", str(e))
                workflow_span.set_status(Status(StatusCode.ERROR, f"Workflow failed: {e}"))
                logger.error(f"❌ Workflow '{workflow_name}' failed: {e}")
                raise


async def main():
    """Main tracing example."""
    # Configuration
    server_url = os.getenv("VERIS_MEMORY_SERVER_URL", "http://localhost:8000")
    api_key = os.getenv("VERIS_MEMORY_API_KEY")

    veris_config = MCPConfig(
        server_url=server_url,
        api_key=api_key,
        max_retries=3,
        request_timeout_ms=30000,
        enable_tracing=True,  # Enable SDK internal tracing
    )

    print(f"🚀 Starting OpenTelemetry Tracing Example")
    print(f"📡 Veris Memory Server: {server_url}")
    print(f"🔐 API Key: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"📊 Jaeger Endpoint: {os.getenv('JAEGER_ENDPOINT', 'Not configured')}")

    # Create traced service
    service = TracedMemoryService(veris_config, service_name="tracing-example")
    await service.start()

    try:
        # Example 1: Basic operations with tracing
        print("\n📊 Example 1: Basic traced operations...")

        context_id = await service.store_with_tracing(
            context_type="example",
            content={
                "title": "OpenTelemetry Example",
                "description": "Demonstrating distributed tracing with Veris Memory",
                "features": ["spans", "attributes", "events", "status"],
            },
            metadata={"example": "basic_tracing", "version": "1.0"},
        )

        if context_id:
            results = await service.retrieve_with_tracing(query="OpenTelemetry tracing", limit=5)
            print(f"Found {len(results.get('results', []))} contexts")

        # Example 2: Batch operations with tracing
        print("\n📊 Example 2: Batch operations with tracing...")

        batch_ops = [
            {
                "context_type": "performance_metric",
                "content": {"metric": "response_time", "value": 100 + i * 10, "unit": "ms"},
                "metadata": {"service": "api", "environment": "production"},
            }
            for i in range(10)
        ]

        batch_result = await service.batch_operations_with_tracing(batch_ops)
        print(
            f"Batch completed: {batch_result['successful']} successful, "
            f"{batch_result['failed']} failed"
        )

        # Example 3: Complex workflow with nested spans
        print("\n📊 Example 3: Complex workflow tracing...")

        await service.workflow_example("telemetry_demo")

        print("\n✅ All tracing examples completed!")
        print("🔍 Check Jaeger UI at http://localhost:16686 for trace visualization")

    except KeyboardInterrupt:
        print("\n⏹️  Tracing example interrupted by user")
    except Exception as e:
        logger.error(f"Example error: {e}")
    finally:
        await service.stop()
        print("🏁 Tracing example completed")


if __name__ == "__main__":
    asyncio.run(main())
