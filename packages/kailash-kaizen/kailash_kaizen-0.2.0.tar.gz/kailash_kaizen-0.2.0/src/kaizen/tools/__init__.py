"""
Kaizen Tool Calling System

Enables AI agents to autonomously execute tools (bash commands, file operations,
API calls, custom tools) with automatic approval workflows based on danger levels.

Core Components:
    - types: Tool definitions, parameters, categories, danger levels
    - registry: Tool registration and discovery
    - executor: Tool execution with approval workflow
    - builtin: Built-in tools (bash, file, API, web)

Example:
    >>> from kaizen.tools import ToolRegistry, ToolExecutor
    >>> from kaizen.tools.types import ToolDefinition, ToolParameter, ToolCategory, DangerLevel
    >>>
    >>> # Create registry and register tool
    >>> registry = ToolRegistry()
    >>> registry.register(
    ...     name="uppercase",
    ...     description="Convert text to uppercase",
    ...     category=ToolCategory.DATA,
    ...     danger_level=DangerLevel.SAFE,
    ...     parameters=[ToolParameter("text", str, "Input text")],
    ...     returns={"result": "str"},
    ...     executor=lambda text: {"result": text.upper()}
    ... )
    >>>
    >>> # Execute tool
    >>> executor = ToolExecutor(registry=registry)
    >>> result = await executor.execute("uppercase", {"text": "hello"})
    >>> print(result.result)  # {"result": "HELLO"}
"""

from kaizen.tools.executor import ToolExecutor
from kaizen.tools.registry import ToolRegistry, get_global_registry
from kaizen.tools.types import (
    ApprovalExtractorFunc,
    DangerLevel,
    ToolCategory,
    ToolDefinition,
    ToolExecutorFunc,
    ToolParameter,
    ToolResult,
    ToolValidationFunc,
)

__all__ = [
    # Core types
    "ToolDefinition",
    "ToolParameter",
    "ToolResult",
    "ToolCategory",
    "DangerLevel",
    # Type aliases
    "ToolExecutorFunc",
    "ToolValidationFunc",
    "ApprovalExtractorFunc",
    # Registry
    "ToolRegistry",
    "get_global_registry",
    # Executor
    "ToolExecutor",
]
