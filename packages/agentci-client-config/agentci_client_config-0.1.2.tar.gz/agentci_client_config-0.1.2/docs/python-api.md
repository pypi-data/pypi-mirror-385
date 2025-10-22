# Python API (Optional)

While the primary use case is writing TOML files, you can also work with configurations programmatically.

## Installation

```bash
pip install agentci-client-config
```

## Discovering Configurations

### Discover Evaluations

```python
from pathlib import Path
from agentci.client_config import discover_evaluations

# Discover all evaluations in the repository
evaluations = discover_evaluations(Path("."))

for eval_config in evaluations:
    print(f"{eval_config.name}: {eval_config.description}")
    print(f"  Type: {eval_config.type}")
    print(f"  Cases: {len(eval_config.cases)}")
```

### Discover Frameworks

```python
from agentci.client_config import discover_frameworks

# Discover built-in + user frameworks
frameworks = discover_frameworks(Path("."))

# Or just built-in frameworks
frameworks = discover_frameworks()

for framework in frameworks:
    print(f"{framework.name}")
    print(f"  Agents: {len(framework.agents)}")
    print(f"  Tools: {len(framework.tools)}")
```

## Filtering Evaluations

```python
# Get evaluations for a specific agent
agent_evals = [
    e for e in evaluations
    if e.targets.targets_agent("my_agent")
]

# Get evaluations for a specific tool
tool_evals = [
    e for e in evaluations
    if e.targets.targets_tool("my_tool")
]
```

## Parsing Individual Files

```python
from pathlib import Path
from agentci.client_config import (
    parse_evaluation_config_toml,
    parse_framework_config_toml,
)

# Parse a single evaluation file
eval_config = parse_evaluation_config_toml(
    Path(".agentci/evals/test.toml"),
    Path(".")
)

# Parse a single framework file
framework_config = parse_framework_config_toml(
    Path(".agentci/frameworks/custom.toml"),
    Path(".")
)
```

## Configuration Settings

```python
from agentci.client_config import config

# Access configuration paths
print(f"Base path: {config.client_base_path}")
print(f"Evals path: {config.evaluation_path_name}")
print(f"Frameworks path: {config.framework_path_name}")
```

## API Reference

For complete API documentation including all schema models and functions:

- [Evals API Reference](api/evals.md)
- [Frameworks API Reference](api/frameworks.md)
- [Config API Reference](api/config.md)
