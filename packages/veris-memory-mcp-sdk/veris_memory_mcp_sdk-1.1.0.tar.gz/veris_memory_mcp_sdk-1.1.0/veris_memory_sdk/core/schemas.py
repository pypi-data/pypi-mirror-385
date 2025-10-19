"""Veris Memory MCP SDK schema definitions."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# Type aliases for better readability
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
ToolArguments = Dict[str, Any]  # Keep flexible for tool arguments
ResponseData = Dict[str, Any]  # Keep flexible for response data
Capabilities = Dict[str, Any]


class MCPMethod(str, Enum):
    """
    MCP protocol methods for Veris Memory operations.

    Defines the standard methods available in the Model Context Protocol
    for interacting with Veris Memory services.
    """

    INITIALIZE = "initialize"
    CALL_TOOL = "tools/call"
    LIST_TOOLS = "tools/list"
    HEALTH = "health"
    STATUS = "status"
    VERIFY_READINESS = "verify_readiness"


@dataclass
class MCPToolCall:
    """
    MCP tool call structure for Veris Memory operations.

    Represents a call to a Veris Memory tool with arguments and metadata.

    Example:
        ```python
        tool_call = MCPToolCall(
            name="store_context",
            arguments={
                "type": "log",
                "content": {
                    "text": "Hello world",
                    "type": "user_query",
                    "title": "User Message"
                }
            },
            user_id="user123",
            trace_id="trace-456"
        )
        ```
    """

    name: str
    """Name of the Veris Memory tool to call"""

    arguments: ToolArguments
    """Arguments to pass to the tool"""

    trace_id: Optional[str] = None
    """Optional trace ID for distributed tracing"""

    user_id: Optional[str] = None
    """User ID for security scoping (required for most operations)"""

    def to_dict(self) -> ResponseData:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of the tool call
        """
        result = {"name": self.name, "arguments": self.arguments}
        if self.trace_id:
            result["trace_id"] = self.trace_id
        if self.user_id:
            result["user_id"] = self.user_id
        return result


@dataclass
class MCPResponse:
    """
    MCP response structure for Veris Memory operations.

    Represents the response from a Veris Memory MCP operation,
    including success status, data, and error information.
    """

    success: bool
    """Whether the operation was successful"""

    data: ResponseData
    """Response data from the operation"""

    error: Optional[str] = None
    """Error message if operation failed"""

    error_code: Optional[str] = None
    """Error code for programmatic handling"""

    trace_id: Optional[str] = None
    """Trace ID for request correlation"""

    duration_ms: Optional[float] = None
    """Operation duration in milliseconds"""

    @classmethod
    def success_response(
        cls,
        data: ResponseData,
        trace_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> "MCPResponse":
        """Create a success response.

        Args:
            data: Response data
            trace_id: Optional trace ID
            duration_ms: Optional operation duration

        Returns:
            MCPResponse with success=True
        """
        return cls(success=True, data=data, trace_id=trace_id, duration_ms=duration_ms)

    @classmethod
    def error_response(
        cls,
        error: str,
        error_code: Optional[str] = None,
        trace_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> "MCPResponse":
        """Create an error response.

        Args:
            error: Error message
            error_code: Optional error code
            trace_id: Optional trace ID
            duration_ms: Optional operation duration

        Returns:
            MCPResponse with success=False
        """
        return cls(
            success=False,
            data={},
            error=error,
            error_code=error_code,
            trace_id=trace_id,
            duration_ms=duration_ms,
        )


@dataclass
class MCPClientInfo:
    """
    MCP client information for Veris Memory connections.

    Identifies the client application and its capabilities
    when connecting to Veris Memory.

    Example:
        ```python
        client_info = MCPClientInfo(
            name="my-chat-app",
            version="2.1.0",
            capabilities={
                "supports_streaming": True,
                "max_context_length": 1000000
            }
        )
        ```
    """

    name: str
    """Client application name"""

    version: str
    """Client application version"""

    protocol_version: str = "1.0"
    """MCP protocol version supported"""

    capabilities: Optional[Capabilities] = None
    """Optional client capabilities"""

    def to_dict(self) -> ResponseData:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of client info
        """
        result: ResponseData = {
            "name": self.name,
            "version": self.version,
            "protocolVersion": self.protocol_version,
        }
        if self.capabilities:
            result["capabilities"] = self.capabilities
        return result


@dataclass
class MCPServerInfo:
    """
    MCP server information from Veris Memory.

    Contains information about the Veris Memory server
    including its capabilities and available tools.
    """

    name: str
    """Server name (e.g., "Veris Memory")"""

    version: str
    """Server version"""

    protocol_version: str
    """MCP protocol version supported by server"""

    capabilities: Optional[Capabilities] = None
    """Server capabilities"""

    tools: Optional[ResponseData] = None
    """Available tools and their schemas"""

    def to_dict(self) -> ResponseData:
        """Convert to dictionary.

        Returns:
            Dictionary representation of server info
        """
        result: ResponseData = {
            "name": self.name,
            "version": self.version,
            "protocolVersion": self.protocol_version,
        }
        if self.capabilities:
            result["capabilities"] = self.capabilities
        if self.tools:
            result["tools"] = self.tools
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPServerInfo":
        """Create from dictionary.

        Args:
            data: Dictionary containing server info

        Returns:
            MCPServerInfo instance
        """
        return cls(
            name=data.get("name", "unknown"),
            version=data.get("version", "unknown"),
            protocol_version=data.get("protocolVersion", "1.0"),
            capabilities=data.get("capabilities"),
            tools=data.get("tools"),
        )
