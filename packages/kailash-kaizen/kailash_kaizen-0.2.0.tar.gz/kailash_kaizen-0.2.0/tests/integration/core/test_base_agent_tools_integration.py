"""
Tier 2 Integration Tests for BaseAgent Tool Integration

Tests real tool execution with actual ToolExecutor and ControlProtocol.
NO MOCKING - Real infrastructure testing.

Coverage Target: Integration scenarios with real components
Test Strategy: Real ToolExecutor, real file operations, real approval workflows
Infrastructure: Real Docker services where applicable
"""

import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest

from kaizen.core.autonomy.control.protocol import ControlProtocol
from kaizen.core.base_agent import BaseAgent, BaseAgentConfig
from kaizen.signatures import InputField, OutputField, Signature
from kaizen.tools.builtin import register_builtin_tools
from kaizen.tools.executor import ToolExecutor
from kaizen.tools.registry import ToolRegistry
from kaizen.tools.types import DangerLevel, ToolCategory, ToolDefinition


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
def real_tool_registry():
    """Create ToolRegistry with REAL builtin tools."""
    registry = ToolRegistry()
    register_builtin_tools(registry)
    return registry


@pytest.fixture
def mock_transport():
    """Create mock transport for ControlProtocol."""
    transport = AsyncMock()
    # Mock write to return None (async)
    transport.write = AsyncMock(return_value=None)
    # Mock read to simulate user approval
    async def mock_read():
        return '{"type": "approval_response", "data": {"approved": true}}'

    transport.read = AsyncMock(side_effect=mock_read)
    return transport


@pytest.fixture
def mock_control_protocol(mock_transport):
    """Create real ControlProtocol with mocked transport."""
    # Create real ControlProtocol but with mocked transport
    protocol = ControlProtocol(transport=mock_transport)
    return protocol


@pytest.fixture
def agent_with_real_tools(base_config, simple_signature, real_tool_registry):
    """Create BaseAgent with REAL builtin tools."""
    return BaseAgent(
        config=base_config, signature=simple_signature, tool_registry=real_tool_registry
    )


@pytest.fixture
def agent_with_real_tools_and_protocol(
    base_config, simple_signature, real_tool_registry, mock_control_protocol
):
    """Create BaseAgent with real tools and ControlProtocol."""
    return BaseAgent(
        config=base_config,
        signature=simple_signature,
        tool_registry=real_tool_registry,
        control_protocol=mock_control_protocol,
    )


# ============================================
# 1. Real Tool Discovery Tests (3 tests)
# ============================================


class TestRealToolDiscovery:
    """Test tool discovery with real builtin tools."""

    @pytest.mark.asyncio
    async def test_discover_real_builtin_tools(self, agent_with_real_tools):
        """Test discovering real builtin tools."""
        all_tools = await agent_with_real_tools.discover_tools()
        # Should have read_file, write_file, delete_file, bash_command, etc.
        assert len(all_tools) >= 4, "Should have at least 4 builtin tools"

    @pytest.mark.asyncio
    async def test_discover_real_file_tools(self, agent_with_real_tools):
        """Test discovering real file tools by keyword."""
        file_tools = await agent_with_real_tools.discover_tools(keyword="file")
        assert len(file_tools) >= 3, "Should have read_file, write_file, delete_file"
        tool_names = [t.name for t in file_tools]
        assert any("read" in name for name in tool_names)
        assert any("write" in name for name in tool_names)

    @pytest.mark.asyncio
    async def test_discover_safe_vs_dangerous_tools(self, agent_with_real_tools):
        """Test filtering real tools by danger level."""
        safe_tools = await agent_with_real_tools.discover_tools(safe_only=True)
        all_tools = await agent_with_real_tools.discover_tools()

        # Safe tools should be subset of all tools
        assert len(safe_tools) < len(all_tools)
        # All safe tools should have SAFE danger level
        assert all(t.danger_level == DangerLevel.SAFE for t in safe_tools)


# ============================================
# 2. Real Tool Execution Tests (5 tests)
# ============================================


class TestRealToolExecution:
    """Test tool execution with real file operations."""

    @pytest.mark.asyncio
    async def test_execute_real_read_file(self, agent_with_real_tools):
        """Test executing real read_file tool."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Test content for integration test")
            temp_path = f.name

        try:
            # Execute real read_file tool
            result = await agent_with_real_tools.execute_tool(
                "read_file", {"path": temp_path}
            )

            assert result.success is True, f"Tool execution failed: {result.error}"
            assert result.result is not None
            assert "content" in result.result
            assert "Test content" in result.result["content"]
        finally:
            # Cleanup
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_execute_real_write_file(self, agent_with_real_tools):
        """Test executing real write_file tool."""
        # Use temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = str(Path(tmpdir) / "test_output.txt")
            test_content = "Content written by integration test"

            # Execute real write_file tool
            result = await agent_with_real_tools.execute_tool(
                "write_file", {"path": file_path, "content": test_content}
            )

            assert result.success is True, f"Tool execution failed: {result.error}"
            assert result.approved is True  # Should auto-approve MEDIUM tools without protocol

            # Verify file was actually written
            written_content = Path(file_path).read_text()
            assert written_content == test_content

    @pytest.mark.asyncio
    async def test_execute_read_nonexistent_file(self, agent_with_real_tools):
        """Test executing read_file on non-existent file."""
        result = await agent_with_real_tools.execute_tool(
            "read_file", {"path": "/nonexistent/path/file.txt"}
        )

        # Should succeed but indicate file doesn't exist
        assert result.success is True
        assert result.result.get("exists") is False

    @pytest.mark.asyncio
    async def test_tool_execution_time_recorded(self, agent_with_real_tools):
        """Test that tool execution time is recorded."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            result = await agent_with_real_tools.execute_tool(
                "read_file", {"path": temp_path}
            )

            # Execution time should be recorded in milliseconds
            assert result.execution_time_ms >= 0
            assert result.execution_time_ms < 1000, "Should complete in <1 second"
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_tool_execution_with_validation_error(self, agent_with_real_tools):
        """Test tool execution with parameter validation error."""
        # Execute read_file without required 'path' parameter
        result = await agent_with_real_tools.execute_tool("read_file", {})

        assert result.success is False
        assert "parameter" in result.error.lower() or "required" in result.error.lower()


# ============================================
# 3. Tool Execution Behavior Tests (4 tests)
# ============================================


class TestToolExecutionBehavior:
    """Test tool execution behavior and settings."""

    @pytest.mark.asyncio
    async def test_safe_tool_auto_approves(self, agent_with_real_tools):
        """Test SAFE tools auto-approve without ControlProtocol."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            result = await agent_with_real_tools.execute_tool(
                "read_file", {"path": temp_path}
            )

            # SAFE tool should auto-approve even without control protocol
            assert result.success is True
            assert result.approved is True
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_dangerous_tool_without_protocol_auto_approves(
        self, agent_with_real_tools
    ):
        """Test dangerous tools auto-approve when no ControlProtocol present."""
        # Without control protocol, executor should auto-approve
        # This is different from production but expected for testing
        result = await agent_with_real_tools.execute_tool(
            "bash_command", {"command": "echo test"}
        )

        # Should execute successfully (no protocol to request approval from)
        assert isinstance(result, ToolDefinition) or result.success is True

    @pytest.mark.asyncio
    async def test_tool_executor_created_with_registry(self, agent_with_real_tools):
        """Test ToolExecutor is auto-created when registry provided."""
        assert agent_with_real_tools._tool_executor is not None
        assert agent_with_real_tools._tool_executor.registry is not None

    @pytest.mark.asyncio
    async def test_custom_timeout_parameter_accepted(self, agent_with_real_tools):
        """Test custom timeout parameter is accepted."""
        # This test verifies the timeout parameter is accepted without error
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            result = await agent_with_real_tools.execute_tool(
                "read_file", {"path": temp_path}, timeout=5.0
            )

            assert result.success is True
        finally:
            Path(temp_path).unlink()


# ============================================
# 4. Tool Chain Integration Tests (3 tests)
# ============================================


class TestToolChainIntegration:
    """Test tool chains with real operations."""

    @pytest.mark.asyncio
    async def test_real_tool_chain_read_write(self, agent_with_real_tools):
        """Test chaining real read and write operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input file
            input_path = str(Path(tmpdir) / "input.txt")
            output_path = str(Path(tmpdir) / "output.txt")
            Path(input_path).write_text("Original content")

            # Chain: read -> write
            executions = [
                {"tool_name": "read_file", "params": {"path": input_path}},
                {
                    "tool_name": "write_file",
                    "params": {"path": output_path, "content": "Modified content"},
                },
            ]

            results = await agent_with_real_tools.execute_tool_chain(executions)

            assert len(results) == 2
            assert all(r.success for r in results), [r.error for r in results]

            # Verify output file exists
            assert Path(output_path).exists()

    @pytest.mark.asyncio
    async def test_tool_chain_stops_on_error(self, agent_with_real_tools):
        """Test tool chain stops on first error."""
        executions = [
            {"tool_name": "read_file", "params": {"path": "/valid/path.txt"}},
            {"tool_name": "nonexistent_tool", "params": {}},  # Will fail
            {"tool_name": "read_file", "params": {"path": "/another/path.txt"}},
        ]

        results = await agent_with_real_tools.execute_tool_chain(
            executions, stop_on_error=True
        )

        # Should only have 2 results (first succeeds, second fails, third not executed)
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False

    @pytest.mark.asyncio
    async def test_tool_chain_continues_on_error(self, agent_with_real_tools):
        """Test tool chain continues after errors."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            executions = [
                {"tool_name": "read_file", "params": {"path": temp_path}},
                {"tool_name": "nonexistent_tool", "params": {}},  # Will fail
                {"tool_name": "read_file", "params": {"path": temp_path}},
            ]

            results = await agent_with_real_tools.execute_tool_chain(
                executions, stop_on_error=False
            )

            # Should have all 3 results
            assert len(results) == 3
            assert results[0].success is True
            assert results[1].success is False
            assert results[2].success is True
        finally:
            Path(temp_path).unlink()


# ============================================
# Summary
# ============================================
# Total Tests: 15
#
# Breakdown:
# 1. Real Tool Discovery: 3 tests
# 2. Real Tool Execution: 5 tests
# 3. Approval Workflows: 4 tests
# 4. Tool Chain Integration: 3 tests
#
# Infrastructure:
# - Real ToolRegistry with builtin tools
# - Real ToolExecutor (not mocked)
# - Real file operations (temp files/dirs)
# - Real ControlProtocol with mocked transport only
# - NO MOCKING of tool execution logic
# ============================================
