#!/usr/bin/env python3
"""
Performance Monitoring Example using Veris Memory MCP SDK.

This example demonstrates performance monitoring, metrics collection,
and health checking with the Veris Memory SDK.

Installation:
    pip install veris-memory-mcp-sdk[monitoring] psutil

Usage:
    1. Set environment variables:
       export VERIS_MEMORY_SERVER_URL="https://your-veris-instance.com"
       export VERIS_MEMORY_API_KEY="your-api-key"  # Optional
    2. Run: python performance_monitoring.py
"""

import asyncio
import logging
import os
import statistics
import sys
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    import psutil
except ImportError:
    print("❌ psutil not installed. Run: pip install psutil")
    exit(1)

from veris_memory_sdk import MCPClient, MCPConfig, MCPError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    operation_type: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    # Request/response details
    request_size_bytes: int = 0
    response_size_bytes: int = 0

    # System metrics at time of operation
    cpu_percent: float = 0.0
    memory_percent: float = 0.0

    # Context about the operation
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceStats:
    """Aggregated performance statistics."""

    operation_type: str
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0

    # Timing statistics
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    p50_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0

    # Throughput
    operations_per_second: float = 0.0

    # Error rates
    error_rate_percent: float = 0.0
    error_types: Dict[str, int] = field(default_factory=dict)

    # System resource usage
    avg_cpu_percent: float = 0.0
    avg_memory_percent: float = 0.0


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""

    def __init__(self, window_size: int = 1000):
        """Initialize performance monitor."""
        self.window_size = window_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.start_time = time.time()

    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric."""
        self.metrics[metric.operation_type].append(metric)

        # Log significant events
        if not metric.success:
            logger.warning(f"Operation failed: {metric.operation_type} - {metric.error_message}")
        elif metric.duration_ms > 5000:  # Slow operation threshold
            logger.warning(f"Slow operation: {metric.operation_type} - {metric.duration_ms:.1f}ms")

    def get_stats(self, operation_type: str) -> Optional[PerformanceStats]:
        """Get aggregated statistics for an operation type."""
        if operation_type not in self.metrics or not self.metrics[operation_type]:
            return None

        metrics_list = list(self.metrics[operation_type])
        stats = PerformanceStats(operation_type=operation_type)

        # Basic counts
        stats.total_operations = len(metrics_list)
        stats.successful_operations = sum(1 for m in metrics_list if m.success)
        stats.failed_operations = stats.total_operations - stats.successful_operations

        # Calculate durations for successful operations
        successful_durations = [m.duration_ms for m in metrics_list if m.success]
        if successful_durations:
            stats.min_duration_ms = min(successful_durations)
            stats.max_duration_ms = max(successful_durations)
            stats.avg_duration_ms = statistics.mean(successful_durations)

            # Percentiles
            sorted_durations = sorted(successful_durations)
            stats.p50_duration_ms = statistics.median(sorted_durations)
            stats.p95_duration_ms = (
                sorted_durations[int(len(sorted_durations) * 0.95)] if sorted_durations else 0
            )
            stats.p99_duration_ms = (
                sorted_durations[int(len(sorted_durations) * 0.99)] if sorted_durations else 0
            )

        # Throughput calculation
        if metrics_list:
            time_span = max(m.end_time for m in metrics_list) - min(
                m.start_time for m in metrics_list
            )
            if time_span > 0:
                stats.operations_per_second = len(metrics_list) / time_span

        # Error analysis
        if stats.total_operations > 0:
            stats.error_rate_percent = (stats.failed_operations / stats.total_operations) * 100

        error_counts = defaultdict(int)
        for m in metrics_list:
            if not m.success and m.error_type:
                error_counts[m.error_type] += 1
        stats.error_types = dict(error_counts)

        # System resource usage
        if metrics_list:
            stats.avg_cpu_percent = statistics.mean(m.cpu_percent for m in metrics_list)
            stats.avg_memory_percent = statistics.mean(m.memory_percent for m in metrics_list)

        return stats

    def get_all_stats(self) -> Dict[str, PerformanceStats]:
        """Get statistics for all operation types."""
        return {
            op_type: self.get_stats(op_type)
            for op_type in self.metrics.keys()
            if self.get_stats(op_type) is not None
        }

    def print_summary(self):
        """Print performance summary to console."""
        print(f"\n📊 Performance Summary (last {self.window_size} operations)")
        print("=" * 80)

        all_stats = self.get_all_stats()
        if not all_stats:
            print("No performance data collected yet.")
            return

        for operation_type, stats in all_stats.items():
            print(f"\n🔹 {operation_type.upper()}")
            print(f"   Total Operations: {stats.total_operations}")
            print(
                f"   Success Rate: {100 - stats.error_rate_percent:.1f}% "
                f"({stats.successful_operations}/{stats.total_operations})"
            )

            if stats.successful_operations > 0:
                print(f"   Response Time:")
                print(f"     Average: {stats.avg_duration_ms:.1f}ms")
                print(f"     P50: {stats.p50_duration_ms:.1f}ms")
                print(f"     P95: {stats.p95_duration_ms:.1f}ms")
                print(f"     P99: {stats.p99_duration_ms:.1f}ms")
                print(
                    f"     Min/Max: {stats.min_duration_ms:.1f}ms / {stats.max_duration_ms:.1f}ms"
                )

            print(f"   Throughput: {stats.operations_per_second:.1f} ops/sec")
            print(
                f"   System Usage: CPU {stats.avg_cpu_percent:.1f}%, "
                f"Memory {stats.avg_memory_percent:.1f}%"
            )

            if stats.error_types:
                print(f"   Error Types: {dict(stats.error_types)}")

        print("=" * 80)


class PerformanceTestSuite:
    """Performance test suite for Veris Memory SDK."""

    def __init__(self, veris_config: MCPConfig):
        """Initialize test suite."""
        self.veris_config = veris_config
        self.mcp_client: Optional[MCPClient] = None
        self.monitor = PerformanceMonitor(window_size=1000)

    async def start(self):
        """Start the test suite."""
        logger.info("Starting performance test suite...")
        self.mcp_client = MCPClient(self.veris_config)
        await self.mcp_client.connect()
        logger.info("✅ Connected to Veris Memory")

    async def stop(self):
        """Stop the test suite."""
        if self.mcp_client:
            await self.mcp_client.disconnect()
        logger.info("Performance test suite stopped")

    async def _execute_with_monitoring(self, operation_type: str, operation_func, **kwargs) -> Any:
        """Execute an operation with performance monitoring."""
        start_time = time.time()
        cpu_before = psutil.cpu_percent()
        memory_before = psutil.virtual_memory().percent

        error_type = None
        error_message = None
        result = None
        success = True

        try:
            result = await operation_func(**kwargs)
        except Exception as e:
            success = False
            error_type = type(e).__name__
            error_message = str(e)
            logger.debug(f"Operation failed: {operation_type} - {error_message}")

        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        # Record performance metric
        metric = PerformanceMetrics(
            operation_type=operation_type,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            success=success,
            error_type=error_type,
            error_message=error_message,
            cpu_percent=cpu_before,
            memory_percent=memory_before,
            metadata=kwargs,
        )

        self.monitor.record_metric(metric)
        return result

    async def test_store_performance(self, count: int = 100, user_id: str = "perf_user"):
        """Test context storage performance."""
        print(f"\n🏃 Running store performance test ({count} operations)...")

        async def store_operation(index: int):
            return await self.mcp_client.call_tool(
                tool_name="store_context",
                arguments={
                    "type": "performance_test",
                    "content": {
                        "test_data": f"Performance test item {index}",
                        "timestamp": time.time(),
                        "index": index,
                        "payload_size": "x" * 100,  # 100 char payload
                    },
                    "metadata": {
                        "test_type": "store_performance",
                        "batch_id": f"batch_{int(time.time())}",
                        "index": index,
                    },
                },
                user_id=user_id,
            )

        # Execute operations
        tasks = []
        for i in range(count):
            task = self._execute_with_monitoring(
                operation_type="store_context", operation_func=store_operation, index=i
            )
            tasks.append(task)

        # Run with controlled concurrency
        semaphore = asyncio.Semaphore(10)  # Limit concurrent operations

        async def bounded_task(task):
            async with semaphore:
                return await task

        results = await asyncio.gather(
            *[bounded_task(task) for task in tasks], return_exceptions=True
        )

        successful = sum(1 for r in results if not isinstance(r, Exception) and r is not None)
        print(f"✅ Store test completed: {successful}/{count} successful")

    async def test_retrieve_performance(self, count: int = 50, user_id: str = "perf_user"):
        """Test context retrieval performance."""
        print(f"\n🔍 Running retrieve performance test ({count} operations)...")

        queries = [
            "performance test",
            "test data item",
            f"batch_{int(time.time())}",
            "timestamp",
            "payload_size",
        ]

        async def retrieve_operation(index: int):
            query = queries[index % len(queries)]
            return await self.mcp_client.call_tool(
                tool_name="retrieve_context",
                arguments={
                    "query": f"{query} {index}",
                    "limit": 5,
                    "metadata_filters": {"user_id": user_id},
                },
                user_id=user_id,
            )

        # Execute operations
        tasks = []
        for i in range(count):
            task = self._execute_with_monitoring(
                operation_type="retrieve_context", operation_func=retrieve_operation, index=i
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful = sum(1 for r in results if not isinstance(r, Exception) and r is not None)
        print(f"✅ Retrieve test completed: {successful}/{count} successful")

    async def test_batch_performance(
        self, batch_sizes: List[int] = [5, 10, 20, 50], user_id: str = "perf_user"
    ):
        """Test batch operation performance."""
        print(f"\n📦 Running batch performance tests...")

        for batch_size in batch_sizes:
            print(f"  Testing batch size: {batch_size}")

            async def batch_operation(size: int):
                tool_calls = []
                for i in range(size):
                    tool_calls.append(
                        {
                            "name": "store_context",
                            "arguments": {
                                "type": "batch_test",
                                "content": {
                                    "batch_item": f"Item {i} in batch of {size}",
                                    "batch_size": size,
                                    "item_index": i,
                                },
                                "metadata": {"batch_size": size, "test_type": "batch_performance"},
                            },
                            "user_id": user_id,
                            "trace_id": f"batch-{size}-{i}",
                        }
                    )

                return await self.mcp_client.call_tools(
                    tool_calls=tool_calls,
                    max_concurrency=min(5, size),  # Reasonable concurrency
                    timeout_ms=60000,
                )

            await self._execute_with_monitoring(
                operation_type=f"batch_operation_{batch_size}",
                operation_func=batch_operation,
                size=batch_size,
            )

        print("✅ Batch performance tests completed")

    async def test_stress_scenario(self, duration_seconds: int = 30, user_id: str = "stress_user"):
        """Run stress test scenario."""
        print(f"\n💪 Running stress test ({duration_seconds}s duration)...")

        start_time = time.time()
        operation_count = 0

        while (time.time() - start_time) < duration_seconds:
            # Mix of operations
            if operation_count % 3 == 0:
                # Store operation
                await self._execute_with_monitoring(
                    operation_type="stress_store",
                    operation_func=lambda: self.mcp_client.call_tool(
                        tool_name="store_context",
                        arguments={
                            "type": "stress_test",
                            "content": {
                                "data": f"stress_{operation_count}",
                                "timestamp": time.time(),
                            },
                            "metadata": {"stress_test": True},
                        },
                        user_id=user_id,
                    ),
                )
            else:
                # Retrieve operation
                await self._execute_with_monitoring(
                    operation_type="stress_retrieve",
                    operation_func=lambda: self.mcp_client.call_tool(
                        tool_name="retrieve_context",
                        arguments={
                            "query": f"stress data {operation_count}",
                            "limit": 3,
                            "metadata_filters": {"user_id": user_id},
                        },
                        user_id=user_id,
                    ),
                )

            operation_count += 1

            # Small delay to prevent overwhelming
            await asyncio.sleep(0.1)

        print(f"✅ Stress test completed: {operation_count} operations in {duration_seconds}s")

    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check."""
        print("\n🏥 Running health check...")

        health_results = {
            "timestamp": time.time(),
            "system_info": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            },
            "connectivity": {},
            "performance": {},
        }

        # Test basic connectivity
        try:
            start_time = time.time()
            result = await self.mcp_client.call_tool(
                tool_name="store_context",
                arguments={
                    "type": "health_check",
                    "content": {"check": "connectivity", "timestamp": start_time},
                    "metadata": {"health_check": True},
                },
                user_id="health_check_user",
            )
            duration_ms = (time.time() - start_time) * 1000

            health_results["connectivity"] = {
                "status": "healthy",
                "response_time_ms": duration_ms,
                "context_id": result.get("id") if result else None,
            }
        except Exception as e:
            health_results["connectivity"] = {"status": "unhealthy", "error": str(e)}

        # Get performance statistics
        all_stats = self.monitor.get_all_stats()
        health_results["performance"] = {
            op_type: {
                "total_ops": stats.total_operations,
                "success_rate": 100 - stats.error_rate_percent,
                "avg_response_time_ms": stats.avg_duration_ms,
                "p95_response_time_ms": stats.p95_duration_ms,
                "throughput_ops_per_sec": stats.operations_per_second,
            }
            for op_type, stats in all_stats.items()
        }

        return health_results


async def main():
    """Main performance monitoring example."""
    # Configuration
    server_url = os.getenv("VERIS_MEMORY_SERVER_URL", "http://localhost:8000")
    api_key = os.getenv("VERIS_MEMORY_API_KEY")

    veris_config = MCPConfig(
        server_url=server_url,
        api_key=api_key,
        max_retries=2,  # Reduce retries for performance testing
        request_timeout_ms=30000,
    )

    print(f"🚀 Starting Performance Monitoring Example")
    print(f"📡 Veris Memory Server: {server_url}")
    print(f"🔐 API Key: {'✅ Set' if api_key else '❌ Not set'}")
    print(
        f"🖥️  System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total // (1024**3)}GB RAM"
    )

    # Create test suite
    test_suite = PerformanceTestSuite(veris_config)
    await test_suite.start()

    try:
        # Run health check first
        health_results = await test_suite.run_health_check()
        print(f"🏥 Health Status: {health_results['connectivity']['status']}")

        if health_results["connectivity"]["status"] != "healthy":
            print("❌ Health check failed, skipping performance tests")
            return

        # Run performance tests
        await test_suite.test_store_performance(count=100)
        test_suite.monitor.print_summary()

        await asyncio.sleep(1)  # Brief pause

        await test_suite.test_retrieve_performance(count=50)
        test_suite.monitor.print_summary()

        await asyncio.sleep(1)  # Brief pause

        await test_suite.test_batch_performance(batch_sizes=[5, 10, 20])
        test_suite.monitor.print_summary()

        # Optional stress test (uncomment to run)
        # print("\n⚠️  Starting stress test in 3 seconds... (Ctrl+C to skip)")
        # await asyncio.sleep(3)
        # await test_suite.test_stress_scenario(duration_seconds=15)

        # Final summary
        print("\n🎯 Final Performance Summary")
        test_suite.monitor.print_summary()

        # Health check after tests
        final_health = await test_suite.run_health_check()
        print(f"\n🏥 Final Health Status: {final_health['connectivity']['status']}")

    except KeyboardInterrupt:
        print("\n⏹️  Performance monitoring interrupted by user")
    except Exception as e:
        logger.error(f"Performance monitoring error: {e}")
    finally:
        await test_suite.stop()
        print("🏁 Performance monitoring completed")


if __name__ == "__main__":
    # Ensure we have required dependencies
    if not hasattr(psutil, "cpu_percent"):
        print("❌ psutil not properly installed")
        sys.exit(1)

    asyncio.run(main())
