"""Veris Memory MCP SDK error definitions."""

from typing import Any, Dict, Optional


class MCPError(Exception):
    """
    Base MCP protocol error for Veris Memory operations.

    All Veris Memory MCP SDK exceptions inherit from this base class,
    providing consistent error handling and debugging information.

    Attributes:
        code: Optional error code for programmatic handling
        details: Additional error details and context
        trace_id: Trace ID for debugging and correlation
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ):
        """Initialize MCP error.

        Args:
            message: Human-readable error message
            code: Optional error code for programmatic handling
            details: Optional error details and context
            trace_id: Optional trace ID for debugging and correlation
        """
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.trace_id = trace_id

    def __str__(self) -> str:
        """String representation with debugging information."""
        parts = [super().__str__()]
        if self.code:
            parts.append(f"Code: {self.code}")
        if self.trace_id:
            parts.append(f"Trace: {self.trace_id}")
        return " | ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error": str(self),
            "code": self.code,
            "details": self.details,
            "trace_id": self.trace_id,
            "type": self.__class__.__name__,
        }


class MCPConnectionError(MCPError):
    """
    MCP connection error for Veris Memory.

    Raised when connection to Veris Memory server fails,
    including network issues, authentication failures,
    and server unavailability.

    Example:
        ```python
        try:
            await client.connect()
        except MCPConnectionError as e:
            print(f"Failed to connect to Veris Memory: {e}")
            if e.code == "AUTH_FAILED":
                print("Check your API key")
        ```
    """

    pass


class MCPTimeoutError(MCPError):
    """
    MCP timeout error for Veris Memory operations.

    Raised when operations exceed configured timeout limits,
    including connection timeouts, request timeouts, and
    total operation timeouts.
    """

    pass


class MCPRetryExhaustedError(MCPError):
    """
    MCP retry attempts exhausted error.

    Raised when all retry attempts have been exhausted
    for a failing operation.

    Attributes:
        attempts: Number of retry attempts made
        last_error: The final error that caused the failure
    """

    def __init__(self, message: str, attempts: int, last_error: Exception):
        """Initialize retry exhausted error.

        Args:
            message: Error message
            attempts: Number of attempts made
            last_error: The final underlying error
        """
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error


class MCPCircuitBreakerError(MCPError):
    """
    MCP circuit breaker error.

    Raised when the circuit breaker is open due to
    repeated failures, preventing further requests.

    Attributes:
        failure_count: Number of failures that triggered the circuit breaker
        timeout_until: Timestamp when circuit breaker will attempt recovery
    """

    def __init__(self, message: str, failure_count: int, timeout_until: float):
        """Initialize circuit breaker error.

        Args:
            message: Error message
            failure_count: Number of failures
            timeout_until: Recovery timeout timestamp
        """
        super().__init__(message)
        self.failure_count = failure_count
        self.timeout_until = timeout_until


class MCPValidationError(MCPError):
    """
    MCP validation error for Veris Memory operations.

    Raised when request validation fails, including
    missing required fields, invalid data types,
    or constraint violations.

    Example:
        ```python
        try:
            await client.call_tool("store_context", {})
        except MCPValidationError as e:
            print(f"Invalid request: {e}")
            # e.details contains validation details
        ```
    """

    pass


class MCPSecurityError(MCPError):
    """
    MCP security error for Veris Memory operations.

    Raised when security checks fail, including
    missing user scoping, authentication failures,
    or unauthorized access attempts.

    Example:
        ```python
        try:
            await client.call_tool("retrieve_context", {})
        except MCPSecurityError as e:
            print(f"Security error: {e}")
            if "user_id" in str(e):
                print("User ID is required for this operation")
        ```
    """

    pass


class MCPRateLimitError(MCPError):
    """
    MCP rate limit error for Veris Memory operations.

    Raised when rate limits are exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying
    """

    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs: Any) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            **kwargs: Additional error parameters
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class MCPQuotaExceededError(MCPError):
    """
    MCP quota exceeded error for Veris Memory operations.

    Raised when usage quotas are exceeded.

    Attributes:
        quota_type: Type of quota that was exceeded
        current_usage: Current usage amount
        quota_limit: Maximum allowed usage
    """

    def __init__(
        self,
        message: str,
        quota_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        quota_limit: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize quota exceeded error.

        Args:
            message: Error message
            quota_type: Type of quota exceeded
            current_usage: Current usage
            quota_limit: Quota limit
            **kwargs: Additional error parameters
        """
        super().__init__(message, **kwargs)
        self.quota_type = quota_type
        self.current_usage = current_usage
        self.quota_limit = quota_limit


class MCPAuthenticationError(MCPSecurityError):
    """
    Authentication error (401).

    Raised when authentication credentials are missing,
    invalid, or expired.
    """

    pass


class MCPAuthorizationError(MCPSecurityError):
    """
    Authorization error (403).

    Raised when the authenticated user lacks permission
    for the requested operation.
    """

    pass


class MCPNotFoundError(MCPError):
    """
    Resource not found error (404).

    Raised when the requested resource or endpoint
    does not exist.
    """

    pass


class MCPConflictError(MCPError):
    """
    Conflict error (409).

    Raised when the request conflicts with the current
    state of the resource.
    """

    pass


class MCPServerError(MCPConnectionError):
    """
    Server error (5xx).

    Raised when the server encounters an error
    processing the request.
    """

    pass


def map_http_status_to_error(
    status_code: int,
    message: str,
    trace_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> MCPError:
    """
    Map HTTP status code to appropriate MCP error.

    Args:
        status_code: HTTP status code
        message: Error message
        trace_id: Optional trace ID
        details: Optional error details

    Returns:
        Appropriate MCP error instance
    """
    error_details = details or {}
    error_details["status_code"] = status_code

    if status_code == 400:
        return MCPValidationError(
            message, code="validation_error", trace_id=trace_id, details=error_details
        )
    elif status_code == 401:
        return MCPAuthenticationError(
            message, code="authentication_required", trace_id=trace_id, details=error_details
        )
    elif status_code == 403:
        return MCPAuthorizationError(
            message, code="access_denied", trace_id=trace_id, details=error_details
        )
    elif status_code == 404:
        return MCPNotFoundError(message, code="not_found", trace_id=trace_id, details=error_details)
    elif status_code == 409:
        return MCPConflictError(message, code="conflict", trace_id=trace_id, details=error_details)
    elif status_code == 429:
        return MCPRateLimitError(
            message, code="rate_limit_exceeded", trace_id=trace_id, details=error_details
        )
    elif status_code == 402:
        # Payment required - treat as quota exceeded
        return MCPQuotaExceededError(
            message,
            quota_type="payment_required",
            code="quota_exceeded",
            trace_id=trace_id,
            details=error_details,
        )
    elif 500 <= status_code < 600:
        return MCPServerError(
            message, code=f"server_error_{status_code}", trace_id=trace_id, details=error_details
        )
    else:
        # Other client errors (4xx)
        return MCPError(
            message, code=f"http_error_{status_code}", trace_id=trace_id, details=error_details
        )
