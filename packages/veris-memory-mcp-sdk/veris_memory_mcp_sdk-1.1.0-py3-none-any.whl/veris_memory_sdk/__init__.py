"""
Veris Memory MCP SDK

A comprehensive Python SDK for interacting with Veris Memory via the Model Context Protocol (MCP).
Provides high-level abstractions, robust error handling, and production-ready features.
"""

import logging
import sys

__version__ = "1.1.0"
__author__ = "◎ Veris Memory Team"
__license__ = "MIT"

from .core.client import MCPClient
from .core.config import MCPConfig
from .core.errors import (
    MCPCircuitBreakerError,
    MCPConnectionError,
    MCPError,
    MCPQuotaExceededError,
    MCPRateLimitError,
    MCPRetryExhaustedError,
    MCPSecurityError,
    MCPTimeoutError,
    MCPValidationError,
)
from .core.schemas import MCPClientInfo, MCPResponse, MCPServerInfo, MCPToolCall
from .monitoring.tracing import get_tracer, start_trace
from .transport.policies import CircuitBreakerPolicy, RetryPolicy, TransportPolicy

# Main exports
__all__ = [
    # Core classes
    "MCPClient",
    "MCPConfig",
    "MCPClientInfo",
    "MCPServerInfo",
    "MCPToolCall",
    "MCPResponse",
    # Error classes
    "MCPError",
    "MCPConnectionError",
    "MCPTimeoutError",
    "MCPValidationError",
    "MCPSecurityError",
    "MCPRetryExhaustedError",
    "MCPCircuitBreakerError",
    "MCPRateLimitError",
    "MCPQuotaExceededError",
    # Transport classes
    "TransportPolicy",
    "RetryPolicy",
    "CircuitBreakerPolicy",
    # Monitoring classes
    "get_tracer",
    "start_trace",
    # Package info
    "__version__",
    "__author__",
    "__license__",
]

# Package-level configuration
# Set up default logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Version compatibility check
if sys.version_info < (3, 10):
    raise RuntimeError("Veris Memory MCP SDK requires Python 3.10 or higher")
