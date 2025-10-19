"""
Transport layer for Veris Memory MCP SDK.

Provides resilient transport mechanisms including:
- Retry policies with exponential backoff
- Circuit breaker pattern for fault tolerance
- Connection pooling and management
- Request/response handling
- HTTP and WebSocket transport implementations
"""

from .factory import TransportFactory
from .http_transport import HTTPTransport
from .policies import CircuitBreakerPolicy, RetryPolicy, TransportPolicy
from .websocket_transport import WebSocketTransport

__all__ = [
    "TransportPolicy",
    "RetryPolicy",
    "CircuitBreakerPolicy",
    "TransportFactory",
    "HTTPTransport",
    "WebSocketTransport",
]
