# Changelog

All notable changes to the Veris Memory MCP SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-16

### Added
- Initial release of Veris Memory MCP SDK
- Core `MCPClient` class with comprehensive async operations
- Production-ready configuration via `MCPConfig`
- Advanced transport layer with retry policies and circuit breaker
- Distributed tracing and monitoring capabilities
- Comprehensive error hierarchy with specific error types
- User scoping and security enforcement
- Connection pooling and resource management
- Extensive documentation and examples
- Type hints throughout the codebase
- Support for Python 3.8+

### Features
- **Core Operations**:
  - `store_context()` - Store context data with metadata
  - `retrieve_context()` - Query and retrieve contexts
  - `update_scratchpad()` - Update user scratchpad
  - `get_agent_state()` - Retrieve agent state information

- **Transport Layer**:
  - Exponential backoff with jitter for retries
  - Circuit breaker pattern for fault tolerance
  - Configurable timeout and connection settings
  - Connection pooling for optimal performance

- **Monitoring**:
  - Distributed tracing for request correlation
  - Performance metrics and timing
  - Structured logging with trace IDs
  - Error tracking and debugging support

- **Security**:
  - User-scoped operations
  - Input validation and sanitization
  - PII-safe logging (hashed user IDs)
  - Secure default configurations

### Technical Details
- Async/await throughout for high performance
- Comprehensive error handling with specific exception types
- Type annotations for better IDE support
- Modular architecture for extensibility
- Production-ready defaults and configurations

### Documentation
- Complete API reference
- Usage examples (basic and advanced)
- Configuration guide
- Error handling patterns
- Performance optimization tips

### Development
- Full test suite with pytest
- Code quality tools (black, isort, flake8, mypy)
- Pre-commit hooks for consistent code quality
- GitHub Actions CI/CD workflows
- Comprehensive documentation

---

## Release Notes

### Version 1.0.0 Highlights

This initial release provides a production-ready SDK for the Veris Memory Model Context Protocol (MCP). The SDK is designed for high-performance production environments with comprehensive error handling, monitoring, and security features.

**Key Benefits:**
- **Production Ready**: Built for scale with connection pooling, retry logic, and fault tolerance
- **Developer Friendly**: Rich examples, comprehensive docs, and excellent IDE support
- **Secure by Default**: User scoping, input validation, and PII protection
- **Observable**: Distributed tracing, metrics, and structured logging
- **Resilient**: Circuit breaker pattern and smart retry policies

**Migration from Direct HTTP Calls:**
If you were previously making direct HTTP calls to Veris Memory, migrating to this SDK provides significant benefits in reliability, security, and observability. See the migration guide in the documentation.

**Next Steps:**
- Review the examples in the `examples/` directory
- Check out the advanced usage patterns for monitoring and transport policies
- Configure your production environment with appropriate timeout and retry settings
- Enable distributed tracing for better observability