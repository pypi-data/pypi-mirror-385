"""Transport factory for Veris Memory MCP SDK."""

from typing import Union

from ..core.config import MCPConfig
from ..core.errors import MCPConnectionError
from ..core.interfaces import MCPTransport
from .http_transport import HTTPTransport
from .websocket_transport import WebSocketTransport


class TransportFactory:
    """
    Factory for creating appropriate transport instances.

    Handles the creation and configuration of different transport
    types based on configuration and availability.
    """

    @staticmethod
    def create_transport(config: MCPConfig) -> Union[HTTPTransport, WebSocketTransport]:
        """
        Create transport instance based on configuration.

        Args:
            config: MCP configuration object

        Returns:
            Configured transport instance

        Raises:
            MCPConnectionError: If required dependencies are not available
        """
        if config.use_websocket:
            return TransportFactory._create_websocket_transport(config)
        else:
            return TransportFactory._create_http_transport(config)

    @staticmethod
    def _create_http_transport(config: MCPConfig) -> HTTPTransport:
        """
        Create HTTP transport instance.

        Args:
            config: MCP configuration object

        Returns:
            Configured HTTP transport

        Raises:
            MCPConnectionError: If httpx is not available
        """
        try:
            return HTTPTransport(config)
        except MCPConnectionError as e:
            # Re-raise with additional context
            raise MCPConnectionError(
                f"Failed to create HTTP transport: {e}. " "Install httpx with: pip install httpx"
            ) from e

    @staticmethod
    def _create_websocket_transport(config: MCPConfig) -> WebSocketTransport:
        """
        Create WebSocket transport instance.

        Args:
            config: MCP configuration object

        Returns:
            Configured WebSocket transport

        Raises:
            MCPConnectionError: If websockets is not available
        """
        try:
            return WebSocketTransport(config)
        except MCPConnectionError as e:
            # Re-raise with additional context
            raise MCPConnectionError(
                f"Failed to create WebSocket transport: {e}. "
                "Install websockets with: pip install websockets"
            ) from e

    @staticmethod
    def get_supported_transports() -> list[str]:
        """
        Get list of supported transport types.

        Returns:
            List of supported transport names
        """
        supported = []

        # Check HTTP support
        try:
            import httpx

            supported.append("http")
        except ImportError:
            pass

        # Check WebSocket support
        try:
            import websockets

            supported.append("websocket")
        except ImportError:
            pass

        return supported

    @staticmethod
    def validate_transport_availability(config: MCPConfig) -> None:
        """
        Validate that the configured transport is available.

        Args:
            config: MCP configuration object

        Raises:
            MCPConnectionError: If configured transport is not available
        """
        supported = TransportFactory.get_supported_transports()

        if config.use_websocket and "websocket" not in supported:
            raise MCPConnectionError(
                "WebSocket transport requested but 'websockets' package not available. "
                "Install with: pip install websockets"
            )

        if not config.use_websocket and "http" not in supported:
            raise MCPConnectionError(
                "HTTP transport requested but 'httpx' package not available. "
                "Install with: pip install httpx"
            )

        if not supported:
            raise MCPConnectionError(
                "No transport packages available. "
                "Install either 'httpx' for HTTP or 'websockets' for WebSocket support."
            )
