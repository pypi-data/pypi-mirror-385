# Troubleshooting Guide

Comprehensive troubleshooting guide for common Kaizen Framework issues, including error resolution, performance problems, and configuration issues.

## Quick Reference

### Most Common Issues

1. **[Framework Import Performance](#framework-import-performance)** - ~1100ms import time
2. **[Missing Required Inputs](#missing-required-inputs)** - Workflow execution errors
3. **[Configuration Parameter Errors](#configuration-parameter-errors)** - Agent creation failures
4. **[Core SDK Compatibility](#core-sdk-compatibility)** - Integration issues
5. **[Performance Degradation](#performance-degradation)** - Slow execution times

### Emergency Fixes

```bash
# Quick diagnostic commands
python -c "from kaizen import Kaizen; print('✅ Framework imports successfully')"
python -c "import time; s=time.time(); from kaizen import Kaizen; print(f'Import time: {(time.time()-s)*1000:.0f}ms')"
pytest tests/unit/test_framework.py::test_framework_initialization -v
```

## Framework Issues

### Framework Import Performance

**Problem**: Framework takes ~1100ms to import (target: <100ms)

**Symptoms**:
```python
import time
start = time.time()
from kaizen import Kaizen  # Takes ~1100ms
end = time.time()
print(f"Import time: {(end - start) * 1000:.0f}ms")
```

**Root Cause**: Core SDK node registration during import

**Solutions**:

1. **Use Lazy Imports** (Current Workaround):
```python
# Instead of importing at module level
def get_kaizen():
    from kaizen import Kaizen
    return Kaizen()

# Use when needed
kaizen = get_kaizen()
```

2. **Enable Import Optimization** (Planned):
```python
# Future optimization
kaizen = Kaizen(config={
    'lazy_loading': True,
    'import_optimization': True
})
```

3. **Pre-import in Application Startup**:
```python
# Import during application initialization, not request handling
import kaizen  # Do this once at startup
```

**Expected Resolution**: Framework optimization planned for future releases

### Missing Required Inputs Error

**Problem**: Workflow execution fails with "Missing required inputs"

**Symptoms**:
```python
agent = kaizen.create_agent("test", {"model": "gpt-4"})
runtime = LocalRuntime()
results, run_id = runtime.execute(agent.workflow.build())
# Error: Missing required inputs: ['input']
```

**Root Cause**: Agent workflow expects input data that wasn't provided

**Solutions**:

1. **Provide Workflow Inputs**:
```python
# Add inputs to workflow before execution
workflow = agent.workflow
workflow.set_inputs({"input": "Your input text here"})
results, run_id = runtime.execute(workflow.build())
```

2. **Use Agent Execute Method** (Planned):
```python
# Future: Direct agent execution
results = agent.execute("Your input text here")
```

3. **Check Agent Configuration**:
```python
# Verify agent workflow structure
print(f"Agent workflow nodes: {agent.workflow.nodes}")
print(f"Required inputs: {agent.workflow.get_required_inputs()}")
```

### Configuration Parameter Errors

**Problem**: Agent creation fails with parameter validation errors

**Symptoms**:
```python
agent = kaizen.create_agent("test", {
    "model": "gpt-4",
    "temperature": 5.0  # Invalid: too high
})
# Error: Temperature must be between 0.0 and 2.0
```

**Solutions**:

1. **Validate Parameters**:
```python
# Check valid parameter ranges
valid_config = {
    "model": "gpt-4",           # Required
    "temperature": 0.7,         # 0.0 - 2.0
    "max_tokens": 1000,         # > 0
    "system_prompt": "Assistant"  # Optional
}
```

2. **Use Configuration Validation**:
```python
from kaizen.core.base import KaizenConfig

# Validate before agent creation
config = KaizenConfig(your_config_dict)
if config.is_valid():
    agent = kaizen.create_agent("test", config)
```

3. **Handle Configuration Errors**:
```python
from kaizen.core.exceptions import ConfigurationError

try:
    agent = kaizen.create_agent("test", config)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Fix configuration and retry
```

## Core SDK Integration Issues

### Runtime Compatibility Problems

**Problem**: Kaizen agents don't execute properly with Core SDK runtime

**Symptoms**:
```python
runtime = LocalRuntime()
results, run_id = runtime.execute(agent.workflow.build())
# Error: Workflow build failed or execution error
```

**Diagnostic Steps**:

1. **Verify Workflow Structure**:
```python
# Debug workflow building
try:
    workflow = agent.workflow
    print(f"Workflow type: {type(workflow)}")
    built_workflow = workflow.build()
    print(f"Built successfully: {built_workflow is not None}")
except Exception as e:
    print(f"Workflow build error: {e}")
```

2. **Check Core SDK Compatibility**:
```python
# Test with traditional Core SDK workflow
from kailash.workflow.builder import WorkflowBuilder

traditional_workflow = WorkflowBuilder()
traditional_workflow.add_node("LLMAgentNode", "test", {
    "model": "gpt-3.5-turbo"
})

try:
    results, run_id = runtime.execute(traditional_workflow.build())
    print("✅ Core SDK working correctly")
except Exception as e:
    print(f"❌ Core SDK issue: {e}")
```

3. **Verify Node Registration**:
```python
from kailash.core.registry import NodeRegistry

registry = NodeRegistry()
available_nodes = registry.list_nodes()
print(f"Available nodes: {available_nodes}")

# Check if Kaizen nodes are registered
kaizen_nodes = [node for node in available_nodes if "Kaizen" in node]
print(f"Kaizen nodes: {kaizen_nodes}")
```

### Parameter Mapping Issues

**Problem**: Kaizen parameters don't map correctly to Core SDK nodes

**Symptoms**:
```python
agent = kaizen.create_agent("test", {"model": "gpt-4"})
# Core SDK node receives unexpected parameters
```

**Solutions**:

1. **Check Parameter Mapping**:
```python
# Debug parameter conversion
agent_config = agent.config
print(f"Agent config: {agent_config}")

# Check how parameters map to Core SDK
workflow = agent.workflow
for node_id, node_config in workflow.nodes.items():
    print(f"Node {node_id}: {node_config}")
```

2. **Use Compatible Parameters**:
```python
# Ensure parameter names match Core SDK expectations
compatible_config = {
    "model": "gpt-4",              # ✅ Core SDK compatible
    "temperature": 0.7,            # ✅ Core SDK compatible
    "max_tokens": 1000,            # ✅ Core SDK compatible
    "system_prompt": "Assistant"   # ✅ Maps to prompt_template
}
```

## Performance Issues

### Performance Degradation

**Problem**: Kaizen agents execute slower than expected

**Diagnostic Steps**:

1. **Measure Performance Components**:
```python
import time

# Measure agent creation
start = time.time()
agent = kaizen.create_agent("perf_test", {"model": "gpt-3.5-turbo"})
creation_time = (time.time() - start) * 1000
print(f"Agent creation: {creation_time:.0f}ms")

# Measure workflow building
start = time.time()
workflow = agent.workflow.build()
build_time = (time.time() - start) * 1000
print(f"Workflow build: {build_time:.0f}ms")

# Measure execution
start = time.time()
results, run_id = runtime.execute(workflow)
exec_time = (time.time() - start) * 1000
print(f"Execution: {exec_time:.0f}ms")
```

2. **Compare with Core SDK Baseline**:
```python
# Core SDK baseline
start = time.time()
traditional_workflow = WorkflowBuilder()
traditional_workflow.add_node("LLMAgentNode", "baseline", {
    "model": "gpt-3.5-turbo"
})
baseline_results, baseline_run_id = runtime.execute(traditional_workflow.build())
baseline_time = (time.time() - start) * 1000

print(f"Baseline time: {baseline_time:.0f}ms")
print(f"Kaizen overhead: {((exec_time - baseline_time) / baseline_time * 100):.1f}%")
```

### Memory Usage Issues

**Problem**: High memory usage or memory leaks

**Diagnostic Steps**:

1. **Monitor Memory Usage**:
```python
import psutil
import os

process = psutil.Process(os.getpid())

# Before Kaizen
baseline_memory = process.memory_info().rss / 1024 / 1024

# After Kaizen initialization
kaizen = Kaizen()
init_memory = process.memory_info().rss / 1024 / 1024

# After agent creation
agent = kaizen.create_agent("memory_test", {"model": "gpt-3.5-turbo"})
agent_memory = process.memory_info().rss / 1024 / 1024

print(f"Baseline: {baseline_memory:.1f}MB")
print(f"After init: {init_memory:.1f}MB (+{init_memory - baseline_memory:.1f}MB)")
print(f"After agent: {agent_memory:.1f}MB (+{agent_memory - init_memory:.1f}MB)")
```

2. **Check for Memory Leaks**:
```python
# Create and destroy multiple agents
baseline = process.memory_info().rss / 1024 / 1024

for i in range(10):
    agent = kaizen.create_agent(f"leak_test_{i}", {"model": "gpt-3.5-turbo"})
    # Agent should be garbage collected when out of scope

final_memory = process.memory_info().rss / 1024 / 1024
memory_growth = final_memory - baseline

print(f"Memory growth after 10 agents: {memory_growth:.1f}MB")
if memory_growth > 50:  # More than 50MB growth
    print("⚠️ Potential memory leak detected")
```

## Configuration Issues

### Environment Variable Problems

**Problem**: API keys or environment variables not loaded correctly

**Symptoms**:
```python
agent = kaizen.create_agent("test", {"model": "gpt-4"})
# Error: OpenAI API key not found
```

**Solutions**:

1. **Verify Environment Variables**:
```python
import os

required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {'*' * (len(value) - 4)}{value[-4:]}")
    else:
        print(f"❌ {var}: Not set")
```

2. **Load from .env File**:
```python
# Install python-dotenv: pip install python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file
api_key = os.getenv("OPENAI_API_KEY")
print(f"API key loaded: {api_key is not None}")
```

3. **Explicit Configuration**:
```python
# Pass API keys directly (not recommended for production)
kaizen = Kaizen(config={
    'api_keys': {
        'openai': 'your_openai_key',
        'anthropic': 'your_anthropic_key'
    }
})
```

### Model Access Issues

**Problem**: AI model not accessible or authentication fails

**Symptoms**:
```python
agent = kaizen.create_agent("test", {"model": "gpt-4"})
results, run_id = runtime.execute(agent.workflow.build())
# Error: Authentication failed or model not found
```

**Solutions**:

1. **Test API Access**:
```python
# Test OpenAI access
try:
    from openai import OpenAI
    client = OpenAI()
    response = client.models.list()
    print("✅ OpenAI API accessible")
    print(f"Available models: {[m.id for m in response.data[:5]]}")
except Exception as e:
    print(f"❌ OpenAI API error: {e}")
```

2. **Use Available Models**:
```python
# Check which models are accessible
available_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
for model in available_models:
    try:
        agent = kaizen.create_agent("test", {"model": model})
        print(f"✅ Model {model} accessible")
        break
    except Exception as e:
        print(f"❌ Model {model}: {e}")
```

## Error Reference

### Common Error Messages

#### `KaizenError: Framework initialization failed`
- **Cause**: Core SDK not properly installed or import conflicts
- **Solution**: `pip install kailash[core]` and verify imports

#### `ConfigurationError: Invalid agent configuration`
- **Cause**: Agent configuration parameters invalid
- **Solution**: Check parameter names and value ranges

#### `ValueError: Agent name cannot be empty`
- **Cause**: Empty or None agent name provided
- **Solution**: Provide non-empty string for agent name

#### `RuntimeError: Workflow execution failed`
- **Cause**: Core SDK runtime error or node execution failure
- **Solution**: Check Core SDK installation and node configuration

#### `ImportError: No module named 'kaizen'`
- **Cause**: Kaizen not installed or not in Python path
- **Solution**: `pip install -e .` for development or `pip install kailash-kaizen`

### Error Handling Patterns

```python
from kaizen.core.exceptions import KaizenError, ConfigurationError

def robust_agent_creation(name, config):
    """Create agent with comprehensive error handling."""
    try:
        agent = kaizen.create_agent(name, config)
        return agent, None

    except ConfigurationError as e:
        return None, f"Configuration error: {e}"

    except KaizenError as e:
        return None, f"Framework error: {e}"

    except Exception as e:
        return None, f"Unexpected error: {e}"

# Usage
agent, error = robust_agent_creation("test", config)
if error:
    print(f"❌ {error}")
else:
    print("✅ Agent created successfully")
```

## Getting Help

### Diagnostic Information

```python
def collect_diagnostic_info():
    """Collect diagnostic information for support."""
    import platform
    import sys

    info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "kaizen_version": "0.1.0",  # Update with actual version
        "environment": {}
    }

    # Check environment variables
    env_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "KAIZEN_ENV"]
    for var in env_vars:
        info["environment"][var] = "SET" if os.getenv(var) else "NOT_SET"

    # Check imports
    try:
        from kaizen import Kaizen
        info["kaizen_import"] = "SUCCESS"
    except Exception as e:
        info["kaizen_import"] = f"FAILED: {e}"

    try:
        from kailash.workflow.builder import WorkflowBuilder
        info["core_sdk_import"] = "SUCCESS"
    except Exception as e:
        info["core_sdk_import"] = f"FAILED: {e}"

    return info

# Collect and display diagnostic info
diag_info = collect_diagnostic_info()
for key, value in diag_info.items():
    print(f"{key}: {value}")
```

### Support Channels

- **Documentation**: [Complete guides](../README.md)
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community questions and support

### Filing Bug Reports

Include this information when filing bug reports:

1. **Diagnostic Information**: Output from `collect_diagnostic_info()`
2. **Error Messages**: Complete error messages and stack traces
3. **Minimal Reproduction**: Smallest code that reproduces the issue
4. **Expected Behavior**: What you expected to happen
5. **Actual Behavior**: What actually happened

---

**🔧 Troubleshooting Complete**: This guide covers the most common issues and provides systematic approaches to resolving problems. For issues not covered here, use the diagnostic tools and support channels listed above.