"""
Integration Tests for ToolExecutor with Control Protocol (Tier 2)

Tests tool execution with REAL Control Protocol using MockTransport.
Verifies approval workflows work correctly with actual protocol logic.

Test Coverage:
    - Tool execution with approval (approved/denied)
    - Different danger levels (SAFE/MEDIUM/HIGH/CRITICAL)
    - Approval timeouts
    - Batch execution with approvals
    - Custom approval messages

Uses MockTransport (simpler than InMemoryTransport) for reliable testing.
"""

import pytest
import pytest_asyncio

from kaizen.core.autonomy.control.protocol import ControlProtocol, ControlResponse
from kaizen.core.autonomy.control.types import ControlRequest
from tests.utils.mock_transport import MockTransport
from kaizen.tools import (
    DangerLevel,
    ToolCategory,
    ToolExecutor,
    ToolParameter,
    ToolRegistry,
)


def create_approval_responder(transport: MockTransport, approved: bool, reason: str = ""):
    """
    Create a responder function that will respond to approval requests.

    Args:
        transport: MockTransport instance
        approved: Whether to approve or deny
        reason: Optional reason text

    Returns:
        Async function that responds to requests
    """
    async def responder():
        """Wait for and respond to approval requests."""
        import anyio

        # Wait for request to be written
        for _ in range(50):  # Max 5 seconds wait (50 * 0.1s)
            await anyio.sleep(0.1)
            if transport.written_messages:
                break

        if not transport.written_messages:
            return  # No request written

        # Get last written request
        last_request_json = transport.written_messages[-1]
        request = ControlRequest.from_json(last_request_json)

        # Create matching response
        response = ControlResponse(
            request_id=request.request_id,
            data={"approved": approved, "reason": reason},
        )

        # Queue response
        transport.queue_message(response.to_json())

    return responder


@pytest.fixture
def registry():
    """Create registry with test tools."""
    reg = ToolRegistry()

    # SAFE tool
    reg.register(
        name="uppercase",
        description="Convert text to uppercase",
        category=ToolCategory.DATA,
        danger_level=DangerLevel.SAFE,
        parameters=[ToolParameter("text", str, "Input text")],
        returns={"result": "str"},
        executor=lambda params: {"result": params["text"].upper()},
    )

    # MEDIUM danger tool
    reg.register(
        name="write_file",
        description="Write to a file",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.MEDIUM,
        parameters=[
            ToolParameter("path", str, "File path"),
            ToolParameter("content", str, "File content"),
        ],
        returns={"written": "bool"},
        executor=lambda params: {"written": True},
        approval_message_template="Write to file: {path}",
    )

    # HIGH danger tool
    reg.register(
        name="delete_file",
        description="Delete a file",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.HIGH,
        parameters=[ToolParameter("path", str, "File path")],
        returns={"deleted": "bool"},
        executor=lambda params: {"deleted": True},
        approval_message_template="Delete file: {path}",
    )

    # CRITICAL danger tool
    reg.register(
        name="format_disk",
        description="Format entire disk",
        category=ToolCategory.SYSTEM,
        danger_level=DangerLevel.CRITICAL,
        parameters=[ToolParameter("disk", str, "Disk path")],
        returns={"formatted": "bool"},
        executor=lambda params: {"formatted": True},
        approval_message_template="⚠️ CRITICAL: Format disk {disk}",
    )

    return reg


@pytest_asyncio.fixture
async def protocol_and_transport():
    """Create Control Protocol with MockTransport."""
    transport = MockTransport()
    await transport.connect()

    protocol = ControlProtocol(transport)

    yield protocol, transport

    # Cleanup
    await protocol.stop()
    await transport.close()


@pytest.mark.asyncio
async def test_safe_tool_execution_with_protocol(registry, protocol_and_transport):
    """Test SAFE tool execution (should not require approval even with protocol)."""
    protocol, transport = protocol_and_transport
    executor = ToolExecutor(registry=registry, control_protocol=protocol)

    # Execute SAFE tool (no approval needed)
    result = await executor.execute("uppercase", {"text": "hello"})

    assert result.success is True
    assert result.result == {"result": "HELLO"}
    assert result.approved is True  # Auto-approved (SAFE)


@pytest.mark.asyncio
async def test_medium_danger_tool_approved(registry, protocol_and_transport):
    """Test MEDIUM danger tool with user approval."""
    import anyio

    protocol, transport = protocol_and_transport
    executor = ToolExecutor(registry=registry, control_protocol=protocol)

    # Start protocol and run test
    async with anyio.create_task_group() as tg:
        await protocol.start(tg)

        # Create responder
        responder = create_approval_responder(transport, approved=True, reason="Approved by test")
        tg.start_soon(responder)

        # Execute MEDIUM danger tool
        result = await executor.execute(
            "write_file", {"path": "/tmp/test.txt", "content": "hello"}
        )

        # Stop protocol
        await protocol.stop()

    assert result.success is True
    assert result.result == {"written": True}
    assert result.approved is True


@pytest.mark.asyncio
async def test_high_danger_tool_approved(registry, protocol_and_transport):
    """Test HIGH danger tool with user approval."""
    import anyio

    protocol, transport = protocol_and_transport
    executor = ToolExecutor(registry=registry, control_protocol=protocol)

    # Start protocol and run test
    async with anyio.create_task_group() as tg:
        await protocol.start(tg)

        # Create responder
        responder = create_approval_responder(transport, approved=True, reason="Approved by test")
        tg.start_soon(responder)

        # Execute HIGH danger tool
        result = await executor.execute("delete_file", {"path": "/tmp/test.txt"})

        # Stop protocol
        await protocol.stop()

    assert result.success is True
    assert result.result == {"deleted": True}
    assert result.approved is True


@pytest.mark.asyncio
async def test_critical_danger_tool_approved(registry, protocol_and_transport):
    """Test CRITICAL danger tool with user approval."""
    import anyio

    protocol, transport = protocol_and_transport
    executor = ToolExecutor(registry=registry, control_protocol=protocol)

    # Start protocol and run test
    async with anyio.create_task_group() as tg:
        await protocol.start(tg)

        # Create responder
        responder = create_approval_responder(transport, approved=True, reason="Approved by test")
        tg.start_soon(responder)

        # Execute CRITICAL danger tool
        result = await executor.execute("format_disk", {"disk": "/dev/sda"})

        # Stop protocol
        await protocol.stop()

    assert result.success is True
    assert result.result == {"formatted": True}
    assert result.approved is True


@pytest.mark.asyncio
async def test_high_danger_tool_denied(registry, protocol_and_transport):
    """Test HIGH danger tool with user denial."""
    import anyio

    protocol, transport = protocol_and_transport
    executor = ToolExecutor(registry=registry, control_protocol=protocol)

    # Start protocol and run test
    async with anyio.create_task_group() as tg:
        await protocol.start(tg)

        # Create responder
        responder = create_approval_responder(transport, approved=False, reason="Denied by test")
        tg.start_soon(responder)

        # Execute HIGH danger tool
        result = await executor.execute("delete_file", {"path": "/tmp/test.txt"})

        # Stop protocol
        await protocol.stop()

    assert result.success is False
    assert result.approved is False
    assert "denied" in result.error.lower() or "approval" in result.error.lower()
    assert result.result is None


@pytest.mark.asyncio
async def test_approval_timeout(registry, protocol_and_transport):
    """Test approval request timeout (no response queued)."""
    import anyio

    protocol, transport = protocol_and_transport
    executor = ToolExecutor(registry=registry, control_protocol=protocol, timeout=0.5)

    # Start protocol and run test (no responder - will timeout)
    async with anyio.create_task_group() as tg:
        await protocol.start(tg)

        # Don't create any responder - will timeout

        # Execute HIGH danger tool (will timeout)
        result = await executor.execute("delete_file", {"path": "/tmp/test.txt"})

        # Stop protocol
        await protocol.stop()

    assert result.success is False
    assert result.approved is False
    assert "no response received" in result.error.lower()


@pytest.mark.asyncio
async def test_batch_execution_with_mixed_danger_levels(registry, protocol_and_transport):
    """Test batch execution with multiple danger levels."""
    import anyio

    protocol, transport = protocol_and_transport
    executor = ToolExecutor(registry=registry, control_protocol=protocol)

    # Create a multi-request responder that handles 2 sequential requests
    async def multi_responder():
        """Respond to multiple approval requests in order."""
        for i in range(2):  # 2 approvals needed (MEDIUM + HIGH)
            # Wait for request
            for _ in range(50):
                await anyio.sleep(0.1)
                if len(transport.written_messages) > i:
                    break

            if len(transport.written_messages) <= i:
                continue

            # Get the i-th request
            request_json = transport.written_messages[i]
            request = ControlRequest.from_json(request_json)

            # Create approval response
            response = ControlResponse(
                request_id=request.request_id,
                data={"approved": True, "reason": f"Approved {i+1}"},
            )

            # Queue response
            transport.queue_message(response.to_json())

    # Start protocol and run test
    async with anyio.create_task_group() as tg:
        await protocol.start(tg)

        # Start multi-responder
        tg.start_soon(multi_responder)

        executions = [
            {"tool_name": "uppercase", "params": {"text": "hello"}},  # SAFE
            {
                "tool_name": "write_file",
                "params": {"path": "/tmp/a.txt", "content": "test"},
            },  # MEDIUM
            {"tool_name": "delete_file", "params": {"path": "/tmp/b.txt"}},  # HIGH
        ]

        results = await executor.execute_batch(executions)

        # Stop protocol
        await protocol.stop()

    assert len(results) == 3

    # SAFE tool (no approval needed)
    assert results[0].success is True
    assert results[0].approved is True

    # MEDIUM tool (approved)
    assert results[1].success is True
    assert results[1].approved is True

    # HIGH tool (approved)
    assert results[2].success is True
    assert results[2].approved is True


@pytest.mark.asyncio
async def test_batch_execution_with_some_denied(registry, protocol_and_transport):
    """Test batch execution where some tools are denied."""
    import anyio

    protocol, transport = protocol_and_transport
    executor = ToolExecutor(registry=registry, control_protocol=protocol)

    # Create a multi-request responder that approves first, denies second
    async def multi_responder():
        """Respond to multiple approval requests in order."""
        approvals = [True, False]  # Approve first, deny second
        reasons = ["Approved", "Denied"]

        for i in range(2):
            # Wait for request
            for _ in range(50):
                await anyio.sleep(0.1)
                if len(transport.written_messages) > i:
                    break

            if len(transport.written_messages) <= i:
                continue

            # Get the i-th request
            request_json = transport.written_messages[i]
            request = ControlRequest.from_json(request_json)

            # Create response
            response = ControlResponse(
                request_id=request.request_id,
                data={"approved": approvals[i], "reason": reasons[i]},
            )

            # Queue response
            transport.queue_message(response.to_json())

    # Start protocol and run test
    async with anyio.create_task_group() as tg:
        await protocol.start(tg)

        # Start multi-responder
        tg.start_soon(multi_responder)

        executions = [
            {
                "tool_name": "write_file",
                "params": {"path": "/tmp/a.txt", "content": "test"},
            },  # MEDIUM (approved)
            {"tool_name": "delete_file", "params": {"path": "/tmp/b.txt"}},  # HIGH (denied)
        ]

        results = await executor.execute_batch(executions)

        # Stop protocol
        await protocol.stop()

    assert len(results) == 2

    # First tool (approved)
    assert results[0].success is True
    assert results[0].approved is True

    # Second tool (denied)
    assert results[1].success is False
    assert results[1].approved is False


@pytest.mark.asyncio
async def test_custom_approval_message(registry, protocol_and_transport):
    """Test tool with custom approval message template."""
    import anyio

    protocol, transport = protocol_and_transport
    executor = ToolExecutor(registry=registry, control_protocol=protocol)

    # Start protocol and run test
    async with anyio.create_task_group() as tg:
        await protocol.start(tg)

        # Create responder
        responder = create_approval_responder(transport, approved=True, reason="Approved")
        tg.start_soon(responder)

        # Execute tool with custom approval message
        result = await executor.execute("delete_file", {"path": "/tmp/test.txt"})

        # Stop protocol
        await protocol.stop()

    assert result.success is True

    # Verify custom message was used (check written messages)
    assert len(transport.written_messages) > 0
    last_request_json = transport.written_messages[-1]
    request = ControlRequest.from_json(last_request_json)

    # Check approval message contains custom template
    assert "Delete file: /tmp/test.txt" in request.data.get("message", "")
