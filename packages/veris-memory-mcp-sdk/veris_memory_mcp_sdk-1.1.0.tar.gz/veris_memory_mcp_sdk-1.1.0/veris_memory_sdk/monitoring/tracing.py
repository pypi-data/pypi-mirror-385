"""Veris Memory MCP SDK distributed tracing and monitoring support."""

import logging
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, ContextManager, Dict, Generator, List, Optional

# Type aliases for monitoring operations
TraceMetrics = Dict[str, Any]
SpanData = Dict[str, Any]
TraceStats = Dict[str, Any]
TraceSummary = Dict[str, Any]

logger = logging.getLogger(__name__)

# Context variable for current trace
_current_trace: ContextVar[Optional["TraceContext"]] = ContextVar("current_trace", default=None)


@dataclass
class TraceSpan:
    """
    A trace span for tracking Veris Memory operations.

    Represents a single operation or step within a larger trace,
    providing detailed timing, tagging, and logging capabilities
    for comprehensive observability.

    Example:
        ```python
        span = trace.create_span("store_context")
        span.add_tag("user_id", user_id)
        span.add_tag("context_type", "decision")
        try:
            # Perform operation
            span.add_log("info", "Context stored successfully")
            span.finish("success")
        except Exception as e:
            span.finish("error", str(e))
        ```
    """

    span_id: str
    """Unique identifier for this span"""

    operation_name: str
    """Name of the operation being traced"""

    start_time: float
    """Unix timestamp when span started"""

    end_time: Optional[float] = None
    """Unix timestamp when span ended"""

    duration_ms: Optional[float] = None
    """Duration of the span in milliseconds"""

    status: str = "started"
    """Span status: started, success, error"""

    tags: Dict[str, Any] = field(default_factory=dict)
    """Key-value tags for categorization and filtering"""

    logs: List[Dict[str, Any]] = field(default_factory=list)
    """Structured log entries within the span"""

    error: Optional[str] = None
    """Error message if span failed"""

    def finish(self, status: str = "success", error: Optional[str] = None) -> None:
        """
        Finish the span with final status.

        Args:
            status: Final status (success, error)
            error: Error message if status is error
        """
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = status
        self.error = error

        if status == "error" and error:
            self.add_log("error", f"Span failed: {error}")

        logger.debug(
            f"Span finished: {self.operation_name} ({self.duration_ms:.2f}ms) - {status}",
            extra={
                "span_id": self.span_id,
                "operation": self.operation_name,
                "duration_ms": self.duration_ms,
                "status": status,
            },
        )

    def add_tag(self, key: str, value: Any) -> None:
        """
        Add a tag to the span for categorization.

        Args:
            key: Tag key
            value: Tag value (will be converted to string for safety)
        """
        # Convert to string for safety and consistency
        self.tags[key] = str(value) if value is not None else None

    def add_log(self, level: str, message: str, **kwargs: Any) -> None:
        """
        Add a structured log entry to the span.

        Args:
            level: Log level (info, warning, error, debug)
            message: Log message
            **kwargs: Additional structured data
        """
        self.logs.append({"timestamp": time.time(), "level": level, "message": message, **kwargs})

    def to_dict(self) -> SpanData:
        """
        Convert span to dictionary for serialization.

        Returns:
            Dictionary representation of the span
        """
        return {
            "span_id": self.span_id,
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "tags": self.tags,
            "logs": self.logs,
            "error": self.error,
        }


@dataclass
class TraceContext:
    """
    Trace context for tracking Veris Memory request flow.

    Provides a container for multiple spans that represent
    a complete operation or user request, enabling distributed
    tracing across Veris Memory components.

    Example:
        ```python
        trace = tracer.start_trace(
            operation="store_and_retrieve",
            user_id="user-123",
            request_type="context_management"
        )

        # Create spans for sub-operations
        store_span = trace.create_span("store_context")
        retrieve_span = trace.create_span("retrieve_context")

        # Get trace summary
        summary = trace.get_summary()
        ```
    """

    trace_id: str
    """Unique identifier for this trace"""

    parent_span_id: Optional[str] = None
    """Parent span ID for distributed tracing"""

    user_id: Optional[str] = None
    """User ID associated with this trace (PII-safe hash used in logs)"""

    operation: Optional[str] = None
    """High-level operation name"""

    spans: List[TraceSpan] = field(default_factory=list)
    """List of spans within this trace"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional trace metadata"""

    def create_span(self, operation_name: str, parent_span_id: Optional[str] = None) -> TraceSpan:
        """
        Create a new span within this trace.

        Args:
            operation_name: Name of the operation
            parent_span_id: Optional parent span ID

        Returns:
            New TraceSpan instance
        """
        span = TraceSpan(
            span_id=str(uuid.uuid4())[:8], operation_name=operation_name, start_time=time.time()
        )

        # Add trace context tags
        span.add_tag("trace_id", self.trace_id)
        span.add_tag("veris_memory_operation", operation_name)

        if self.user_id:
            # Use hash for PII safety in logs
            span.add_tag("user_id_hash", hash(self.user_id))

        if parent_span_id:
            span.add_tag("parent_span_id", parent_span_id)

        if self.operation:
            span.add_tag("trace_operation", self.operation)

        self.spans.append(span)
        return span

    def get_active_span(self) -> Optional[TraceSpan]:
        """
        Get the most recent active (unfinished) span.

        Returns:
            Active TraceSpan or None if no active spans
        """
        for span in reversed(self.spans):
            if span.status == "started":
                return span
        return None

    def finish_trace(self) -> None:
        """Finish all active spans in the trace."""
        active_spans = [span for span in self.spans if span.status == "started"]
        for span in active_spans:
            span.finish("success")
            logger.debug(f"Auto-finished active span: {span.operation_name}")

    def get_summary(self) -> TraceSummary:
        """
        Get trace summary with key metrics.

        Returns:
            Dictionary containing trace statistics and summary
        """
        total_duration = 0.0
        error_count = 0
        success_count = 0

        for span in self.spans:
            if span.duration_ms:
                total_duration += span.duration_ms
            if span.status == "error":
                error_count += 1
            elif span.status == "success":
                success_count += 1

        return {
            "trace_id": self.trace_id,
            "user_id_hash": hash(self.user_id) if self.user_id else None,
            "operation": self.operation,
            "span_count": len(self.spans),
            "success_count": success_count,
            "error_count": error_count,
            "total_duration_ms": total_duration,
            "avg_duration_ms": total_duration / len(self.spans) if self.spans else 0,
            "status": "error" if error_count > 0 else "success",
            "metadata": self.metadata,
        }

    def to_dict(self) -> SpanData:
        """
        Convert trace to dictionary for export/analysis.

        Returns:
            Complete dictionary representation of the trace
        """
        return {
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "user_id_hash": hash(self.user_id) if self.user_id else None,
            "operation": self.operation,
            "spans": [span.to_dict() for span in self.spans],
            "metadata": self.metadata,
            "summary": self.get_summary(),
        }


class Tracer:
    """
    Distributed tracer for Veris Memory MCP operations.

    Provides comprehensive tracing capabilities for monitoring
    and debugging Veris Memory SDK operations, including
    distributed tracing, performance monitoring, and error tracking.

    Example:
        ```python
        tracer = Tracer(enabled=True)

        # Start a trace
        trace = tracer.start_trace(
            operation="context_workflow",
            user_id="user-123"
        )

        # Use spans for operations
        with tracer.span("store_context", context_type="decision") as span:
            span.add_tag("size_bytes", len(context_data))
            # Perform operation
            span.add_log("info", "Context stored successfully")

        # Get statistics
        stats = tracer.get_trace_stats()
        ```
    """

    def __init__(self, enabled: bool = True) -> None:
        """
        Initialize tracer.

        Args:
            enabled: Whether tracing is enabled (disable for production if needed)
        """
        self.enabled = enabled
        self.traces: Dict[str, TraceContext] = {}
        self.max_traces = 1000  # Keep last N traces to prevent memory growth

        logger.info(f"Veris Memory tracer initialized (enabled: {enabled})")

    def start_trace(
        self,
        operation: str,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        **metadata: Any,
    ) -> TraceContext:
        """
        Start a new trace for Veris Memory operations.

        Args:
            operation: High-level operation name
            user_id: User ID for user-scoped operations
            trace_id: Optional custom trace ID
            parent_span_id: Parent span for distributed tracing
            **metadata: Additional trace metadata

        Returns:
            New TraceContext instance
        """
        if not self.enabled:
            return TraceContext(trace_id="disabled")

        trace_id = trace_id or str(uuid.uuid4())

        trace = TraceContext(
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            user_id=user_id,
            operation=operation,
            metadata=metadata,
        )

        # Store trace (with size limit to prevent memory leaks)
        self.traces[trace_id] = trace
        if len(self.traces) > self.max_traces:
            # Remove oldest trace
            oldest_trace_id = next(iter(self.traces))
            del self.traces[oldest_trace_id]
            logger.debug(f"Removed oldest trace {oldest_trace_id} (max_traces limit)")

        # Set as current trace in context
        _current_trace.set(trace)

        logger.debug(
            f"Started Veris Memory trace: {operation}",
            extra={
                "trace_id": trace_id,
                "user_id_hash": hash(user_id) if user_id else None,
                "operation": operation,
                "metadata": metadata,
            },
        )

        return trace

    def get_current_trace(self) -> Optional[TraceContext]:
        """
        Get current trace from context.

        Returns:
            Current TraceContext or None if no active trace
        """
        return _current_trace.get()

    def get_trace(self, trace_id: str) -> Optional[TraceContext]:
        """
        Get trace by ID.

        Args:
            trace_id: Trace identifier

        Returns:
            TraceContext or None if not found
        """
        return self.traces.get(trace_id)

    @contextmanager
    def span(
        self, operation_name: str, trace_id: Optional[str] = None, **tags: Any
    ) -> Generator[TraceSpan, None, None]:
        """
        Context manager for creating spans with automatic lifecycle management.

        Args:
            operation_name: Name of the operation
            trace_id: Optional specific trace ID
            **tags: Tags to add to the span

        Yields:
            TraceSpan instance

        Example:
            ```python
            with tracer.span("store_context", user_id="123") as span:
                span.add_tag("context_type", "decision")
                # Perform operation
                span.add_log("info", "Operation completed")
            # Span automatically finished on exit
            ```
        """
        if not self.enabled:
            # Create a dummy span that does nothing
            yield TraceSpan(
                span_id="disabled", operation_name=operation_name, start_time=time.time()
            )
            return

        # Get or create trace
        trace = None
        if trace_id:
            trace = self.get_trace(trace_id)
        if not trace:
            trace = self.get_current_trace()
        if not trace:
            trace = self.start_trace(operation_name)

        # Create span
        span = trace.create_span(operation_name)

        # Add custom tags
        for key, value in tags.items():
            span.add_tag(key, value)

        span.add_log("info", f"Started Veris Memory operation: {operation_name}")

        try:
            yield span
            span.finish("success")
            span.add_log("info", f"Completed Veris Memory operation: {operation_name}")

        except Exception as e:
            span.finish("error", str(e))
            span.add_log("error", f"Failed Veris Memory operation: {operation_name}", error=str(e))
            raise

    def finish_trace(self, trace_id: str) -> None:
        """
        Finish a trace and all its active spans.

        Args:
            trace_id: Trace identifier to finish
        """
        trace = self.traces.get(trace_id)
        if trace:
            trace.finish_trace()

            summary = trace.get_summary()
            logger.debug(
                f"Finished Veris Memory trace: {trace.operation}",
                extra={"trace_id": trace_id, "summary": summary},
            )

    def get_trace_stats(self) -> TraceStats:
        """
        Get comprehensive tracer statistics.

        Returns:
            Dictionary containing tracer metrics and status
        """
        if not self.enabled:
            return {"enabled": False}

        total_spans = sum(len(trace.spans) for trace in self.traces.values())
        error_traces = sum(
            1 for trace in self.traces.values() if trace.get_summary()["status"] == "error"
        )

        # Calculate average metrics
        if self.traces:
            avg_spans_per_trace = total_spans / len(self.traces)
            error_rate = error_traces / len(self.traces)
        else:
            avg_spans_per_trace = 0
            error_rate = 0

        return {
            "enabled": True,
            "active_traces": len(self.traces),
            "total_spans": total_spans,
            "avg_spans_per_trace": avg_spans_per_trace,
            "error_traces": error_traces,
            "error_rate": error_rate,
            "max_traces": self.max_traces,
            "memory_usage_traces": len(self.traces),
        }

    def export_traces(self, limit: int = 100) -> List[SpanData]:
        """
        Export traces for analysis and monitoring.

        Args:
            limit: Maximum number of traces to export

        Returns:
            List of trace dictionaries for analysis
        """
        traces = list(self.traces.values())[-limit:]
        return [trace.to_dict() for trace in traces]

    def clear_traces(self) -> None:
        """Clear all stored traces (useful for testing or memory management)."""
        count = len(self.traces)
        self.traces.clear()
        logger.info(f"Cleared {count} traces from tracer")


# Global tracer instance for Veris Memory SDK
_tracer = Tracer()


def get_tracer() -> Tracer:
    """
    Get global tracer instance for Veris Memory operations.

    Returns:
        Global Tracer instance
    """
    return _tracer


def set_tracer(tracer: Tracer) -> None:
    """
    Set global tracer instance.

    Args:
        tracer: New tracer instance to use globally
    """
    global _tracer
    _tracer = tracer
    logger.info("Global Veris Memory tracer updated")


def start_trace(
    operation: str, user_id: Optional[str] = None, trace_id: Optional[str] = None, **metadata: Any
) -> TraceContext:
    """
    Start a new trace using global tracer.

    Args:
        operation: Operation name
        user_id: User ID for user-scoped operations
        trace_id: Optional custom trace ID
        **metadata: Additional trace metadata

    Returns:
        New TraceContext instance
    """
    return get_tracer().start_trace(operation, user_id, trace_id, **metadata)


def span(operation_name: str, **tags: Any) -> ContextManager[TraceSpan]:
    """
    Create a span using global tracer.

    Args:
        operation_name: Name of the operation
        **tags: Tags to add to the span

    Returns:
        Context manager for the span
    """
    return get_tracer().span(operation_name, **tags)


def get_current_trace() -> Optional[TraceContext]:
    """
    Get current trace using global tracer.

    Returns:
        Current TraceContext or None
    """
    return get_tracer().get_current_trace()


def finish_current_trace() -> None:
    """Finish current trace using global tracer."""
    trace = get_current_trace()
    if trace:
        get_tracer().finish_trace(trace.trace_id)


def get_trace_stats() -> TraceStats:
    """
    Get trace statistics from global tracer.

    Returns:
        Dictionary containing tracer statistics
    """
    return get_tracer().get_trace_stats()
