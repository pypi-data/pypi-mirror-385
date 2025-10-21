"""
Unit Tests for Tool Registry (Tier 1)

Tests tool registration, lookup, filtering, and discovery functionality.

Coverage:
- Tool registration (register, register_tool)
- Tool lookup (get, has)
- Tool listing (list_all, list_by_category, list_by_danger_level)
- Tool filtering (list_dangerous_tools, list_safe_tools)
- Tool search
- Registry management (unregister, clear, count)
- Global registry singleton
"""

import pytest

from kaizen.tools.registry import ToolRegistry, get_global_registry
from kaizen.tools.types import (
    DangerLevel,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
)


@pytest.fixture
def empty_registry():
    """Create empty registry for each test."""
    return ToolRegistry()


@pytest.fixture
def simple_tool():
    """Create simple test tool."""
    return ToolDefinition(
        name="uppercase",
        description="Convert to uppercase",
        category=ToolCategory.DATA,
        danger_level=DangerLevel.SAFE,
        parameters=[ToolParameter("text", str, "Input text")],
        returns={"result": "str"},
        executor=lambda text: {"result": text.upper()}
    )


@pytest.fixture
def dangerous_tool():
    """Create dangerous test tool."""
    return ToolDefinition(
        name="bash_command",
        description="Execute bash",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.HIGH,
        parameters=[ToolParameter("command", str, "Command")],
        returns={"stdout": "str", "stderr": "str"},
        executor=lambda command: {}
    )


@pytest.fixture
def critical_tool():
    """Create critical danger tool."""
    return ToolDefinition(
        name="delete_all",
        description="Delete all files",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.CRITICAL,
        parameters=[],
        returns={"deleted_count": "int"},
        executor=lambda: {}
    )


class TestToolRegistryRegistration:
    """Test tool registration methods."""

    def test_register_convenience_method(self, empty_registry):
        """Test registering tool with convenience method."""
        tool = empty_registry.register(
            name="test_tool",
            description="Test tool",
            category=ToolCategory.CUSTOM,
            danger_level=DangerLevel.SAFE,
            parameters=[],
            returns={},
            executor=lambda: {}
        )

        assert isinstance(tool, ToolDefinition)
        assert tool.name == "test_tool"
        assert empty_registry.has("test_tool")

    def test_register_tool_definition(self, empty_registry, simple_tool):
        """Test registering ToolDefinition object."""
        result = empty_registry.register_tool(simple_tool)

        assert result == simple_tool
        assert empty_registry.has("uppercase")

    def test_register_duplicate_raises_error(self, empty_registry, simple_tool):
        """Test registering duplicate tool raises ValueError."""
        empty_registry.register_tool(simple_tool)

        with pytest.raises(ValueError, match="already registered"):
            empty_registry.register_tool(simple_tool)

    def test_register_updates_category_cache(self, empty_registry, simple_tool):
        """Test registration updates category cache."""
        empty_registry.register_tool(simple_tool)

        data_tools = empty_registry.list_by_category(ToolCategory.DATA)
        assert len(data_tools) == 1
        assert data_tools[0].name == "uppercase"

    def test_register_updates_danger_level_cache(self, empty_registry, simple_tool):
        """Test registration updates danger level cache."""
        empty_registry.register_tool(simple_tool)

        safe_tools = empty_registry.list_by_danger_level(DangerLevel.SAFE)
        assert len(safe_tools) == 1
        assert safe_tools[0].name == "uppercase"

    def test_register_multiple_tools(self, empty_registry, simple_tool, dangerous_tool):
        """Test registering multiple tools."""
        empty_registry.register_tool(simple_tool)
        empty_registry.register_tool(dangerous_tool)

        assert empty_registry.count() == 2
        assert empty_registry.has("uppercase")
        assert empty_registry.has("bash_command")


class TestToolRegistryLookup:
    """Test tool lookup methods."""

    def test_get_existing_tool(self, empty_registry, simple_tool):
        """Test getting existing tool."""
        empty_registry.register_tool(simple_tool)

        retrieved = empty_registry.get("uppercase")
        assert retrieved is not None
        assert retrieved.name == "uppercase"

    def test_get_nonexistent_tool_returns_none(self, empty_registry):
        """Test getting nonexistent tool returns None."""
        result = empty_registry.get("nonexistent")
        assert result is None

    def test_has_existing_tool_returns_true(self, empty_registry, simple_tool):
        """Test has() returns True for existing tool."""
        empty_registry.register_tool(simple_tool)

        assert empty_registry.has("uppercase") is True

    def test_has_nonexistent_tool_returns_false(self, empty_registry):
        """Test has() returns False for nonexistent tool."""
        assert empty_registry.has("nonexistent") is False


class TestToolRegistryListing:
    """Test tool listing methods."""

    def test_list_all_empty_registry(self, empty_registry):
        """Test list_all() on empty registry."""
        tools = empty_registry.list_all()
        assert tools == []

    def test_list_all_with_tools(self, empty_registry, simple_tool, dangerous_tool):
        """Test list_all() with registered tools."""
        empty_registry.register_tool(simple_tool)
        empty_registry.register_tool(dangerous_tool)

        tools = empty_registry.list_all()
        assert len(tools) == 2
        names = [t.name for t in tools]
        assert "uppercase" in names
        assert "bash_command" in names

    def test_list_by_category_system(self, empty_registry, simple_tool, dangerous_tool):
        """Test list_by_category() for SYSTEM category."""
        empty_registry.register_tool(simple_tool)  # DATA category
        empty_registry.register_tool(dangerous_tool)  # SYSTEM category

        system_tools = empty_registry.list_by_category(ToolCategory.SYSTEM)
        assert len(system_tools) == 1
        assert system_tools[0].name == "bash_command"

    def test_list_by_category_empty(self, empty_registry, simple_tool):
        """Test list_by_category() for category with no tools."""
        empty_registry.register_tool(simple_tool)

        network_tools = empty_registry.list_by_category(ToolCategory.NETWORK)
        assert network_tools == []

    def test_list_by_danger_level_safe(self, empty_registry, simple_tool, dangerous_tool):
        """Test list_by_danger_level() for SAFE level."""
        empty_registry.register_tool(simple_tool)  # SAFE
        empty_registry.register_tool(dangerous_tool)  # HIGH

        safe_tools = empty_registry.list_by_danger_level(DangerLevel.SAFE)
        assert len(safe_tools) == 1
        assert safe_tools[0].name == "uppercase"

    def test_list_by_danger_level_high(self, empty_registry, simple_tool, dangerous_tool):
        """Test list_by_danger_level() for HIGH level."""
        empty_registry.register_tool(simple_tool)  # SAFE
        empty_registry.register_tool(dangerous_tool)  # HIGH

        high_tools = empty_registry.list_by_danger_level(DangerLevel.HIGH)
        assert len(high_tools) == 1
        assert high_tools[0].name == "bash_command"

    def test_list_dangerous_tools(self, empty_registry, simple_tool, dangerous_tool, critical_tool):
        """Test list_dangerous_tools() returns HIGH and CRITICAL."""
        empty_registry.register_tool(simple_tool)  # SAFE
        empty_registry.register_tool(dangerous_tool)  # HIGH
        empty_registry.register_tool(critical_tool)  # CRITICAL

        dangerous = empty_registry.list_dangerous_tools()
        assert len(dangerous) == 2
        names = [t.name for t in dangerous]
        assert "bash_command" in names
        assert "delete_all" in names
        assert "uppercase" not in names

    def test_list_safe_tools(self, empty_registry, simple_tool, dangerous_tool):
        """Test list_safe_tools() returns only SAFE tools."""
        empty_registry.register_tool(simple_tool)  # SAFE
        empty_registry.register_tool(dangerous_tool)  # HIGH

        safe = empty_registry.list_safe_tools()
        assert len(safe) == 1
        assert safe[0].name == "uppercase"


class TestToolRegistrySearch:
    """Test tool search functionality."""

    def test_search_by_name_exact(self, empty_registry, simple_tool):
        """Test search by exact name match."""
        empty_registry.register_tool(simple_tool)

        results = empty_registry.search("uppercase")
        assert len(results) == 1
        assert results[0].name == "uppercase"

    def test_search_by_name_partial(self, empty_registry, simple_tool):
        """Test search by partial name match."""
        empty_registry.register_tool(simple_tool)

        results = empty_registry.search("upper")
        assert len(results) == 1
        assert results[0].name == "uppercase"

    def test_search_by_description(self, empty_registry, simple_tool):
        """Test search by description match."""
        empty_registry.register_tool(simple_tool)

        results = empty_registry.search("convert")
        assert len(results) == 1
        assert results[0].name == "uppercase"

    def test_search_case_insensitive(self, empty_registry, simple_tool):
        """Test search is case-insensitive."""
        empty_registry.register_tool(simple_tool)

        results = empty_registry.search("UPPERCASE")
        assert len(results) == 1

        results = empty_registry.search("CONVERT")
        assert len(results) == 1

    def test_search_no_results(self, empty_registry, simple_tool):
        """Test search returns empty list when no matches."""
        empty_registry.register_tool(simple_tool)

        results = empty_registry.search("nonexistent")
        assert results == []

    def test_search_multiple_results(self, empty_registry):
        """Test search returns multiple matching tools."""
        empty_registry.register(
            name="read_file",
            description="Read file contents",
            category=ToolCategory.SYSTEM,
            danger_level=DangerLevel.SAFE,
            parameters=[],
            returns={},
            executor=lambda: {}
        )
        empty_registry.register(
            name="write_file",
            description="Write file contents",
            category=ToolCategory.SYSTEM,
            danger_level=DangerLevel.MEDIUM,
            parameters=[],
            returns={},
            executor=lambda: {}
        )

        results = empty_registry.search("file")
        assert len(results) == 2
        names = [t.name for t in results]
        assert "read_file" in names
        assert "write_file" in names


class TestToolRegistryManagement:
    """Test registry management methods."""

    def test_unregister_existing_tool(self, empty_registry, simple_tool):
        """Test unregistering existing tool."""
        empty_registry.register_tool(simple_tool)

        removed = empty_registry.unregister("uppercase")
        assert removed is not None
        assert removed.name == "uppercase"
        assert not empty_registry.has("uppercase")

    def test_unregister_nonexistent_tool(self, empty_registry):
        """Test unregistering nonexistent tool returns None."""
        removed = empty_registry.unregister("nonexistent")
        assert removed is None

    def test_unregister_updates_category_cache(self, empty_registry, simple_tool):
        """Test unregister updates category cache."""
        empty_registry.register_tool(simple_tool)
        assert len(empty_registry.list_by_category(ToolCategory.DATA)) == 1

        empty_registry.unregister("uppercase")
        assert len(empty_registry.list_by_category(ToolCategory.DATA)) == 0

    def test_unregister_updates_danger_level_cache(self, empty_registry, simple_tool):
        """Test unregister updates danger level cache."""
        empty_registry.register_tool(simple_tool)
        assert len(empty_registry.list_by_danger_level(DangerLevel.SAFE)) == 1

        empty_registry.unregister("uppercase")
        assert len(empty_registry.list_by_danger_level(DangerLevel.SAFE)) == 0

    def test_clear_removes_all_tools(self, empty_registry, simple_tool, dangerous_tool):
        """Test clear() removes all tools."""
        empty_registry.register_tool(simple_tool)
        empty_registry.register_tool(dangerous_tool)
        assert empty_registry.count() == 2

        empty_registry.clear()
        assert empty_registry.count() == 0
        assert empty_registry.list_all() == []

    def test_count_empty_registry(self, empty_registry):
        """Test count() on empty registry."""
        assert empty_registry.count() == 0

    def test_count_with_tools(self, empty_registry, simple_tool, dangerous_tool):
        """Test count() with tools registered."""
        empty_registry.register_tool(simple_tool)
        assert empty_registry.count() == 1

        empty_registry.register_tool(dangerous_tool)
        assert empty_registry.count() == 2

    def test_get_tool_names(self, empty_registry, simple_tool, dangerous_tool):
        """Test get_tool_names() returns list of names."""
        empty_registry.register_tool(simple_tool)
        empty_registry.register_tool(dangerous_tool)

        names = empty_registry.get_tool_names()
        assert len(names) == 2
        assert "uppercase" in names
        assert "bash_command" in names

    def test_get_categories(self, empty_registry, simple_tool, dangerous_tool):
        """Test get_categories() returns categories with tools."""
        empty_registry.register_tool(simple_tool)  # DATA
        empty_registry.register_tool(dangerous_tool)  # SYSTEM

        categories = empty_registry.get_categories()
        assert len(categories) == 2
        assert ToolCategory.DATA in categories
        assert ToolCategory.SYSTEM in categories


class TestToolRegistryExport:
    """Test registry export functionality."""

    def test_to_dict_empty_registry(self, empty_registry):
        """Test to_dict() on empty registry."""
        data = empty_registry.to_dict()
        assert data == {}

    def test_to_dict_with_tools(self, empty_registry, simple_tool):
        """Test to_dict() exports tool metadata."""
        empty_registry.register_tool(simple_tool)

        data = empty_registry.to_dict()
        assert "uppercase" in data
        tool_data = data["uppercase"]
        assert tool_data["name"] == "uppercase"
        assert tool_data["description"] == "Convert to uppercase"
        assert tool_data["category"] == "data"
        assert tool_data["danger_level"] == "safe"
        assert len(tool_data["parameters"]) == 1
        assert tool_data["parameters"][0]["name"] == "text"

    def test_to_dict_multiple_tools(self, empty_registry, simple_tool, dangerous_tool):
        """Test to_dict() with multiple tools."""
        empty_registry.register_tool(simple_tool)
        empty_registry.register_tool(dangerous_tool)

        data = empty_registry.to_dict()
        assert len(data) == 2
        assert "uppercase" in data
        assert "bash_command" in data


class TestGlobalRegistry:
    """Test global registry singleton."""

    def test_get_global_registry_returns_instance(self):
        """Test get_global_registry() returns ToolRegistry."""
        registry = get_global_registry()
        assert isinstance(registry, ToolRegistry)

    def test_get_global_registry_returns_same_instance(self):
        """Test get_global_registry() returns same instance (singleton)."""
        registry1 = get_global_registry()
        registry2 = get_global_registry()
        assert registry1 is registry2

    def test_global_registry_persists_tools(self, simple_tool):
        """Test tools registered in global registry persist across calls."""
        registry1 = get_global_registry()
        # Clear any existing tools from previous tests
        registry1.clear()

        registry1.register_tool(simple_tool)

        registry2 = get_global_registry()
        assert registry2.has("uppercase")
        assert registry2.count() == 1

        # Clean up
        registry2.clear()
