"""Veris Memory MCP SDK tool execution engine."""

import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .client import MCPClient

from .errors import MCPSecurityError
from .logging_utils import (
    OperationTimer,
    RequestContext,
    clear_request_context,
    create_contextual_logger,
    set_request_context,
)
from .schemas import MCPToolCall, ToolArguments

# Type alias to avoid circular imports
ToolResult = Dict[str, Any]
from .validation import get_validator

logger = create_contextual_logger(__name__)


class ToolExecutor:
    """
    Handles the execution of MCP tool calls with comprehensive validation and logging.

    Separates the concerns of tool execution from the main client logic,
    providing a focused interface for tool operations.
    """

    def __init__(self, client: "MCPClient"):
        """
        Initialize tool executor.

        Args:
            client: Reference to the MCP client
        """
        self.client = client
        self.validator = get_validator()

    async def execute_tool(
        self,
        tool_name: str,
        arguments: ToolArguments,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> ToolResult:
        """
        Execute a tool call with comprehensive validation and logging.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as dictionary
            user_id: User ID for security scoping
            trace_id: Optional trace ID for request tracing
            timeout_ms: Optional timeout override in milliseconds

        Returns:
            Tool response data as dictionary

        Raises:
            MCPValidationError: If validation fails
            MCPSecurityError: If security checks fail
            MCPTimeoutError: If request times out
            MCPConnectionError: If connection fails
            MCPError: For other MCP protocol errors
        """
        # Set up request context for enhanced logging
        request_context = self._create_request_context(
            tool_name, arguments, user_id, trace_id, timeout_ms
        )
        set_request_context(request_context)

        try:
            # Ensure connection
            await self._ensure_connected(trace_id)

            # Security validation
            self._validate_security(tool_name, user_id)

            # Create and validate tool call
            tool_call = self._create_tool_call(tool_name, arguments, trace_id, user_id)
            self._validate_tool_call(tool_call)

            # Execute with comprehensive timing and logging
            return await self._execute_with_timing(tool_call, timeout_ms)

        finally:
            # Always clear request context
            clear_request_context()

    def _create_request_context(
        self,
        tool_name: str,
        arguments: ToolArguments,
        user_id: Optional[str],
        trace_id: Optional[str],
        timeout_ms: Optional[int],
    ) -> RequestContext:
        """Create request context for logging."""
        return RequestContext(
            request_id=trace_id or str(uuid.uuid4())[:8],
            user_id=user_id,
            trace_id=trace_id,
            operation="call_tool",
            tool_name=tool_name,
            metadata={
                "argument_count": len(arguments),
                "timeout_ms": timeout_ms,
                "server_url": self.client.config.server_url,
            },
        )

    async def _ensure_connected(self, trace_id: Optional[str]) -> None:
        """Ensure client is connected."""
        if not self.client.connected:
            await self.client.connect(trace_id)

    def _validate_security(self, tool_name: str, user_id: Optional[str]) -> None:
        """Validate security requirements."""
        if self.client.config.enforce_user_scoping and not user_id:
            logger.log_security_event(
                "missing_user_id",
                f"User ID required for tool {tool_name} when user scoping is enforced",
                tool_name=tool_name,
                enforce_user_scoping=self.client.config.enforce_user_scoping,
            )
            raise MCPSecurityError("user_id is required when user scoping is enforced")

    def _create_tool_call(
        self,
        tool_name: str,
        arguments: ToolArguments,
        trace_id: Optional[str],
        user_id: Optional[str],
    ) -> MCPToolCall:
        """Create tool call object."""
        return MCPToolCall(name=tool_name, arguments=arguments, trace_id=trace_id, user_id=user_id)

    def _validate_tool_call(self, tool_call: MCPToolCall) -> None:
        """Validate tool call with enhanced error handling."""
        if not self.client.config.validate_requests:
            return

        try:
            self.client._validate_tool_call(tool_call)
        except Exception as e:
            logger.log_validation_error(
                "tool_call",
                {"name": tool_call.name, "arguments": tool_call.arguments},
                str(e),
                tool_name=tool_call.name,
            )
            raise

    async def _execute_with_timing(
        self, tool_call: MCPToolCall, timeout_ms: Optional[int]
    ) -> ToolResult:
        """Execute tool call with comprehensive timing and logging."""
        with OperationTimer(
            f"tool_call.{tool_call.name}",
            logger,
            performance_threshold_ms=self.client.config.request_timeout_ms * 0.8,
            tool_name=tool_call.name,
            argument_size=len(str(tool_call.arguments)),
            use_websocket=self.client.config.use_websocket,
        ) as timer:

            # Execute with tracing if enabled
            result = await self._execute_with_tracing(tool_call, timeout_ms, timer)

            # Add result metadata to timer
            timer.add_metadata("result_size", len(str(result)) if result else 0)
            timer.add_metadata("result_type", type(result).__name__)

            return result

    async def _execute_with_tracing(
        self, tool_call: MCPToolCall, timeout_ms: Optional[int], timer: OperationTimer
    ) -> ToolResult:
        """Execute with optional distributed tracing."""
        if self.client.config.enable_tracing and self.client.tracer:
            with self.client.tracer.span(
                f"veris_memory.mcp.call_tool.{tool_call.name}",
                trace_id=tool_call.trace_id,
                tool_name=tool_call.name,
                user_id=hash(tool_call.user_id) if tool_call.user_id else None,
            ) as span:
                span.add_tag("arguments", str(tool_call.arguments)[:200])  # Truncate for logs
                result = await self.client._execute_tool_call(tool_call, timeout_ms)
                timer.add_metadata("tracing_enabled", True)
                return result
        else:
            result = await self.client._execute_tool_call(tool_call, timeout_ms)
            timer.add_metadata("tracing_enabled", False)
            return result


class ToolCallBuilder:
    """
    Builder pattern for constructing MCP tool calls with validation.

    Provides a fluent interface for building complex tool calls
    with automatic validation and security checks.
    """

    def __init__(self, tool_name: str):
        """
        Initialize tool call builder.

        Args:
            tool_name: Name of the tool to call
        """
        self.tool_name = tool_name
        self.arguments: ToolArguments = {}
        self.user_id: Optional[str] = None
        self.trace_id: Optional[str] = None
        self.timeout_ms: Optional[int] = None

    def with_arguments(self, **arguments: Any) -> "ToolCallBuilder":
        """
        Add arguments to the tool call.

        Args:
            **arguments: Tool arguments as keyword arguments

        Returns:
            Self for method chaining
        """
        self.arguments.update(arguments)
        return self

    def with_user_id(self, user_id: str) -> "ToolCallBuilder":
        """
        Set user ID for the tool call.

        Args:
            user_id: User ID for security scoping

        Returns:
            Self for method chaining
        """
        self.user_id = user_id
        return self

    def with_trace_id(self, trace_id: str) -> "ToolCallBuilder":
        """
        Set trace ID for the tool call.

        Args:
            trace_id: Trace ID for request correlation

        Returns:
            Self for method chaining
        """
        self.trace_id = trace_id
        return self

    def with_timeout(self, timeout_ms: int) -> "ToolCallBuilder":
        """
        Set timeout for the tool call.

        Args:
            timeout_ms: Timeout in milliseconds

        Returns:
            Self for method chaining
        """
        self.timeout_ms = timeout_ms
        return self

    async def execute(self, executor: ToolExecutor) -> ToolResult:
        """
        Execute the tool call.

        Args:
            executor: Tool executor to use

        Returns:
            Tool execution result
        """
        return await executor.execute_tool(
            self.tool_name,
            self.arguments,
            self.user_id,
            self.trace_id,
            self.timeout_ms,
        )

    def build(self) -> MCPToolCall:
        """
        Build the tool call object without executing.

        Returns:
            MCPToolCall object
        """
        return MCPToolCall(
            name=self.tool_name,
            arguments=self.arguments,
            trace_id=self.trace_id,
            user_id=self.user_id,
        )


def create_tool_call(tool_name: str) -> ToolCallBuilder:
    """
    Create a new tool call builder.

    Args:
        tool_name: Name of the tool to call

    Returns:
        ToolCallBuilder instance for fluent construction

    Example:
        ```python
        result = await create_tool_call("store_context")
            .with_arguments(content={"text": "Hello"})
            .with_user_id("user123")
            .with_timeout(5000)
            .execute(tool_executor)
        ```
    """
    return ToolCallBuilder(tool_name)
