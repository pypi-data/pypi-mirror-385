"""Veris Memory MCP SDK logging utilities and context enhancement."""

import logging
import time
import traceback
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from .security import sanitize_log_data

# Context variables for request tracking
_request_context: ContextVar[Optional["RequestContext"]] = ContextVar(
    "request_context", default=None
)


@dataclass
class RequestContext:
    """
    Request context for enhanced logging and debugging.

    Provides contextual information that gets automatically included
    in log messages for better traceability and debugging.
    """

    request_id: str
    """Unique identifier for this request"""

    user_id: Optional[str] = None
    """User ID for user-scoped operations (PII-safe hash used in logs)"""

    trace_id: Optional[str] = None
    """Distributed tracing ID"""

    operation: Optional[str] = None
    """High-level operation name"""

    tool_name: Optional[str] = None
    """MCP tool being called"""

    start_time: float = field(default_factory=time.time)
    """Request start timestamp"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional contextual metadata"""

    def to_log_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary for structured logging.

        Returns:
            Dictionary with sanitized context information
        """
        duration_ms = (time.time() - self.start_time) * 1000

        return {
            "request_id": self.request_id,
            "user_id_hash": hash(self.user_id) if self.user_id else None,
            "trace_id": self.trace_id,
            "operation": self.operation,
            "tool_name": self.tool_name,
            "duration_ms": round(duration_ms, 2),
            **self.metadata,
        }


class ContextualLogger:
    """
    Enhanced logger that automatically includes request context.

    Provides structured logging with automatic context injection,
    performance tracking, and security-aware log sanitization.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initialize contextual logger.

        Args:
            logger: Base logger instance to wrap
        """
        self.logger = logger

    def _get_enhanced_extra(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get enhanced log extra data with automatic context injection.

        Args:
            extra: Additional log context

        Returns:
            Combined extra data with request context
        """
        enhanced_extra = {}

        # Add request context if available
        context = _request_context.get()
        if context:
            enhanced_extra.update(context.to_log_dict())

        # Add custom extra data with security sanitization
        if extra:
            sanitized_extra = sanitize_log_data(extra)
            enhanced_extra.update(sanitized_extra)

        return enhanced_extra

    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message with context."""
        self.logger.debug(msg, extra=self._get_enhanced_extra(extra))

    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message with context."""
        self.logger.info(msg, extra=self._get_enhanced_extra(extra))

    def warning(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message with context."""
        self.logger.warning(msg, extra=self._get_enhanced_extra(extra))

    def error(
        self, msg: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False
    ) -> None:
        """Log error message with context and optional exception info."""
        enhanced_extra = self._get_enhanced_extra(extra)

        # Add exception context if requested
        if exc_info:
            enhanced_extra["exception_traceback"] = traceback.format_exc()

        self.logger.error(msg, extra=enhanced_extra, exc_info=exc_info)

    def critical(
        self, msg: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False
    ) -> None:
        """Log critical message with context and optional exception info."""
        enhanced_extra = self._get_enhanced_extra(extra)

        if exc_info:
            enhanced_extra["exception_traceback"] = traceback.format_exc()

        self.logger.critical(msg, extra=enhanced_extra, exc_info=exc_info)

    def log_operation_start(self, operation: str, **metadata: Any) -> None:
        """
        Log the start of an operation with timing.

        Args:
            operation: Operation name
            **metadata: Additional operation metadata
        """
        self.info(
            f"Starting operation: {operation}",
            extra={"operation_event": "start", "operation": operation, **metadata},
        )

    def log_operation_success(self, operation: str, duration_ms: float, **metadata: Any) -> None:
        """
        Log successful completion of an operation.

        Args:
            operation: Operation name
            duration_ms: Operation duration in milliseconds
            **metadata: Additional operation metadata
        """
        self.info(
            f"Operation completed successfully: {operation} ({duration_ms:.2f}ms)",
            extra={
                "operation_event": "success",
                "operation": operation,
                "operation_duration_ms": duration_ms,
                **metadata,
            },
        )

    def log_operation_error(
        self, operation: str, error: Exception, duration_ms: float, **metadata: Any
    ) -> None:
        """
        Log operation failure with error details.

        Args:
            operation: Operation name
            error: Exception that occurred
            duration_ms: Operation duration in milliseconds
            **metadata: Additional operation metadata
        """
        self.error(
            f"Operation failed: {operation} ({duration_ms:.2f}ms) - {error}",
            extra={
                "operation_event": "error",
                "operation": operation,
                "operation_duration_ms": duration_ms,
                "error_type": type(error).__name__,
                "error_message": str(error),
                **metadata,
            },
            exc_info=True,
        )

    def log_validation_error(self, field: str, value: Any, error: str, **metadata: Any) -> None:
        """
        Log validation error with field context.

        Args:
            field: Field that failed validation
            value: Value that failed (will be sanitized)
            error: Validation error message
            **metadata: Additional context
        """
        from .validation import get_validator

        sanitized_value = get_validator().sanitize_log_data(value)

        self.warning(
            f"Validation failed for field '{field}': {error}",
            extra={
                "validation_event": "error",
                "field": field,
                "sanitized_value": sanitized_value,
                "validation_error": error,
                **metadata,
            },
        )

    def log_security_event(self, event_type: str, description: str, **metadata: Any) -> None:
        """
        Log security-related event with high priority.

        Args:
            event_type: Type of security event
            description: Event description
            **metadata: Additional security context
        """
        self.warning(
            f"Security event [{event_type}]: {description}",
            extra={
                "security_event": event_type,
                "security_description": description,
                "requires_attention": True,
                **metadata,
            },
        )

    def log_performance_warning(
        self, operation: str, duration_ms: float, threshold_ms: float, **metadata: Any
    ) -> None:
        """
        Log performance warning when operations exceed thresholds.

        Args:
            operation: Operation that was slow
            duration_ms: Actual duration
            threshold_ms: Expected threshold
            **metadata: Additional context
        """
        self.warning(
            f"Performance warning: {operation} took {duration_ms:.2f}ms "
            f"(threshold: {threshold_ms:.2f}ms)",
            extra={
                "performance_event": "slow_operation",
                "operation": operation,
                "duration_ms": duration_ms,
                "threshold_ms": threshold_ms,
                "slowness_factor": duration_ms / threshold_ms,
                **metadata,
            },
        )


def set_request_context(context: RequestContext) -> None:
    """
    Set request context for current task/thread.

    Args:
        context: Request context to set
    """
    _request_context.set(context)


def get_request_context() -> Optional[RequestContext]:
    """
    Get current request context.

    Returns:
        Current request context or None
    """
    return _request_context.get()


def clear_request_context() -> None:
    """Clear current request context."""
    _request_context.set(None)


def create_contextual_logger(name: str) -> ContextualLogger:
    """
    Create a contextual logger for the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        ContextualLogger instance
    """
    base_logger = logging.getLogger(name)
    return ContextualLogger(base_logger)


class OperationTimer:
    """
    Context manager for timing operations with automatic logging.

    Example:
        ```python
        with OperationTimer("store_context", logger, user_id="user123") as timer:
            # Perform operation
            timer.add_metadata("items_processed", 42)
        # Automatically logs success or error with timing
        ```
    """

    def __init__(
        self,
        operation: str,
        logger: ContextualLogger,
        log_start: bool = True,
        performance_threshold_ms: Optional[float] = None,
        **metadata: Any,
    ):
        """
        Initialize operation timer.

        Args:
            operation: Operation name
            logger: Contextual logger to use
            log_start: Whether to log operation start
            performance_threshold_ms: Threshold for performance warnings
            **metadata: Initial operation metadata
        """
        self.operation = operation
        self.logger = logger
        self.log_start = log_start
        self.performance_threshold_ms = performance_threshold_ms
        self.metadata = metadata
        self.start_time = 0.0
        self.error: Optional[Exception] = None

    def __enter__(self) -> "OperationTimer":
        """Start timing operation."""
        self.start_time = time.time()

        if self.log_start:
            self.logger.log_operation_start(self.operation, **self.metadata)

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Finish timing and log result."""
        duration_ms = (time.time() - self.start_time) * 1000

        if exc_type is not None:
            # Operation failed
            self.logger.log_operation_error(self.operation, exc_val, duration_ms, **self.metadata)
        else:
            # Operation succeeded
            self.logger.log_operation_success(self.operation, duration_ms, **self.metadata)

            # Check performance threshold
            if self.performance_threshold_ms and duration_ms > self.performance_threshold_ms:
                self.logger.log_performance_warning(
                    self.operation, duration_ms, self.performance_threshold_ms, **self.metadata
                )

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the operation.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value


def sanitize_error_for_logging(error: Exception, max_length: int = 500) -> Dict[str, Any]:
    """
    Sanitize exception for safe logging.

    Args:
        error: Exception to sanitize
        max_length: Maximum length of error message

    Returns:
        Sanitized error information
    """
    error_msg = str(error)
    if len(error_msg) > max_length:
        error_msg = error_msg[: max_length - 3] + "..."

    return {
        "error_type": type(error).__name__,
        "error_message": error_msg,
        "error_module": getattr(type(error), "__module__", "unknown"),
    }


def format_duration(duration_ms: float) -> str:
    """
    Format duration for human-readable logging.

    Args:
        duration_ms: Duration in milliseconds

    Returns:
        Formatted duration string
    """
    if duration_ms < 1000:
        return f"{duration_ms:.1f}ms"
    elif duration_ms < 60000:
        return f"{duration_ms/1000:.2f}s"
    else:
        return f"{duration_ms/60000:.2f}m"
