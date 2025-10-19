"""HTTP transport implementation for Veris Memory MCP SDK."""

import json
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import httpx

if TYPE_CHECKING:
    from ..core.config import MCPConfig

from ..core.errors import (
    MCPConnectionError,
    MCPError,
    MCPSecurityError,
    MCPTimeoutError,
    MCPValidationError,
    map_http_status_to_error,
)
from ..core.logging_utils import create_contextual_logger
from ..core.schemas import MCPToolCall
from ..core.security import redact_headers, redact_url_params

# Type alias to avoid circular imports
ToolResult = Dict[str, Any]
JSONDict = Dict[str, Any]
JSONList = List[JSONDict]

# Backward compatibility alias
HTTPClientManager = None  # Will be set after class definition

logger = create_contextual_logger(__name__)


class HTTPTransport:
    """
    HTTP transport implementation for MCP operations.

    Handles HTTP-specific communication with Veris Memory servers,
    providing reliable request/response semantics with comprehensive
    error handling and status code mapping.
    """

    def __init__(self, config: "MCPConfig"):
        """
        Initialize HTTP transport.

        Args:
            config: MCP configuration object
        """

        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._connected = False

    async def connect(self, server_url: str, headers: Dict[str, str]) -> None:
        """
        Connect to MCP server via HTTP.

        Args:
            server_url: Server URL to connect to
            headers: HTTP headers to include

        Raises:
            MCPConnectionError: If connection fails
        """
        if self._connected and self._client:
            return

        # Create HTTP client with timeouts and connection pooling
        timeout = httpx.Timeout(
            connect=self.config.connect_timeout_ms / 1000.0,
            read=self.config.request_timeout_ms / 1000.0,
            write=self.config.request_timeout_ms / 1000.0,
            pool=self.config.total_timeout_ms / 1000.0,
        )

        # Configure connection limits
        try:
            from ..core.config import MCPConnectionPool

            pool = MCPConnectionPool()
            limits = pool.to_httpx_limits() or httpx.Limits()
        except Exception:
            limits = httpx.Limits()

        # Build httpx client kwargs with configuration
        client_kwargs = {
            "timeout": timeout,
            "limits": limits,
            "headers": headers,
            "verify": self.config.verify_ssl,
            "http2": self.config.http2,
        }

        # Add proxy settings if configured
        if self.config.proxies:
            client_kwargs["proxies"] = self.config.proxies

        # Add client certificate if configured
        if self.config.client_cert:
            client_kwargs["cert"] = self.config.client_cert

        # Add any extra httpx kwargs
        if self.config.extra_httpx_kwargs:
            client_kwargs.update(self.config.extra_httpx_kwargs)

        self._client = httpx.AsyncClient(**client_kwargs)  # type: ignore[arg-type]

        # Perform health check to verify connection
        try:
            response = await self._client.get(f"{server_url}/health")
            if response.status_code != 200:
                raise MCPConnectionError(
                    f"Health check failed: HTTP {response.status_code}",
                    details={"status_code": response.status_code, "response": response.text[:200]},
                )

            self._connected = True
            logger.debug(
                "HTTP transport connected successfully",
                extra={
                    "server_url": redact_url_params(server_url),
                    "headers": redact_headers(headers),
                    "verify_ssl": self.config.verify_ssl,
                    "http2": self.config.http2,
                    "has_proxies": bool(self.config.proxies),
                    "has_client_cert": bool(self.config.client_cert),
                },
            )

        except httpx.RequestError as e:
            await self._cleanup_client()
            raise MCPConnectionError(f"Failed to connect via HTTP: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect HTTP transport."""
        if self._client:
            try:
                await self._client.aclose()
            except Exception as e:
                logger.warning(f"Error during HTTP client cleanup: {e}")
            finally:
                self._client = None
                self._connected = False

        logger.debug("HTTP transport disconnected")

    async def call_tool(
        self, tool_call: MCPToolCall, timeout_ms: Optional[int] = None
    ) -> ToolResult:
        """
        Execute tool call via HTTP.

        Args:
            tool_call: Tool call to execute
            timeout_ms: Optional timeout override

        Returns:
            Tool execution result

        Raises:
            MCPConnectionError: If not connected or connection fails
            MCPTimeoutError: If request times out
            MCPValidationError: If request validation fails (400)
            MCPSecurityError: If authentication/authorization fails (401/403)
            MCPError: For other HTTP errors
        """
        if not self._connected or not self._client:
            raise MCPConnectionError("HTTP transport not connected")

        # Prepare request data with user scoping
        request_data = tool_call.arguments.copy()
        if tool_call.user_id and "user_id" not in request_data:
            request_data["user_id"] = tool_call.user_id

        # Override timeout if specified
        timeout = None
        if timeout_ms:
            timeout = httpx.Timeout(timeout_ms / 1000.0)

        url = f"{self.config.server_url}/tools/{tool_call.name}"

        try:
            logger.debug(
                f"HTTP POST to tool endpoint: {tool_call.name}",
                extra={
                    "tool_name": tool_call.name,
                    "url": redact_url_params(url),
                    "trace_id": tool_call.trace_id,
                    "has_user_id": bool(tool_call.user_id),
                    "timeout_ms": timeout_ms,
                },
            )

            response = await self._client.post(url, json=request_data, timeout=timeout)

            # Handle different HTTP status codes with specific exceptions
            await self._handle_response_status(response, tool_call)

            # Parse and return result
            result = response.json()
            return result if isinstance(result, dict) else {}

        except httpx.TimeoutException as e:
            error_msg = f"HTTP timeout for tool {tool_call.name}"
            logger.warning(
                error_msg, extra={"tool_name": tool_call.name, "trace_id": tool_call.trace_id}
            )
            raise MCPTimeoutError(
                error_msg,
                trace_id=tool_call.trace_id,
                details={"tool_name": tool_call.name, "timeout_ms": timeout_ms},
            ) from e

        except httpx.ConnectError as e:
            error_msg = f"HTTP connection error for tool {tool_call.name}: {e}"
            logger.error(
                error_msg, extra={"tool_name": tool_call.name, "trace_id": tool_call.trace_id}
            )
            raise MCPConnectionError(
                error_msg, trace_id=tool_call.trace_id, details={"tool_name": tool_call.name}
            ) from e

        except httpx.RequestError as e:
            error_msg = f"HTTP request error for tool {tool_call.name}: {e}"
            logger.error(
                error_msg, extra={"tool_name": tool_call.name, "trace_id": tool_call.trace_id}
            )
            raise MCPConnectionError(
                error_msg, trace_id=tool_call.trace_id, details={"tool_name": tool_call.name}
            ) from e

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response for tool {tool_call.name}"
            logger.error(
                error_msg, extra={"tool_name": tool_call.name, "trace_id": tool_call.trace_id}
            )
            raise MCPError(
                error_msg,
                code="invalid_json",
                trace_id=tool_call.trace_id,
                details={"tool_name": tool_call.name},
            ) from e

    async def _handle_response_status(
        self, response: httpx.Response, tool_call: MCPToolCall
    ) -> None:
        """
        Handle HTTP response status codes with appropriate exception mapping.

        Args:
            response: HTTP response object
            tool_call: Original tool call for context

        Raises:
            MCPTimeoutError: For 408 status
            MCPValidationError: For 400 status
            MCPSecurityError: For 401/403 status
            MCPConnectionError: For 5xx status
            MCPError: For other non-200 status
        """
        if 200 <= response.status_code < 300:
            return

        response_text = response.text[:200] if response.text else "No response body"

        # Special handling for 408 Request Timeout
        if response.status_code == 408:
            raise MCPTimeoutError(
                f"Tool call timed out: {tool_call.name}",
                trace_id=tool_call.trace_id,
                details={"tool_name": tool_call.name, "status_code": 408},
            )

        # Use the centralized error mapping for all other status codes
        error_message = f"Tool {tool_call.name} failed: {response_text}"
        error_details = {
            "tool_name": tool_call.name,
            "response_snippet": response_text,
            "request_id": getattr(response, "headers", {}).get("x-request-id"),
        }

        # Extract Retry-After header for rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            if retry_after:
                try:
                    error_details["retry_after_seconds"] = int(retry_after)
                except ValueError:
                    # Could be HTTP-date format, handle gracefully
                    error_details["retry_after_header"] = retry_after

        mapped_error = map_http_status_to_error(
            response.status_code, error_message, trace_id=tool_call.trace_id, details=error_details
        )

        # Add retry_after to rate limit errors
        if hasattr(mapped_error, "retry_after") and "retry_after_seconds" in error_details:
            mapped_error.retry_after = error_details["retry_after_seconds"]

        raise mapped_error

    def is_connected(self) -> bool:
        """
        Check if HTTP transport is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._connected and self._client is not None

    async def _cleanup_client(self) -> None:
        """Clean up HTTP client resources."""
        if self._client:
            try:
                await self._client.aclose()
            except Exception as e:
                logger.warning(f"Error during HTTP client cleanup: {e}")
            finally:
                self._client = None
                self._connected = False

    async def get_json(
        self,
        endpoint: str,
        trace_id: Optional[str] = None,
        expected_key: Optional[str] = None,
        default_value: Any = None,
    ) -> Any:
        """
        Perform GET request and return JSON response.

        Args:
            endpoint: API endpoint (relative to server URL)
            trace_id: Optional trace ID for request tracing
            expected_key: Optional key to extract from response
            default_value: Default value if expected_key not found

        Returns:
            JSON response data or extracted value

        Raises:
            MCPConnectionError: If HTTP client not connected or connection fails
            MCPTimeoutError: If request times out
            MCPError: If request fails or response is invalid
        """
        if not self._connected or not self._client:
            raise MCPConnectionError("HTTP transport not connected", trace_id=trace_id)

        url = f"{self.config.server_url}{endpoint}"

        try:
            logger.debug(
                f"HTTP GET request to {endpoint}",
                extra={"url": redact_url_params(url), "trace_id": trace_id},
            )

            response = await self._client.get(url)

            # Handle different status codes
            self._handle_get_response_status(response, endpoint, trace_id)

            # Parse JSON response
            result = response.json()

            # Extract expected key if specified
            if expected_key is not None:
                if isinstance(result, dict) and expected_key in result:
                    value = result[expected_key]
                    logger.debug(
                        f"Extracted key '{expected_key}' from response",
                        extra={
                            "endpoint": endpoint,
                            "trace_id": trace_id,
                            "value_type": type(value).__name__,
                        },
                    )
                    return value
                else:
                    logger.warning(
                        f"Expected key '{expected_key}' not found in response",
                        extra={
                            "endpoint": endpoint,
                            "trace_id": trace_id,
                            "response_keys": (
                                list(result.keys()) if isinstance(result, dict) else None
                            ),
                        },
                    )
                    return default_value

            return result

        except httpx.TimeoutException as e:
            error_msg = f"Timeout on GET {endpoint}"
            logger.error(error_msg, extra={"endpoint": endpoint, "trace_id": trace_id})
            raise MCPTimeoutError(error_msg, trace_id=trace_id) from e
        except httpx.RequestError as e:
            error_msg = f"Request error on GET {endpoint}: {e}"
            logger.error(error_msg, extra={"endpoint": endpoint, "trace_id": trace_id})
            raise MCPConnectionError(error_msg, trace_id=trace_id) from e
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from GET {endpoint}: {e}"
            logger.error(error_msg, extra={"endpoint": endpoint, "trace_id": trace_id})
            raise MCPError(
                "Invalid JSON response from server", code="invalid_json", trace_id=trace_id
            ) from e
        except Exception as e:
            error_msg = f"Unexpected error on GET {endpoint}: {e}"
            logger.error(
                error_msg,
                extra={"endpoint": endpoint, "trace_id": trace_id, "error_type": type(e).__name__},
            )
            raise MCPError(error_msg, trace_id=trace_id) from e

    def _handle_get_response_status(
        self, response: httpx.Response, endpoint: str, trace_id: Optional[str] = None
    ) -> None:
        """Handle HTTP response status codes for GET requests."""
        if 200 <= response.status_code < 300:
            return  # Success

        response_text = response.text[:200] if response.text else "No response body"

        # Use centralized error mapping
        error_message = f"GET {endpoint} failed: {response_text}"
        error_details = {
            "endpoint": endpoint,
            "response_snippet": response_text,
            "request_id": getattr(response, "headers", {}).get("x-request-id"),
        }

        # Extract Retry-After header for rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            if retry_after:
                try:
                    error_details["retry_after_seconds"] = int(retry_after)
                except ValueError:
                    error_details["retry_after_header"] = retry_after

        mapped_error = map_http_status_to_error(
            response.status_code, error_message, trace_id=trace_id, details=error_details
        )

        # Add retry_after to rate limit errors
        if hasattr(mapped_error, "retry_after") and "retry_after_seconds" in error_details:
            mapped_error.retry_after = error_details["retry_after_seconds"]

        raise mapped_error

    def update_client(self, client: httpx.AsyncClient, server_url: str) -> None:
        """
        Update the HTTP client and server URL.

        Args:
            client: New HTTP client to use
            server_url: Server URL for requests
        """
        self._client = client
        self.server_url = server_url
        logger.debug("HTTP client updated", extra={"server_url": redact_url_params(server_url)})


# Backward compatibility alias - HTTPTransport acts as HTTPClientManager
HTTPClientManager = HTTPTransport
