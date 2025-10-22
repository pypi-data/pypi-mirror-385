# AgentCI Client Config

Define evaluations and framework configurations for AI agent applications using simple TOML files.

## What is This?

AgentCI Client Config provides a TOML-based configuration format for:

- **Evaluations**: Test cases for AI agents and tools with support for accuracy, performance, consistency, and safety testing
- **Framework Configurations**: Patterns for discovering agents and tools in popular AI frameworks

## Quick Start

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

## Configuration Schema

### Evaluations

Evaluation TOML files define test cases for agents and tools:

- **Evaluation Types**: accuracy, performance, consistency, safety, llm, custom
- **String Matching**: exact, contains, regex, semantic similarity
- **Schema Validation**: Validate structured JSON outputs
- **Tool Calls**: Verify correct tool usage
- **Multiple Iterations**: Run tests multiple times for consistency

[Full Evaluation Schema →](guide/evaluations.md)

### Frameworks

Framework TOML files define agent and tool discovery patterns:

- **Built-in Frameworks**: LangChain, LlamaIndex, Pydantic AI
- **Custom Frameworks**: Define your own patterns
- **Agent Discovery**: Map framework parameters to standard fields
- **Tool Discovery**: Configure tool types (decorator, function, class, constructor)
- **Execution Config**: Define how to run agents and tools

[Full Framework Schema →](guide/frameworks.md)

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

## Next Steps

- [Evaluation Schema Guide](guide/evaluations.md) - Complete TOML schema for evaluations
- [Framework Schema Guide](guide/frameworks.md) - Complete TOML schema for frameworks
- [Python API](python-api.md) - Programmatic usage (optional)
