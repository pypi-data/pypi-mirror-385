"""
API Tools for HTTP Requests

Provides tools for making HTTP requests (GET, POST, PUT, DELETE) with safety controls.

Example:
    >>> from kaizen.tools import ToolRegistry, ToolExecutor
    >>> from kaizen.tools.builtin.api import register_api_tools
    >>>
    >>> registry = ToolRegistry()
    >>> register_api_tools(registry)
    >>>
    >>> executor = ToolExecutor(registry=registry)
    >>> result = await executor.execute("http_get", {"url": "https://api.example.com/data"})
    >>> print(result.result["status_code"])
"""

import ipaddress
import json
from typing import Any, Dict, Optional, Tuple, TypedDict
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse

from kaizen.tools import DangerLevel, ToolCategory, ToolParameter
from kaizen.tools.registry import ToolRegistry


class HTTPResult(TypedDict, total=False):
    """
    Type definition for HTTP tool results.

    Attributes:
        status_code: HTTP status code (0 if request failed)
        body: Response body as string
        headers: Response headers as dict
        success: True if status code is 2xx
        error: Error message if request failed (optional)
        warning: Warning message if response was truncated (optional)
    """
    status_code: int
    body: str
    headers: Dict[str, str]
    success: bool
    error: str  # Optional
    warning: str  # Optional

# Security constants
MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TIMEOUT = 300  # 5 minutes
MIN_TIMEOUT = 1  # 1 second
ALLOWED_SCHEMES = {"http", "https"}


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL for security (SSRF protection).

    Validates that:
    1. URL uses http or https scheme only
    2. URL does not target localhost or private IP addresses

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if URL is safe, False otherwise
        - error_message: None if valid, error description otherwise

    Example:
        >>> is_valid, error = validate_url("https://example.com")
        >>> assert is_valid is True
        >>> is_valid, error = validate_url("ftp://example.com")
        >>> assert is_valid is False
    """
    if not url:
        return False, "URL cannot be empty"

    try:
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False, f"URL scheme must be http or https, got: {parsed.scheme}"

        # Check hostname exists
        if not parsed.hostname:
            return False, "URL must have a valid hostname"

        hostname = parsed.hostname.lower()

        # Check for localhost
        if hostname in ("localhost", "127.0.0.1", "::1"):
            return False, "Access to localhost is not allowed (SSRF protection)"

        # Check for private IP addresses
        try:
            ip = ipaddress.ip_address(hostname)

            # Check if private, loopback, link-local, or multicast
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
                return False, f"Access to private/internal IP addresses is not allowed (SSRF protection): {hostname}"

        except ValueError:
            # Not an IP address, it's a domain name - that's fine
            # We only block private IPs, not domain names that might resolve to private IPs
            # (DNS resolution happens later and is harder to exploit)
            pass

        return True, None

    except Exception as e:
        return False, f"Invalid URL: {str(e)}"


def validate_timeout(timeout: int) -> Tuple[bool, Optional[str]]:
    """
    Validate timeout is within safe range.

    Validates that timeout is between 1 and 300 seconds to prevent:
    1. Zero/negative timeouts (invalid)
    2. Extremely long timeouts (DoS risk)

    Args:
        timeout: Timeout value in seconds

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_timeout(30)
        >>> assert is_valid is True
        >>> is_valid, error = validate_timeout(500)
        >>> assert is_valid is False
    """
    if timeout < MIN_TIMEOUT:
        return False, f"Timeout must be at least {MIN_TIMEOUT} second(s)"

    if timeout > MAX_TIMEOUT:
        return False, f"Timeout must not exceed {MAX_TIMEOUT} seconds"

    return True, None


def read_response_with_limit(response, max_size: int = MAX_RESPONSE_SIZE) -> Tuple[str, bool]:
    """
    Read HTTP response with size limit to prevent DoS.

    Reads response body up to max_size bytes. If response exceeds limit,
    reading is truncated to prevent memory exhaustion attacks.

    Args:
        response: HTTP response object from urllib
        max_size: Maximum bytes to read (default 10MB)

    Returns:
        Tuple of (body, was_truncated)
        - body: Response body (possibly truncated)
        - was_truncated: True if response exceeded max_size

    Example:
        >>> # Simulated response
        >>> body, truncated = read_response_with_limit(response, max_size=1024)
        >>> if truncated:
        ...     print("Response was too large and was truncated")
    """
    chunks = []
    total_size = 0
    was_truncated = False

    # Read in 8KB chunks
    chunk_size = 8192

    while True:
        chunk = response.read(chunk_size)
        if not chunk:
            break

        total_size += len(chunk)

        if total_size > max_size:
            # Truncate to max_size
            excess = total_size - max_size
            chunk = chunk[:-excess]
            chunks.append(chunk)
            was_truncated = True
            break

        chunks.append(chunk)

    body = b"".join(chunks).decode("utf-8", errors="replace")
    return body, was_truncated


def _make_http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    data: Optional[Any] = None,
) -> HTTPResult:
    """
    Internal helper for making HTTP requests with shared validation and error handling.

    This function consolidates common logic across all HTTP methods (GET, POST, PUT, DELETE):
    - URL and timeout security validation
    - Request preparation with optional data encoding
    - Response reading with size limits
    - Consistent error handling

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: URL to request
        headers: HTTP headers (optional)
        timeout: Request timeout in seconds (default 30)
        data: Request body data for POST/PUT (optional)

    Returns:
        Dictionary with:
            - status_code (int): HTTP status code
            - body (str): Response body
            - headers (dict): Response headers
            - success (bool): True if status code is 2xx
            - error (str, optional): Error message if request failed
            - warning (str, optional): Warning if response was truncated

    Note:
        This is an internal helper function. Use the public http_get_tool,
        http_post_tool, http_put_tool, or http_delete_tool instead.
    """
    headers = headers or {}

    # Security validation: URL
    is_valid, error = validate_url(url)
    if not is_valid:
        return {
            "status_code": 0,
            "body": "",
            "headers": {},
            "success": False,
            "error": f"URL validation failed: {error}",
        }

    # Security validation: timeout
    is_valid, error = validate_timeout(timeout)
    if not is_valid:
        return {
            "status_code": 0,
            "body": "",
            "headers": {},
            "success": False,
            "error": f"Timeout validation failed: {error}",
        }

    try:
        # Prepare request data (for POST/PUT)
        data_bytes = None
        if data is not None:
            if isinstance(data, dict):
                # Default to JSON if dict
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/json"
                data_bytes = json.dumps(data).encode("utf-8")
            else:
                data_bytes = data.encode("utf-8") if isinstance(data, str) else data

        # Create and execute request
        req = urllib_request.Request(url, data=data_bytes, headers=headers, method=method)
        with urllib_request.urlopen(req, timeout=timeout) as response:
            # Security: Read response with size limit
            body, was_truncated = read_response_with_limit(response)
            status_code = response.status
            response_headers = dict(response.headers)

            result = {
                "status_code": status_code,
                "body": body,
                "headers": response_headers,
                "success": 200 <= status_code < 300,
            }

            # Warn if response was truncated
            if was_truncated:
                result["warning"] = f"Response exceeded {MAX_RESPONSE_SIZE} bytes and was truncated"

            return result

    except HTTPError as e:
        return {
            "status_code": e.code,
            "body": e.read().decode("utf-8") if e.fp else "",
            "headers": dict(e.headers) if e.headers else {},
            "success": False,
            "error": str(e),
        }

    except URLError as e:
        return {
            "status_code": 0,
            "body": "",
            "headers": {},
            "success": False,
            "error": str(e.reason),
        }

    except Exception as e:
        return {
            "status_code": 0,
            "body": "",
            "headers": {},
            "success": False,
            "error": str(e),
        }


def http_get_tool(params: Dict[str, Any]) -> HTTPResult:
    """
    Make an HTTP GET request.

    Args:
        params: Dictionary with:
            - url (str): URL to request
            - headers (dict, optional): HTTP headers
            - timeout (int, optional): Request timeout in seconds (default 30)

    Returns:
        Dictionary with:
            - status_code (int): HTTP status code
            - body (str): Response body
            - headers (dict): Response headers
            - success (bool): True if status code is 2xx
    """
    return _make_http_request(
        method="GET",
        url=params["url"],
        headers=params.get("headers"),
        timeout=params.get("timeout", 30),
    )


def http_post_tool(params: Dict[str, Any]) -> HTTPResult:
    """
    Make an HTTP POST request.

    Args:
        params: Dictionary with:
            - url (str): URL to request
            - data (dict or str): POST data
            - headers (dict, optional): HTTP headers
            - timeout (int, optional): Request timeout in seconds (default 30)

    Returns:
        Dictionary with:
            - status_code (int): HTTP status code
            - body (str): Response body
            - headers (dict): Response headers
            - success (bool): True if status code is 2xx
    """
    return _make_http_request(
        method="POST",
        url=params["url"],
        headers=params.get("headers"),
        timeout=params.get("timeout", 30),
        data=params.get("data", {}),
    )


def http_put_tool(params: Dict[str, Any]) -> HTTPResult:
    """
    Make an HTTP PUT request.

    Args:
        params: Dictionary with:
            - url (str): URL to request
            - data (dict or str): PUT data
            - headers (dict, optional): HTTP headers
            - timeout (int, optional): Request timeout in seconds (default 30)

    Returns:
        Dictionary with:
            - status_code (int): HTTP status code
            - body (str): Response body
            - headers (dict): Response headers
            - success (bool): True if status code is 2xx
    """
    return _make_http_request(
        method="PUT",
        url=params["url"],
        headers=params.get("headers"),
        timeout=params.get("timeout", 30),
        data=params.get("data", {}),
    )


def http_delete_tool(params: Dict[str, Any]) -> HTTPResult:
    """
    Make an HTTP DELETE request.

    Args:
        params: Dictionary with:
            - url (str): URL to request
            - headers (dict, optional): HTTP headers
            - timeout (int, optional): Request timeout in seconds (default 30)

    Returns:
        Dictionary with:
            - status_code (int): HTTP status code
            - body (str): Response body
            - headers (dict): Response headers
            - success (bool): True if status code is 2xx
    """
    return _make_http_request(
        method="DELETE",
        url=params["url"],
        headers=params.get("headers"),
        timeout=params.get("timeout", 30),
    )


def register_api_tools(registry: ToolRegistry) -> None:
    """
    Register API tools to a registry.

    Args:
        registry: ToolRegistry instance to register tools to

    Registers:
        - http_get: Make HTTP GET requests (LOW danger)
        - http_post: Make HTTP POST requests (MEDIUM danger)
        - http_put: Make HTTP PUT requests (MEDIUM danger)
        - http_delete: Make HTTP DELETE requests (HIGH danger)

    Example:
        >>> registry = ToolRegistry()
        >>> register_api_tools(registry)
        >>> tool = registry.get("http_get")
        >>> print(tool.name)
    """
    # HTTP GET tool
    registry.register(
        name="http_get",
        description="Make an HTTP GET request",
        category=ToolCategory.NETWORK,
        danger_level=DangerLevel.LOW,
        parameters=[
            ToolParameter(name="url", type=str, description="URL to request", required=True),
            ToolParameter(
                name="headers",
                type=dict,
                description="HTTP headers",
                required=False,
            ),
            ToolParameter(
                name="timeout",
                type=int,
                description="Request timeout in seconds (default 30)",
                required=False,
            ),
        ],
        returns={
            "status_code": "int",
            "body": "str",
            "headers": "dict",
            "success": "bool",
        },
        executor=http_get_tool,
    )

    # HTTP POST tool
    registry.register(
        name="http_post",
        description="Make an HTTP POST request",
        category=ToolCategory.NETWORK,
        danger_level=DangerLevel.MEDIUM,
        parameters=[
            ToolParameter(name="url", type=str, description="URL to request", required=True),
            ToolParameter(
                name="data",
                type=(dict, str),
                description="POST data (dict or string)",
                required=False,
            ),
            ToolParameter(
                name="headers",
                type=dict,
                description="HTTP headers",
                required=False,
            ),
            ToolParameter(
                name="timeout",
                type=int,
                description="Request timeout in seconds (default 30)",
                required=False,
            ),
        ],
        returns={
            "status_code": "int",
            "body": "str",
            "headers": "dict",
            "success": "bool",
        },
        executor=http_post_tool,
        approval_message_template="POST to URL: {url}",
    )

    # HTTP PUT tool
    registry.register(
        name="http_put",
        description="Make an HTTP PUT request",
        category=ToolCategory.NETWORK,
        danger_level=DangerLevel.MEDIUM,
        parameters=[
            ToolParameter(name="url", type=str, description="URL to request", required=True),
            ToolParameter(
                name="data",
                type=(dict, str),
                description="PUT data (dict or string)",
                required=False,
            ),
            ToolParameter(
                name="headers",
                type=dict,
                description="HTTP headers",
                required=False,
            ),
            ToolParameter(
                name="timeout",
                type=int,
                description="Request timeout in seconds (default 30)",
                required=False,
            ),
        ],
        returns={
            "status_code": "int",
            "body": "str",
            "headers": "dict",
            "success": "bool",
        },
        executor=http_put_tool,
        approval_message_template="PUT to URL: {url}",
    )

    # HTTP DELETE tool
    registry.register(
        name="http_delete",
        description="Make an HTTP DELETE request",
        category=ToolCategory.NETWORK,
        danger_level=DangerLevel.HIGH,
        parameters=[
            ToolParameter(name="url", type=str, description="URL to request", required=True),
            ToolParameter(
                name="headers",
                type=dict,
                description="HTTP headers",
                required=False,
            ),
            ToolParameter(
                name="timeout",
                type=int,
                description="Request timeout in seconds (default 30)",
                required=False,
            ),
        ],
        returns={
            "status_code": "int",
            "body": "str",
            "headers": "dict",
            "success": "bool",
        },
        executor=http_delete_tool,
        approval_message_template="DELETE request to URL: {url}",
    )
