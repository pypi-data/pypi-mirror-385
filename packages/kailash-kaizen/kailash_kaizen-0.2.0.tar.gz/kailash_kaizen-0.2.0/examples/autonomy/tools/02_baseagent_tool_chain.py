"""
Tool Chaining with BaseAgent

Demonstrates executing multiple tools in sequence with automatic approval workflows.

Key Concepts:
    - execute_tool_chain() for sequential operations
    - Mixed danger levels (SAFE, LOW, MEDIUM, HIGH)
    - Approval workflows for dangerous tools
    - Error handling in tool chains

Example Output:
    $ python examples/autonomy/tools/02_baseagent_tool_chain.py

    Executing tool chain with 4 operations...
    ✓ Tool 1: file_exists (SAFE) - auto-approved
    ✓ Tool 2: write_file (MEDIUM) - approved
    ✓ Tool 3: read_file (LOW) - approved
    ✓ Tool 4: delete_file (HIGH) - approved
"""

import asyncio
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# Add tests/utils to path for MockTransport (example only)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tests" / "utils"))

from kaizen.core.autonomy.control.protocol import ControlProtocol
from kaizen.core.base_agent import BaseAgent
from kaizen.signatures import InputField, OutputField, Signature
from kaizen.tools import ToolRegistry
from kaizen.tools.builtin import register_builtin_tools
from mock_transport import MockTransport  # Test utility for demonstration


class DataProcessorSignature(Signature):
    """Signature for data processing agent."""

    operation: str = InputField(description="Data processing operation")
    result: str = OutputField(description="Operation result")


@dataclass
class DataProcessorConfig:
    """Configuration for data processor agent."""

    llm_provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.0


class DataProcessorAgent(BaseAgent):
    """Agent that processes data using tool chains."""

    def __init__(
        self, config: DataProcessorConfig, tool_registry: ToolRegistry, protocol: ControlProtocol
    ):
        super().__init__(
            config=config,
            signature=DataProcessorSignature(),
            tool_registry=tool_registry,
            control_protocol=protocol,  # For approval workflows
        )


async def approval_responder(transport: MockTransport):
    """Automatically approve all tool requests."""
    import anyio

    from kaizen.core.autonomy.control.types import ControlRequest, ControlResponse

    while True:
        await anyio.sleep(0.05)

        if transport.written_messages:
            # Get latest request
            request_data = transport.written_messages[-1]
            request = ControlRequest.from_json(request_data)

            # Send approval
            response = ControlResponse(
                request_id=request.request_id,
                data={"approved": True, "reason": "Auto-approved for demo"},
            )
            transport.queue_message(response.to_json())

            # Clear for next request
            transport.written_messages.clear()


async def main():
    """Demonstrate tool chaining with BaseAgent."""
    import anyio

    print("\n" + "=" * 80)
    print("BaseAgent Tool Chain Example")
    print("=" * 80 + "\n")

    # Step 1: Setup tool registry
    registry = ToolRegistry()
    register_builtin_tools(registry)

    # Step 2: Setup control protocol for approvals (using MockTransport for demo)
    transport = MockTransport()
    await transport.connect()
    protocol = ControlProtocol(transport)

    # Step 3: Create temp file path
    temp_dir = tempfile.gettempdir()
    test_file = Path(temp_dir) / "chain_test.txt"

    # Step 4: Create agent with protocol
    config = DataProcessorConfig()
    agent = DataProcessorAgent(config=config, tool_registry=registry, protocol=protocol)

    async with anyio.create_task_group() as tg:
        # Start protocol and responder
        await protocol.start(tg)
        tg.start_soon(approval_responder, transport)

        try:
            # Step 5: Execute tool chain
            print("Executing tool chain with 4 operations...\n")

            chain = [
                # 1. Check if file exists (SAFE - auto-approved)
                {
                    "tool_name": "file_exists",
                    "params": {"path": str(test_file)},
                },
                # 2. Write file (MEDIUM - requires approval)
                {
                    "tool_name": "write_file",
                    "params": {
                        "path": str(test_file),
                        "content": "Tool chain demonstration",
                        "create_dirs": True,
                    },
                },
                # 3. Read file back (LOW - requires approval)
                {
                    "tool_name": "read_file",
                    "params": {"path": str(test_file)},
                },
                # 4. Delete file (HIGH - requires approval)
                {
                    "tool_name": "delete_file",
                    "params": {"path": str(test_file)},
                },
            ]

            results = await agent.execute_tool_chain(
                executions=chain,
                stop_on_error=True,  # Stop if any tool fails
            )

            # Step 6: Display results
            for i, result in enumerate(results, 1):
                tool_name = chain[i - 1]["tool_name"]
                tool = registry.get(tool_name)
                status = "✓" if result.success else "✗"
                approval = "auto-approved" if tool.danger_level.value == "safe" else "approved"

                print(f"{status} Tool {i}: {tool_name} ({tool.danger_level.value.upper()}) - {approval}")

                if not result.success:
                    print(f"  Error: {result.error}")

            print("\n" + "=" * 80)
            print("Tool chain executed successfully!")
            print("=" * 80 + "\n")

        finally:
            # Cleanup
            await protocol.stop()
            await transport.close()

            # Remove file if it still exists
            if test_file.exists():
                test_file.unlink()


if __name__ == "__main__":
    asyncio.run(main())
