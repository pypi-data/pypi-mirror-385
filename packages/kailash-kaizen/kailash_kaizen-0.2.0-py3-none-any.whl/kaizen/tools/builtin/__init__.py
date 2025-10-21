"""
Builtin Tools for Kaizen Tool Calling System

Provides pre-built tools for common operations:
- Bash: Execute shell commands
- File: File operations (read, write, delete, list)
- API: HTTP requests (GET, POST, PUT, DELETE)
- Web: Web scraping and content fetching

Example:
    >>> from kaizen.tools import ToolRegistry
    >>> from kaizen.tools.builtin import register_builtin_tools
    >>>
    >>> registry = ToolRegistry()
    >>> register_builtin_tools(registry)
    >>>
    >>> # All builtin tools now available
    >>> registry.count()  # 12+ tools registered
"""

from kaizen.tools.builtin.bash import register_bash_tools
from kaizen.tools.builtin.file import register_file_tools
from kaizen.tools.builtin.api import register_api_tools
from kaizen.tools.builtin.web import register_web_tools
from kaizen.tools.registry import ToolRegistry


def register_builtin_tools(registry: ToolRegistry) -> None:
    """
    Register all builtin tools to a registry.

    Args:
        registry: ToolRegistry instance to register tools to

    Registers:
        - Bash tools: bash_command
        - File tools: read_file, write_file, delete_file, list_directory, file_exists
        - API tools: http_get, http_post, http_put, http_delete
        - Web tools: fetch_url, extract_links

    Example:
        >>> registry = ToolRegistry()
        >>> register_builtin_tools(registry)
        >>> print(f"Registered {registry.count()} tools")
    """
    register_bash_tools(registry)
    register_file_tools(registry)
    register_api_tools(registry)
    register_web_tools(registry)


__all__ = [
    "register_builtin_tools",
    "register_bash_tools",
    "register_file_tools",
    "register_api_tools",
    "register_web_tools",
]
