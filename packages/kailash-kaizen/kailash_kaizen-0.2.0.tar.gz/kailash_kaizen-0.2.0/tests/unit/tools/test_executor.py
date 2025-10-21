"""
Unit Tests for ToolExecutor (Tier 1)

Tests tool execution without real Control Protocol integration.
Uses mocked or simple tools to verify basic functionality.

Test Coverage:
    - Tool execution (success/failure)
    - Parameter validation
    - Error handling
    - Batch execution
    - Control protocol management
    - Approval workflow logic
"""

import pytest

from kaizen.tools import (
    DangerLevel,
    ToolCategory,
    ToolExecutor,
    ToolParameter,
    ToolRegistry,
)


@pytest.fixture
def registry():
    """Create a fresh registry for each test."""
    return ToolRegistry()


@pytest.fixture
def executor(registry):
    """Create executor without control protocol (autonomous mode)."""
    return ToolExecutor(registry=registry)


@pytest.fixture
def registry_with_tools(registry):
    """Registry with sample tools registered."""
    # SAFE tool
    registry.register(
        name="uppercase",
        description="Convert text to uppercase",
        category=ToolCategory.DATA,
        danger_level=DangerLevel.SAFE,
        parameters=[ToolParameter("text", str, "Input text")],
        returns={"result": "str"},
        executor=lambda params: {"result": params["text"].upper()},
    )

    # LOW danger tool
    registry.register(
        name="read_file",
        description="Read file contents",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.LOW,
        parameters=[ToolParameter("path", str, "File path")],
        returns={"content": "str"},
        executor=lambda params: {"content": f"Contents of {params['path']}"},
    )

    # HIGH danger tool
    registry.register(
        name="delete_file",
        description="Delete a file",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.HIGH,
        parameters=[ToolParameter("path", str, "File path")],
        returns={"deleted": "bool"},
        executor=lambda params: {"deleted": True},
    )

    # Tool that raises exception
    def error_tool(params):
        raise ValueError("Simulated error")

    registry.register(
        name="error_tool",
        description="Tool that always fails",
        category=ToolCategory.CUSTOM,
        danger_level=DangerLevel.SAFE,
        parameters=[],
        returns={},
        executor=error_tool,
    )

    return registry


@pytest.mark.asyncio
async def test_executor_initialization():
    """Test ToolExecutor initialization."""
    registry = ToolRegistry()
    executor = ToolExecutor(registry=registry)

    assert executor.registry is registry
    assert executor.control_protocol is None
    assert executor.auto_approve_safe is True
    assert executor.timeout == 30.0


@pytest.mark.asyncio
async def test_executor_initialization_with_custom_params():
    """Test ToolExecutor initialization with custom parameters."""
    registry = ToolRegistry()
    executor = ToolExecutor(
        registry=registry,
        auto_approve_safe=False,
        timeout=10.0,
    )

    assert executor.auto_approve_safe is False
    assert executor.timeout == 10.0


@pytest.mark.asyncio
async def test_execute_tool_not_found():
    """Test execution with non-existent tool."""
    registry = ToolRegistry()
    executor = ToolExecutor(registry=registry)

    result = await executor.execute("nonexistent", {})

    assert result.success is False
    assert result.tool_name == "nonexistent"
    assert "not found in registry" in result.error
    assert result.error_type == "ToolNotFoundError"


@pytest.mark.asyncio
async def test_execute_safe_tool_success(registry_with_tools):
    """Test successful execution of SAFE tool."""
    executor = ToolExecutor(registry=registry_with_tools)

    result = await executor.execute("uppercase", {"text": "hello"})

    assert result.success is True
    assert result.tool_name == "uppercase"
    assert result.result == {"result": "HELLO"}
    assert result.error is None
    assert result.execution_time_ms is not None
    assert result.execution_time_ms > 0
    assert result.approved is True  # Auto-approved (SAFE)


@pytest.mark.asyncio
async def test_execute_low_danger_tool_autonomous_mode(registry_with_tools):
    """Test LOW danger tool in autonomous mode (no control protocol)."""
    executor = ToolExecutor(registry=registry_with_tools)

    result = await executor.execute("read_file", {"path": "/tmp/test.txt"})

    assert result.success is True
    assert result.tool_name == "read_file"
    assert result.result == {"content": "Contents of /tmp/test.txt"}
    assert result.approved is True  # Auto-approved in autonomous mode


@pytest.mark.asyncio
async def test_execute_high_danger_tool_autonomous_mode(registry_with_tools):
    """Test HIGH danger tool in autonomous mode (no control protocol)."""
    executor = ToolExecutor(registry=registry_with_tools)

    result = await executor.execute("delete_file", {"path": "/tmp/test.txt"})

    # In autonomous mode (no control protocol), even HIGH danger tools are auto-approved
    assert result.success is True
    assert result.tool_name == "delete_file"
    assert result.result == {"deleted": True}
    assert result.approved is True


@pytest.mark.asyncio
async def test_execute_tool_with_exception(registry_with_tools):
    """Test tool that raises exception."""
    executor = ToolExecutor(registry=registry_with_tools)

    result = await executor.execute("error_tool", {})

    assert result.success is False
    assert result.tool_name == "error_tool"
    assert result.error == "Simulated error"
    assert result.error_type == "ValueError"
    assert result.result is None
    assert result.execution_time_ms is not None


@pytest.mark.asyncio
async def test_execute_tool_with_invalid_parameters(registry_with_tools):
    """Test tool execution with invalid parameters."""
    executor = ToolExecutor(registry=registry_with_tools)

    # Missing required parameter
    result = await executor.execute("uppercase", {})

    assert result.success is False
    assert result.tool_name == "uppercase"
    assert "Required parameter 'text' missing" in result.error
    assert result.error_type in ["ValueError", "TypeError"]


@pytest.mark.asyncio
async def test_execute_tool_with_unknown_parameter(registry_with_tools):
    """Test tool execution with unknown parameter."""
    executor = ToolExecutor(registry=registry_with_tools)

    result = await executor.execute(
        "uppercase", {"text": "hello", "unknown_param": "value"}
    )

    # Should fail due to unknown parameter
    assert result.success is False
    assert "Unknown parameter 'unknown_param'" in result.error


@pytest.mark.asyncio
async def test_execute_batch_success(registry_with_tools):
    """Test batch execution with multiple tools."""
    executor = ToolExecutor(registry=registry_with_tools)

    executions = [
        {"tool_name": "uppercase", "params": {"text": "hello"}},
        {"tool_name": "uppercase", "params": {"text": "world"}},
        {"tool_name": "read_file", "params": {"path": "/tmp/test.txt"}},
    ]

    results = await executor.execute_batch(executions)

    assert len(results) == 3

    # First execution
    assert results[0].success is True
    assert results[0].tool_name == "uppercase"
    assert results[0].result == {"result": "HELLO"}

    # Second execution
    assert results[1].success is True
    assert results[1].tool_name == "uppercase"
    assert results[1].result == {"result": "WORLD"}

    # Third execution
    assert results[2].success is True
    assert results[2].tool_name == "read_file"
    assert results[2].result == {"content": "Contents of /tmp/test.txt"}


@pytest.mark.asyncio
async def test_execute_batch_with_failures(registry_with_tools):
    """Test batch execution with some failures."""
    executor = ToolExecutor(registry=registry_with_tools)

    executions = [
        {"tool_name": "uppercase", "params": {"text": "hello"}},
        {"tool_name": "error_tool", "params": {}},
        {"tool_name": "nonexistent", "params": {}},
    ]

    results = await executor.execute_batch(executions)

    assert len(results) == 3

    # First execution (success)
    assert results[0].success is True
    assert results[0].tool_name == "uppercase"

    # Second execution (tool error)
    assert results[1].success is False
    assert results[1].tool_name == "error_tool"
    assert "Simulated error" in results[1].error

    # Third execution (tool not found)
    assert results[2].success is False
    assert results[2].tool_name == "nonexistent"
    assert "not found in registry" in results[2].error


@pytest.mark.asyncio
async def test_execute_batch_with_invalid_execution(registry_with_tools):
    """Test batch execution with invalid execution (missing tool_name)."""
    executor = ToolExecutor(registry=registry_with_tools)

    executions = [
        {"params": {"text": "hello"}},  # Missing tool_name
    ]

    results = await executor.execute_batch(executions)

    assert len(results) == 1
    assert results[0].success is False
    assert results[0].tool_name == "unknown"
    assert "Missing 'tool_name'" in results[0].error


@pytest.mark.asyncio
async def test_control_protocol_management():
    """Test control protocol getter/setter methods."""
    from unittest.mock import MagicMock

    registry = ToolRegistry()
    executor = ToolExecutor(registry=registry)

    # Initially no protocol
    assert executor.has_control_protocol() is False

    # Set protocol
    mock_protocol = MagicMock()
    executor.set_control_protocol(mock_protocol)

    assert executor.has_control_protocol() is True
    assert executor.control_protocol is mock_protocol


@pytest.mark.asyncio
async def test_get_registry():
    """Test get_registry method."""
    registry = ToolRegistry()
    executor = ToolExecutor(registry=registry)

    retrieved_registry = executor.get_registry()

    assert retrieved_registry is registry


@pytest.mark.asyncio
async def test_execution_timing(registry_with_tools):
    """Test that execution time is measured."""
    executor = ToolExecutor(registry=registry_with_tools)

    result = await executor.execute("uppercase", {"text": "hello"})

    assert result.execution_time_ms is not None
    assert result.execution_time_ms > 0
    assert result.execution_time_ms < 1000  # Should be very fast


@pytest.mark.asyncio
async def test_tool_result_to_dict(registry_with_tools):
    """Test ToolResult to_dict method."""
    executor = ToolExecutor(registry=registry_with_tools)

    result = await executor.execute("uppercase", {"text": "hello"})

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert result_dict["tool_name"] == "uppercase"
    assert result_dict["success"] is True
    assert result_dict["result"] == {"result": "HELLO"}
    assert "execution_time_ms" in result_dict


@pytest.mark.asyncio
async def test_auto_approve_safe_disabled(registry_with_tools):
    """Test with auto_approve_safe disabled (should still work without control protocol)."""
    executor = ToolExecutor(registry=registry_with_tools, auto_approve_safe=False)

    # Even with auto_approve_safe=False, autonomous mode (no control protocol) approves all
    result = await executor.execute("uppercase", {"text": "hello"})

    assert result.success is True
    assert result.result == {"result": "HELLO"}
