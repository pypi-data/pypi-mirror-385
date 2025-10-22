# AISentinel Python SDK

[![PyPI version](https://badge.fury.io/py/aisentinel-sdk.svg)](https://pypi.org/project/aisentinel-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/aisentinel-sdk.svg)](https://pypi.org/project/aisentinel-sdk/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/mfifth/aisentinel-python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/mfifth/aisentinel-python-sdk/actions/workflows/ci.yml)

The official Python SDK for AISentinel - zero-latency governance for AI agents.

## Features

- **Preflight Checks**: Validate agent actions before execution
- **Offline Support**: Continue operating when network connectivity is lost
- **Local Caching**: Cache decisions and rulepacks for improved performance
- **Multi-tenant**: Support for multiple organizations and environments
- **Thread-safe**: Designed for concurrent agent deployments
- **Embedded Database**: SQLite-based storage for audit logs and metrics

## Installation

```bash
pip install aisentinel-sdk
```

## Quick Start

```python
from aisentinel import Governor

# Initialize the governor
governor = Governor(
    base_url="https://aisentinel.fly.dev",
    token="your-api-token"
)

# Check if an action is allowed
candidate = {
    "tool": "web_search",
    "args": {"query": "python tutorials"}
}

state = {"user_id": "user123", "session_id": "sess456"}

decision = governor.preflight(candidate, state)

if decision["allowed"]:
    # Execute your tool
    result = perform_web_search(candidate["args"]["query"])
    print(f"Search results: {result}")
else:
    print(f"Blocked: {decision['reasons']}")
```

## Advanced Usage

### Offline Mode

The SDK automatically handles network interruptions and queues operations for later execution:

```python
# The governor automatically detects connectivity and handles offline scenarios
governor = Governor(token="your-token")

# If offline, decisions are cached or deferred
decision = governor.preflight(candidate, state)
```

### Multi-tenant Support

```python
# Configure multiple tenants
governor = Governor(token="default-token")

# Use tenant-specific tokens
decision = governor.preflight(candidate, state, tenant_id="tenant-123")
```

### Rulepack Management

```python
# Fetch and cache rulepacks
rulepack = governor.fetch_rulepack("security-rules", version="1.2.0")
print(f"Rulepack version: {rulepack['version']}")
```

### Guarded Execution

```python
# Automatically execute allowed actions, return alternatives for blocked ones
def search_web(query):
    return {"results": ["result1", "result2"]}

result = governor.guarded_execute(
    search_web,
    {"tool": "web_search", "args": {"query": "python"}},
    {"user_id": "user123"}
)

if "error" in result:
    print(f"Action blocked: {result['error']}")
else:
    print(f"Results: {result}")
```

## Configuration

Configure the SDK via environment variables, config files, or programmatically:

```bash
# Environment variables
export AISENTINEL_BASE_URL="https://aisentinel.fly.dev"
export AISENTINEL_TOKEN="your-token"
export AISENTINEL_CACHE_TTL_SECONDS="600"
```

```python
# Programmatic configuration
from aisentinel import Governor, SDKConfig

config = SDKConfig.load(
    overrides={
        "base_url": "https://aisentinel.fly.dev",
        "token": "your-token",
        "offline_mode_enabled": True
    }
)

governor = Governor(config=config)
```

### Config File

Create a `aisentinel.json` file:

```json
{
  "base_url": "https://aisentinel.fly.dev",
  "token": "your-token",
  "cache_ttl_seconds": 300,
  "offline_mode_enabled": true,
  "tenants": {
    "tenant-1": {
      "token": "tenant-specific-token"
    }
  }
}
```

## Integration Examples

### LangChain Integration

```python
from langchain.tools import Tool
from aisentinel import Governor

governor = Governor(token="your-token")

def guarded_web_search(query: str) -> str:
    candidate = {"tool": "web_search", "args": {"query": query}}
    state = {"user_id": "agent123"}

    decision = governor.preflight(candidate, state)
    if not decision["allowed"]:
        return f"Search blocked: {decision['reasons'][0]}"

    # Perform actual search
    return perform_search(query)

search_tool = Tool(
    name="WebSearch",
    description="Search the web for information",
    func=guarded_web_search
)
```

### CrewAI Integration

```python
from crewai import Agent, Task
from aisentinel import Governor

governor = Governor(token="your-token")

class GovernedAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.governor = governor

    def execute_task(self, task: Task):
        # Check if task execution is allowed
        candidate = {
            "tool": "agent_execution",
            "args": {"task": task.description}
        }
        state = {"agent_id": self.id}

        decision = self.governor.preflight(candidate, state)
        if not decision["allowed"]:
            raise ValueError(f"Task execution blocked: {decision['reasons']}")

        return super().execute_task(task)
```

## API Reference

### Governor

The main SDK class for AISentinel governance.

#### Methods

- `preflight(candidate, state, tenant_id=None)` - Check if an action is allowed
- `guarded_execute(func, candidate, state, tenant_id=None)` - Execute function if allowed
- `fetch_rulepack(rulepack_id, version=None)` - Fetch rulepack with caching
- `get_cache_metrics()` - Get cache performance metrics

### SDKConfig

Configuration management for the SDK.

#### Methods

- `SDKConfig.load(file_path=None, env_prefix="AISENTINEL_", overrides=None)` - Load configuration

## Development

```bash
# Clone the repository
git clone https://github.com/aisentinel/aisentinel-python-sdk.git
cd aisentinel-python-sdk

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black aisentinel/
isort aisentinel/
mypy aisentinel/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://aisentinel.fly.dev/docs)
- 🐛 [Issue Tracker](https://github.com/mfifth/aisentinel-python-sdk/issues)
