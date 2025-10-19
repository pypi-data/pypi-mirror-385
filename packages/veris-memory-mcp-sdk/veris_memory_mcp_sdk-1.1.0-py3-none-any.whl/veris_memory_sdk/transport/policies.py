"""Veris Memory MCP SDK transport policies for resilient communication."""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, Union

# Type aliases for transport operations
T = TypeVar("T")
AsyncFunc = Callable[..., Awaitable[T]]
SyncFunc = Callable[..., T]
StatusDict = Dict[str, Any]
PolicyMetrics = Dict[str, Union[str, int, float, bool]]

from ..core.errors import (
    MCPCircuitBreakerError,
    MCPConnectionError,
    MCPRetryExhaustedError,
    MCPTimeoutError,
)

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """
    Circuit breaker states for fault tolerance.

    The circuit breaker implements the Circuit Breaker pattern to prevent
    cascading failures when Veris Memory is experiencing issues.
    """

    CLOSED = "closed"  # Normal operation, requests allowed
    OPEN = "open"  # Failing state, requests blocked
    HALF_OPEN = "half_open"  # Testing recovery, limited requests allowed


@dataclass
class RetryPolicy:
    """
    Retry policy configuration for Veris Memory operations.

    Implements exponential backoff with jitter to handle transient failures
    gracefully while avoiding thundering herd problems.

    Example:
        ```python
        retry_policy = RetryPolicy(
            max_attempts=5,
            base_delay_ms=1000,
            max_delay_ms=30000,
            exponential_backoff=True,
            jitter=True
        )
        ```
    """

    max_attempts: int = 3
    """Maximum number of retry attempts"""

    base_delay_ms: int = 1000
    """Base delay between retries in milliseconds"""

    max_delay_ms: int = 10000
    """Maximum delay between retries in milliseconds"""

    exponential_backoff: bool = True
    """Whether to use exponential backoff"""

    jitter: bool = True
    """Whether to add random jitter to delays"""

    backoff_multiplier: float = 2.0
    """Multiplier for exponential backoff"""

    def calculate_delay(self, attempt: int, retry_after: Optional[int] = None) -> float:
        """Calculate delay for retry attempt.

        Args:
            attempt: Retry attempt number (1-based)
            retry_after: Server-specified retry delay in seconds (from Retry-After header)

        Returns:
            Delay in seconds
        """
        if attempt <= 0:
            return 0.0

        # Honor server-specified Retry-After header if present
        if retry_after is not None:
            # Apply jitter to server-specified delay to avoid thundering herd
            delay_ms: float = retry_after * 1000
            if self.jitter:
                jitter_range = delay_ms * 0.1  # 10% jitter
                delay_ms += random.uniform(-jitter_range, jitter_range)
            return max(0, delay_ms / 1000.0)

        if self.exponential_backoff:
            delay = self.base_delay_ms * (self.backoff_multiplier ** (attempt - 1))
        else:
            delay = self.base_delay_ms

        # Cap at max delay
        delay = min(delay, self.max_delay_ms)

        # Add jitter to avoid thundering herd
        if self.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay / 1000.0)  # Convert to seconds

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if an error should trigger a retry.

        Args:
            attempt: Current attempt number (1-based)
            error: The error that occurred

        Returns:
            True if the operation should be retried
        """
        if attempt >= self.max_attempts:
            return False

        # Retry on connection errors, timeouts, and server errors
        from ..core.errors import (
            MCPConnectionError,
            MCPRateLimitError,
            MCPServerError,
            MCPTimeoutError,
        )

        retryable_errors = (
            MCPConnectionError,
            MCPTimeoutError,
            MCPServerError,
            MCPRateLimitError,
        )

        return isinstance(error, retryable_errors)

    def extract_retry_after(self, error: Exception) -> Optional[int]:
        """Extract retry-after value from an error.

        Args:
            error: Exception that may contain retry-after information

        Returns:
            Retry-after seconds if available, None otherwise
        """
        if hasattr(error, "retry_after") and error.retry_after is not None:
            return int(error.retry_after) if isinstance(error.retry_after, (int, float)) else None

        if hasattr(error, "details") and isinstance(error.details, dict):
            return error.details.get("retry_after_seconds")

        return None


async def retry_with_policy(
    func: AsyncFunc[T], retry_policy: RetryPolicy, *args: Any, **kwargs: Any
) -> T:
    """
    Execute a function with retry policy.

    Args:
        func: Async function to execute
        retry_policy: Retry policy configuration
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result

    Raises:
        MCPRetryExhaustedError: If all retry attempts are exhausted
    """
    last_error: Optional[Exception] = None

    for attempt in range(1, retry_policy.max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as error:
            last_error = error

            # Don't retry if this error type shouldn't be retried
            if not retry_policy.should_retry(attempt, error):
                raise

            # Don't retry if this is the last attempt
            if attempt >= retry_policy.max_attempts:
                break

            # Calculate delay with potential Retry-After consideration
            retry_after = retry_policy.extract_retry_after(error)
            delay = retry_policy.calculate_delay(attempt, retry_after)

            logger.debug(
                f"Retry attempt {attempt}/{retry_policy.max_attempts} in {delay:.2f}s",
                extra={
                    "attempt": attempt,
                    "max_attempts": retry_policy.max_attempts,
                    "delay_seconds": delay,
                    "retry_after": retry_after,
                    "error_type": type(error).__name__,
                    "error": str(error)[:100],  # Truncate long errors
                },
            )

            if delay > 0:
                await asyncio.sleep(delay)

    # If we get here, all retries were exhausted
    from ..core.errors import MCPRetryExhaustedError

    raise MCPRetryExhaustedError(
        f"All {retry_policy.max_attempts} retry attempts exhausted",
        attempts=retry_policy.max_attempts,
        last_error=last_error or Exception("Unknown error"),
    )


@dataclass
class CircuitBreakerPolicy:
    """
    Circuit breaker policy configuration for Veris Memory operations.

    Implements the Circuit Breaker pattern to protect against cascading
    failures and provide fast failure when Veris Memory is unavailable.

    Example:
        ```python
        circuit_breaker_policy = CircuitBreakerPolicy(
            enabled=True,
            failure_threshold=5,
            recovery_timeout_ms=60000,
            half_open_max_calls=3
        )
        ```
    """

    enabled: bool = True
    """Whether circuit breaker is enabled"""

    failure_threshold: int = 5
    """Number of failures before opening the circuit"""

    recovery_timeout_ms: int = 60000
    """Time to wait before attempting recovery"""

    half_open_max_calls: int = 3
    """Maximum calls allowed in half-open state"""

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.failure_threshold <= 0:
            raise ValueError("failure_threshold must be > 0")
        if self.recovery_timeout_ms <= 0:
            raise ValueError("recovery_timeout_ms must be > 0")
        if self.half_open_max_calls <= 0:
            raise ValueError("half_open_max_calls must be > 0")


class CircuitBreaker:
    """
    Circuit breaker implementation for Veris Memory operations.

    Provides fault tolerance by monitoring failures and preventing
    requests when the service is likely to fail.
    """

    def __init__(self, policy: CircuitBreakerPolicy):
        """Initialize circuit breaker.

        Args:
            policy: Circuit breaker configuration
        """
        self.policy = policy
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.half_open_calls = 0
        self._lock = asyncio.Lock()

    async def call(self, func: AsyncFunc[T], *args: Any, **kwargs: Any) -> T:
        """Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            MCPCircuitBreakerError: If circuit breaker is open
        """
        if not self.policy.enabled:
            return await func(*args, **kwargs)

        async with self._lock:
            await self._check_state()

        if self.state == CircuitBreakerState.OPEN:
            raise MCPCircuitBreakerError(
                f"Circuit breaker is OPEN. Failure count: {self.failure_count}. "
                f"Veris Memory appears to be unavailable.",
                failure_count=self.failure_count,
                timeout_until=self.last_failure_time + (self.policy.recovery_timeout_ms / 1000.0),
            )

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure(e)
            raise

    async def _check_state(self) -> None:
        """Check and update circuit breaker state."""
        now = time.time()

        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if now - self.last_failure_time >= (self.policy.recovery_timeout_ms / 1000.0):
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(
                    "Circuit breaker moving to HALF_OPEN state - testing Veris Memory recovery"
                )

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_calls += 1
                if self.half_open_calls >= self.policy.half_open_max_calls:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info("Circuit breaker moving to CLOSED state - Veris Memory recovered")
            elif self.state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

    async def _on_failure(self, exception: Exception) -> None:
        """Handle failed call.

        Args:
            exception: The exception that occurred
        """
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitBreakerState.HALF_OPEN:
                # Any failure in half-open goes back to open
                self.state = CircuitBreakerState.OPEN
                logger.warning(
                    "Circuit breaker moving back to OPEN state - Veris Memory still failing"
                )
            elif (
                self.state == CircuitBreakerState.CLOSED
                and self.failure_count >= self.policy.failure_threshold
            ):
                self.state = CircuitBreakerState.OPEN
                logger.warning(
                    f"Circuit breaker moving to OPEN state after {self.failure_count} failures - "
                    f"Veris Memory appears to be down"
                )

    def get_status(self) -> StatusDict:
        """Get circuit breaker status.

        Returns:
            Status information including state and failure count
        """
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "half_open_calls": (
                self.half_open_calls if self.state == CircuitBreakerState.HALF_OPEN else None
            ),
            "enabled": self.policy.enabled,
        }


class TransportPolicy:
    """
    Transport policy combining retry and circuit breaker for Veris Memory operations.

    Provides resilient communication with Veris Memory by combining:
    - Retry logic with exponential backoff
    - Circuit breaker pattern for fault tolerance
    - Comprehensive error handling and logging

    Example:
        ```python
        transport = TransportPolicy(
            retry_policy=RetryPolicy(max_attempts=3),
            circuit_breaker_policy=CircuitBreakerPolicy(failure_threshold=5)
        )

        # Use with async function
        result = await transport.execute_with_policy(
            some_async_function,
            arg1, arg2,
            operation_name="store_context",
            trace_id="trace-123"
        )
        ```
    """

    def __init__(
        self,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker_policy: Optional[CircuitBreakerPolicy] = None,
    ) -> None:
        """Initialize transport policy.

        Args:
            retry_policy: Retry configuration (uses defaults if None)
            circuit_breaker_policy: Circuit breaker configuration (uses defaults if None)
        """
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit_breaker_policy = circuit_breaker_policy or CircuitBreakerPolicy()
        self.circuit_breaker = CircuitBreaker(self.circuit_breaker_policy)

    async def execute_with_policy(
        self,
        func: AsyncFunc[T],
        *args: Any,
        operation_name: str = "unknown",
        trace_id: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        """Execute function with retry and circuit breaker policies.

        Args:
            func: Async function to execute
            *args: Function arguments
            operation_name: Name of operation for logging
            trace_id: Optional trace ID for correlation
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            MCPRetryExhaustedError: If all retry attempts are exhausted
            MCPCircuitBreakerError: If circuit breaker is open
            Other exceptions: If non-retryable errors occur
        """
        start_time = time.time()

        async def _execute() -> T:
            return await self.circuit_breaker.call(func, *args, **kwargs)

        last_exception = None

        for attempt in range(self.retry_policy.max_attempts):
            try:
                logger.debug(
                    f"Executing Veris Memory operation {operation_name} "
                    f"(attempt {attempt + 1}/{self.retry_policy.max_attempts})",
                    extra={"trace_id": trace_id, "attempt": attempt + 1},
                )

                result = await _execute()

                duration_ms = (time.time() - start_time) * 1000
                logger.debug(
                    f"Veris Memory operation {operation_name} succeeded on attempt {attempt + 1}",
                    extra={
                        "trace_id": trace_id,
                        "attempt": attempt + 1,
                        "duration_ms": duration_ms,
                    },
                )

                return result

            except (MCPTimeoutError, MCPConnectionError, asyncio.TimeoutError) as e:
                last_exception = e

                if attempt < self.retry_policy.max_attempts - 1:
                    delay = self.retry_policy.calculate_delay(attempt + 1)
                    logger.warning(
                        f"Veris Memory operation {operation_name} failed on attempt {attempt + 1}, "
                        f"retrying in {delay:.2f}s: {str(e)}",
                        extra={
                            "trace_id": trace_id,
                            "attempt": attempt + 1,
                            "error": str(e),
                            "retry_delay_s": delay,
                        },
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Veris Memory operation {operation_name} failed after "
                        f"{attempt + 1} attempts: {str(e)}",
                        extra={"trace_id": trace_id, "attempts": attempt + 1, "error": str(e)},
                    )

            except MCPCircuitBreakerError:
                # Don't retry circuit breaker errors - fail fast
                logger.error(
                    f"Veris Memory operation {operation_name} blocked by circuit breaker",
                    extra={"trace_id": trace_id, "circuit_breaker_state": "OPEN"},
                )
                raise

            except Exception as e:
                # Non-retryable errors (validation, security, etc.)
                logger.error(
                    f"Veris Memory operation {operation_name} failed with "
                    f"non-retryable error: {str(e)}",
                    extra={
                        "trace_id": trace_id,
                        "attempt": attempt + 1,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
                raise

        # All attempts exhausted
        total_duration_ms = (time.time() - start_time) * 1000
        raise MCPRetryExhaustedError(
            f"Veris Memory operation {operation_name} failed after "
            f"{self.retry_policy.max_attempts} attempts. Last error: {last_exception}. "
            f"Total duration: {total_duration_ms:.1f}ms",
            attempts=self.retry_policy.max_attempts,
            last_error=last_exception or Exception("Unknown error"),
        )

    def get_status(self) -> StatusDict:
        """Get transport policy status.

        Returns:
            Status information for retry policy and circuit breaker
        """
        return {
            "retry_policy": {
                "max_attempts": self.retry_policy.max_attempts,
                "base_delay_ms": self.retry_policy.base_delay_ms,
                "max_delay_ms": self.retry_policy.max_delay_ms,
                "exponential_backoff": self.retry_policy.exponential_backoff,
                "jitter": self.retry_policy.jitter,
                "backoff_multiplier": self.retry_policy.backoff_multiplier,
            },
            "circuit_breaker": self.circuit_breaker.get_status(),
        }


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable.

    Args:
        error: Exception to check

    Returns:
        True if the error should be retried
    """
    retryable_types = (
        MCPTimeoutError,
        MCPConnectionError,
        asyncio.TimeoutError,
        ConnectionError,
        OSError,
    )

    return isinstance(error, retryable_types)


def is_circuit_breaker_error(error: Exception) -> bool:
    """Check if an error should trigger circuit breaker.

    Args:
        error: Exception to check

    Returns:
        True if the error should count towards circuit breaker failure threshold
    """
    # Circuit breaker triggers on connection and timeout errors
    trigger_types = (MCPTimeoutError, MCPConnectionError, asyncio.TimeoutError, ConnectionError)

    return isinstance(error, trigger_types)
