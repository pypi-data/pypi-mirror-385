"""Veris Memory MCP SDK resource management and cleanup utilities."""

import asyncio
import time
import weakref
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Set
from weakref import WeakSet

from .logging_utils import create_contextual_logger

logger = create_contextual_logger(__name__)


@dataclass
class ResourceInfo:
    """Information about a managed resource."""

    resource_id: str
    """Unique identifier for the resource"""

    resource_type: str
    """Type of resource (connection, file, etc.)"""

    created_at: float
    """Timestamp when resource was created"""

    last_used: float
    """Timestamp when resource was last used"""

    cleanup_callback: Optional[Callable[[], Any]] = None
    """Optional cleanup callback"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional resource metadata"""

    def age_seconds(self) -> float:
        """Get resource age in seconds."""
        return time.time() - self.created_at

    def idle_seconds(self) -> float:
        """Get resource idle time in seconds."""
        return time.time() - self.last_used

    def touch(self) -> None:
        """Update last used timestamp."""
        self.last_used = time.time()


class ResourceManager:
    """
    Comprehensive resource manager for Veris Memory MCP SDK.

    Manages connections, timeouts, cleanup tasks, and resource lifecycle
    to prevent resource leaks and ensure proper cleanup.
    """

    def __init__(self, max_idle_time: float = 300.0, cleanup_interval: float = 60.0):
        """
        Initialize resource manager.

        Args:
            max_idle_time: Maximum idle time before resource cleanup (seconds)
            cleanup_interval: Interval between cleanup cycles (seconds)
        """
        self.max_idle_time = max_idle_time
        self.cleanup_interval = cleanup_interval

        self._resources: Dict[str, ResourceInfo] = {}
        self._cleanup_tasks: WeakSet[asyncio.Task] = WeakSet()
        self._active_operations: WeakSet[asyncio.Task] = WeakSet()
        self._shutdown_event = asyncio.Event()
        self._cleanup_task: Optional[asyncio.Task] = None

        logger.info(
            "Resource manager initialized",
            extra={"max_idle_time": max_idle_time, "cleanup_interval": cleanup_interval},
        )

    async def start(self) -> None:
        """Start the resource manager background tasks."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Resource manager started")

    async def stop(self) -> None:
        """Stop the resource manager and cleanup all resources."""
        logger.info("Stopping resource manager")

        # Signal shutdown
        self._shutdown_event.set()

        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Cancel all active operations
        for task in list(self._active_operations):
            if not task.done():
                task.cancel()

        # Wait for active operations to complete (with timeout)
        if self._active_operations:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._active_operations, return_exceptions=True), timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "Some operations did not complete within timeout during shutdown",
                    extra={"remaining_operations": len(self._active_operations)},
                )

        # Cleanup all managed resources
        await self._cleanup_all_resources()

        logger.info("Resource manager stopped")

    def register_resource(
        self,
        resource_id: str,
        resource_type: str,
        cleanup_callback: Optional[Callable[[], Any]] = None,
        **metadata: Any,
    ) -> None:
        """
        Register a resource for management.

        Args:
            resource_id: Unique identifier for the resource
            resource_type: Type of resource
            cleanup_callback: Optional cleanup function
            **metadata: Additional resource metadata
        """
        now = time.time()
        resource_info = ResourceInfo(
            resource_id=resource_id,
            resource_type=resource_type,
            created_at=now,
            last_used=now,
            cleanup_callback=cleanup_callback,
            metadata=metadata,
        )

        self._resources[resource_id] = resource_info

        logger.debug(
            f"Registered resource: {resource_type}",
            extra={
                "resource_id": resource_id,
                "resource_type": resource_type,
                "total_resources": len(self._resources),
            },
        )

    def unregister_resource(self, resource_id: str) -> None:
        """
        Unregister a resource from management.

        Args:
            resource_id: Resource ID to unregister
        """
        if resource_id in self._resources:
            resource_info = self._resources.pop(resource_id)
            logger.debug(
                f"Unregistered resource: {resource_info.resource_type}",
                extra={
                    "resource_id": resource_id,
                    "resource_type": resource_info.resource_type,
                    "age_seconds": resource_info.age_seconds(),
                    "total_resources": len(self._resources),
                },
            )

    def touch_resource(self, resource_id: str) -> None:
        """
        Update resource last-used timestamp.

        Args:
            resource_id: Resource ID to touch
        """
        if resource_id in self._resources:
            self._resources[resource_id].touch()

    def get_resource_info(self, resource_id: str) -> Optional[ResourceInfo]:
        """
        Get information about a resource.

        Args:
            resource_id: Resource ID

        Returns:
            ResourceInfo or None if not found
        """
        return self._resources.get(resource_id)

    def get_resource_stats(self) -> Dict[str, Any]:
        """
        Get resource manager statistics.

        Returns:
            Dictionary with resource statistics
        """
        now = time.time()
        resource_types: Dict[str, int] = {}
        idle_resources = 0
        old_resources = 0

        for resource in self._resources.values():
            # Count by type
            resource_types[resource.resource_type] = (
                resource_types.get(resource.resource_type, 0) + 1
            )

            # Count idle and old resources
            if resource.idle_seconds() > self.max_idle_time:
                idle_resources += 1
            if resource.age_seconds() > 3600:  # 1 hour
                old_resources += 1

        return {
            "total_resources": len(self._resources),
            "resource_types": resource_types,
            "idle_resources": idle_resources,
            "old_resources": old_resources,
            "active_operations": len(self._active_operations),
            "cleanup_tasks": len(self._cleanup_tasks),
            "max_idle_time": self.max_idle_time,
            "cleanup_interval": self.cleanup_interval,
        }

    @asynccontextmanager
    async def managed_operation(
        self, operation_name: str, timeout_seconds: Optional[float] = None, **metadata: Any
    ) -> AsyncGenerator[None, None]:
        """
        Context manager for managed operations with timeout and cleanup.

        Args:
            operation_name: Name of the operation
            timeout_seconds: Optional timeout for the operation
            **metadata: Additional operation metadata

        Yields:
            None
        """
        task = asyncio.current_task()
        if task:
            self._active_operations.add(task)

        operation_start = time.time()

        logger.debug(
            f"Starting managed operation: {operation_name}",
            extra={
                "operation_name": operation_name,
                "timeout_seconds": timeout_seconds,
                **metadata,
            },
        )

        try:
            # Note: Timeout should be handled by the caller using asyncio.wait_for
            yield

        except asyncio.TimeoutError:
            duration = time.time() - operation_start
            logger.warning(
                f"Operation timed out: {operation_name}",
                extra={
                    "operation_name": operation_name,
                    "timeout_seconds": timeout_seconds,
                    "actual_duration": duration,
                    **metadata,
                },
            )
            raise

        except Exception as e:
            duration = time.time() - operation_start
            logger.error(
                f"Operation failed: {operation_name}",
                extra={
                    "operation_name": operation_name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration": duration,
                    **metadata,
                },
            )
            raise

        finally:
            duration = time.time() - operation_start
            logger.debug(
                f"Completed managed operation: {operation_name}",
                extra={"operation_name": operation_name, "duration": duration, **metadata},
            )

            if task:
                self._active_operations.discard(task)

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        logger.info("Resource cleanup loop started")

        while not self._shutdown_event.is_set():
            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=self.cleanup_interval)
                # If we get here, shutdown was signaled
                break
            except asyncio.TimeoutError:
                # Normal cleanup cycle
                pass

            try:
                await self._cleanup_cycle()
            except Exception as e:
                logger.error(f"Error in cleanup cycle: {e}", extra={"error_type": type(e).__name__})

        logger.info("Resource cleanup loop stopped")

    async def _cleanup_cycle(self) -> None:
        """Perform one cleanup cycle."""
        now = time.time()
        resources_to_cleanup = []

        # Find resources that need cleanup
        for resource_id, resource_info in self._resources.items():
            if resource_info.idle_seconds() > self.max_idle_time:
                resources_to_cleanup.append(resource_id)

        if resources_to_cleanup:
            logger.info(
                f"Cleaning up {len(resources_to_cleanup)} idle resources",
                extra={
                    "idle_resources": len(resources_to_cleanup),
                    "max_idle_time": self.max_idle_time,
                },
            )

            for resource_id in resources_to_cleanup:
                await self._cleanup_resource(resource_id)

    async def _cleanup_resource(self, resource_id: str) -> None:
        """
        Cleanup a specific resource.

        Args:
            resource_id: Resource ID to cleanup
        """
        resource_info = self._resources.get(resource_id)
        if not resource_info:
            return

        logger.debug(
            f"Cleaning up resource: {resource_info.resource_type}",
            extra={
                "resource_id": resource_id,
                "resource_type": resource_info.resource_type,
                "age_seconds": resource_info.age_seconds(),
                "idle_seconds": resource_info.idle_seconds(),
            },
        )

        try:
            if resource_info.cleanup_callback:
                if asyncio.iscoroutinefunction(resource_info.cleanup_callback):
                    await resource_info.cleanup_callback()
                else:
                    resource_info.cleanup_callback()
        except Exception as e:
            logger.error(
                f"Error cleaning up resource {resource_id}: {e}",
                extra={
                    "resource_id": resource_id,
                    "resource_type": resource_info.resource_type,
                    "error_type": type(e).__name__,
                },
            )
        finally:
            # Always remove from tracking
            self.unregister_resource(resource_id)

    async def _cleanup_all_resources(self) -> None:
        """Cleanup all managed resources."""
        resource_ids = list(self._resources.keys())

        if resource_ids:
            logger.info(
                f"Cleaning up all {len(resource_ids)} resources",
                extra={"total_resources": len(resource_ids)},
            )

            for resource_id in resource_ids:
                await self._cleanup_resource(resource_id)


# Global resource manager instance
_resource_manager: Optional[ResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """
    Get global resource manager instance.

    Returns:
        Global ResourceManager instance
    """
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


def set_resource_manager(manager: ResourceManager) -> None:
    """
    Set global resource manager instance.

    Args:
        manager: New resource manager instance
    """
    global _resource_manager
    _resource_manager = manager


async def ensure_resource_manager_started() -> None:
    """Ensure the global resource manager is started."""
    manager = get_resource_manager()
    await manager.start()


async def shutdown_resource_manager() -> None:
    """Shutdown the global resource manager."""
    global _resource_manager
    if _resource_manager:
        await _resource_manager.stop()
        _resource_manager = None


class TimeoutManager:
    """
    Enhanced timeout manager with cascading timeouts and resource cleanup.
    """

    def __init__(self, default_timeout: float = 30.0):
        """
        Initialize timeout manager.

        Args:
            default_timeout: Default timeout in seconds
        """
        self.default_timeout = default_timeout
        self._active_timeouts: Dict[str, asyncio.Task] = {}

    async def with_timeout(
        self,
        operation: Any,
        timeout: Optional[float] = None,
        operation_name: str = "unknown",
        cleanup_callback: Optional[Callable[[], Any]] = None,
    ) -> Any:
        """
        Execute operation with timeout and optional cleanup.

        Args:
            operation: Async operation to execute
            timeout: Timeout in seconds (uses default if None)
            operation_name: Name for logging
            cleanup_callback: Optional cleanup function called on timeout

        Returns:
            Operation result

        Raises:
            asyncio.TimeoutError: If operation times out
        """
        timeout = timeout or self.default_timeout

        logger.debug(
            f"Starting operation with timeout: {operation_name}",
            extra={"timeout_seconds": timeout, "operation_name": operation_name},
        )

        try:
            result = await asyncio.wait_for(operation, timeout=timeout)
            logger.debug(
                f"Operation completed within timeout: {operation_name}",
                extra={"timeout_seconds": timeout, "operation_name": operation_name},
            )
            return result

        except asyncio.TimeoutError:
            logger.warning(
                f"Operation timed out: {operation_name}",
                extra={"timeout_seconds": timeout, "operation_name": operation_name},
            )

            # Call cleanup if provided
            if cleanup_callback:
                try:
                    if asyncio.iscoroutinefunction(cleanup_callback):
                        await cleanup_callback()
                    else:
                        cleanup_callback()
                except Exception as e:
                    logger.error(
                        f"Error in timeout cleanup for {operation_name}: {e}",
                        extra={"operation_name": operation_name, "error_type": type(e).__name__},
                    )

            raise
