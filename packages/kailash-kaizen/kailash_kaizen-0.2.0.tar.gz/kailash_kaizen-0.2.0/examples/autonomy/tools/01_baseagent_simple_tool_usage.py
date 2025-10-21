"""
Simple Tool Usage with BaseAgent

Demonstrates basic tool calling with BaseAgent using a single file operation tool.

Key Concepts:
    - BaseAgent initialization with tool_registry
    - Tool discovery and filtering
    - Single tool execution
    - Result handling with approval workflow

Example Output:
    $ python examples/autonomy/tools/01_baseagent_simple_tool_usage.py

    Available file tools: 5
    Reading file: /tmp/test_data.txt
    File content: Hello from BaseAgent tool integration!
    File size: 42 bytes
"""

import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path

from kaizen.core.base_agent import BaseAgent
from kaizen.signatures import InputField, OutputField, Signature
from kaizen.tools import ToolRegistry
from kaizen.tools.builtin import register_builtin_tools
from kaizen.tools.types import ToolCategory


class FileProcessorSignature(Signature):
    """Signature for file processing agent."""

    task: str = InputField(description="File processing task to perform")
    result: str = OutputField(description="Processing result")


@dataclass
class FileProcessorConfig:
    """Configuration for file processor agent."""

    llm_provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.0


class FileProcessorAgent(BaseAgent):
    """Agent that processes files using tool calling."""

    def __init__(self, config: FileProcessorConfig, tool_registry: ToolRegistry):
        super().__init__(
            config=config,
            signature=FileProcessorSignature(),
            tool_registry=tool_registry,  # Enable tool calling
        )


async def main():
    """Demonstrate simple tool usage with BaseAgent."""
    print("\n" + "=" * 80)
    print("BaseAgent Simple Tool Usage Example")
    print("=" * 80 + "\n")

    # Step 1: Create tool registry with builtin tools
    registry = ToolRegistry()
    register_builtin_tools(registry)

    # Step 2: Create agent with tool support
    config = FileProcessorConfig()
    agent = FileProcessorAgent(config=config, tool_registry=registry)

    # Step 3: Verify tool support is enabled
    assert agent.has_tool_support(), "Tool support should be enabled"
    print("✓ Tool support enabled\n")

    # Step 4: Discover available file tools
    file_tools = await agent.discover_tools(category=ToolCategory.SYSTEM)
    print(f"Available file tools: {len(file_tools)}")
    for tool in file_tools[:3]:  # Show first 3
        print(f"  - {tool.name}: {tool.description} [{tool.danger_level.value}]")
    print()

    # Step 5: Create test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        test_content = "Hello from BaseAgent tool integration!"
        f.write(test_content)
        test_file = f.name

    try:
        # Step 6: Use tool to read file
        print(f"Reading file: {test_file}")
        result = await agent.execute_tool(
            tool_name="read_file",
            params={"path": test_file},
        )

        # Step 7: Handle result
        if result.success and result.approved:
            print(f"File content: {result.result['content']}")
            print(f"File size: {result.result['size']} bytes\n")
        else:
            print(f"Tool execution failed: {result.error}\n")

        # Step 8: Demonstrate safe tool (auto-approved)
        exists_result = await agent.execute_tool(
            tool_name="file_exists",
            params={"path": test_file},
        )

        if exists_result.success:
            print(f"File exists check:")
            print(f"  exists: {exists_result.result['exists']}")
            print(f"  is_file: {exists_result.result['is_file']}")
            print(f"  Auto-approved (SAFE tool): {exists_result.approved}\n")

    finally:
        # Cleanup
        Path(test_file).unlink()
        print("=" * 80)
        print("Example completed successfully!")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
