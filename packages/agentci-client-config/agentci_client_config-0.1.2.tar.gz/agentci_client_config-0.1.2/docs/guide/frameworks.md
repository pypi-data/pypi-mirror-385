# Framework Configuration Schema

Framework configurations define how to discover and execute agents and tools from AI frameworks.

## Overview

AgentCI includes built-in configurations for:
- **LangChain** (`langchain.toml`)
- **LlamaIndex** (`llamaindex.toml`)
- **Pydantic AI** (`pydantic_ai.toml`)

You can create custom framework configurations or override built-in ones by placing TOML files in `.agentci/frameworks/`.

## Complete TOML Structure

```toml
[framework]
name = "framework-name"
dependencies = ["package-name", "alternative-name"]

[[agents]]
path = "module.path.to.Agent"
type = "constructor"  # Optional: constructor | class_method | function
args.model = "model_param"
args.prompt = "prompt_param"
args.tools = "tools_param"
execution.method = "run"
execution.args.prompt = "user_input"

[[tools]]
type = "decorator"  # Required: decorator | constructor | class | function
path = "module.path.to.tool"
execution.method = "invoke"
```

## Framework Metadata

### `[framework]`

```toml
[framework]
name = "my-framework"              # Required: Unique identifier
dependencies = ["package1", "pkg2"] # Required: PyPI package names
```

**Fields:**

- **`name`** (required, string): Unique identifier for this framework
  - Used for override resolution (user configs override built-in configs with matching names)
  - Typically lowercase with hyphens (e.g., `"langchain"`, `"llamaindex"`)

- **`dependencies`** (required, array of strings): PyPI package names
  - At least one required
  - Used to detect if the framework is installed in the project
  - Include all naming variants (e.g., `["langchain", "langchain-core"]`)

## Agent Configuration

### `[[agents]]`

Defines patterns for discovering and executing agents. You can specify multiple `[[agents]]` blocks for different agent patterns.

```toml
[[agents]]
path = "module.path.to.Agent"
type = "constructor"
args.model = "llm"
args.prompt = "system_prompt"
args.tools = "tools"
execution.method = "run"
execution.args.prompt = "input"
```

**Discovery Fields:**

- **`path`** (required, string): Fully qualified Python path to the agent class, function, or method
  - Constructor: `"my_framework.Agent"`
  - Function: `"my_framework.create_agent"`
  - Class method: `"my_framework.Agent.from_tools"`

- **`type`** (optional, string): How the agent is created
  - `"constructor"` (default): Direct class instantiation or function call
  - `"class_method"`: Class method (e.g., `Agent.from_tools()`)
  - `"function"`: Factory function
  - **Note**: `class_method` must be explicitly specified; others auto-detected

- **`args`** (required): Parameter name mappings (at least one field required)
  - **`args.model`** (optional, string): Parameter name for the LLM model
  - **`args.prompt`** (optional, string): Parameter name for the system prompt
  - **`args.tools`** (optional, string): Parameter name for the tools list

**Execution Fields:**

- **`execution.method`** (required, string): Method name to call on the agent instance

- **`execution.args.prompt`** (required, string): Parameter name for the user's input prompt

### Agent Type Reference

| Type | Description | Path Example |
|------|-------------|--------------|
| `constructor` | Class instantiation or function call | `"my_framework.Agent"` |
| `class_method` | Class method creation | `"my_framework.Agent.from_tools"` |
| `function` | Factory function | `"my_framework.create_agent"` |

### Agent Discovery Arguments

At least one of the following must be specified:

| Field | Type | Purpose |
|-------|------|---------|
| `args.model` | string | Parameter name for LLM model |
| `args.prompt` | string | Parameter name for system prompt |
| `args.tools` | string | Parameter name for tools list |

## Tool Configuration

### `[[tools]]`

Defines patterns for discovering and executing tools. You can specify multiple `[[tools]]` blocks for different tool patterns.

```toml
[[tools]]
type = "decorator"
path = "my_framework.tool"
execution.method = "invoke"
```

**Discovery Fields:**

- **`type`** (required, string): How tools are defined
  - `"decorator"`: Functions with a decorator (e.g., `@tool`)
  - `"constructor"`: Created via class method (e.g., `Tool.from_function()`)
  - `"class"`: Inherit from a base class (e.g., `BaseTool`)
  - `"function"`: Plain Python functions (no decorator)

- **`path`** (conditional, string): Fully qualified Python path
  - **Required** for `decorator`, `constructor`, and `class` types
  - **Not used** for `function` type (discovers all public functions)
  - Examples:
    - Decorator: `"langchain_core.tools.tool"`
    - Constructor: `"llama_index.core.tools.FunctionTool.from_defaults"`
    - Class: `"langchain_core.tools.BaseTool"`

**Execution Fields:**

- **`execution.method`** (required, string): Method name to call on the tool
  - `"__call__"`: Direct function call
  - `"invoke"`: Framework-specific method
  - `"run"`: Alternative execution method

### Tool Type Reference

| Type | Description | Path Required | Path Example |
|------|-------------|---------------|--------------|
| `decorator` | Functions with decorator | Yes | `"framework.tool"` |
| `constructor` | Class method creation | Yes | `"framework.Tool.from_function"` |
| `class` | Base class inheritance | Yes | `"framework.BaseTool"` |
| `function` | Plain functions | No | (none) |

## Discovery Mechanism

Framework configurations are discovered from two sources in order:

1. **Built-in configs**: Bundled with the library in `frameworks/configs/`
2. **User configs**: Located in `.agentci/frameworks/`

User configs with the same `name` as built-in configs will **override** the built-in version.

```python
from agentci.client_config import discover_frameworks
from pathlib import Path

# Returns built-in + user configs (with overrides applied)
frameworks = discover_frameworks(Path("."))

# Returns only built-in configs
frameworks = discover_frameworks()
```

## Validation Rules

Framework configs are validated when discovered:

- Must have at least one `[[agents]]` or `[[tools]]` section
- `framework.dependencies` must have at least one entry
- `agents.path` must not be empty
- Class method agents must have paths with at least 2 parts (e.g., `Class.method`)
- Non-function tools must have `path` specified
- Agent `args` must have at least one of: `model`, `prompt`, or `tools`

## Examples

### Basic Framework

```toml
[framework]
name = "my-framework"
dependencies = ["my-framework"]

[[agents]]
path = "my_framework.Agent"
args.model = "llm"
args.prompt = "system_prompt"
args.tools = "tools"
execution.method = "run"
execution.args.prompt = "user_input"

[[tools]]
type = "function"
execution.method = "__call__"
```

### Multiple Agent Patterns

```toml
[framework]
name = "multi-pattern-framework"
dependencies = ["multi-pattern"]

# Constructor pattern
[[agents]]
path = "framework.Agent"
type = "constructor"
args.model = "model"
args.tools = "tools"
execution.method = "run"
execution.args.prompt = "input"

# Class method pattern
[[agents]]
path = "framework.Agent.from_config"
type = "class_method"
args.model = "llm"
args.prompt = "prompt"
execution.method = "execute"
execution.args.prompt = "message"
```

### Multiple Tool Patterns

```toml
[framework]
name = "multi-tool-framework"
dependencies = ["multi-tool"]

[[agents]]
path = "framework.Agent"
args.model = "model"
execution.method = "run"
execution.args.prompt = "input"

# Decorator-based tools
[[tools]]
type = "decorator"
path = "framework.tool"
execution.method = "invoke"

# Class-based tools
[[tools]]
type = "class"
path = "framework.BaseTool"
execution.method = "run"

# Plain function tools
[[tools]]
type = "function"
execution.method = "__call__"
```

## Next Steps

- [Advanced Framework Configuration](frameworks-advanced.md) - Detailed examples and practical workflows
- [Frameworks API Reference](../api/frameworks.md) - Python API documentation
- [Evaluations](evaluations.md) - Learn about evaluation configurations
