"""
Tool Registry for Tool Management

Centralized registry for managing tool definitions, discovery, and lookup.
Supports built-in tools, custom tools, and MCP tools.

Architecture:
    ToolRegistry manages a dictionary of ToolDefinition objects keyed by name.
    Tools can be registered, retrieved, listed by category/danger level, and validated.

Example:
    >>> from kaizen.tools.registry import ToolRegistry
    >>> from kaizen.tools.types import ToolDefinition, ToolParameter, ToolCategory, DangerLevel
    >>>
    >>> registry = ToolRegistry()
    >>>
    >>> # Register a tool
    >>> def uppercase_impl(text: str) -> dict:
    ...     return {"result": text.upper()}
    >>>
    >>> registry.register(
    ...     name="uppercase",
    ...     description="Convert text to uppercase",
    ...     category=ToolCategory.DATA,
    ...     danger_level=DangerLevel.SAFE,
    ...     parameters=[ToolParameter("text", str, "Input text")],
    ...     returns={"result": "str"},
    ...     executor=uppercase_impl
    ... )
    >>>
    >>> # Get tool
    >>> tool = registry.get("uppercase")
    >>> print(tool.name)  # "uppercase"
    >>>
    >>> # List all tools
    >>> all_tools = registry.list_all()
    >>> print(len(all_tools))  # 1
    >>>
    >>> # List by category
    >>> data_tools = registry.list_by_category(ToolCategory.DATA)
    >>> print(len(data_tools))  # 1
"""

from typing import Dict, List, Optional

from kaizen.tools.types import (
    DangerLevel,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
)


class ToolRegistry:
    """
    Centralized registry for tool management.

    Manages tool registration, lookup, and discovery. Supports filtering
    by category, danger level, and other criteria.

    Attributes:
        _tools: Dictionary mapping tool names to ToolDefinition objects
        _categories: Cache of tools grouped by category
        _danger_levels: Cache of tools grouped by danger level

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register_tool(tool_definition)
        >>> tool = registry.get("tool_name")
        >>> tools = registry.list_by_category(ToolCategory.SYSTEM)
    """

    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, ToolDefinition] = {}
        self._categories: Dict[ToolCategory, List[ToolDefinition]] = {}
        self._danger_levels: Dict[DangerLevel, List[ToolDefinition]] = {}

    def register(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        danger_level: DangerLevel,
        parameters: List[ToolParameter],
        returns: Dict,
        executor: callable,
        examples: Optional[List[Dict]] = None,
        approval_message_template: Optional[str] = None,
        approval_details_extractor: Optional[callable] = None,
    ) -> ToolDefinition:
        """
        Register a new tool (convenience method).

        Args:
            name: Unique tool identifier
            description: Human-readable description
            category: Tool category
            danger_level: Danger level for approval
            parameters: List of ToolParameter definitions
            returns: Return value schema
            executor: Callable implementing tool logic
            examples: Optional list of examples
            approval_message_template: Custom approval message
            approval_details_extractor: Custom details extractor

        Returns:
            Created ToolDefinition

        Raises:
            ValueError: If tool with same name already registered

        Example:
            >>> registry.register(
            ...     name="read_file",
            ...     description="Read file contents",
            ...     category=ToolCategory.SYSTEM,
            ...     danger_level=DangerLevel.SAFE,
            ...     parameters=[ToolParameter("path", str, "File path")],
            ...     returns={"content": "str"},
            ...     executor=lambda path: {"content": open(path).read()}
            ... )
        """
        tool = ToolDefinition(
            name=name,
            description=description,
            category=category,
            danger_level=danger_level,
            parameters=parameters,
            returns=returns,
            executor=executor,
            examples=examples,
            approval_message_template=approval_message_template,
            approval_details_extractor=approval_details_extractor,
        )

        return self.register_tool(tool)

    def register_tool(self, tool: ToolDefinition) -> ToolDefinition:
        """
        Register a tool definition.

        Args:
            tool: ToolDefinition to register

        Returns:
            The registered ToolDefinition

        Raises:
            ValueError: If tool with same name already registered

        Example:
            >>> tool = ToolDefinition(...)
            >>> registry.register_tool(tool)
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool

        # Update category cache
        if tool.category not in self._categories:
            self._categories[tool.category] = []
        self._categories[tool.category].append(tool)

        # Update danger level cache
        if tool.danger_level not in self._danger_levels:
            self._danger_levels[tool.danger_level] = []
        self._danger_levels[tool.danger_level].append(tool)

        return tool

    def unregister(self, name: str) -> Optional[ToolDefinition]:
        """
        Unregister a tool by name.

        Args:
            name: Tool name to unregister

        Returns:
            Unregistered ToolDefinition, or None if not found

        Example:
            >>> tool = registry.unregister("old_tool")
        """
        if name not in self._tools:
            return None

        tool = self._tools.pop(name)

        # Update category cache
        if tool.category in self._categories:
            self._categories[tool.category].remove(tool)
            if not self._categories[tool.category]:
                del self._categories[tool.category]

        # Update danger level cache
        if tool.danger_level in self._danger_levels:
            self._danger_levels[tool.danger_level].remove(tool)
            if not self._danger_levels[tool.danger_level]:
                del self._danger_levels[tool.danger_level]

        return tool

    def get(self, name: str) -> Optional[ToolDefinition]:
        """
        Get tool by name.

        Args:
            name: Tool name to retrieve

        Returns:
            ToolDefinition if found, None otherwise

        Example:
            >>> tool = registry.get("read_file")
            >>> if tool:
            ...     print(tool.description)
        """
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        """
        Check if tool exists in registry.

        Args:
            name: Tool name to check

        Returns:
            True if tool registered, False otherwise

        Example:
            >>> if registry.has("bash_command"):
            ...     print("Bash tool available")
        """
        return name in self._tools

    def list_all(self) -> List[ToolDefinition]:
        """
        List all registered tools.

        Returns:
            List of all ToolDefinition objects

        Example:
            >>> all_tools = registry.list_all()
            >>> print(f"Total tools: {len(all_tools)}")
        """
        return list(self._tools.values())

    def list_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """
        List tools by category.

        Args:
            category: ToolCategory to filter by

        Returns:
            List of ToolDefinition objects in category

        Example:
            >>> system_tools = registry.list_by_category(ToolCategory.SYSTEM)
            >>> for tool in system_tools:
            ...     print(f"System tool: {tool.name}")
        """
        return self._categories.get(category, [])

    def list_by_danger_level(self, danger_level: DangerLevel) -> List[ToolDefinition]:
        """
        List tools by danger level.

        Args:
            danger_level: DangerLevel to filter by

        Returns:
            List of ToolDefinition objects with danger level

        Example:
            >>> safe_tools = registry.list_by_danger_level(DangerLevel.SAFE)
            >>> for tool in safe_tools:
            ...     print(f"Safe tool: {tool.name}")
        """
        return self._danger_levels.get(danger_level, [])

    def list_dangerous_tools(self) -> List[ToolDefinition]:
        """
        List all dangerous tools (HIGH and CRITICAL danger levels).

        Returns:
            List of ToolDefinition objects with HIGH or CRITICAL danger

        Example:
            >>> dangerous = registry.list_dangerous_tools()
            >>> print(f"Dangerous tools: {[t.name for t in dangerous]}")
        """
        high_tools = self.list_by_danger_level(DangerLevel.HIGH)
        critical_tools = self.list_by_danger_level(DangerLevel.CRITICAL)
        return high_tools + critical_tools

    def list_safe_tools(self) -> List[ToolDefinition]:
        """
        List all safe tools (SAFE danger level, no approval needed).

        Returns:
            List of ToolDefinition objects with SAFE danger level

        Example:
            >>> safe = registry.list_safe_tools()
            >>> for tool in safe:
            ...     print(f"Safe tool: {tool.name} - {tool.description}")
        """
        return self.list_by_danger_level(DangerLevel.SAFE)

    def search(self, query: str) -> List[ToolDefinition]:
        """
        Search tools by name or description.

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching ToolDefinition objects

        Example:
            >>> results = registry.search("file")
            >>> for tool in results:
            ...     print(f"Found: {tool.name} - {tool.description}")
        """
        query_lower = query.lower()
        results = []

        for tool in self._tools.values():
            if query_lower in tool.name.lower() or query_lower in tool.description.lower():
                results.append(tool)

        return results

    def get_tool_names(self) -> List[str]:
        """
        Get list of all tool names.

        Returns:
            List of tool name strings

        Example:
            >>> names = registry.get_tool_names()
            >>> print(f"Available tools: {', '.join(names)}")
        """
        return list(self._tools.keys())

    def get_categories(self) -> List[ToolCategory]:
        """
        Get list of all categories with registered tools.

        Returns:
            List of ToolCategory enums

        Example:
            >>> categories = registry.get_categories()
            >>> for cat in categories:
            ...     tools = registry.list_by_category(cat)
            ...     print(f"{cat.value}: {len(tools)} tools")
        """
        return list(self._categories.keys())

    def clear(self):
        """
        Clear all registered tools.

        Warning: This removes ALL tools from registry, including built-ins.

        Example:
            >>> registry.clear()
            >>> print(len(registry.list_all()))  # 0
        """
        self._tools.clear()
        self._categories.clear()
        self._danger_levels.clear()

    def count(self) -> int:
        """
        Get count of registered tools.

        Returns:
            Number of registered tools

        Example:
            >>> print(f"Total tools: {registry.count()}")
        """
        return len(self._tools)

    def to_dict(self) -> Dict[str, Dict]:
        """
        Export registry to dictionary for serialization.

        Returns:
            Dict mapping tool names to tool metadata

        Example:
            >>> data = registry.to_dict()
            >>> import json
            >>> json.dump(data, open("tools.json", "w"))
        """
        return {
            name: {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "danger_level": tool.danger_level.value,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type.__name__,
                        "description": p.description,
                        "required": p.required,
                        "default": p.default,
                    }
                    for p in tool.parameters
                ],
                "returns": tool.returns,
            }
            for name, tool in self._tools.items()
        }


# Global registry instance (lazy-loaded)
_global_registry: Optional[ToolRegistry] = None


def get_global_registry() -> ToolRegistry:
    """
    Get global tool registry instance (singleton).

    Returns:
        Global ToolRegistry instance

    Example:
        >>> from kaizen.tools.registry import get_global_registry
        >>> registry = get_global_registry()
        >>> registry.register(...)
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
