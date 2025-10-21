"""
Web Tools for Content Fetching and Parsing

Provides tools for fetching web pages and extracting content.

Example:
    >>> from kaizen.tools import ToolRegistry, ToolExecutor
    >>> from kaizen.tools.builtin.web import register_web_tools
    >>>
    >>> registry = ToolRegistry()
    >>> register_web_tools(registry)
    >>>
    >>> executor = ToolExecutor(registry=registry)
    >>> result = await executor.execute("fetch_url", {"url": "https://example.com"})
    >>> print(result.result["content"][:100])
"""

from html.parser import HTMLParser
from typing import Any, Dict, List, TypedDict
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse

from kaizen.tools import DangerLevel, ToolCategory, ToolParameter
from kaizen.tools.registry import ToolRegistry


class FetchURLResult(TypedDict, total=False):
    """Type definition for fetch_url tool results."""
    content: str
    status_code: int
    content_type: str
    size: int
    success: bool
    error: str  # Optional


class ExtractLinksResult(TypedDict, total=False):
    """Type definition for extract_links tool results."""
    links: List[str]
    count: int
    unique_count: int
    unique_links: List[str]
    error: str  # Optional


class LinkExtractor(HTMLParser):
    """
    HTML parser for extracting links from <a> tags.

    More robust than regex-based extraction:
    - Only extracts from actual <a href="..."> tags
    - Handles malformed HTML gracefully
    - Prevents extraction from scripts, comments, or attributes
    - Properly handles nested tags and edge cases
    """

    def __init__(self):
        super().__init__()
        self.links: List[str] = []
        self._in_script = False
        self._in_style = False

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        """
        Handle start tags, extracting href from <a> tags.

        Args:
            tag: HTML tag name
            attrs: List of (attribute, value) tuples
        """
        # Track if we're inside script or style tags (don't extract from these)
        if tag == "script":
            self._in_script = True
        elif tag == "style":
            self._in_style = True

        # Only extract from <a> tags, not script/style
        if tag == "a" and not self._in_script and not self._in_style:
            for attr_name, attr_value in attrs:
                if attr_name.lower() == "href" and attr_value:
                    self.links.append(attr_value)

    def handle_endtag(self, tag: str) -> None:
        """Handle end tags to track context."""
        if tag == "script":
            self._in_script = False
        elif tag == "style":
            self._in_style = False


def fetch_url_tool(params: Dict[str, Any]) -> FetchURLResult:
    """
    Fetch content from a URL.

    Args:
        params: Dictionary with:
            - url (str): URL to fetch
            - timeout (int, optional): Request timeout in seconds (default 30)
            - user_agent (str, optional): User agent string

    Returns:
        Dictionary with:
            - content (str): Page content
            - status_code (int): HTTP status code
            - content_type (str): Content type
            - size (int): Content size in bytes
            - success (bool): True if fetch succeeded
    """
    url = params["url"]
    timeout = params.get("timeout", 30)
    user_agent = params.get(
        "user_agent", "Kaizen-ToolCalling/1.0 (compatible; bot)"
    )

    try:
        headers = {"User-Agent": user_agent}
        req = urllib_request.Request(url, headers=headers)

        with urllib_request.urlopen(req, timeout=timeout) as response:
            content = response.read().decode("utf-8")
            status_code = response.status
            content_type = response.headers.get("Content-Type", "")
            size = len(content.encode("utf-8"))

            return {
                "content": content,
                "status_code": status_code,
                "content_type": content_type,
                "size": size,
                "success": True,
            }

    except HTTPError as e:
        return {
            "content": "",
            "status_code": e.code,
            "content_type": "",
            "size": 0,
            "success": False,
            "error": f"HTTP Error {e.code}: {e.reason}",
        }

    except URLError as e:
        return {
            "content": "",
            "status_code": 0,
            "content_type": "",
            "size": 0,
            "success": False,
            "error": str(e.reason),
        }

    except Exception as e:
        return {
            "content": "",
            "status_code": 0,
            "content_type": "",
            "size": 0,
            "success": False,
            "error": str(e),
        }


def extract_links_tool(params: Dict[str, Any]) -> ExtractLinksResult:
    """
    Extract links from HTML content using HTMLParser.

    Uses html.parser.HTMLParser for robust link extraction:
    - Only extracts from actual <a href="..."> tags
    - Handles malformed HTML gracefully
    - Prevents extraction from scripts, comments, attributes
    - More reliable than regex-based parsing

    Args:
        params: Dictionary with:
            - html (str): HTML content to parse
            - base_url (str, optional): Base URL for resolving relative links

    Returns:
        Dictionary with:
            - links (list[str]): List of extracted links (in order found)
            - count (int): Number of links found
            - unique_count (int): Number of unique links
            - unique_links (list[str]): Sorted list of unique links
    """
    html = params["html"]
    base_url = params.get("base_url", "")

    try:
        # Use HTMLParser for robust link extraction
        parser = LinkExtractor()
        parser.feed(html)

        links = []
        for link in parser.links:
            # Skip empty links, anchors, and javascript
            if not link or link.startswith("#") or link.startswith("javascript:"):
                continue

            # Skip data URIs and mailto links
            if link.startswith(("data:", "mailto:")):
                continue

            # Convert relative to absolute if base_url provided
            if base_url:
                # urljoin handles all cases: absolute paths, relative paths, already absolute URLs
                link = urljoin(base_url, link)

            links.append(link)

        unique_links = list(set(links))

        return {
            "links": links,
            "count": len(links),
            "unique_count": len(unique_links),
            "unique_links": sorted(unique_links),
        }

    except Exception as e:
        return {
            "links": [],
            "count": 0,
            "unique_count": 0,
            "unique_links": [],
            "error": str(e),
        }


def register_web_tools(registry: ToolRegistry) -> None:
    """
    Register web tools to a registry.

    Args:
        registry: ToolRegistry instance to register tools to

    Registers:
        - fetch_url: Fetch web page content (LOW danger)
        - extract_links: Extract links from HTML (SAFE)

    Example:
        >>> registry = ToolRegistry()
        >>> register_web_tools(registry)
        >>> tool = registry.get("fetch_url")
        >>> print(tool.name)
    """
    # Fetch URL tool
    registry.register(
        name="fetch_url",
        description="Fetch content from a URL",
        category=ToolCategory.NETWORK,
        danger_level=DangerLevel.LOW,
        parameters=[
            ToolParameter(name="url", type=str, description="URL to fetch", required=True),
            ToolParameter(
                name="timeout",
                type=int,
                description="Request timeout in seconds (default 30)",
                required=False,
            ),
            ToolParameter(
                name="user_agent",
                type=str,
                description="User agent string",
                required=False,
            ),
        ],
        returns={
            "content": "str",
            "status_code": "int",
            "content_type": "str",
            "size": "int",
            "success": "bool",
        },
        executor=fetch_url_tool,
    )

    # Extract links tool
    registry.register(
        name="extract_links",
        description="Extract links from HTML content",
        category=ToolCategory.DATA,
        danger_level=DangerLevel.SAFE,
        parameters=[
            ToolParameter(
                name="html",
                type=str,
                description="HTML content to parse",
                required=True,
            ),
            ToolParameter(
                name="base_url",
                type=str,
                description="Base URL for resolving relative links",
                required=False,
            ),
        ],
        returns={
            "links": "list[str]",
            "count": "int",
            "unique_count": "int",
            "unique_links": "list[str]",
        },
        executor=extract_links_tool,
    )
