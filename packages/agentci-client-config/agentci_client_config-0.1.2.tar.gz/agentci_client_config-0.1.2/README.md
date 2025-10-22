# AgentCI Client Config

Define evaluations and framework configurations for AI agent applications using simple TOML files.

📚 **[Full Documentation](https://agent-ci.com/docs)** | 🚀 **[Getting Started](docs/guide/getting-started.md)** | 📖 **[TOML Schema Guides](docs/index.md)**

## What is This?

AgentCI Client Config provides a TOML-based configuration format for:

- **Evaluations**: Test cases for AI agents and tools with support for accuracy, performance, consistency, and safety testing
- **Framework Configurations**: Patterns for discovering agents and tools in popular AI frameworks (LangChain, LlamaIndex, Pydantic AI)

## Quick Example

Create evaluation configs in `.agentci/evals/`:

```toml
# .agentci/evals/test_accuracy.toml
[eval]
description = "Test that the agent responds with correct information"
type = "accuracy"

[eval.targets]
agents = ["my_agent"]

[[eval.cases]]
prompt = "What is the capital of France?"
expected.exact = "Paris"
```

Create framework configs in `.agentci/frameworks/`:

```toml
# .agentci/frameworks/my_framework.toml
[framework]
name = "my-framework"
dependencies = ["my-framework"]

[[agents]]
path = "my_framework.Agent"
args.model = "llm"
args.prompt = "system_prompt"
execution.method = "run"
execution.args.prompt = "user_input"
```

## Installation

```bash
pip install agentci-client-config
```

## Documentation

For complete TOML schema documentation and guides:

- **[Getting Started](docs/guide/getting-started.md)** - Project setup and first configs
- **[Evaluation Schema](docs/guide/evaluations.md)** - Complete guide to evaluation TOML format
- **[Framework Schema](docs/guide/frameworks.md)** - Complete guide to framework TOML format
- **[Python API](docs/python-api.md)** - Optional programmatic usage

## Features

### Evaluations

- **Six evaluation types**: accuracy, performance, consistency, safety, llm, custom
- **Flexible matching**: exact, contains, regex, semantic similarity
- **Schema validation**: Validate structured JSON outputs
- **Tool call validation**: Verify correct tool usage
- **Multiple iterations**: Run tests multiple times for consistency

### Frameworks

- **Built-in support**: LangChain, LlamaIndex, Pydantic AI
- **Custom frameworks**: Define your own discovery patterns
- **Agent discovery**: Map framework parameters to standard fields
- **Tool discovery**: Configure tool types (decorator, function, class, constructor)
- **Execution config**: Define how to run agents and tools

## Directory Structure

```
your-project/
├── .agentci/
│   ├── evals/              # Evaluation configurations
│   │   ├── accuracy.toml
│   │   ├── performance.toml
│   │   └── safety.toml
│   └── frameworks/         # Framework configurations (optional)
│       └── custom.toml
├── src/
└── tests/
```

## License

MIT

