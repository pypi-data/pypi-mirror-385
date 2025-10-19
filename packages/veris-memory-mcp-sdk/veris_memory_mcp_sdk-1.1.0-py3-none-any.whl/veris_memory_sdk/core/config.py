"""Veris Memory MCP SDK configuration."""

from dataclasses import dataclass, field

# Import after to avoid circular imports
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from .schemas import MCPClientInfo

if TYPE_CHECKING:
    from .validation import InputValidator

# Type aliases for configuration
HTTPHeaders = Dict[str, str]
ConnectionParams = Dict[str, Any]


@dataclass
class MCPConfig:
    """
    Veris Memory MCP SDK configuration.

    Provides comprehensive configuration options for the MCP client including
    connection settings, timeouts, retry policies, security options, and monitoring.

    Example:
        ```python
        from veris_memory_sdk import MCPConfig, MCPClientInfo

        config = MCPConfig(
            server_url="https://your-veris-instance.com",
            api_key="your-api-key",
            client_info=MCPClientInfo(
                name="my-application",
                version="1.0.0"
            ),
            # Timeout settings
            connect_timeout_ms=10000,
            request_timeout_ms=30000,
            # Retry settings
            max_retries=3,
            exponential_backoff=True,
            # Security
            enforce_user_scoping=True,
            # Monitoring
            enable_tracing=True
        )
        ```
    """

    # Connection settings
    server_url: str
    """Veris Memory server URL (e.g., https://your-veris-instance.com)"""

    api_key: Optional[str] = None
    """Optional API key for authentication"""

    use_websocket: bool = False
    """Whether to use WebSocket transport instead of HTTP"""

    # Client information
    client_info: MCPClientInfo = field(
        default_factory=lambda: MCPClientInfo(name="veris-memory-mcp-sdk", version="1.0.0")
    )
    """Client identification information"""

    # Timeout settings (milliseconds)
    connect_timeout_ms: int = 5000
    """Connection timeout in milliseconds"""

    request_timeout_ms: int = 30000
    """Individual request timeout in milliseconds"""

    total_timeout_ms: int = 60000
    """Total operation timeout in milliseconds"""

    # Retry settings
    max_retries: int = 3
    """Maximum number of retry attempts"""

    base_delay_ms: int = 1000
    """Base delay between retries in milliseconds"""

    max_delay_ms: int = 10000
    """Maximum delay between retries in milliseconds"""

    exponential_backoff: bool = True
    """Whether to use exponential backoff for retries"""

    jitter: bool = True
    """Whether to add random jitter to retry delays"""

    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    """Whether to enable circuit breaker pattern"""

    failure_threshold: int = 5
    """Number of failures before opening circuit"""

    recovery_timeout_ms: int = 60000
    """Time to wait before attempting recovery"""

    half_open_max_calls: int = 3
    """Maximum calls in half-open state"""

    # Security settings
    enforce_user_scoping: bool = True
    """Whether to enforce user scoping for all operations"""

    validate_requests: bool = True
    """Whether to validate requests before sending"""

    sanitize_logs: bool = True
    """Whether to sanitize sensitive data in logs"""

    # Monitoring settings
    enable_tracing: bool = True
    """Whether to enable distributed tracing"""

    enable_metrics: bool = True
    """Whether to enable metrics collection"""

    log_level: str = "INFO"
    """Logging level (DEBUG, INFO, WARNING, ERROR)"""

    # Additional headers
    extra_headers: HTTPHeaders = field(default_factory=dict)
    """Additional HTTP headers to include in requests"""

    # TLS/SSL settings
    verify_ssl: bool = True
    """Whether to verify SSL certificates"""

    client_cert: Optional[Tuple[str, str]] = None
    """Client certificate tuple: (cert_path, key_path)"""

    # Proxy settings
    proxies: Optional[Dict[str, str]] = None
    """HTTP proxy settings: {'http': 'proxy_url', 'https': 'proxy_url'}"""

    # HTTP/2 settings
    http2: bool = False
    """Whether to enable HTTP/2 support"""

    # Additional httpx settings
    extra_httpx_kwargs: Optional[Dict[str, Any]] = None
    """Additional keyword arguments to pass to httpx.AsyncClient"""

    def get_http_headers(self) -> HTTPHeaders:
        """Get HTTP headers for requests.

        Returns:
            Dictionary of HTTP headers including content type, user agent,
            authentication, and any extra headers
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"{self.client_info.name}/{self.client_info.version}",
            "X-MCP-SDK": "veris-memory-mcp-sdk",
            "X-MCP-SDK-Version": "1.0.0",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        headers.update(self.extra_headers)
        return headers

    def get_websocket_headers(self) -> HTTPHeaders:
        """Get WebSocket headers for connection.

        Returns:
            Dictionary of WebSocket headers including authentication
            and any extra headers
        """
        headers = {"X-MCP-SDK": "veris-memory-mcp-sdk", "X-MCP-SDK-Version": "1.0.0"}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        headers.update(self.extra_headers)
        return headers

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        # Import here to avoid circular imports
        from .validation import get_validator

        validator = get_validator()

        # Use comprehensive URL validation
        try:
            validator.validate_server_url(self.server_url)
        except Exception as e:
            raise ValueError(str(e))

        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")

        if self.connect_timeout_ms <= 0:
            raise ValueError("connect_timeout_ms must be > 0")

        if self.request_timeout_ms <= 0:
            raise ValueError("request_timeout_ms must be > 0")

        if self.total_timeout_ms <= 0:
            raise ValueError("total_timeout_ms must be > 0")

        if self.failure_threshold <= 0:
            raise ValueError("failure_threshold must be > 0")

        if self.base_delay_ms <= 0:
            raise ValueError("base_delay_ms must be > 0")

        if self.max_delay_ms < self.base_delay_ms:
            raise ValueError("max_delay_ms must be >= base_delay_ms")

        if self.recovery_timeout_ms <= 0:
            raise ValueError("recovery_timeout_ms must be > 0")

        if self.half_open_max_calls <= 0:
            raise ValueError("half_open_max_calls must be > 0")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            raise ValueError("log_level must be one of: DEBUG, INFO, WARNING, ERROR")


@dataclass
class MCPConnectionPool:
    """
    Configuration for HTTP connection pooling.

    Manages connection reuse and limits to optimize performance
    for high-throughput applications.
    """

    max_connections: int = 10
    """Maximum total connections in the pool"""

    max_keepalive_connections: int = 5
    """Maximum keepalive connections to maintain"""

    keepalive_expiry_ms: int = 30000
    """Keepalive connection expiry time in milliseconds"""

    pool_timeout_ms: int = 5000
    """Timeout for acquiring connection from pool"""

    def to_httpx_limits(self) -> Optional[Any]:
        """Convert to httpx limits object.

        Returns:
            httpx.Limits object if httpx is available, None otherwise
        """
        try:
            import httpx

            return httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive_connections,
                keepalive_expiry=self.keepalive_expiry_ms / 1000,
            )
        except ImportError:
            return None
