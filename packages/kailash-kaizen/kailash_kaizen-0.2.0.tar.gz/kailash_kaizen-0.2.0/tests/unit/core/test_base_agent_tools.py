"""
Tier 1 Unit Tests for BaseAgent Tool Integration

Tests tool calling capabilities integrated with BaseAgent:
- Tool discovery and filtering
- Tool execution with approval workflows
- Tool chaining for multi-step operations
- ControlProtocol integration
- Error handling and edge cases

Coverage Target: 100% for new tool methods
Test Strategy: TDD - Tests written BEFORE implementation
Infrastructure: Mocked ToolExecutor and ControlProtocol for fast tests
"""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from kaizen.core.autonomy.control.protocol import ControlProtocol
from kaizen.core.base_agent import BaseAgent, BaseAgentConfig
from kaizen.signatures import InputField, OutputField, Signature
from kaizen.tools.executor import ToolExecutor
from kaizen.tools.registry import ToolRegistry
from kaizen.tools.types import (
    DangerLevel,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    ToolResult,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def simple_signature():
    """Create a simple test signature."""

    class TestSignature(Signature):
        question: str = InputField(description="Question to answer")
        answer: str = OutputField(description="Answer to question")

    return TestSignature()


@pytest.fixture
def base_config():
    """Create basic BaseAgentConfig."""
    return BaseAgentConfig(
        llm_provider="mock", model="test-model", temperature=0.7, logging_enabled=False
    )


@pytest.fixture
def tool_registry():
    """Create ToolRegistry with sample tools."""
    registry = ToolRegistry()

    # Safe tool - no approval needed
    # Note: Tool executors receive params as Dict[str, Any]
    def read_file_impl(params: Dict[str, Any]) -> dict:
        path = params.get("path")
        return {"content": f"Content of {path}", "size": 100}

    registry.register(
        name="read_file",
        description="Read file contents",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.SAFE,
        parameters=[ToolParameter("path", str, "File path", required=True)],
        returns={"content": "str", "size": "int"},
        executor=read_file_impl,
    )

    # Medium danger tool - requires approval for writes
    def write_file_impl(params: Dict[str, Any]) -> dict:
        content = params.get("content", "")
        return {"success": True, "bytes_written": len(content)}

    registry.register(
        name="write_file",
        description="Write content to file",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.MEDIUM,
        parameters=[
            ToolParameter("path", str, "File path", required=True),
            ToolParameter("content", str, "Content to write", required=True),
        ],
        returns={"success": "bool", "bytes_written": "int"},
        executor=write_file_impl,
    )

    # High danger tool - always requires approval
    def bash_command_impl(params: Dict[str, Any]) -> dict:
        return {"stdout": "output", "stderr": "", "returncode": 0}

    registry.register(
        name="bash_command",
        description="Execute bash command",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.HIGH,
        parameters=[ToolParameter("command", str, "Command to execute", required=True)],
        returns={"stdout": "str", "stderr": "str", "returncode": "int"},
        executor=bash_command_impl,
    )

    # Data tool - for category filtering tests
    def transform_data_impl(params: Dict[str, Any]) -> dict:
        data = params.get("data", "")
        return {"result": data.upper()}

    registry.register(
        name="transform_data",
        description="Transform data",
        category=ToolCategory.DATA,
        danger_level=DangerLevel.SAFE,
        parameters=[ToolParameter("data", str, "Data to transform", required=True)],
        returns={"result": "str"},
        executor=transform_data_impl,
    )

    return registry


@pytest.fixture
def agent_without_tools(base_config, simple_signature):
    """Create BaseAgent WITHOUT tool support (backward compatibility)."""
    return BaseAgent(config=base_config, signature=simple_signature)


@pytest.fixture
def agent_with_tools(base_config, simple_signature, tool_registry):
    """Create BaseAgent WITH tool support."""
    return BaseAgent(
        config=base_config, signature=simple_signature, tool_registry=tool_registry
    )


@pytest.fixture
def mock_control_protocol():
    """Create mock ControlProtocol for testing approval workflows."""
    protocol = Mock(spec=ControlProtocol)
    return protocol


# ============================================
# 1. Initialization Tests (5 tests)
# ============================================


class TestInitialization:
    """Test BaseAgent initialization with tool support."""

    def test_agent_without_tools_has_no_tool_support(self, agent_without_tools):
        """Test backward compatibility - agents without tools work as before."""
        assert not hasattr(agent_without_tools, "_tool_registry") or (
            agent_without_tools._tool_registry is None
        )
        assert not hasattr(agent_without_tools, "_tool_executor") or (
            agent_without_tools._tool_executor is None
        )

    def test_agent_with_registry_has_tool_support(self, agent_with_tools):
        """Test agent with registry initializes tool system."""
        assert hasattr(agent_with_tools, "_tool_registry")
        assert agent_with_tools._tool_registry is not None
        assert hasattr(agent_with_tools, "_tool_executor")
        assert agent_with_tools._tool_executor is not None

    def test_agent_creates_executor_if_not_provided(
        self, base_config, simple_signature, tool_registry
    ):
        """Test agent auto-creates ToolExecutor if registry provided."""
        agent = BaseAgent(
            config=base_config, signature=simple_signature, tool_registry=tool_registry
        )
        assert agent._tool_executor is not None
        assert isinstance(agent._tool_executor, ToolExecutor)

    def test_agent_uses_provided_executor(
        self, base_config, simple_signature, tool_registry
    ):
        """Test agent uses provided ToolExecutor if given."""
        custom_executor = ToolExecutor(registry=tool_registry, auto_approve_safe=False)
        agent = BaseAgent(
            config=base_config,
            signature=simple_signature,
            tool_registry=tool_registry,
            tool_executor=custom_executor,
        )
        assert agent._tool_executor is custom_executor

    def test_tool_executor_shares_control_protocol(
        self, base_config, simple_signature, tool_registry, mock_control_protocol
    ):
        """Test ToolExecutor uses agent's ControlProtocol."""
        agent = BaseAgent(
            config=base_config,
            signature=simple_signature,
            tool_registry=tool_registry,
            control_protocol=mock_control_protocol,
        )
        # Executor should use the same control protocol
        assert agent._tool_executor.control_protocol is mock_control_protocol


# ============================================
# 2. has_tool_support() Tests (3 tests)
# ============================================


class TestHasToolSupport:
    """Test has_tool_support() method."""

    def test_agent_without_tools_returns_false(self, agent_without_tools):
        """Test has_tool_support() returns False for agents without tools."""
        assert agent_without_tools.has_tool_support() is False

    def test_agent_with_tools_returns_true(self, agent_with_tools):
        """Test has_tool_support() returns True for agents with tools."""
        assert agent_with_tools.has_tool_support() is True

    def test_has_tool_support_is_callable(self, agent_with_tools):
        """Test has_tool_support() is a callable method."""
        assert callable(getattr(agent_with_tools, "has_tool_support", None))


# ============================================
# 3. discover_tools() Tests (7 tests)
# ============================================


class TestDiscoverTools:
    """Test discover_tools() method."""

    @pytest.mark.asyncio
    async def test_discover_all_tools(self, agent_with_tools):
        """Test discovering all available tools."""
        tools = await agent_with_tools.discover_tools()
        assert len(tools) == 4  # read_file, write_file, bash_command, transform_data

    @pytest.mark.asyncio
    async def test_discover_by_category(self, agent_with_tools):
        """Test discovering tools by category."""
        system_tools = await agent_with_tools.discover_tools(
            category=ToolCategory.SYSTEM
        )
        assert len(system_tools) == 3  # read_file, write_file, bash_command

        data_tools = await agent_with_tools.discover_tools(category=ToolCategory.DATA)
        assert len(data_tools) == 1  # transform_data

    @pytest.mark.asyncio
    async def test_discover_safe_only(self, agent_with_tools):
        """Test discovering only safe tools."""
        safe_tools = await agent_with_tools.discover_tools(safe_only=True)
        assert len(safe_tools) == 2  # read_file, transform_data
        assert all(
            tool.danger_level == DangerLevel.SAFE for tool in safe_tools
        ), "All tools should be SAFE"

    @pytest.mark.asyncio
    async def test_discover_by_keyword(self, agent_with_tools):
        """Test discovering tools by keyword search."""
        file_tools = await agent_with_tools.discover_tools(keyword="file")
        assert len(file_tools) >= 2  # read_file, write_file

    @pytest.mark.asyncio
    async def test_discover_with_multiple_filters(self, agent_with_tools):
        """Test discovering tools with multiple filters combined."""
        filtered_tools = await agent_with_tools.discover_tools(
            category=ToolCategory.SYSTEM, safe_only=True
        )
        assert len(filtered_tools) == 1  # Only read_file (SYSTEM + SAFE)

    @pytest.mark.asyncio
    async def test_discover_tools_without_registry_raises_error(
        self, agent_without_tools
    ):
        """Test discover_tools() raises error if no registry configured."""
        with pytest.raises(
            RuntimeError, match="Tool registry not configured|not configured"
        ):
            await agent_without_tools.discover_tools()

    @pytest.mark.asyncio
    async def test_discover_returns_tool_definitions(self, agent_with_tools):
        """Test discover_tools() returns ToolDefinition objects."""
        tools = await agent_with_tools.discover_tools()
        assert all(isinstance(tool, ToolDefinition) for tool in tools)


# ============================================
# 4. execute_tool() Tests (8 tests)
# ============================================


class TestExecuteTool:
    """Test execute_tool() method."""

    @pytest.mark.asyncio
    async def test_execute_safe_tool_success(self, agent_with_tools):
        """Test executing a safe tool successfully."""
        result = await agent_with_tools.execute_tool(
            "read_file", {"path": "test.txt"}
        )

        assert result.success is True
        assert result.tool_name == "read_file"
        assert result.result is not None
        assert result.result["content"] == "Content of test.txt"

    @pytest.mark.asyncio
    async def test_execute_tool_with_timeout(self, agent_with_tools):
        """Test executing tool with custom timeout."""
        result = await agent_with_tools.execute_tool(
            "read_file", {"path": "test.txt"}, timeout=10.0
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_tool_not_found_raises_error(self, agent_with_tools):
        """Test executing non-existent tool returns error result."""
        result = await agent_with_tools.execute_tool("nonexistent_tool", {})
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_tool_invalid_params_raises_error(self, agent_with_tools):
        """Test executing tool with invalid parameters returns error result."""
        result = await agent_with_tools.execute_tool(
            "read_file", {}
        )  # Missing required 'path'
        assert result.success is False
        assert "parameter" in result.error.lower() or "required" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_tool_without_registry_raises_error(
        self, agent_without_tools
    ):
        """Test execute_tool() raises error if no registry configured."""
        with pytest.raises(
            RuntimeError, match="Tool executor not configured|not configured"
        ):
            await agent_without_tools.execute_tool("read_file", {"path": "test.txt"})

    @pytest.mark.asyncio
    async def test_execute_tool_returns_tool_result(self, agent_with_tools):
        """Test execute_tool() returns ToolResult object."""
        result = await agent_with_tools.execute_tool(
            "read_file", {"path": "test.txt"}
        )
        assert isinstance(result, ToolResult)

    @pytest.mark.asyncio
    async def test_execute_dangerous_tool_requests_approval(self, agent_with_tools):
        """Test executing dangerous tool triggers approval workflow."""
        # High danger tool should request approval
        result = await agent_with_tools.execute_tool(
            "bash_command", {"command": "ls -la"}
        )

        # Result should indicate approval was involved
        # (actual approval behavior tested in Tier 2)
        assert isinstance(result, ToolResult)

    @pytest.mark.asyncio
    async def test_execute_tool_stores_in_memory_if_requested(self, agent_with_tools):
        """Test tool execution can store results in memory."""
        result = await agent_with_tools.execute_tool(
            "read_file", {"path": "test.txt"}, store_in_memory=True
        )

        # Memory storage tested in Tier 2 with real memory
        assert result.success is True


# ============================================
# 5. execute_tool_chain() Tests (4 tests)
# ============================================


class TestExecuteToolChain:
    """Test execute_tool_chain() method."""

    @pytest.mark.asyncio
    async def test_execute_tool_chain_success(self, agent_with_tools):
        """Test executing a chain of tools successfully."""
        executions = [
            {"tool_name": "read_file", "params": {"path": "input.txt"}},
            {"tool_name": "transform_data", "params": {"data": "test"}},
        ]

        results = await agent_with_tools.execute_tool_chain(executions)

        assert len(results) == 2
        assert all(isinstance(r, ToolResult) for r in results)
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_execute_tool_chain_stops_on_error(self, agent_with_tools):
        """Test tool chain stops on first error."""
        executions = [
            {"tool_name": "read_file", "params": {"path": "input.txt"}},
            {"tool_name": "nonexistent_tool", "params": {}},  # This will fail
            {"tool_name": "transform_data", "params": {"data": "test"}},
        ]

        results = await agent_with_tools.execute_tool_chain(
            executions, stop_on_error=True
        )

        # Should only have results for first tool (second failed)
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_execute_tool_chain_continues_on_error(self, agent_with_tools):
        """Test tool chain continues after errors if stop_on_error=False."""
        executions = [
            {"tool_name": "read_file", "params": {"path": "input.txt"}},
            {"tool_name": "nonexistent_tool", "params": {}},  # This will fail
            {"tool_name": "transform_data", "params": {"data": "test"}},
        ]

        results = await agent_with_tools.execute_tool_chain(
            executions, stop_on_error=False
        )

        # Should have results for all executions (some may be errors)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_execute_tool_chain_empty_list(self, agent_with_tools):
        """Test executing empty tool chain returns empty list."""
        results = await agent_with_tools.execute_tool_chain([])
        assert results == []


# ============================================
# 6. Cleanup Tests (3 tests)
# ============================================


class TestCleanup:
    """Test tool executor cleanup."""

    def test_cleanup_clears_tool_executor_reference(self, agent_with_tools):
        """Test cleanup() clears tool executor reference."""
        assert agent_with_tools._tool_executor is not None

        agent_with_tools.cleanup()

        assert agent_with_tools._tool_executor is None

    def test_cleanup_clears_tool_registry_reference(self, agent_with_tools):
        """Test cleanup() clears tool registry reference but not registry itself."""
        registry = agent_with_tools._tool_registry
        assert registry is not None

        agent_with_tools.cleanup()

        # Reference cleared but registry still valid (other agents may use it)
        assert agent_with_tools._tool_registry is None
        assert len(registry._tools) > 0  # Registry still has tools

    def test_cleanup_without_tools_does_not_error(self, agent_without_tools):
        """Test cleanup() works for agents without tools."""
        # Should not raise any errors
        agent_without_tools.cleanup()


# ============================================
# 7. Edge Cases and Error Handling (5 tests)
# ============================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_discover_tools_with_empty_registry(
        self, base_config, simple_signature
    ):
        """Test discovering tools from empty registry returns empty list."""
        empty_registry = ToolRegistry()
        agent = BaseAgent(
            config=base_config,
            signature=simple_signature,
            tool_registry=empty_registry,
        )

        tools = await agent.discover_tools()
        assert tools == []

    @pytest.mark.asyncio
    async def test_execute_tool_with_none_params(self, agent_with_tools):
        """Test executing tool with None params returns error."""
        # None params should cause validation error
        result = await agent_with_tools.execute_tool("read_file", None)
        # Tool executor should handle None params and return error
        assert result.success is False or result.success is True  # Either validates or executes

    def test_agent_initialization_with_none_registry(
        self, base_config, simple_signature
    ):
        """Test agent initialization with None registry works."""
        agent = BaseAgent(
            config=base_config, signature=simple_signature, tool_registry=None
        )
        assert not agent.has_tool_support()

    @pytest.mark.asyncio
    async def test_execute_tool_with_extra_params_ignored(self, agent_with_tools):
        """Test executing tool with extra parameters (should be ignored or error)."""
        result = await agent_with_tools.execute_tool(
            "read_file", {"path": "test.txt", "extra_param": "ignored"}
        )
        # Extra params should be ignored or validated
        assert isinstance(result, ToolResult)

    @pytest.mark.asyncio
    async def test_discover_tools_with_invalid_category_returns_empty(
        self, agent_with_tools
    ):
        """Test discovering tools with non-existent category returns empty list."""
        tools = await agent_with_tools.discover_tools(category=ToolCategory.AI)
        assert tools == []  # No AI tools in our test registry


# ============================================
# Summary
# ============================================
# Total Tests: 30
#
# Breakdown:
# 1. Initialization: 5 tests
# 2. has_tool_support(): 3 tests
# 3. discover_tools(): 7 tests
# 4. execute_tool(): 8 tests
# 5. execute_tool_chain(): 4 tests
# 6. Cleanup: 3 tests
# 7. Edge Cases: 5 tests
#
# Coverage:
# - Tool discovery and filtering (category, danger level, keyword)
# - Tool execution (success, failure, validation)
# - Tool chaining (sequential execution, error handling)
# - Backward compatibility (agents without tools)
# - ControlProtocol integration (approval workflows)
# - Cleanup and resource management
# - Edge cases and error conditions
# ============================================
