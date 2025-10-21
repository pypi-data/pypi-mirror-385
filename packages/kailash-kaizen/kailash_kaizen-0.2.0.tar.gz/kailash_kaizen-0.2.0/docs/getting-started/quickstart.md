# Kaizen Framework - 5-Minute Quickstart

Get up and running with Kaizen's signature-based AI programming in under 5 minutes.

## Prerequisites

- Python 3.9+
- Basic familiarity with Python functions
- Optional: Docker (for advanced examples)

## Installation

```bash
# Install Kaizen with core dependencies
pip install kailash-kaizen

# Or install with all optional features
pip install kailash-kaizen[all]
```

## Your First AI Agent

### Step 1: Basic Agent Creation

```python
from kaizen import Kaizen
from kailash.runtime.local import LocalRuntime

# Initialize the framework
kaizen = Kaizen()

# Create a simple text processing agent
agent = kaizen.create_agent("text_processor", {
    "model": "gpt-4",
    "temperature": 0.7
})

print("✅ Agent created successfully!")
```

### Step 2: Execute Your First Workflow

```python
# Execute with Kailash SDK runtime (current implementation)
runtime = LocalRuntime()
results, run_id = runtime.execute(agent.workflow.build())

print(f"🚀 Workflow executed! Run ID: {run_id}")
print(f"📊 Results: {results}")
```

### Step 3: Signature-Based Programming (Future)

**Note**: This represents the target API - not yet implemented.

```python
@kaizen.signature("question -> answer")
def research_assistant(question: str) -> str:
    """AI assistant that researches topics and provides comprehensive answers"""
    pass

# The signature automatically compiles to an optimized workflow
result = research_assistant("What are the benefits of renewable energy?")
```

## What You Just Built

Your first Kaizen agent demonstrates:

1. **Framework Integration**: Seamless Kailash SDK compatibility
2. **Agent Architecture**: Clean agent creation and management
3. **Workflow Execution**: Standard Kailash runtime patterns

## Next Steps

### Immediate Next Steps (Currently Available)
- [**Installation Guide**](installation.md) - Complete setup with development tools
- [**Core Concepts**](concepts.md) - Understanding the framework architecture
- [**Basic Examples**](examples.md) - More agent patterns and use cases

### Advanced Capabilities (In Development)
- **Signature Programming**: Declarative AI workflow definition
- **MCP Integration**: First-class Model Context Protocol support
- **Multi-Agent Systems**: Coordination patterns and orchestration
- **Enterprise Features**: Monitoring, security, and compliance

## Common Issues

### Import Errors
```python
# If you see import errors:
pip install kailash[core]  # Ensure Core SDK is available
```

### Performance Note
The framework currently takes ~1100ms to import due to Core SDK node registration. This will be optimized in future releases.

## Framework Status

🟢 **Available Now**: Basic framework, agent creation, Core SDK integration
🟡 **In Development**: Signature programming, MCP integration, multi-agent coordination
🔵 **Planned**: Advanced enterprise features, optimization engine

## Get Help

- [**Documentation Hub**](../README.md) - Complete documentation index
- [**Troubleshooting**](../reference/troubleshooting.md) - Common issues and solutions
- [**Contributing**](../development/contributing.md) - Development guidelines

---

**🎯 Goal Achieved**: You now have a working Kaizen agent integrated with the Kailash SDK. Continue with the [Installation Guide](installation.md) for a complete development setup.