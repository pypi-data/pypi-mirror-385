# Control Protocol API Reference

**Version:** 1.0.0
**Status:** Production Ready
**Architecture:** ADR-011

---

## Overview

The Control Protocol enables bidirectional communication between AI agents and users during execution. Agents can ask questions, request approvals, and report progress—creating truly interactive AI workflows.

**Core Benefits:**
- **Interactive Agents:** Break free from fire-and-forget execution
- **User Control:** Human-in-the-loop for critical decisions
- **Real-time Feedback:** Progress updates during long operations
- **Multiple Transports:** CLI, HTTP/SSE, or Stdio for different deployment scenarios

---

## Quick Start

### 1. Setup Control Protocol

```python
import anyio
from kaizen.core.base_agent import BaseAgent
from kaizen.core.autonomy.control.protocol import ControlProtocol
from kaizen.core.autonomy.control.transports import CLITransport

# Create transport (choose based on deployment)
transport = CLITransport()  # Terminal-based interaction
await transport.connect()

# Create protocol
protocol = ControlProtocol(transport)

# Create agent with control protocol
agent = BaseAgent(
    config=your_config,
    signature=your_signature,
    control_protocol=protocol  # Enable interactive capabilities
)

# Start protocol message handling
async with anyio.create_task_group() as tg:
    await protocol.start(tg)

    # ... agent execution with interactive methods ...

    await protocol.stop()

await transport.close()
```

### 2. Use Interactive Methods

```python
# Ask user a question
answer = await agent.ask_user_question(
    question="Which file should I process?",
    options=["data.csv", "report.pdf"],  # Optional
    timeout=30.0
)

# Request approval for an action
approved = await agent.request_approval(
    action="Delete 100 temporary files",
    details={"count": 100, "size_mb": 250},  # Optional
    timeout=60.0
)

# Report progress (fire-and-forget)
await agent.report_progress(
    message="Processing file 5 of 10",
    percentage=50.0,  # Optional
    details={"current": 5, "total": 10}  # Optional
)
```

---

## API Reference

### BaseAgent.ask_user_question()

Ask the user a question during agent execution and wait for their answer.

```python
async def ask_user_question(
    question: str,
    options: Optional[List[str]] = None,
    timeout: float = 60.0
) -> str
```

**Parameters:**
- `question` (str): Question to ask the user
- `options` (Optional[List[str]]): Optional list of valid answers (multiple choice)
- `timeout` (float): Maximum seconds to wait for answer (default: 60.0)

**Returns:**
- `str`: User's answer

**Raises:**
- `RuntimeError`: If control_protocol is not configured
- `TimeoutError`: If user doesn't respond within timeout
- `RuntimeError`: If user response contains an error

**Example:**
```python
# Open-ended question
file_path = await agent.ask_user_question(
    "Which file should I analyze?"
)

# Multiple choice
mode = await agent.ask_user_question(
    "Select processing mode:",
    options=["quick", "thorough", "custom"]
)

# With custom timeout
urgent_answer = await agent.ask_user_question(
    "Emergency: Proceed with rollback?",
    options=["yes", "no"],
    timeout=10.0  # 10 second timeout
)
```

**Notes:**
- Blocks agent execution until user responds or timeout
- Use for critical decisions that require human input
- For progress updates (non-blocking), use `report_progress()` instead

---

### BaseAgent.request_approval()

Request user approval for an action and wait for their decision.

```python
async def request_approval(
    action: str,
    details: Optional[Dict[str, Any]] = None,
    timeout: float = 60.0
) -> bool
```

**Parameters:**
- `action` (str): Description of the action requiring approval
- `details` (Optional[Dict[str, Any]]): Additional details about the action
- `timeout` (float): Maximum seconds to wait for decision (default: 60.0)

**Returns:**
- `bool`: True if approved, False if denied

**Raises:**
- `RuntimeError`: If control_protocol is not configured
- `TimeoutError`: If user doesn't respond within timeout
- `RuntimeError`: If user response contains an error

**Example:**
```python
# Basic approval
if await agent.request_approval("Delete temporary files"):
    cleanup()

# Approval with details
approved = await agent.request_approval(
    action="Execute database migration",
    details={
        "tables_affected": ["users", "orders"],
        "rows_to_update": 1_000_000,
        "estimated_duration": "5 minutes",
        "reversible": True
    },
    timeout=120.0
)

if approved:
    run_migration()
else:
    logger.info("Migration cancelled by user")
```

**Notes:**
- Blocks agent execution until user approves/denies or timeout
- Returns False if user denies (allows graceful handling)
- Include detailed information to help user make informed decision

---

### BaseAgent.report_progress()

Report progress update to user during execution (non-blocking).

```python
async def report_progress(
    message: str,
    percentage: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None
) -> None
```

**Parameters:**
- `message` (str): Progress message to display
- `percentage` (Optional[float]): Progress percentage (0.0-100.0)
- `details` (Optional[Dict[str, Any]]): Additional progress details

**Returns:**
- None (fire-and-forget, does not wait for acknowledgment)

**Raises:**
- `RuntimeError`: If control_protocol is not configured
- `ValueError`: If percentage is not between 0.0 and 100.0

**Example:**
```python
# Simple progress message
await agent.report_progress("Analyzing data...")

# Progress with percentage
for i, file in enumerate(files):
    await agent.report_progress(
        f"Processing {file}",
        percentage=(i / len(files)) * 100
    )
    process(file)

# Progress with structured details
await agent.report_progress(
    "Training model - Epoch 5/10",
    percentage=50.0,
    details={
        "epoch": 5,
        "total_epochs": 10,
        "loss": 0.042,
        "accuracy": 0.95
    }
)
```

**Notes:**
- **Fire-and-forget:** Does not wait for user acknowledgment
- Use for keeping users informed during long-running operations
- Does NOT block agent execution (unlike `ask_user_question()` and `request_approval()`)

---

## Transport Options

### CLITransport (Terminal)

Best for: CLI applications, development, debugging

```python
from kaizen.core.autonomy.control.transports import CLITransport

transport = CLITransport()
await transport.connect()
# ... use with protocol ...
await transport.close()
```

**Characteristics:**
- Questions/approvals: Printed to stderr, answers read from stdin
- Progress updates: Printed to stderr
- Human-readable format
- No special setup required

---

### HTTPTransport (Web Applications)

Best for: Web applications, REST APIs, browser-based UIs

```python
from kaizen.core.autonomy.control.transports import HTTPTransport

transport = HTTPTransport(base_url="http://localhost:3000")
await transport.connect()
# ... use with protocol ...
await transport.close()
```

**Characteristics:**
- Questions/approvals: POST to `/control` endpoint
- Progress updates: Streamed via Server-Sent Events (SSE) from `/control/events`
- JSON-based communication
- Requires HTTP server implementation

**Server Requirements:**
- POST `/control`: Accept control requests, return responses
- GET `/control/events`: SSE stream for progress updates
- See `tests/utils/test_http_server.py` for reference implementation

---

### StdioTransport (Subprocess)

Best for: Agent-to-agent communication, subprocess coordination

```python
from kaizen.core.autonomy.control.transports import StdioTransport

transport = StdioTransport()
await transport.connect()
# ... use with protocol ...
await transport.close()
```

**Characteristics:**
- Questions/approvals: Written to stdout, answers read from stdin
- Progress updates: Written to stdout
- Line-delimited JSON
- Designed for programmatic parent↔child communication

**Usage Pattern:**
```python
# Parent process launches child with StdioTransport
import subprocess

proc = subprocess.Popen(
    ["python", "child_agent.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Parent reads control requests from child's stdout
# Parent writes responses to child's stdin
```

---

## Complete Example

```python
import anyio
from dataclasses import dataclass
from kaizen.core.base_agent import BaseAgent
from kaizen.signatures import Signature, InputField, OutputField
from kaizen.core.autonomy.control.protocol import ControlProtocol
from kaizen.core.autonomy.control.transports import CLITransport


# 1. Define signature
class DataProcessorSignature(Signature):
    task: str = InputField(description="Processing task")
    result: str = OutputField(description="Processing result")


# 2. Define config
@dataclass
class ProcessorConfig:
    llm_provider: str = "ollama"
    model: str = "llama3.2:latest"


# 3. Create interactive agent
class InteractiveProcessor(BaseAgent):
    """Processor that asks for user guidance."""

    async def process_with_interaction(self, files: list[str]):
        # Ask which file to process
        selected_file = await self.ask_user_question(
            "Which file should I process first?",
            options=files,
            timeout=30.0
        )

        # Request approval for processing
        approved = await self.request_approval(
            f"Process {selected_file}?",
            details={"file": selected_file, "action": "analyze"},
            timeout=60.0
        )

        if not approved:
            return {"status": "cancelled"}

        # Process with progress updates
        await self.report_progress(f"Starting {selected_file}")

        result = self.run(task=f"Analyze {selected_file}")

        await self.report_progress(
            f"Completed {selected_file}",
            percentage=100.0
        )

        return result


# 4. Use the agent
async def main():
    # Setup transport and protocol
    transport = CLITransport()
    await transport.connect()

    protocol = ControlProtocol(transport)

    # Create agent
    agent = InteractiveProcessor(
        config=ProcessorConfig(),
        control_protocol=protocol
    )

    # Run with protocol
    async with anyio.create_task_group() as tg:
        await protocol.start(tg)

        result = await agent.process_with_interaction(
            files=["data.csv", "report.pdf", "log.txt"]
        )

        print(f"Result: {result}")

        await protocol.stop()

    await transport.close()


if __name__ == "__main__":
    anyio.run(main)
```

---

## Error Handling

### Common Errors

**RuntimeError: "Control protocol not configured"**
```python
# ❌ Forgot to pass control_protocol
agent = BaseAgent(config=config, signature=signature)
await agent.ask_user_question("Test?")  # RuntimeError!

# ✅ Correct
agent = BaseAgent(config=config, signature=signature, control_protocol=protocol)
await agent.ask_user_question("Test?")  # Works!
```

**TimeoutError: No response within timeout**
```python
try:
    answer = await agent.ask_user_question(
        "Critical decision?",
        timeout=10.0
    )
except TimeoutError:
    # Handle timeout - use default, retry, or abort
    answer = "default"
```

**ValueError: Invalid percentage**
```python
# ❌ Invalid percentage
await agent.report_progress("Done", percentage=150.0)  # ValueError!

# ✅ Correct
await agent.report_progress("Done", percentage=100.0)  # Works!
```

---

## Best Practices

### 1. Use Appropriate Methods

- **Questions**: Use `ask_user_question()` for decisions requiring user input
- **Approvals**: Use `request_approval()` for yes/no authorization checks
- **Progress**: Use `report_progress()` for keeping users informed (non-blocking)

### 2. Set Reasonable Timeouts

```python
# Quick decisions: short timeout
urgent = await agent.ask_user_question(
    "Emergency shutdown?",
    options=["yes", "no"],
    timeout=10.0  # 10 seconds
)

# Complex decisions: longer timeout
strategy = await agent.ask_user_question(
    "Review this 50-page report and choose approach:",
    timeout=300.0  # 5 minutes
)
```

### 3. Provide Context in Approvals

```python
# ❌ Vague approval request
if await agent.request_approval("Run operation"):
    ...

# ✅ Detailed approval request
if await agent.request_approval(
    "Deploy model v2.0 to production",
    details={
        "environment": "production",
        "affected_users": 10_000,
        "rollback_available": True,
        "test_coverage": "98%"
    }
):
    ...
```

### 4. Handle Denial Gracefully

```python
approved = await agent.request_approval("Delete all data")

if approved:
    delete_data()
else:
    logger.info("Deletion cancelled by user - keeping data")
    # Graceful fallback
```

### 5. Use Progress Updates for Long Operations

```python
async def process_large_dataset(agent, data):
    total = len(data)

    for i, item in enumerate(data):
        # Report progress every 10%
        if i % (total // 10) == 0:
            await agent.report_progress(
                f"Processing item {i+1}/{total}",
                percentage=(i / total) * 100
            )

        process(item)

    await agent.report_progress("Complete!", percentage=100.0)
```

---

## Performance

**Benchmarked Latencies (P95):**
- Protocol overhead: **0.077ms** (negligible)
- Subprocess I/O: **0.011ms** (54x better than 20ms target)
- HTTP transport: **0.484ms** (41x better than 20ms target)

**Real-World Latency:**
- **Human response time dominates:** 1-2 seconds (asking question → user reads → thinks → types answer)
- **Protocol overhead is negligible:** <0.1ms
- **Conclusion:** Protocol will never be the bottleneck in interactive applications

**Source:** `WEEK_11_FINAL_PERFORMANCE_REPORT.md`

---

## Troubleshooting

### Protocol Not Starting

**Problem:** Methods hang or timeout immediately

**Solution:** Ensure protocol.start() is called within task group
```python
async with anyio.create_task_group() as tg:
    await protocol.start(tg)  # Required!
    await agent.ask_user_question("...")  # Now works
```

### Transport Not Connected

**Problem:** RuntimeError about transport not ready

**Solution:** Call transport.connect() before creating protocol
```python
transport = CLITransport()
await transport.connect()  # Required!
protocol = ControlProtocol(transport)
```

### Messages Not Received

**Problem:** Questions sent but no response received

**Solution:** Check transport implementation is handling messages correctly
- CLITransport: Ensure stdin is available and not closed
- HTTPTransport: Ensure server is listening on correct endpoint
- StdioTransport: Ensure parent process is reading stdout

---

## See Also

- **Architecture:** [ADR-011: Bidirectional Agent Communication](../architecture/adr/ADR-011-bidirectional-agent-communication.md)
- **Tutorial:** [Control Protocol Quickstart](../guides/control-protocol-tutorial.md)
- **Examples:** `examples/autonomy/`
- **Source Code:** `src/kaizen/core/autonomy/control/`

---

**Last Updated:** 2025-10-19
**Maintainers:** Kaizen AI Framework Team
