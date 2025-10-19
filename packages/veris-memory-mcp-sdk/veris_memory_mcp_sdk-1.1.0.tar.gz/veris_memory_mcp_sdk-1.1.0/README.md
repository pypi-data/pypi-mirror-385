# ◎ Veris Memory MCP SDK

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.1.0-green)](https://github.com/credentum/veris-memory-mcp-sdk/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](http://mypy-lang.org/)
[![Test Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)](https://github.com/credentum/veris-memory-mcp-sdk)
[![Code Quality](https://img.shields.io/badge/code%20quality-A+-brightgreen)](https://github.com/credentum/veris-memory-mcp-sdk)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A production-ready Python SDK for the ◎ Veris Memory Model Context Protocol (MCP), providing robust client capabilities for context storage, retrieval, and management.

## Features

- **🚀 Production Ready**: Built for high-performance production environments
- **🔄 Resilient Communication**: Advanced retry policies and circuit breaker pattern
- **📊 Comprehensive Monitoring**: Distributed tracing and performance metrics
- **🔒 Security First**: User scoping, input validation, and security enforcement
- **⚡ Async/Await**: Native asyncio support for optimal performance
- **🛠️ Developer Friendly**: Rich examples, comprehensive documentation, and type hints

## Quality Assurance

This SDK follows enterprise development practices including:
- Comprehensive test coverage (87%) with integration and performance tests
- Type checking with MyPy in strict mode
- Security scanning with Bandit
- Pre-commit hooks for code quality
- PII-safe logging and input validation

## Installation

```bash
# Basic installation
pip install veris-memory-mcp-sdk

# With development dependencies
pip install veris-memory-mcp-sdk[dev]

# With monitoring dependencies
pip install veris-memory-mcp-sdk[monitoring]

# Full installation
pip install veris-memory-mcp-sdk[all]
```

## Quick Start

```python
import asyncio
from veris_memory_sdk import MCPClient, MCPConfig

async def main():
    # Configure client
    config = MCPConfig(
        server_url="http://localhost:8000",
        user_id="your-user-id",
        timeout_ms=30000
    )
    
    # Create and connect client
    client = MCPClient(config)
    await client.connect()
    
    try:
        # Store context
        result = await client.store_context(
            context_type="decision",
            content={
                "title": "API Design Decision",
                "decision": "Use REST API with GraphQL layer",
                "reasoning": "Better developer experience and flexibility"
            },
            metadata={"project": "platform-v2", "priority": "high"}
        )
        
        print(f"Stored context: {result['context_id']}")
        
        # Retrieve contexts
        contexts = await client.retrieve_context(
            query="API design decision",
            limit=10
        )
        
        print(f"Found {len(contexts)} related contexts")
        
    finally:
        await client.disconnect()

# Run the example
asyncio.run(main())
```

## Advanced Usage

### Custom Transport Policies

```python
from veris_memory_sdk.transport import TransportPolicy, RetryPolicy, CircuitBreakerPolicy

# Configure retry policy
retry_policy = RetryPolicy(
    max_attempts=5,
    base_delay_ms=1000,
    max_delay_ms=30000,
    exponential_backoff=True,
    jitter=True
)

# Configure circuit breaker
circuit_breaker_policy = CircuitBreakerPolicy(
    enabled=True,
    failure_threshold=3,
    recovery_timeout_ms=60000
)

# Create transport policy
transport_policy = TransportPolicy(
    retry_policy=retry_policy,
    circuit_breaker_policy=circuit_breaker_policy
)

# Use with client
client = MCPClient(config, transport_policy=transport_policy)
```

### Distributed Tracing

```python
from veris_memory_sdk.monitoring import get_tracer, start_trace

# Start a trace
tracer = get_tracer()
trace = start_trace(
    operation="context_workflow",
    user_id="user-123",
    workflow_type="data_analysis"
)

# Use spans for detailed operation tracking
with tracer.span("store_analysis_context") as span:
    span.add_tag("analysis_type", "performance")
    span.add_tag("data_size_mb", 15.2)
    
    result = await client.store_context(
        context_type="analysis",
        content=analysis_data
    )
    
    span.add_log("info", f"Analysis stored with ID: {result['context_id']}")

# Get trace statistics
stats = tracer.get_trace_stats()
print(f"Active traces: {stats['active_traces']}")
```

## Configuration

The SDK supports comprehensive configuration options:

```python
config = MCPConfig(
    # Connection settings
    server_url="http://localhost:8000",
    user_id="user-123",
    
    # Timeout settings
    timeout_ms=30000,
    connection_timeout_ms=10000,
    
    # Retry settings
    retry_attempts=3,
    
    # Feature flags
    enable_tracing=True,
    enable_compression=True,
    
    # Security settings
    api_key="your-api-key",  # Optional
    
    # Advanced settings
    max_connections=10,
    keepalive_timeout_ms=30000
)
```

### Authentication

The SDK supports multiple authentication methods:

```python
# API Key authentication (recommended for production)
config = MCPConfig(
    server_url="https://api.verismemory.com",
    api_key="vm_your_api_key_here",
    user_id="your-user-id"
)

# Basic authentication
config = MCPConfig(
    server_url="https://api.verismemory.com",
    auth_username="your-username",
    auth_password="your-password",
    user_id="your-user-id"
)
```

### Context Types and Metadata

**Valid context types** (per veris-memory-mcp-server issue #2):

**Allowed values**: `"design"`, `"decision"`, `"trace"`, `"sprint"`, `"log"`

```python
# Decision context
await client.store_context(
    context_type="decision",
    content={"title": "...", "decision": "...", "reasoning": "..."},
    metadata={"project": "project-name", "priority": "high|medium|low"}
)

# Design context  
await client.store_context(
    context_type="design",
    content={"title": "...", "design": "...", "rationale": "..."}, 
    metadata={"component": "ui|api|database", "tags": ["tag1", "tag2"]}
)

# Sprint context
await client.store_context(
    context_type="sprint",
    content={"sprint_name": "...", "goals": [...], "outcomes": [...]},
    metadata={"team": "...", "sprint_number": 1}
)

# Trace context
await client.store_context(
    context_type="trace",
    content={"operation": "...", "duration_ms": 123, "details": {...}},
    metadata={"service": "...", "trace_id": "..."}
)

# Log context
await client.store_context(
    context_type="log",
    content={"message": "...", "level": "info|warn|error", "data": {...}},
    metadata={"source": "...", "timestamp": "..."}
)
```

**Note**: Content structure is flexible. Each context type can have different fields based on your needs.

Searchable metadata fields: `project`, `priority`, `component`, `tags`, `team`, `service`, `created_date`, `user_id`.

## Error Handling

The SDK provides a comprehensive error hierarchy:

```python
from veris_memory_sdk.core.errors import (
    MCPError,
    MCPConnectionError,
    MCPTimeoutError,
    MCPValidationError,
    MCPSecurityError,
    MCPRetryExhaustedError,
    MCPCircuitBreakerError
)

try:
    result = await client.store_context(context_type="test", content={})
except MCPValidationError as e:
    print(f"Validation failed: {e}")
except MCPConnectionError as e:
    print(f"Connection failed: {e}")
except MCPTimeoutError as e:
    print(f"Operation timed out: {e}")
except MCPError as e:
    print(f"General MCP error: {e}")
```

## Batch Operations

The SDK supports efficient batch operations for high-throughput scenarios:

```python
# Define multiple tool calls
tool_calls = [
    {
        "name": "store_context",
        "arguments": {
            "type": "user_note",
            "content": {"text": f"Note {i}", "timestamp": "2025-01-01T00:00:00Z"},
            "metadata": {"batch": "demo", "index": i}
        },
        "user_id": "demo_user",
        "trace_id": f"batch-note-{i}"
    }
    for i in range(50)
]

# Execute with controlled concurrency
results = await client.call_tools(
    tool_calls=tool_calls,
    max_concurrency=10,  # Limit concurrent requests
    timeout_ms=60000     # Extended timeout for batch
)

print(f"Processed {len(results)} operations")
for result in results:
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Success: {result.content.get('id')}")
```

### Batch Best Practices

- **Concurrency control**: Use `max_concurrency` to prevent overwhelming the server
- **Error handling**: Each operation in a batch can succeed or fail independently
- **Timeout management**: Set appropriate timeouts for large batches
- **Progress tracking**: Monitor results as they complete

## TLS and Proxy Configuration

The SDK supports advanced HTTP configurations for enterprise environments:

```python
# TLS/SSL Configuration
config = MCPConfig(
    server_url="https://api.verismemory.com",
    verify_ssl=True,                    # Enable SSL verification
    client_cert=("/path/to/cert.pem", "/path/to/key.pem"),  # Client certificate
    proxies={
        "http": "http://proxy.company.com:8080",
        "https": "https://proxy.company.com:8080"
    }
)

# HTTP/2 Support
config = MCPConfig(
    server_url="https://api.verismemory.com",
    http2=True,  # Enable HTTP/2
    extra_httpx_kwargs={
        "limits": {"max_connections": 100},
        "headers": {"User-Agent": "MyApp/1.0"}
    }
)
```

### Enterprise Features

- **Client certificates**: Mutual TLS authentication
- **Proxy support**: HTTP/HTTPS proxy configuration
- **HTTP/2**: Better multiplexing for high-throughput applications
- **Custom headers**: Additional headers for authentication or tracking

## Security Features

The SDK implements comprehensive security measures:

### Header Redaction

Sensitive headers are automatically redacted in logs:

```python
from veris_memory_sdk.core.security import redact_headers, sanitize_log_data

# Headers are automatically sanitized in logs
headers = {
    "Authorization": "Bearer secret-token",
    "X-API-Key": "api-key-123",
    "Content-Type": "application/json"
}

safe_headers = redact_headers(headers)
# Result: {"Authorization": "[REDACTED]", "X-API-Key": "[REDACTED]", "Content-Type": "application/json"}
```

### Data Sanitization

Sensitive data in request/response payloads is protected:

```python
# Automatic PII protection in logs
data = {
    "user_info": {"password": "secret123", "email": "user@example.com"},
    "api_key": "sk-1234567890abcdef",
    "content": "This is safe content"
}

safe_data = sanitize_log_data(data)
# Passwords, API keys, and other secrets are redacted
```

### Transport Security

- **TLS 1.2+**: Modern encryption protocols
- **Certificate validation**: Strict SSL verification by default
- **Secure headers**: Automatic security header handling
- **URL sanitization**: Sensitive query parameters are redacted in logs

## API Reference

### Core Classes

- **`MCPClient`**: Main client for Veris Memory operations
  - `call_tools()`: Batch operations with concurrency control
  - `store_context()`: Store individual context items
  - `retrieve_context()`: Search and retrieve contexts
  - `connect()`/`disconnect()`: Connection management

- **`MCPConfig`**: Configuration container for client settings
  - `verify_ssl`: SSL certificate verification
  - `client_cert`: Client certificate for mTLS
  - `proxies`: HTTP/HTTPS proxy configuration
  - `http2`: HTTP/2 protocol support
  - `extra_httpx_kwargs`: Advanced HTTPX configuration

- **`MCPError`**: Base exception class for all SDK errors
  - `MCPAuthenticationError`: Authentication failures (HTTP 401)
  - `MCPAuthorizationError`: Authorization failures (HTTP 403)
  - `MCPRateLimitError`: Rate limiting (HTTP 429)
  - `MCPValidationError`: Input validation failures (HTTP 400)
  - `MCPServerError`: Server errors (HTTP 5xx)

### Transport Layer

- **`TransportPolicy`**: Combines retry and circuit breaker policies
- **`RetryPolicy`**: Configures retry behavior with exponential backoff and jitter
  - `respect_retry_after`: Honor server Retry-After headers
  - `jitter`: Add randomness to prevent thundering herd
- **`CircuitBreakerPolicy`**: Configures circuit breaker for fault tolerance

### Security Module

- **`redact_headers()`**: Sanitize HTTP headers for safe logging
- **`sanitize_log_data()`**: Recursively redact sensitive data
- **`create_safe_log_context()`**: Create logging-safe request context
- **`validate_no_secrets_in_logs()`**: Detect potential secret leaks

### Monitoring

- **`Tracer`**: Distributed tracing for request correlation
- **`TraceContext`**: Container for trace spans and metadata
- **`TraceSpan`**: Individual operation tracking within a trace

## Integration Examples

The SDK includes production-ready integration templates:

### Telegram Bot Integration

```bash
# Install dependencies
pip install veris-memory-mcp-sdk python-telegram-bot

# Configure environment
export TELEGRAM_BOT_TOKEN="your-bot-token"
export VERIS_MEMORY_SERVER_URL="https://your-veris-instance.com"

# Run the bot
python examples/telegram_bot.py
```

**Features:**
- Automatic conversation storage in Veris Memory
- `/remember` command for explicit memory storage
- `/recall` command for semantic search
- User-scoped data with privacy protection

### Document Ingestion Pipeline

```bash
# Install dependencies  
pip install veris-memory-mcp-sdk aiohttp beautifulsoup4 pypdf

# Configure environment
export VERIS_MEMORY_SERVER_URL="https://your-veris-instance.com"
export VERIS_MEMORY_API_KEY="your-api-key"

# Run the ingester
python examples/document_ingester.py
```

**Features:**
- Web page scraping with content extraction
- Text file processing with chunking
- Batch ingestion with concurrency control
- Metadata extraction and tagging
- Progress tracking and error handling

### Real-world Usage

```python
# Production-ready service integration
from veris_memory_sdk import MCPClient, MCPConfig
from examples.telegram_bot import VerisMemoryBot
from examples.document_ingester import IngestionPipeline

# Multi-service architecture
class ProductionService:
    def __init__(self):
        self.config = MCPConfig(
            server_url=os.getenv("VERIS_MEMORY_SERVER_URL"),
            api_key=os.getenv("VERIS_MEMORY_API_KEY"),
            verify_ssl=True,
            http2=True,
            max_concurrency=20
        )
        
        self.memory_client = MCPClient(self.config)
        self.telegram_bot = VerisMemoryBot(
            telegram_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            veris_config=self.config
        )
        self.document_pipeline = IngestionPipeline(self.config)
    
    async def start_all_services(self):
        # Start all services concurrently
        await asyncio.gather(
            self.memory_client.connect(),
            self.telegram_bot.start_bot(),
            self.document_pipeline.start()
        )
```

## Examples

The SDK includes comprehensive examples:

- **`examples/basic_usage.py`**: Basic operations and error handling
- **`examples/advanced_usage.py`**: Advanced features, monitoring, and policies
- **`examples/telegram_bot.py`**: Production Telegram bot with memory integration
- **`examples/document_ingester.py`**: Document processing and ingestion pipeline

Run examples:

```bash
# Basic usage
python examples/basic_usage.py

# Advanced usage with monitoring
python examples/advanced_usage.py

# Telegram bot (requires token)
python examples/telegram_bot.py

# Document ingester
python examples/document_ingester.py
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/credentum/veris-memory-mcp-sdk.git
cd veris-memory-mcp-sdk

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=veris_memory_sdk --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Run comprehensive quality checks
./scripts/quality-gate.sh

# Individual tools
black veris_memory_sdk tests examples          # Format code
isort veris_memory_sdk tests examples          # Sort imports  
flake8 veris_memory_sdk tests examples         # Lint code
mypy veris_memory_sdk --config-file mypy.ini   # Type checking
bandit -r veris_memory_sdk                     # Security analysis

# Pre-commit hooks (runs automatically on commit)
pre-commit run --all-files
```

## Performance

The SDK is optimized for high-performance production use:

- **Async/await**: Native asyncio for concurrent operations
- **Connection pooling**: Efficient connection reuse
- **Compression**: Optional response compression
- **Circuit breaker**: Fast failure for unavailable services
- **Retry policies**: Smart backoff strategies

### Performance Tuning

Configure the SDK for different use cases:

```python
# High throughput configuration
config = MCPConfig(
    server_url="https://api.verismemory.com",
    max_connections=50,
    timeout_ms=5000,
    enable_compression=True,
    use_websocket=True,  # Lower latency for real-time applications
)

# Reliability over speed configuration
config = MCPConfig(
    server_url="https://api.verismemory.com",
    retry_attempts=5,
    timeout_ms=60000,
    enable_tracing=True,
    max_connections=10,
)

# Batch operations for efficiency
contexts = []
for i in range(100):
    contexts.append({
        "context_type": "batch_item",
        "content": {"data": f"item_{i}"},
        "metadata": {"batch_id": "batch_001"}
    })

# Store multiple contexts efficiently
results = await asyncio.gather(*[
    client.store_context(**context) for context in contexts
])
```

### Rate Limiting

The SDK automatically handles server rate limits:

- **Exponential backoff**: Automatic retry with increasing delays
- **Circuit breaker**: Prevents cascading failures during outages
- **Rate limit headers**: Respects `X-RateLimit-*` headers from server
- **Queue management**: Internal request queuing during high load

```python
# Configure rate limiting behavior
config = MCPConfig(
    retry_attempts=3,
    base_retry_delay_ms=1000,  # Start with 1 second delay
    max_retry_delay_ms=30000,  # Cap at 30 seconds
    enable_jitter=True,        # Add randomness to prevent thundering herd
)
```

### Benchmarks

Typical performance characteristics:

- **Connection establishment**: ~10ms
- **Context storage**: ~50ms (95th percentile)
- **Context retrieval**: ~100ms (95th percentile)
- **Concurrent operations**: 1000+ ops/second

## Security

The SDK implements security best practices:

- **User scoping**: All operations scoped to authenticated users
- **Input validation**: Comprehensive validation of all inputs
- **PII protection**: Automatic hashing of sensitive data in logs
- **Secure defaults**: Conservative timeout and retry settings

## Connection State Management

For long-running applications, the SDK provides robust connection management:

```python
import asyncio
from veris_memory_sdk import MCPClient, MCPConfig

class LongRunningService:
    def __init__(self):
        self.client = MCPClient(MCPConfig(
            server_url="https://api.verismemory.com",
            api_key="your-api-key",
            user_id="service-user",
            # Connection health settings
            keepalive_timeout_ms=30000,
            max_connections=10,
            enable_connection_pooling=True
        ))
        self._running = False
    
    async def start(self):
        """Start the service with automatic reconnection."""
        self._running = True
        await self.client.connect()
        
        # Start background health check
        asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self):
        """Background task to monitor connection health."""
        while self._running:
            try:
                if not self.client.connected:
                    print("Connection lost, attempting to reconnect...")
                    await self.client.connect()
                    print("Reconnection successful")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Health check failed: {e}")
                await asyncio.sleep(60)  # Wait longer on failure
    
    async def store_with_retry(self, context_type, content, metadata=None):
        """Store context with automatic reconnection on failure."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                return await self.client.store_context(
                    context_type=context_type,
                    content=content,
                    metadata=metadata
                )
            except ConnectionError:
                if attempt == max_attempts - 1:
                    raise
                print(f"Connection failed, retrying... (attempt {attempt + 1})")
                await self.client.connect()
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def stop(self):
        """Gracefully stop the service."""
        self._running = False
        await self.client.disconnect()

# Usage
service = LongRunningService()
await service.start()

# Use the service
result = await service.store_with_retry(
    context_type="event",
    content={"message": "Service started"},
    metadata={"service": "long-running-example"}
)

await service.stop()
```

## Troubleshooting

### Common Issues

**Connection refused errors**
```
MCPConnectionError: Failed to connect via HTTP: Connection refused
```
- Verify server URL and port are correct
- Check firewall settings and network connectivity
- Ensure the Veris Memory server is running
- Test with `curl` or browser: `curl http://your-server:8000/health`

**Timeout errors**
```
MCPTimeoutError: HTTP timeout for tool store_context
```
- Increase `timeout_ms` in config (default: 30000ms)
- Check network latency: `ping your-server`
- Consider using retry policies for unreliable networks
- For large payloads, increase `request_timeout_ms`

**Authentication failures**
```
MCPSecurityError: Authentication failed for tool store_context
```
- Verify API key is correct and not expired
- Check user_id is provided when `enforce_user_scoping=True`
- Ensure server accepts your authentication method
- Test authentication with a simple health check

**Rate limiting**
```
MCPError: HTTP error 429 for tool store_context: Too Many Requests
```
- The SDK handles this automatically with exponential backoff
- Reduce request frequency in your application
- Consider implementing client-side queuing
- Monitor rate limit headers for optimization

**JSON parsing errors**
```
MCPError: Invalid JSON response for tool store_context
```
- Check server logs for errors or malformed responses
- Verify content-type headers are correct
- Test with smaller payloads to isolate the issue
- Enable debug logging to see raw responses

**Memory issues with large payloads**
```
MemoryError: Unable to allocate memory
```
- Split large contexts into smaller chunks
- Use streaming operations where available
- Implement pagination for large result sets
- Monitor memory usage in your application

### Debug Mode

Enable comprehensive logging for troubleshooting:

```python
import logging
from veris_memory_sdk import MCPClient, MCPConfig

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

config = MCPConfig(
    server_url="http://localhost:8000",
    user_id="debug-user",
    enable_tracing=True,  # Additional request tracing
    validate_requests=True,  # Extra validation
)

client = MCPClient(config)

# All operations will now produce detailed logs
await client.connect()
result = await client.store_context(
    context_type="debug",
    content={"test": "data"}
)
```

## Version Compatibility

The SDK is designed to work with specific versions of the Veris Memory server:

| SDK Version | Server Version | Python Version | Status |
|-------------|----------------|----------------|---------|
| 1.0.x       | 1.0.x - 1.2.x | 3.10+         | ✅ Supported |
| 0.9.x       | 0.9.x - 1.1.x | 3.9+          | ⚠️ Legacy |
| 0.8.x       | 0.8.x - 0.9.x | 3.8+          | ❌ Deprecated |

### Migration Guide

**Upgrading from 0.9.x to 1.0.x:**

1. **Updated imports:**
   ```python
   # Old (0.9.x)
   from veris_memory_sdk.client import MCPClient
   from veris_memory_sdk.config import MCPConfig
   
   # New (1.0.x)
   from veris_memory_sdk import MCPClient, MCPConfig
   ```

2. **Configuration changes:**
   ```python
   # Old (0.9.x)
   config = MCPConfig(
       base_url="http://localhost:8000",  # Changed
       timeout=30000,                     # Changed
   )
   
   # New (1.0.x)
   config = MCPConfig(
       server_url="http://localhost:8000",  # Renamed
       timeout_ms=30000,                    # Renamed with units
   )
   ```

3. **Error handling:**
   ```python
   # Old (0.9.x)
   from veris_memory_sdk.exceptions import MCPException
   
   # New (1.0.x)
   from veris_memory_sdk.core.errors import MCPError, MCPConnectionError
   ```

4. **Async context manager (new in 1.0.x):**
   ```python
   # Recommended approach in 1.0.x
   async with MCPClient(config) as client:
       result = await client.store_context(...)
   ```

**Breaking changes in 1.0.x:**
- User scoping is now enforced by default (`enforce_user_scoping=True`)
- Transport layer completely rewritten (affects custom transport implementations)
- Monitoring and tracing moved to separate modules
- Some method signatures changed for consistency

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://credentum.ai/docs/sdk](https://credentum.ai/docs/sdk)
- **Issues**: [GitHub Issues](https://github.com/credentum/veris-memory-mcp-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/credentum/veris-memory-mcp-sdk/discussions)
- **Email**: credento@credentum.ai

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and migration guides.

---

Built with ❤️ by the ◎ Veris Memory Team