"""
HTTP Tool Usage with BaseAgent

Demonstrates using HTTP tools for API interactions with approval workflows.

Key Concepts:
    - HTTP tools (GET, POST, PUT, DELETE)
    - Network tool category
    - Danger levels for HTTP operations
    - Approval workflows for data-modifying requests

Example Output:
    $ python examples/autonomy/tools/03_baseagent_http_tools.py

    Available HTTP tools: 4
    Making GET request...
    Response status: 200
    Content preview: <!doctype html>...
"""

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

# Add tests/utils to path for MockTransport (example only)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tests" / "utils"))

from kaizen.core.autonomy.control.protocol import ControlProtocol
from kaizen.core.base_agent import BaseAgent
from kaizen.signatures import InputField, OutputField, Signature
from kaizen.tools import ToolRegistry
from kaizen.tools.builtin import register_builtin_tools
from kaizen.tools.types import ToolCategory
from mock_transport import MockTransport  # Test utility for demonstration


class APIClientSignature(Signature):
    """Signature for API client agent."""

    request: str = InputField(description="API request to make")
    response: str = OutputField(description="API response")


@dataclass
class APIClientConfig:
    """Configuration for API client agent."""

    llm_provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.0


class APIClientAgent(BaseAgent):
    """Agent that makes API requests using HTTP tools."""

    def __init__(
        self, config: APIClientConfig, tool_registry: ToolRegistry, protocol: ControlProtocol
    ):
        super().__init__(
            config=config,
            signature=APIClientSignature(),
            tool_registry=tool_registry,
            control_protocol=protocol,
        )


async def approval_responder(transport: MockTransport):
    """Automatically approve all HTTP requests."""
    import anyio

    from kaizen.core.autonomy.control.types import ControlRequest, ControlResponse

    while True:
        await anyio.sleep(0.05)

        if transport.written_messages:
            request_data = transport.written_messages[-1]
            request = ControlRequest.from_json(request_data)

            response = ControlResponse(
                request_id=request.request_id,
                data={"approved": True, "reason": "Safe API endpoint"},
            )
            transport.queue_message(response.to_json())
            transport.written_messages.clear()


async def main():
    """Demonstrate HTTP tool usage with BaseAgent."""
    import anyio

    print("\n" + "=" * 80)
    print("BaseAgent HTTP Tools Example")
    print("=" * 80 + "\n")

    # Step 1: Setup (using MockTransport for demo)
    registry = ToolRegistry()
    register_builtin_tools(registry)

    transport = MockTransport()
    await transport.connect()
    protocol = ControlProtocol(transport)

    # Step 2: Create agent
    config = APIClientConfig()
    agent = APIClientAgent(config=config, tool_registry=registry, protocol=protocol)

    async with anyio.create_task_group() as tg:
        await protocol.start(tg)
        tg.start_soon(approval_responder, transport)

        try:
            # Step 3: Discover HTTP tools
            http_tools = await agent.discover_tools(category=ToolCategory.NETWORK)
            print(f"Available HTTP tools: {len(http_tools)}")
            for tool in http_tools:
                print(f"  - {tool.name}: {tool.description} [{tool.danger_level.value}]")
            print()

            # Step 4: Make GET request (LOW danger)
            print("Making GET request to example.com...")
            result = await agent.execute_tool(
                tool_name="http_get",
                params={"url": "https://example.com", "timeout": 10},
            )

            if result.success and result.approved:
                status = result.result["status_code"]
                body = result.result["body"]
                print(f"Response status: {status}")
                print(f"Content preview: {body[:100]}...\n")
            else:
                print(f"Request failed: {result.error}\n")

            # Step 5: Demonstrate tool discovery with filtering
            safe_tools = await agent.discover_tools(safe_only=True)
            print(f"Safe HTTP tools (auto-approved): {len(safe_tools)}")
            if safe_tools:
                for tool in safe_tools:
                    print(f"  - {tool.name}")
            else:
                print("  (No SAFE HTTP tools - all require approval)")
            print()

            # Step 6: Show danger level progression
            print("HTTP Tool Danger Levels:")
            print("  http_get    → LOW (read-only)")
            print("  http_post   → MEDIUM (create data)")
            print("  http_put    → MEDIUM (update data)")
            print("  http_delete → HIGH (delete data)")
            print()

            print("=" * 80)
            print("HTTP tools demonstration completed!")
            print("=" * 80 + "\n")

        finally:
            await protocol.stop()
            await transport.close()


if __name__ == "__main__":
    asyncio.run(main())
