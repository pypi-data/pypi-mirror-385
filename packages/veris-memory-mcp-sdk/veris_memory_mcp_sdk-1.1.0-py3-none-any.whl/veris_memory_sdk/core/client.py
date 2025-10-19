"""Veris Memory MCP SDK - Async client with comprehensive error handling."""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, Union

# Type aliases for better readability
JSONDict = Dict[str, Any]
JSONList = List[JSONDict]
ToolArguments = Dict[str, Any]
ToolResult = Dict[str, Any]

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import websockets

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

from ..monitoring.tracing import get_tracer, start_trace
from ..transport.http_transport import HTTPClientManager
from ..transport.policies import CircuitBreakerPolicy, RetryPolicy, TransportPolicy
from .config import MCPConfig, MCPConnectionPool
from .errors import (
    MCPConnectionError,
    MCPError,
    MCPSecurityError,
    MCPTimeoutError,
    MCPValidationError,
)
from .logging_utils import (
    OperationTimer,
    RequestContext,
    clear_request_context,
    create_contextual_logger,
    set_request_context,
)
from .resource_manager import TimeoutManager, get_resource_manager
from .schemas import MCPMethod, MCPServerInfo, MCPToolCall
from .tool_executor import ToolExecutor
from .validation import get_validator

logger = create_contextual_logger(__name__)


class MCPClient:
    """
    Veris Memory MCP Client

    A production-ready async client for the Model Context Protocol (MCP) with:
    - Comprehensive error handling and retry logic
    - Circuit breaker pattern for resilience
    - Distributed tracing support
    - User scoping and security enforcement
    - Support for both HTTP and WebSocket transports

    Example:
        ```python
        from veris_memory_sdk import MCPClient, MCPConfig, MCPClientInfo

        config = MCPConfig(
            server_url="https://your-veris-instance.com",
            client_info=MCPClientInfo(name="my-app", version="1.0.0")
        )

        async with MCPClient(config) as client:
            result = await client.call_tool(
                tool_name="store_context",
                arguments={"content": {"text": "Hello", "type": "user_query"}},
                user_id="user123"
            )
        ```
    """

    def __init__(self, config: MCPConfig):
        """Initialize MCP client.

        Args:
            config: MCP configuration object with server URL, timeouts, and policies

        Raises:
            MCPValidationError: If configuration is invalid
        """
        # Validate configuration
        config.validate()

        self.config: MCPConfig = config
        self.server_info: Optional[MCPServerInfo] = None
        self.connected: bool = False
        self._http_client: Optional["httpx.AsyncClient"] = None
        self._ws_connection: Optional[Any] = (
            None  # websockets.WebSocketServerProtocol when available
        )

        # Transport policies
        retry_policy = RetryPolicy(
            max_attempts=config.max_retries,
            base_delay_ms=config.base_delay_ms,
            max_delay_ms=config.max_delay_ms,
            exponential_backoff=config.exponential_backoff,
            jitter=config.jitter,
        )

        circuit_breaker_policy = CircuitBreakerPolicy(
            enabled=config.circuit_breaker_enabled,
            failure_threshold=config.failure_threshold,
            recovery_timeout_ms=config.recovery_timeout_ms,
            half_open_max_calls=config.half_open_max_calls,
        )

        self.transport: TransportPolicy = TransportPolicy(retry_policy, circuit_breaker_policy)

        # Initialize tracer if enabled
        self.tracer: Optional[Any] = get_tracer() if config.enable_tracing else None

        # Initialize resource management
        self.resource_manager = get_resource_manager()
        self.timeout_manager = TimeoutManager(default_timeout=config.request_timeout_ms / 1000.0)
        self._client_id = str(uuid.uuid4())[:8]

        # Initialize tool executor and HTTP client manager
        self.tool_executor = ToolExecutor(self)
        self.http_manager = HTTPClientManager(config)  # type: ignore[misc]

        logger.info(
            f"Initialized Veris Memory MCP client for {config.server_url}",
            extra={
                "client_name": config.client_info.name,
                "client_version": config.client_info.version,
                "use_websocket": config.use_websocket,
                "tracing_enabled": config.enable_tracing,
            },
        )

    async def connect(self, trace_id: Optional[str] = None) -> None:
        """Connect to Veris Memory MCP server.

        Args:
            trace_id: Optional trace ID for request tracing

        Raises:
            MCPConnectionError: If connection fails
            MCPTimeoutError: If connection times out
        """
        if self.connected:
            return

        trace_context = None
        if self.config.enable_tracing and self.tracer:
            trace_context = start_trace(
                operation="veris_memory.mcp.connect",
                trace_id=trace_id,
                server_url=self.config.server_url,
                use_websocket=self.config.use_websocket,
            )

        async def _connect() -> None:
            if self.config.use_websocket:
                await self._connect_websocket()
            else:
                await self._connect_http()

            self.connected = True

        try:
            await self.transport.execute_with_policy(
                _connect,
                operation_name="veris_memory.mcp.connect",
                trace_id=trace_context.trace_id if trace_context else None,
            )

            logger.info("Successfully connected to Veris Memory MCP server")

        except (MCPConnectionError, MCPTimeoutError) as e:
            # Re-raise MCP-specific errors as-is
            logger.error(
                f"Failed to connect to Veris Memory MCP server: {e}",
                extra={"trace_id": trace_context.trace_id if trace_context else None},
            )
            raise
        except asyncio.TimeoutError as e:
            error_msg = f"Connection timed out after {self.config.connect_timeout_ms}ms"
            logger.error(
                error_msg,
                extra={
                    "trace_id": trace_context.trace_id if trace_context else None,
                    "timeout_ms": self.config.connect_timeout_ms,
                },
            )
            raise MCPTimeoutError(
                error_msg, trace_id=trace_context.trace_id if trace_context else None
            ) from e
        except OSError as e:
            error_msg = f"Network error connecting to Veris Memory: {e}"
            logger.error(
                error_msg,
                extra={
                    "trace_id": trace_context.trace_id if trace_context else None,
                    "server_url": self.config.server_url,
                },
            )
            raise MCPConnectionError(
                error_msg, trace_id=trace_context.trace_id if trace_context else None
            ) from e
        except Exception as e:
            error_msg = f"Unexpected error connecting to Veris Memory: {e}"
            logger.error(
                error_msg,
                extra={
                    "trace_id": trace_context.trace_id if trace_context else None,
                    "error_type": type(e).__name__,
                },
            )
            raise MCPConnectionError(
                error_msg, trace_id=trace_context.trace_id if trace_context else None
            ) from e

        finally:
            if trace_context and self.tracer:
                self.tracer.finish_trace(trace_context.trace_id)

    async def _connect_http(self) -> None:
        """Connect via HTTP."""
        if not HTTPX_AVAILABLE:
            raise MCPConnectionError(
                "httpx is required for HTTP connections. Install with: pip install httpx"
            )

        # Create HTTP client with proper configuration
        timeout = httpx.Timeout(
            connect=self.config.connect_timeout_ms / 1000.0,
            read=self.config.request_timeout_ms / 1000.0,
            write=self.config.request_timeout_ms / 1000.0,
            pool=self.config.total_timeout_ms / 1000.0,
        )

        pool = MCPConnectionPool()
        limits = pool.to_httpx_limits()
        if limits is None:
            limits = httpx.Limits()

        self._http_client = httpx.AsyncClient(
            timeout=timeout, limits=limits, headers=self.config.get_http_headers()
        )

        # Update HTTP client manager
        self.http_manager.update_client(self._http_client, self.config.server_url)

        # Register HTTP client as managed resource
        http_resource_id = f"http_client_{self._client_id}"
        self.resource_manager.register_resource(
            resource_id=http_resource_id,
            resource_type="http_client",
            cleanup_callback=lambda: (
                asyncio.create_task(self._http_client.aclose()) if self._http_client else None
            ),
            server_url=self.config.server_url,
            client_id=self._client_id,
        )

        # Test connection with health check
        response = await self._http_client.get(f"{self.config.server_url}/health")
        if response.status_code != 200:
            raise MCPConnectionError(f"Health check failed: {response.status_code}")

        logger.debug("HTTP connection established", extra={"resource_id": http_resource_id})

    async def _connect_websocket(self) -> None:
        """Connect via WebSocket."""
        if not WEBSOCKETS_AVAILABLE:
            raise MCPConnectionError(
                "websockets is required for WebSocket connections. "
                "Install with: pip install websockets"
            )

        ws_url = self.config.server_url.replace("http://", "ws://").replace("https://", "wss://")

        self._ws_connection = await websockets.connect(
            f"{ws_url}/mcp",
            additional_headers=self.config.get_websocket_headers(),
            open_timeout=self.config.connect_timeout_ms / 1000.0,
            close_timeout=self.config.request_timeout_ms / 1000.0,
        )

        # Register WebSocket connection as managed resource
        ws_resource_id = f"websocket_{self._client_id}"
        self.resource_manager.register_resource(
            resource_id=ws_resource_id,
            resource_type="websocket",
            cleanup_callback=lambda: (
                asyncio.create_task(self._ws_connection.close()) if self._ws_connection else None
            ),
            server_url=ws_url,
            client_id=self._client_id,
        )

        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "method": MCPMethod.INITIALIZE.value,
            "params": {
                "protocolVersion": self.config.client_info.protocol_version,
                "clientInfo": self.config.client_info.to_dict(),
            },
            "id": str(uuid.uuid4()),
        }

        await self._send_ws(init_message)
        response = await self._receive_ws()

        if "error" in response:
            raise MCPConnectionError(f"Initialization failed: {response['error']}")

        # Store server info
        result = response.get("result", {})
        if "serverInfo" in result:
            self.server_info = MCPServerInfo.from_dict(result["serverInfo"])

        logger.debug("WebSocket connection established")

    async def disconnect(self) -> None:
        """Disconnect from Veris Memory MCP server with proper resource cleanup."""
        logger.info("Disconnecting from Veris Memory MCP server")

        # Unregister and cleanup WebSocket
        if self._ws_connection:
            ws_resource_id = f"websocket_{self._client_id}"
            self.resource_manager.unregister_resource(ws_resource_id)
            try:
                await self._ws_connection.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")
            finally:
                self._ws_connection = None

        # Unregister and cleanup HTTP client
        if self._http_client:
            http_resource_id = f"http_client_{self._client_id}"
            self.resource_manager.unregister_resource(http_resource_id)
            try:
                await self._http_client.aclose()
            except Exception as e:
                logger.warning(f"Error closing HTTP client: {e}")
            finally:
                self._http_client = None

        self.connected = False
        logger.info("Disconnected from Veris Memory MCP server")

    async def call_tool(
        self,
        tool_name: str,
        arguments: ToolArguments,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> ToolResult:
        """Call a Veris Memory MCP tool with comprehensive error handling.

        Args:
            tool_name: Name of the tool to call (e.g., "store_context", "retrieve_context")
            arguments: Tool arguments as dictionary
            user_id: User ID for security scoping (required if enforce_user_scoping is True)
            trace_id: Optional trace ID for request tracing
            timeout_ms: Optional timeout override in milliseconds

        Returns:
            Tool response data as dictionary

        Raises:
            MCPValidationError: If validation fails
            MCPSecurityError: If security checks fail (e.g., missing user_id)
            MCPTimeoutError: If request times out
            MCPConnectionError: If connection fails
            MCPError: For other MCP protocol errors

        Example:
            ```python
            # Store context
            result = await client.call_tool(
                tool_name="store_context",
                arguments={
                    "type": "log",
                    "content": {
                        "text": "User said hello",
                        "type": "user_query",
                        "title": "User Message"
                    }
                },
                user_id="user123"
            )

            # Retrieve context
            results = await client.call_tool(
                tool_name="retrieve_context",
                arguments={
                    "query": "hello",
                    "limit": 5,
                    "filters": {"user_id": "user123"}
                },
                user_id="user123"
            )
            ```
        """
        # Delegate to the specialized tool executor for clean separation of concerns
        return await self.tool_executor.execute_tool(
            tool_name=tool_name,
            arguments=arguments,
            user_id=user_id,
            trace_id=trace_id,
            timeout_ms=timeout_ms,
        )

    async def call_tools(
        self,
        tool_calls: List[Dict[str, Any]],
        max_concurrency: Optional[int] = None,
        timeout_ms: Optional[int] = None,
    ) -> List[ToolResult]:
        """
        Execute multiple tool calls concurrently with backpressure control.

        Args:
            tool_calls: List of tool call dictionaries with 'name', 'arguments',
                       optional 'user_id' and 'trace_id'
            max_concurrency: Maximum concurrent operations (default: 10)
            timeout_ms: Optional timeout override in milliseconds

        Returns:
            List of tool results in the same order as input calls

        Raises:
            MCPValidationError: If any call validation fails
            MCPConnectionError: If connection fails
            MCPError: For other MCP protocol errors

        Example:
            ```python
            tool_calls = [
                {
                    "name": "store_context",
                    "arguments": {"type": "log", "content": {"text": "Hello"}},
                    "user_id": "user1",
                    "trace_id": "trace-1"
                },
                {
                    "name": "retrieve_context",
                    "arguments": {"query": "hello", "limit": 5},
                    "user_id": "user1",
                    "trace_id": "trace-2"
                }
            ]

            results = await client.call_tools(tool_calls, max_concurrency=5)
            ```
        """
        if not tool_calls:
            return []

        # Default concurrency limit
        concurrency = max_concurrency or 10
        semaphore = asyncio.Semaphore(concurrency)

        async def call_with_semaphore(tool_call_dict: Dict[str, Any]) -> ToolResult:
            """Execute single tool call with semaphore protection."""
            async with semaphore:
                return await self.call_tool(
                    tool_name=tool_call_dict["name"],
                    arguments=tool_call_dict["arguments"],
                    user_id=tool_call_dict.get("user_id"),
                    trace_id=tool_call_dict.get("trace_id"),
                    timeout_ms=timeout_ms,
                )

        # Execute all calls concurrently
        logger.debug(
            f"Executing {len(tool_calls)} tool calls with max_concurrency={concurrency}",
            extra={
                "tool_count": len(tool_calls),
                "max_concurrency": concurrency,
                "tool_names": [tc.get("name") for tc in tool_calls],
            },
        )

        try:
            results = await asyncio.gather(
                *[call_with_semaphore(tc) for tc in tool_calls], return_exceptions=True
            )

            # Convert exceptions to results and log errors
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Tool call {i} ({tool_calls[i].get('name')}) failed: {result}",
                        extra={
                            "tool_index": i,
                            "tool_name": tool_calls[i].get("name"),
                            "error_type": type(result).__name__,
                            "trace_id": tool_calls[i].get("trace_id"),
                        },
                    )
                    # Re-raise the exception for the caller to handle
                    raise result
                else:
                    processed_results.append(result)

            logger.debug(
                f"Successfully completed {len(processed_results)}/{len(tool_calls)} tool calls",
                extra={"success_count": len(processed_results), "total_count": len(tool_calls)},
            )

            return processed_results  # type: ignore[return-value]

        except Exception as e:
            logger.error(f"Batch tool call failed: {e}")
            raise

    async def _execute_tool_call(
        self, tool_call: MCPToolCall, timeout_ms: Optional[int] = None
    ) -> ToolResult:
        """Execute tool call with transport policies."""

        async def _call() -> ToolResult:
            if self.config.use_websocket:
                return await self._call_tool_ws(tool_call)
            else:
                return await self._call_tool_http(tool_call, timeout_ms)

        result = await self.transport.execute_with_policy(
            _call,
            operation_name=f"veris_memory.mcp.tool.{tool_call.name}",
            trace_id=tool_call.trace_id,
        )
        return result if isinstance(result, dict) else {}

    async def _call_tool_http(
        self, tool_call: MCPToolCall, timeout_ms: Optional[int] = None
    ) -> ToolResult:
        """Call tool via HTTP."""
        if not self._http_client:
            raise MCPConnectionError("HTTP client not connected")

        # Prepare request with user scoping
        request_data = tool_call.arguments.copy()
        if tool_call.user_id and self.config.enforce_user_scoping:
            # Ensure user_id is in the request
            if "user_id" not in request_data:
                request_data["user_id"] = tool_call.user_id

        # Override timeout if specified
        timeout = None
        if timeout_ms:
            timeout = httpx.Timeout(timeout_ms / 1000.0)

        try:
            response = await self._http_client.post(
                f"{self.config.server_url}/tools/{tool_call.name}",
                json=request_data,
                timeout=timeout,
            )

            if response.status_code == 408:
                raise MCPTimeoutError(
                    f"Tool call timed out: {tool_call.name}",
                    trace_id=tool_call.trace_id,
                    details={"tool_name": tool_call.name, "timeout_ms": timeout_ms},
                )

            if response.status_code >= 500:
                raise MCPConnectionError(
                    f"Server error {response.status_code}: {response.text}",
                    code=str(response.status_code),
                    trace_id=tool_call.trace_id,
                    details={"tool_name": tool_call.name, "status_code": response.status_code},
                )

            if response.status_code == 400:
                raise MCPValidationError(
                    f"Invalid request for tool {tool_call.name}: {response.text}",
                    code=str(response.status_code),
                    trace_id=tool_call.trace_id,
                    details={"tool_name": tool_call.name, "arguments": tool_call.arguments},
                )

            if response.status_code == 401:
                raise MCPSecurityError(
                    f"Authentication failed for tool {tool_call.name}",
                    code=str(response.status_code),
                    trace_id=tool_call.trace_id,
                    details={"tool_name": tool_call.name},
                )

            if response.status_code == 403:
                raise MCPSecurityError(
                    f"Access denied for tool {tool_call.name}",
                    code=str(response.status_code),
                    trace_id=tool_call.trace_id,
                    details={"tool_name": tool_call.name, "user_id": tool_call.user_id},
                )

            if response.status_code != 200:
                raise MCPError(
                    f"HTTP error {response.status_code}: {response.text}",
                    code=str(response.status_code),
                    trace_id=tool_call.trace_id,
                    details={"tool_name": tool_call.name, "status_code": response.status_code},
                )

            result = response.json()
            return result if isinstance(result, dict) else {}

        except asyncio.TimeoutError as e:
            error_msg = f"Tool call timed out: {tool_call.name} (asyncio timeout)"
            logger.warning(
                error_msg,
                extra={
                    "tool_name": tool_call.name,
                    "trace_id": tool_call.trace_id,
                    "timeout_ms": timeout_ms,
                },
            )
            raise MCPTimeoutError(
                error_msg,
                trace_id=tool_call.trace_id,
                details={
                    "tool_name": tool_call.name,
                    "timeout_ms": timeout_ms,
                    "timeout_type": "asyncio",
                },
            ) from e
        except httpx.TimeoutException as e:
            error_msg = f"Tool call timed out: {tool_call.name} (HTTP timeout)"
            logger.warning(
                error_msg,
                extra={
                    "tool_name": tool_call.name,
                    "trace_id": tool_call.trace_id,
                    "timeout_ms": timeout_ms,
                },
            )
            raise MCPTimeoutError(
                error_msg,
                trace_id=tool_call.trace_id,
                details={
                    "tool_name": tool_call.name,
                    "timeout_ms": timeout_ms,
                    "timeout_type": "http",
                },
            ) from e
        except httpx.ConnectError as e:
            error_msg = f"Connection error for tool {tool_call.name}: {e}"
            logger.error(
                error_msg,
                extra={
                    "tool_name": tool_call.name,
                    "trace_id": tool_call.trace_id,
                    "server_url": self.config.server_url,
                },
            )
            raise MCPConnectionError(
                error_msg,
                trace_id=tool_call.trace_id,
                details={"tool_name": tool_call.name, "server_url": self.config.server_url},
            ) from e
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP status error for tool {tool_call.name}: {e.response.status_code}"
            logger.error(
                error_msg,
                extra={
                    "tool_name": tool_call.name,
                    "trace_id": tool_call.trace_id,
                    "status_code": e.response.status_code,
                },
            )
            raise MCPError(
                error_msg,
                code=str(e.response.status_code),
                trace_id=tool_call.trace_id,
                details={"tool_name": tool_call.name, "status_code": e.response.status_code},
            ) from e
        except httpx.RequestError as e:
            error_msg = f"Request error for tool {tool_call.name}: {e}"
            logger.error(
                error_msg, extra={"tool_name": tool_call.name, "trace_id": tool_call.trace_id}
            )
            raise MCPConnectionError(
                error_msg,
                trace_id=tool_call.trace_id,
                details={"tool_name": tool_call.name, "request_error": str(e)},
            ) from e
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response for tool {tool_call.name}: {e}"
            logger.error(
                error_msg, extra={"tool_name": tool_call.name, "trace_id": tool_call.trace_id}
            )
            raise MCPError(
                error_msg,
                code="invalid_json",
                trace_id=tool_call.trace_id,
                details={"tool_name": tool_call.name, "json_error": str(e)},
            ) from e

    async def _call_tool_ws(self, tool_call: MCPToolCall) -> ToolResult:
        """Call tool via WebSocket."""
        if not self._ws_connection:
            raise MCPConnectionError("WebSocket not connected")

        request = {
            "jsonrpc": "2.0",
            "method": MCPMethod.CALL_TOOL.value,
            "params": tool_call.to_dict(),
            "id": str(uuid.uuid4()),
        }

        await self._send_ws(request)
        response = await self._receive_ws()

        if "error" in response:
            error_info = response["error"]
            raise MCPError(
                error_info.get("message", "Unknown error"),
                code=error_info.get("code"),
                details=error_info.get("data"),
                trace_id=tool_call.trace_id,
            )

        result = response.get("result", {})
        return result if isinstance(result, dict) else {}

    async def _send_ws(self, data: JSONDict) -> None:
        """Send data via WebSocket."""
        if self._ws_connection:
            await self._ws_connection.send(json.dumps(data))

    async def _receive_ws(self) -> JSONDict:
        """Receive data via WebSocket."""
        if self._ws_connection:
            data = await self._ws_connection.recv()
            result = json.loads(data)
            return result if isinstance(result, dict) else {}
        return {}

    def _validate_tool_call(self, tool_call: MCPToolCall) -> None:
        """
        Comprehensive validation for tool calls.

        Args:
            tool_call: Tool call to validate

        Raises:
            MCPValidationError: If validation fails
            MCPSecurityError: If security checks fail
        """
        validator = get_validator()

        # Validate tool name
        validator.validate_tool_name(tool_call.name)

        # Validate arguments structure and content
        validator.validate_arguments(tool_call.arguments, tool_call.name)

        # Validate user ID if present
        validator.validate_user_id(tool_call.user_id)

        # Validate trace ID if present
        validator.validate_trace_id(tool_call.trace_id)

        logger.debug(
            f"Tool call validation passed: {tool_call.name}",
            extra={
                "tool_name": tool_call.name,
                "argument_count": len(tool_call.arguments),
                "has_user_id": bool(tool_call.user_id),
                "trace_id": tool_call.trace_id,
            },
        )

    async def list_tools(self, trace_id: Optional[str] = None) -> JSONList:
        """List available Veris Memory MCP tools.

        Args:
            trace_id: Optional trace ID for request tracing

        Returns:
            List of available tools with their schemas
        """
        if not self.connected:
            await self.connect(trace_id)

        # Use HTTP client manager for consistent error handling
        tools = await self.http_manager.get_json(
            endpoint="/mcp/tools", trace_id=trace_id, expected_key="tools", default_value=[]
        )

        return tools if isinstance(tools, list) else []

    async def get_status(self, trace_id: Optional[str] = None) -> JSONDict:
        """Get Veris Memory server status.

        Args:
            trace_id: Optional trace ID for request tracing

        Returns:
            Server status information
        """
        if not self.connected:
            await self.connect(trace_id)

        # Use HTTP client manager for consistent error handling
        result = await self.http_manager.get_json(endpoint="/status", trace_id=trace_id)

        return result if isinstance(result, dict) else {}

    async def verify_readiness_enhanced(self, trace_id: Optional[str] = None) -> JSONDict:
        """Get enhanced readiness with detailed service status levels.

        This method provides detailed information about Veris Memory's operational status:
        - FULL: All services operational, optimal performance
        - STANDARD: Core services operational, some degradation
        - BASIC: Minimal services operational, limited functionality
        - UNKNOWN: Status cannot be determined

        Args:
            trace_id: Optional trace ID for request tracing

        Returns:
            Enhanced readiness information with structure:
            {
                "readiness_level": "FULL|STANDARD|BASIC|UNKNOWN",
                "ready": bool,
                "services": {
                    "service_name": {"status": "operational|degraded|offline"}
                },
                "recommendations": ["actionable items..."]
            }
        """
        try:
            result = await self.call_tool(
                tool_name="verify_readiness", arguments={}, trace_id=trace_id
            )

            readiness_level = result.get("readiness_level", "UNKNOWN")
            services = result.get("services", {})
            recommendations = result.get("recommendations", [])

            logger.info(
                f"Veris Memory readiness check: {readiness_level}",
                extra={
                    "readiness_level": readiness_level,
                    "services_count": len(services),
                    "recommendations_count": len(recommendations),
                    "trace_id": trace_id,
                },
            )

            return result

        except (MCPTimeoutError, MCPConnectionError) as e:
            logger.warning(
                f"Enhanced readiness check failed with transport error: {e}",
                extra={"trace_id": trace_id, "error_type": type(e).__name__},
            )
            return {
                "readiness_level": "UNKNOWN",
                "ready": False,
                "error": str(e),
                "fallback": True,
                "error_type": "transport",
            }
        except MCPError as e:
            logger.warning(
                f"Enhanced readiness check failed with MCP error: {e}",
                extra={"trace_id": trace_id, "error_code": e.code},
            )
            return {
                "readiness_level": "UNKNOWN",
                "ready": False,
                "error": str(e),
                "fallback": True,
                "error_type": "mcp",
                "error_code": e.code,
            }
        except Exception as e:
            logger.error(
                f"Enhanced readiness check failed with unexpected error: {e}",
                extra={"trace_id": trace_id, "error_type": type(e).__name__},
            )
            return {
                "readiness_level": "UNKNOWN",
                "ready": False,
                "error": str(e),
                "fallback": True,
                "error_type": "unexpected",
            }

    async def check_service_health(self, trace_id: Optional[str] = None) -> JSONDict:
        """Check overall Veris Memory service health with actionable insights.

        Combines readiness information with client-side health indicators.

        Args:
            trace_id: Optional trace ID for request tracing

        Returns:
            Service health summary with operational recommendations
        """
        readiness = await self.verify_readiness_enhanced(trace_id)
        client_status = self.get_client_status()

        # Determine overall health
        readiness_level = readiness.get("readiness_level", "UNKNOWN")
        transport_status = client_status["transport_status"]
        circuit_breaker_state = transport_status["circuit_breaker"]["state"]

        if readiness_level == "FULL" and circuit_breaker_state == "closed":
            health = "HEALTHY"
        elif readiness_level in ["STANDARD", "BASIC"] and circuit_breaker_state == "closed":
            health = "DEGRADED"
        else:
            health = "UNHEALTHY"

        return {
            "overall_health": health,
            "readiness": readiness,
            "client_status": client_status,
            "recommendations": readiness.get("recommendations", []),
            "timestamp": time.time(),
        }

    def get_client_status(self) -> JSONDict:
        """Get client-side status and metrics.

        Returns:
            Client status information including connection state and transport metrics
        """
        return {
            "connected": self.connected,
            "server_url": self.config.server_url,
            "use_websocket": self.config.use_websocket,
            "client_info": self.config.client_info.to_dict(),
            "server_info": self.server_info.to_dict() if self.server_info else None,
            "transport_status": self.transport.get_status(),
            "tracer_stats": self.tracer.get_trace_stats() if self.tracer else None,
        }

    async def store_context(
        self,
        context_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Store a context item in Veris Memory.

        Convenience method that wraps call_tool for store_context operations.

        Args:
            context_type: Type of context. Must be one of: "design", "decision",
                "trace", "sprint", "log"
            content: Context content dictionary (flexible structure)
            metadata: Optional metadata dictionary
            user_id: User ID for scoping (uses config.user_id if not provided)
            trace_id: Optional trace ID for request tracking

        Returns:
            Dictionary containing the operation result, typically with 'context_id'

        Raises:
            MCPValidationError: If context_type is not one of the allowed values
                or other arguments are invalid
            MCPConnectionError: If connection fails
            MCPTimeoutError: If operation times out

        Note:
            Updated per veris-memory-mcp-server issue #2:
            - context_type must be one of: "design", "decision", "trace", "sprint", "log"
            - Content structure is flexible (no required 'text' field)

        Example:
            >>> result = await client.store_context(
            ...     context_type="decision",
            ...     content={
            ...         "title": "API Design Decision",
            ...         "decision": "Use REST API",
            ...         "reasoning": "Better compatibility"
            ...     },
            ...     metadata={"project": "platform-v2", "priority": "high"}
            ... )
            >>> print(result["context_id"])
        """
        # Validate context_type early for better error messages
        from .validation import VALID_CONTEXT_TYPES

        if context_type not in VALID_CONTEXT_TYPES:
            raise MCPValidationError(
                f"context_type must be one of: {', '.join(sorted(VALID_CONTEXT_TYPES))}. "
                f"Got: '{context_type}'"
            )

        arguments = {
            "type": context_type,
            "content": content,
        }

        if metadata is not None:
            arguments["metadata"] = metadata

        result = await self.call_tool(
            tool_name="store_context",
            arguments=arguments,
            user_id=user_id,
            trace_id=trace_id,
        )

        return result

    async def retrieve_context(
        self,
        query: str,
        limit: int = 10,
        context_type: Optional[str] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve contexts from Veris Memory using semantic search.

        Convenience method that wraps call_tool for retrieve_context operations.

        Args:
            query: Search query string for semantic matching
            limit: Maximum number of results to return (1-1000, default: 10)
            context_type: Optional filter by context type
            metadata_filters: Optional metadata filters as key-value pairs
            user_id: User ID for scoping (uses config.user_id if not provided)
            trace_id: Optional trace ID for request tracking

        Returns:
            List of context dictionaries matching the search criteria

        Raises:
            MCPValidationError: If arguments are invalid
            MCPConnectionError: If connection fails
            MCPTimeoutError: If operation times out

        Example:
            >>> contexts = await client.retrieve_context(
            ...     query="API design decision",
            ...     limit=5,
            ...     context_type="decision",
            ...     metadata_filters={"project": "platform-v2"}
            ... )
            >>> print(f"Found {len(contexts)} contexts")
        """
        arguments = {
            "query": query,
            "limit": limit,
        }

        if context_type is not None:
            arguments["context_type"] = context_type

        if metadata_filters is not None:
            arguments["metadata_filters"] = metadata_filters

        result = await self.call_tool(
            tool_name="retrieve_context",
            arguments=arguments,
            user_id=user_id,
            trace_id=trace_id,
        )

        # retrieve_context typically returns a list in the result
        # result is guaranteed to be Dict[str, Any] from call_tool
        if "contexts" in result:
            contexts = result["contexts"]
            if isinstance(contexts, list):
                return contexts
            else:
                return [contexts] if contexts else []

        # Fallback case - wrap the result dict
        return [result] if result else []

    async def __aenter__(self) -> "MCPClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()
