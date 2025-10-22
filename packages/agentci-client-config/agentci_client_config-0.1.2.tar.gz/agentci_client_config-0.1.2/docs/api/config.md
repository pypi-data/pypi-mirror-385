# Configuration API Reference

This page documents the configuration settings for the library.

## ClientConfig

The `config` object provides access to configuration paths and settings.

::: agentci.client_config._config.ClientConfig

## Usage

```python
from agentci.client_config import config

# Access configuration paths
print(f"Base path: {config.client_base_path}")
print(f"Evals path: {config.evaluation_path_name}")
print(f"Frameworks path: {config.framework_path_name}")
```

## Environment Variables

### AGENTCI_CLIENT_BASE_PATH

Override the default `.agentci` base directory:

```bash
export AGENTCI_CLIENT_BASE_PATH=".custom"
```

This changes the paths to:
- `.custom/evals/` for evaluations
- `.custom/frameworks/` for framework configs
