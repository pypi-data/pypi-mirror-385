"""WebSocket transport implementation for Veris Memory MCP SDK."""

import json
import uuid
from typing import Any, Dict, Optional

try:
    import websockets

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.config import MCPConfig

from ..core.errors import MCPConnectionError, MCPError
from ..core.logging_utils import create_contextual_logger
from ..core.schemas import MCPMethod, MCPToolCall

# Type alias to avoid circular imports
ToolResult = Dict[str, Any]

logger = create_contextual_logger(__name__)


class WebSocketTransport:
    """
    WebSocket transport implementation for MCP operations.

    Provides real-time bidirectional communication with Veris Memory
    servers using the WebSocket protocol with JSON-RPC messaging.
    """

    def __init__(self, config: "MCPConfig"):
        """
        Initialize WebSocket transport.

        Args:
            config: MCP configuration object
        """
        if not WEBSOCKETS_AVAILABLE:
            raise MCPConnectionError(
                "websockets is required for WebSocket transport. "
                "Install with: pip install websockets"
            )

        self.config = config
        self._connection: Optional[Any] = None  # websockets.WebSocketServerProtocol
        self._connected = False

    async def connect(self, server_url: str, headers: Dict[str, str]) -> None:
        """
        Connect to MCP server via WebSocket.

        Args:
            server_url: Server URL to connect to
            headers: WebSocket headers to include

        Raises:
            MCPConnectionError: If connection fails
        """
        if self._connected and self._connection:
            return

        # Convert HTTP URLs to WebSocket URLs
        ws_url = server_url.replace("http://", "ws://").replace("https://", "wss://")

        try:
            logger.debug(f"Connecting to WebSocket: {ws_url}/mcp")

            self._connection = await websockets.connect(
                f"{ws_url}/mcp",
                additional_headers=headers,
                open_timeout=self.config.connect_timeout_ms / 1000.0,
                close_timeout=self.config.request_timeout_ms / 1000.0,
            )

            # Send initialization message
            await self._send_initialization()

            self._connected = True
            logger.debug("WebSocket transport connected successfully", extra={"server_url": ws_url})

        except Exception as e:
            await self._cleanup_connection()
            raise MCPConnectionError(f"Failed to connect via WebSocket: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect WebSocket transport."""
        if self._connection:
            try:
                await self._connection.close()
            except Exception as e:
                logger.warning(f"Error during WebSocket disconnect: {e}")
            finally:
                self._connection = None
                self._connected = False

        logger.debug("WebSocket transport disconnected")

    async def call_tool(
        self, tool_call: MCPToolCall, timeout_ms: Optional[int] = None
    ) -> ToolResult:
        """
        Execute tool call via WebSocket.

        Args:
            tool_call: Tool call to execute
            timeout_ms: Optional timeout override (not currently implemented for WebSocket)

        Returns:
            Tool execution result

        Raises:
            MCPConnectionError: If not connected
            MCPError: If tool call fails
        """
        if not self._connected or not self._connection:
            raise MCPConnectionError("WebSocket transport not connected")

        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "method": MCPMethod.CALL_TOOL.value,
            "params": tool_call.to_dict(),
            "id": str(uuid.uuid4()),
        }

        try:
            logger.debug(
                f"WebSocket tool call: {tool_call.name}",
                extra={
                    "tool_name": tool_call.name,
                    "trace_id": tool_call.trace_id,
                    "has_user_id": bool(tool_call.user_id),
                    "request_id": request["id"],
                },
            )

            # Send request and wait for response
            await self._send_message(request)
            response = await self._receive_message()

            # Handle JSON-RPC error response
            if "error" in response:
                error_info = response["error"]
                raise MCPError(
                    error_info.get("message", "Unknown WebSocket error"),
                    code=str(error_info.get("code", "unknown")),
                    details=error_info.get("data"),
                    trace_id=tool_call.trace_id,
                )

            # Extract and return result
            result = response.get("result", {})
            return result if isinstance(result, dict) else {}

        except MCPError:
            # Re-raise MCP errors as-is
            raise
        except Exception as e:
            error_msg = f"WebSocket error for tool {tool_call.name}: {e}"
            logger.error(
                error_msg, extra={"tool_name": tool_call.name, "trace_id": tool_call.trace_id}
            )
            raise MCPConnectionError(
                error_msg, trace_id=tool_call.trace_id, details={"tool_name": tool_call.name}
            ) from e

    async def _send_initialization(self) -> None:
        """Send WebSocket initialization message."""
        init_message = {
            "jsonrpc": "2.0",
            "method": MCPMethod.INITIALIZE.value,
            "params": {
                "protocolVersion": self.config.client_info.protocol_version,
                "clientInfo": self.config.client_info.to_dict(),
            },
            "id": str(uuid.uuid4()),
        }

        await self._send_message(init_message)
        response = await self._receive_message()

        if "error" in response:
            raise MCPConnectionError(f"WebSocket initialization failed: {response['error']}")

        # Store server info if provided
        result = response.get("result", {})
        if "serverInfo" in result:
            logger.debug(
                "Received server info via WebSocket", extra={"server_info": result["serverInfo"]}
            )

    async def _send_message(self, message: Dict[str, Any]) -> None:
        """
        Send message via WebSocket.

        Args:
            message: Message to send
        """
        if not self._connection:
            raise MCPConnectionError("WebSocket not connected")

        try:
            await self._connection.send(json.dumps(message))
        except Exception as e:
            raise MCPConnectionError(f"Failed to send WebSocket message: {e}") from e

    async def _receive_message(self) -> Dict[str, Any]:
        """
        Receive message via WebSocket.

        Returns:
            Received message as dictionary
        """
        if not self._connection:
            raise MCPConnectionError("WebSocket not connected")

        try:
            data = await self._connection.recv()
            result = json.loads(data)
            return result if isinstance(result, dict) else {}
        except json.JSONDecodeError as e:
            raise MCPError(f"Invalid JSON received via WebSocket: {e}") from e
        except Exception as e:
            raise MCPConnectionError(f"Failed to receive WebSocket message: {e}") from e

    def is_connected(self) -> bool:
        """
        Check if WebSocket transport is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._connected and self._connection is not None

    async def _cleanup_connection(self) -> None:
        """Clean up WebSocket connection resources."""
        if self._connection:
            try:
                await self._connection.close()
            except Exception as e:
                logger.warning(f"Error during WebSocket cleanup: {e}")
            finally:
                self._connection = None
        # Always reset connected state during cleanup
        self._connected = False
