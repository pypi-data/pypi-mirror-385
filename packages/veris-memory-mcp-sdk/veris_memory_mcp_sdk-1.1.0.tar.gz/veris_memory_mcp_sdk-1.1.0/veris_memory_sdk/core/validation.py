"""Veris Memory MCP SDK input validation and sanitization."""

import os
import re
import sys
import urllib.parse
from typing import Any, Dict, List, Optional, Union

from .errors import MCPSecurityError, MCPValidationError

# Type aliases for validation
ValidationRules = Dict[str, Any]
FieldConstraints = Dict[str, Union[str, int, bool, List[str]]]

# Valid context types per veris-memory-mcp-server issue #2
VALID_CONTEXT_TYPES = frozenset({"design", "decision", "trace", "sprint", "log"})


class InputValidator:
    """
    Comprehensive input validator for Veris Memory MCP operations.

    Provides validation for tool calls, arguments, and security-sensitive
    parameters to prevent injection attacks and ensure data integrity.
    """

    # Maximum sizes for various inputs
    MAX_TOOL_NAME_LENGTH = 100
    MAX_STRING_FIELD_LENGTH = 10000
    MAX_NESTED_DEPTH = 10
    MAX_ARRAY_LENGTH = 1000
    MAX_ARGUMENT_COUNT = 50

    # Allowed characters for tool names (alphanumeric, underscore, hyphen)
    TOOL_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

    # Patterns for potentially dangerous content
    DANGEROUS_PATTERNS = [
        re.compile(r"<\s*script[^>]*>", re.IGNORECASE),  # Script tags
        re.compile(r"javascript\s*:", re.IGNORECASE),  # JavaScript URLs
        re.compile(r"on\w+\s*=", re.IGNORECASE),  # Event handlers
        re.compile(r"eval\s*\(", re.IGNORECASE),  # eval() calls
        re.compile(r"exec\s*\(", re.IGNORECASE),  # exec() calls
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize input validator.

        Args:
            strict_mode: Whether to use strict validation rules
        """
        self.strict_mode = strict_mode

    def validate_tool_name(self, tool_name: str) -> None:
        """
        Validate tool name for security and format compliance.

        Args:
            tool_name: Name of the tool to validate

        Raises:
            MCPValidationError: If tool name is invalid
            MCPSecurityError: If tool name contains dangerous patterns
        """
        if not tool_name:
            raise MCPValidationError("Tool name is required")

        if not isinstance(tool_name, str):
            raise MCPValidationError(f"Tool name must be a string, got {type(tool_name).__name__}")

        if len(tool_name) > self.MAX_TOOL_NAME_LENGTH:
            raise MCPValidationError(
                f"Tool name too long: {len(tool_name)} > {self.MAX_TOOL_NAME_LENGTH}"
            )

        if not self.TOOL_NAME_PATTERN.match(tool_name):
            raise MCPSecurityError(
                f"Tool name contains invalid characters: {tool_name}. "
                "Only alphanumeric characters, underscores, and hyphens are allowed."
            )

    def validate_arguments(self, arguments: Dict[str, Any], tool_name: str) -> None:
        """
        Validate tool arguments for security and structure.

        Args:
            arguments: Tool arguments to validate
            tool_name: Name of the tool for context

        Raises:
            MCPValidationError: If arguments are invalid
            MCPSecurityError: If arguments contain dangerous content
        """
        if not isinstance(arguments, dict):
            raise MCPValidationError("Tool arguments must be a dictionary")

        if len(arguments) > self.MAX_ARGUMENT_COUNT:
            raise MCPValidationError(
                f"Too many arguments: {len(arguments)} > {self.MAX_ARGUMENT_COUNT}"
            )

        # Validate argument structure recursively
        self._validate_data_structure(arguments, "arguments", depth=0)

        # Tool-specific validation
        self._validate_tool_specific_arguments(arguments, tool_name)

    def _validate_data_structure(self, data: Any, field_path: str, depth: int) -> None:
        """
        Recursively validate data structure for security and size limits.

        Args:
            data: Data to validate
            field_path: Path to the current field (for error messages)
            depth: Current nesting depth

        Raises:
            MCPValidationError: If structure is invalid
            MCPSecurityError: If dangerous content is detected
        """
        if depth > self.MAX_NESTED_DEPTH:
            raise MCPValidationError(
                f"Data structure too deeply nested at {field_path}: "
                f"{depth} > {self.MAX_NESTED_DEPTH}"
            )

        if isinstance(data, str):
            self._validate_string_content(data, field_path)
        elif isinstance(data, list):
            self._validate_array(data, field_path, depth)
        elif isinstance(data, dict):
            self._validate_object(data, field_path, depth)
        elif isinstance(data, (int, float, bool)) or data is None:
            # Basic types are safe
            pass
        else:
            raise MCPValidationError(
                f"Unsupported data type at {field_path}: {type(data).__name__}"
            )

    def _validate_string_content(self, content: str, field_path: str) -> None:
        """
        Validate string content for length and security.

        Args:
            content: String content to validate
            field_path: Path to the field for error messages

        Raises:
            MCPValidationError: If string is too long
            MCPSecurityError: If dangerous patterns are detected
        """
        if len(content) > self.MAX_STRING_FIELD_LENGTH:
            raise MCPValidationError(
                f"String too long at {field_path}: {len(content)} > {self.MAX_STRING_FIELD_LENGTH}"
            )

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.search(content):
                raise MCPSecurityError(
                    f"Potentially dangerous content detected at {field_path}: "
                    f"matches pattern {pattern.pattern}"
                )

    def _validate_array(self, array: List[Any], field_path: str, depth: int) -> None:
        """
        Validate array structure and contents.

        Args:
            array: Array to validate
            field_path: Path to the field
            depth: Current nesting depth
        """
        if len(array) > self.MAX_ARRAY_LENGTH:
            raise MCPValidationError(
                f"Array too long at {field_path}: {len(array)} > {self.MAX_ARRAY_LENGTH}"
            )

        for i, item in enumerate(array):
            self._validate_data_structure(item, f"{field_path}[{i}]", depth + 1)

    def _validate_object(self, obj: Dict[str, Any], field_path: str, depth: int) -> None:
        """
        Validate object structure and contents.

        Args:
            obj: Object to validate
            field_path: Path to the field
            depth: Current nesting depth
        """
        if len(obj) > self.MAX_ARGUMENT_COUNT:
            raise MCPValidationError(
                f"Object has too many fields at {field_path}: "
                f"{len(obj)} > {self.MAX_ARGUMENT_COUNT}"
            )

        for key, value in obj.items():
            if not isinstance(key, str):
                raise MCPValidationError(
                    f"Object key must be string at {field_path}, got {type(key).__name__}"
                )

            self._validate_string_content(key, f"{field_path}.{key}")
            self._validate_data_structure(value, f"{field_path}.{key}", depth + 1)

    def _validate_tool_specific_arguments(self, arguments: Dict[str, Any], tool_name: str) -> None:
        """
        Validate arguments specific to known Veris Memory tools.

        Args:
            arguments: Tool arguments
            tool_name: Name of the tool

        Raises:
            MCPValidationError: If tool-specific validation fails
        """
        if tool_name == "store_context":
            self._validate_store_context_arguments(arguments)
        elif tool_name == "retrieve_context":
            self._validate_retrieve_context_arguments(arguments)
        elif tool_name == "search_context":
            # Legacy endpoint - fallback to retrieve_context validation
            self._validate_retrieve_context_arguments(arguments)
        elif tool_name == "delete_context":
            self._validate_delete_context_arguments(arguments)
        elif tool_name == "search_context":
            self._validate_search_context_arguments(arguments)

    def _validate_store_context_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate store_context tool arguments."""
        required_fields = ["type", "content"]
        self._check_required_fields(arguments, required_fields, "store_context")

        # Validate type field (updated per issue #2)
        context_type = arguments["type"]
        if not isinstance(context_type, str):
            raise MCPValidationError("store_context 'type' must be a string")

        # Enforce allowed types per veris-memory-mcp-server issue #2
        if context_type not in VALID_CONTEXT_TYPES:
            raise MCPValidationError(
                f"store_context 'type' must be one of: {', '.join(sorted(VALID_CONTEXT_TYPES))}. "
                f"Got: '{context_type}'"
            )

        content = arguments["content"]
        if not isinstance(content, dict):
            raise MCPValidationError("store_context 'content' must be a dictionary")

        # Content validation is flexible - no required 'text' field
        # Different content types may have different structures

    def _validate_retrieve_context_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate retrieve_context tool arguments."""
        required_fields = ["query"]
        self._check_required_fields(arguments, required_fields, "retrieve_context")

        query = arguments["query"]
        if not isinstance(query, str):
            raise MCPValidationError("retrieve_context 'query' must be a string")

        if not query.strip():
            raise MCPValidationError("retrieve_context 'query' cannot be empty")

        # Validate optional parameters
        if "limit" in arguments:
            limit = arguments["limit"]
            if not isinstance(limit, int) or limit <= 0 or limit > 1000:
                raise MCPValidationError(
                    "retrieve_context 'limit' must be an integer between 1 and 1000"
                )

    def _validate_delete_context_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate delete_context tool arguments."""
        required_fields = ["context_id"]
        self._check_required_fields(arguments, required_fields, "delete_context")

        context_id = arguments["context_id"]
        if not isinstance(context_id, str):
            raise MCPValidationError("delete_context 'context_id' must be a string")

        if not context_id.strip():
            raise MCPValidationError("delete_context 'context_id' cannot be empty")

    def _validate_search_context_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate search_context tool arguments."""
        if not arguments:
            raise MCPValidationError("search_context requires at least one search parameter")

        allowed_fields = ["query", "filters", "limit", "offset", "sort_by"]
        for field in arguments:
            if field not in allowed_fields:
                raise MCPValidationError(f"search_context unknown field: {field}")

    def _check_required_fields(
        self, arguments: Dict[str, Any], required_fields: List[str], tool_name: str
    ) -> None:
        """
        Check that all required fields are present.

        Args:
            arguments: Arguments to check
            required_fields: List of required field names
            tool_name: Tool name for error messages
        """
        for field in required_fields:
            if field not in arguments:
                raise MCPValidationError(f"{tool_name} requires '{field}' argument")

    def validate_user_id(self, user_id: Optional[str]) -> None:
        """
        Validate user ID format and security.

        Args:
            user_id: User ID to validate

        Raises:
            MCPValidationError: If user ID format is invalid
            MCPSecurityError: If user ID contains dangerous content
        """
        if user_id is None:
            return

        if not isinstance(user_id, str):
            raise MCPValidationError(f"User ID must be a string, got {type(user_id).__name__}")

        if not user_id.strip():
            raise MCPValidationError("User ID cannot be empty")

        if len(user_id) > 255:
            raise MCPValidationError(f"User ID too long: {len(user_id)} > 255")

        # Check for dangerous patterns in user ID
        self._validate_string_content(user_id, "user_id")

    def validate_trace_id(self, trace_id: Optional[str]) -> None:
        """
        Validate trace ID format.

        Args:
            trace_id: Trace ID to validate

        Raises:
            MCPValidationError: If trace ID format is invalid
        """
        if trace_id is None:
            return

        if not isinstance(trace_id, str):
            raise MCPValidationError(f"Trace ID must be a string, got {type(trace_id).__name__}")

        if len(trace_id) > 100:
            raise MCPValidationError(f"Trace ID too long: {len(trace_id)} > 100")

        # Trace IDs should only contain safe characters
        if not re.match(r"^[a-zA-Z0-9_-]+$", trace_id):
            raise MCPValidationError("Trace ID contains invalid characters")

    def validate_server_url(self, server_url: str) -> None:
        """
        Validate server URL format and security.

        Args:
            server_url: Server URL to validate

        Raises:
            MCPValidationError: If URL format is invalid
            MCPSecurityError: If URL is potentially dangerous
        """
        if not server_url:
            raise MCPValidationError("Server URL cannot be empty")

        if not isinstance(server_url, str):
            raise MCPValidationError(
                f"Server URL must be a string, got {type(server_url).__name__}"
            )

        # Parse URL to validate structure
        try:
            parsed = urllib.parse.urlparse(server_url)
        except Exception as e:
            raise MCPValidationError(f"Invalid URL format: {e}")

        # Check scheme
        if parsed.scheme not in ["http", "https", "ws", "wss"]:
            raise MCPValidationError(
                f"Invalid URL scheme: {parsed.scheme}. Must be http, https, ws, or wss"
            )

        # Security check: prevent local network access in production
        if self.strict_mode and parsed.hostname:
            if parsed.hostname in ["localhost", "127.0.0.1", "::1"]:
                raise MCPSecurityError("Local URLs not allowed in strict mode")

            # Check for private IP ranges
            if self._is_private_ip(parsed.hostname):
                raise MCPSecurityError("Private network URLs not allowed in strict mode")

    def _is_private_ip(self, hostname: str) -> bool:
        """
        Check if hostname is a private IP address.

        Args:
            hostname: Hostname to check

        Returns:
            True if hostname appears to be a private IP
        """
        import ipaddress

        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_private
        except ValueError:
            # Not an IP address
            return False

    def sanitize_log_data(self, data: Any, max_length: int = 200) -> str:
        """
        Sanitize data for safe logging.

        Args:
            data: Data to sanitize
            max_length: Maximum length of sanitized output

        Returns:
            Sanitized string representation safe for logging
        """
        if data is None:
            return "null"

        # Convert to string and truncate
        str_data = str(data)
        if len(str_data) > max_length:
            str_data = str_data[: max_length - 3] + "..."

        # Remove potentially sensitive patterns
        sanitized = re.sub(r'(["\'])(.*?)\1', r"\1[REDACTED]\1", str_data)
        sanitized = re.sub(
            r"(password|key|token|secret)[\s:=]+\S+",
            r"\1=[REDACTED]",
            sanitized,
            flags=re.IGNORECASE,
        )

        return sanitized


# Global validator instance
# Use non-strict mode for tests to allow localhost URLs
_is_testing = "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None
_validator = InputValidator(strict_mode=not _is_testing)


def get_validator() -> InputValidator:
    """
    Get global input validator instance.

    Returns:
        Global InputValidator instance
    """
    return _validator


def set_validator(validator: InputValidator) -> None:
    """
    Set global input validator instance.

    Args:
        validator: New validator instance
    """
    global _validator
    _validator = validator
