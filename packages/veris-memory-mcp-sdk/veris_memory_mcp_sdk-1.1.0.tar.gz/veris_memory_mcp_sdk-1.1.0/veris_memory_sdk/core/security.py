"""Security utilities for the Veris Memory MCP SDK."""

import re
from typing import Any, Dict, List, Set, Union


def redact_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Redact sensitive headers for safe logging.

    Args:
        headers: HTTP headers dictionary

    Returns:
        Dictionary with sensitive headers replaced with [REDACTED]
    """
    # Sensitive header names (case-insensitive)
    sensitive_headers: Set[str] = {
        "authorization",
        "api-key",
        "x-api-key",
        "x-auth-token",
        "cookie",
        "set-cookie",
        "proxy-authorization",
        "www-authenticate",
        "authentication",
        "x-access-token",
        "x-csrf-token",
        "x-xsrf-token",
    }

    redacted = {}
    for key, value in headers.items():
        if key.lower() in sensitive_headers:
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value

    return redacted


def redact_url_params(url: str) -> str:
    """
    Redact sensitive URL parameters for safe logging.

    Args:
        url: URL that may contain sensitive parameters

    Returns:
        URL with sensitive parameters redacted
    """
    # Sensitive parameter names (case-insensitive)
    sensitive_params = [
        "api_key",
        "apikey",
        "key",
        "token",
        "auth",
        "authorization",
        "password",
        "pwd",
        "pass",
        "secret",
        "private",
        "credential",
        "access_token",
        "refresh_token",
        "csrf_token",
        "xsrf_token",
    ]

    # Pattern to match query parameters
    pattern = r"([&?])(" + "|".join(sensitive_params) + r")=([^&]*)"

    def replace_param(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2)}=[REDACTED]"

    return re.sub(pattern, replace_param, url, flags=re.IGNORECASE)


def sanitize_log_data(data: Any) -> Any:
    """
    Recursively sanitize dictionary data for safe logging.

    Args:
        data: Data that may contain sensitive information

    Returns:
        Data with sensitive values redacted
    """
    if not isinstance(data, dict):
        return data

    # Sensitive key names (case-insensitive)
    sensitive_keys: Set[str] = {
        "password",
        "pwd",
        "pass",
        "secret",
        "private",
        "credential",
        "api_key",
        "apikey",
        "key",
        "token",
        "auth",
        "authorization",
        "access_token",
        "refresh_token",
        "csrf_token",
        "xsrf_token",
        "session_id",
        "sessionid",
        "jsessionid",
        "phpsessid",
        "client_secret",
        "private_key",
        "passphrase",
        "certificate",
    }

    sanitized: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_log_data(value)
        elif isinstance(value, list):
            # Sanitize lists that might contain dictionaries
            sanitized[key] = [
                sanitize_log_data(item) if isinstance(item, dict) else item for item in value
            ]
        elif key.lower() in sensitive_keys:
            # Redact sensitive values
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, str) and _looks_like_secret(value):
            # Redact values that look like secrets
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = value

    return sanitized


def _looks_like_secret(value: str) -> bool:
    """
    Check if a string value looks like a secret.

    Args:
        value: String to check

    Returns:
        True if the value looks like a secret
    """
    if not value or len(value) < 8:
        return False

    # Patterns that indicate secrets
    secret_patterns = [
        r"^sk-[a-zA-Z0-9]{32,}$",  # OpenAI-style API keys
        r"^[a-zA-Z0-9]{32,}$",  # Long alphanumeric strings
        r"^[a-fA-F0-9]{32,}$",  # Long hex strings
        r"-----BEGIN [A-Z ]+-----",  # PEM formatted keys/certificates
        r"^eyJ[a-zA-Z0-9+/=._-]+$",  # JWT tokens
        r"^Bearer [a-zA-Z0-9+/=]+$",  # Bearer tokens
    ]

    for pattern in secret_patterns:
        if re.match(pattern, value.strip()):
            return True

    return False


def create_safe_log_context(
    headers: Dict[str, str], url: str, data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a safe logging context with all sensitive data redacted.

    Args:
        headers: HTTP headers
        url: Request URL
        data: Request/response data

    Returns:
        Safe dictionary for logging
    """
    return {
        "headers": redact_headers(headers),
        "url": redact_url_params(url),
        "data": sanitize_log_data(data),
    }


def validate_no_secrets_in_logs(log_message: str) -> List[str]:
    """
    Validate that a log message doesn't contain secrets.

    Args:
        log_message: Log message to validate

    Returns:
        List of potential secret patterns found (for testing)
    """
    potential_secrets = []

    # Common secret patterns in logs
    patterns = [
        (r"authorization:\s+bearer\s+[a-zA-Z0-9+/=\-]{16,}", "Authorization Bearer token"),
        (r'api[_-]?key["\']?:\s*["\']?[a-zA-Z0-9]{20,}', "API key"),
        (r'password["\']?:\s*["\']?[^"\s]{8,}', "Password"),
        (r'secret["\']?:\s*["\']?[a-zA-Z0-9]{16,}', "Secret"),
        (r'token["\']?:\s*["\']?[a-zA-Z0-9+/=]{20,}', "Token"),
        (r"-----BEGIN [A-Z ]+-----", "Private key or certificate"),
    ]

    log_lower = log_message.lower()
    for pattern, description in patterns:
        if re.search(pattern, log_lower, re.IGNORECASE):
            potential_secrets.append(description)

    return potential_secrets
