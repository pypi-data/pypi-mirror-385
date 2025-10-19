"""
Core MCP SDK components.

This module contains the fundamental classes and utilities for the Veris Memory MCP SDK:
- MCPClient: Main client for MCP communication
- MCPConfig: Configuration management
- Schemas: Data structures for MCP protocol
- Errors: Exception hierarchy for error handling
"""

from .client import MCPClient
from .config import MCPConfig, MCPConnectionPool
from .errors import (
    MCPConnectionError,
    MCPError,
    MCPSecurityError,
    MCPTimeoutError,
    MCPValidationError,
)
from .schemas import MCPClientInfo, MCPMethod, MCPResponse, MCPServerInfo, MCPToolCall

__all__ = [
    "MCPClient",
    "MCPConfig",
    "MCPConnectionPool",
    "MCPMethod",
    "MCPClientInfo",
    "MCPServerInfo",
    "MCPToolCall",
    "MCPResponse",
    "MCPError",
    "MCPConnectionError",
    "MCPTimeoutError",
    "MCPValidationError",
    "MCPSecurityError",
]
