"""Veris Memory MCP SDK interfaces and abstract base classes."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol

from .schemas import MCPToolCall, ToolArguments

# Type aliases defined here to avoid circular imports
JSONDict = Dict[str, Any]
JSONList = List[JSONDict]
ToolResult = Dict[str, Any]


class MCPTransport(Protocol):
    """
    Protocol for MCP transport implementations.

    Defines the interface that all transport implementations
    (HTTP, WebSocket, etc.) must implement.
    """

    async def connect(self, server_url: str, headers: Dict[str, str]) -> None:
        """
        Connect to the MCP server.

        Args:
            server_url: Server URL to connect to
            headers: Headers to include in connection
        """
        ...

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        ...

    async def call_tool(
        self, tool_call: MCPToolCall, timeout_ms: Optional[int] = None
    ) -> ToolResult:
        """
        Execute a tool call via this transport.

        Args:
            tool_call: Tool call to execute
            timeout_ms: Optional timeout override

        Returns:
            Tool execution result
        """
        ...

    def is_connected(self) -> bool:
        """
        Check if transport is connected.

        Returns:
            True if connected, False otherwise
        """
        ...


class MCPClientInterface(Protocol):
    """
    Protocol defining the core MCP client interface.

    This interface can be implemented by different client types
    (basic, enhanced, mock, etc.) while maintaining compatibility.
    """

    async def connect(self, trace_id: Optional[str] = None) -> None:
        """Connect to Veris Memory MCP server."""
        ...

    async def disconnect(self) -> None:
        """Disconnect from Veris Memory MCP server."""
        ...

    async def call_tool(
        self,
        tool_name: str,
        arguments: ToolArguments,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> ToolResult:
        """Call a Veris Memory MCP tool."""
        ...

    async def list_tools(self, trace_id: Optional[str] = None) -> JSONList:
        """List available Veris Memory MCP tools."""
        ...

    async def get_status(self, trace_id: Optional[str] = None) -> JSONDict:
        """Get Veris Memory server status."""
        ...


class ToolValidator(ABC):
    """
    Abstract base class for tool validation strategies.

    Allows different validation approaches for different environments
    (development, staging, production) or tool types.
    """

    @abstractmethod
    def validate_tool_name(self, tool_name: str) -> None:
        """
        Validate tool name.

        Args:
            tool_name: Tool name to validate

        Raises:
            MCPValidationError: If validation fails
        """
        pass

    @abstractmethod
    def validate_arguments(self, arguments: ToolArguments, tool_name: str) -> None:
        """
        Validate tool arguments.

        Args:
            arguments: Arguments to validate
            tool_name: Tool name for context

        Raises:
            MCPValidationError: If validation fails
        """
        pass

    @abstractmethod
    def validate_user_context(self, user_id: Optional[str], tool_name: str) -> None:
        """
        Validate user context for tool execution.

        Args:
            user_id: User ID to validate
            tool_name: Tool name for context

        Raises:
            MCPSecurityError: If validation fails
        """
        pass


class ConnectionManager(ABC):
    """
    Abstract base class for connection management strategies.

    Handles different connection approaches (pooled, single, mock, etc.)
    while providing a consistent interface.
    """

    @abstractmethod
    async def get_connection(self, server_url: str) -> MCPTransport:
        """
        Get a connection to the specified server.

        Args:
            server_url: Server URL to connect to

        Returns:
            Connected transport instance
        """
        pass

    @abstractmethod
    async def release_connection(self, connection: MCPTransport) -> None:
        """
        Release a connection back to the pool or close it.

        Args:
            connection: Connection to release
        """
        pass

    @abstractmethod
    async def close_all(self) -> None:
        """Close all managed connections."""
        pass


class ErrorHandler(ABC):
    """
    Abstract base class for error handling strategies.

    Allows different error handling approaches for different
    environments or requirements.
    """

    @abstractmethod
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if an error should trigger a retry.

        Args:
            error: The exception that occurred
            attempt: Current attempt number (1-based)

        Returns:
            True if the operation should be retried
        """
        pass

    @abstractmethod
    def get_retry_delay(self, error: Exception, attempt: int) -> float:
        """
        Get delay before next retry attempt.

        Args:
            error: The exception that occurred
            attempt: Current attempt number (1-based)

        Returns:
            Delay in seconds before retry
        """
        pass

    @abstractmethod
    def handle_final_error(self, error: Exception, attempts: int) -> Exception:
        """
        Handle the final error after all retries are exhausted.

        Args:
            error: The final exception
            attempts: Total number of attempts made

        Returns:
            Exception to raise (may be transformed or wrapped)
        """
        pass


class MetricsCollector(Protocol):
    """
    Protocol for metrics collection implementations.

    Allows different metrics backends (Prometheus, StatsD, etc.)
    while maintaining a consistent interface.
    """

    def increment_counter(
        self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Increment a counter metric.

        Args:
            name: Metric name
            value: Value to increment by
            tags: Optional tags/labels
        """
        ...

    def record_histogram(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a histogram/timing metric.

        Args:
            name: Metric name
            value: Value to record
            tags: Optional tags/labels
        """
        ...

    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge metric.

        Args:
            name: Metric name
            value: Value to set
            tags: Optional tags/labels
        """
        ...


class CacheProvider(Protocol):
    """
    Protocol for caching implementations.

    Supports different cache backends (Redis, Memcached, in-memory)
    for caching tool results, connection metadata, etc.
    """

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        ...

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional time-to-live in seconds
        """
        ...

    async def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key to delete
        """
        ...

    async def clear(self) -> None:
        """Clear all cached values."""
        ...


class ConfigurationProvider(ABC):
    """
    Abstract base class for configuration providers.

    Supports different configuration sources (file, environment,
    remote config service, etc.) with hot reloading capabilities.
    """

    @abstractmethod
    def get_string(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get string configuration value."""
        pass

    @abstractmethod
    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Get integer configuration value."""
        pass

    @abstractmethod
    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        """Get boolean configuration value."""
        pass

    @abstractmethod
    def get_list(self, key: str, default: Optional[List[str]] = None) -> Optional[List[str]]:
        """Get list configuration value."""
        pass

    @abstractmethod
    def reload(self) -> None:
        """Reload configuration from source."""
        pass


class HealthChecker(Protocol):
    """
    Protocol for health checking implementations.

    Provides standardized health checking across different
    service types and environments.
    """

    async def check_health(self) -> Dict[str, Any]:
        """
        Perform health check.

        Returns:
            Health check results with status and details
        """
        ...

    async def check_readiness(self) -> Dict[str, Any]:
        """
        Perform readiness check.

        Returns:
            Readiness check results with status and details
        """
        ...

    def get_health_status(self) -> str:
        """
        Get current health status.

        Returns:
            Health status string (HEALTHY, UNHEALTHY, UNKNOWN)
        """
        ...
