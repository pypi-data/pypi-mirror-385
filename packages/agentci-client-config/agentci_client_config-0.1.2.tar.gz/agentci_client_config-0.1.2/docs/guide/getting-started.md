# Getting Started

This guide will help you get started writing evaluation configurations for your AI agents and tools.

## Project Setup

Create a `.agentci/evals` directory in your project root:

```bash
mkdir -p .agentci/evals
```

Your project structure should look like:

```
your-project/
├── .agentci/
│   └── evals/              # Evaluation TOML files
├── src/
└── tests/
```

## Your First Evaluation

Create a TOML file in `.agentci/evals/` to define test cases for your agents:

```toml
# .agentci/evals/test_accuracy.toml
[eval]
description = "Test basic agent responses"
type = "accuracy"
targets.agents = ["*"]  # Test all agents
targets.tools = []      # Skip tools

[[eval.cases]]
prompt = "What is 2+2?"
output = "4"

[[eval.cases]]
prompt = "What is the capital of France?"
output.contains = "Paris"
```

## Evaluation Types

AgentCI supports six types of evaluations:

### 1. Accuracy
Test that outputs match expected values:

```toml
[eval]
description = "Test response accuracy"
type = "accuracy"
targets.agents = ["my-agent"]
targets.tools = []

[[eval.cases]]
prompt = "What is the capital of Japan?"
output.contains = "Tokyo"
```

### 2. Performance
Measure response time and token usage:

```toml
[eval]
description = "Test response speed"
type = "performance"
targets.agents = ["my-agent"]
targets.tools = []

[[eval.cases]]
prompt = "Quick question"
latency = { max_ms = 2000 }  # Must respond within 2 seconds
tokens = { max = 500 }        # Max 500 tokens
```

### 3. Safety
Test for harmful content and security issues:

```toml
[eval]
description = "Test prompt injection resistance"
type = "safety"
template = "prompt_injection"  # Use built-in safety tests
targets.agents = ["*"]
targets.tools = []
```

### 4. Consistency
Verify reproducible outputs across multiple runs:

```toml
[eval]
description = "Test output consistency"
type = "consistency"
targets.agents = ["my-agent"]
targets.tools = []
iterations = 5  # Run each test 5 times

[[eval.cases]]
prompt = "Calculate 15 * 23"
min_similarity = 1.0  # Expect exact same answer every time
```

### 5. LLM (AI-Powered Quality Assessment)
Use an LLM to evaluate subjective quality:

```toml
[eval]
description = "Evaluate response quality with AI"
type = "llm"
targets.agents = ["customer-support"]
targets.tools = []

[eval.llm]
model = "gpt-4"
prompt = "Rate the helpfulness of this response (1-10)"

[eval.llm.output_schema]
score = { type = "int", min = 1, max = 10 }
reasoning = { type = "str" }

[[eval.cases]]
prompt = "I need help with my account"
score = { min = 7 }  # Expect score of 7 or higher
```

### 6. Custom
Use your own Python evaluation logic:

```toml
[eval]
description = "Custom business logic validation"
type = "custom"
targets.agents = ["sales-agent"]
targets.tools = []

[eval.custom]
module = "my_evaluations.sales"
function = "validate_quote"

[[eval.cases]]
prompt = "Create a quote for 100 units"
parameters = { max_discount = 0.15 }
```

## Testing Tools Instead of Agents

You can also test tools directly by providing `context` instead of `prompt`:

```toml
[eval]
description = "Test weather API tool"
type = "accuracy"
targets.agents = []
targets.tools = ["weather-api"]

[[eval.cases]]
context = { city = "San Francisco" }  # Tool parameters

[eval.cases.output.schema]
temperature = { type = "float" }
condition = { type = "str" }
humidity = { type = "int" }
```

## TOML File Naming

The filename becomes the evaluation name:
- `accuracy_test.toml` → Evaluation name: `accuracy_test`
- `performance_test.toml` → Evaluation name: `performance_test`
- `safety_checks.toml` → Evaluation name: `safety_checks`

Use descriptive names that indicate what you're testing.

## Common Patterns

### Testing Specific Agents

```toml
[eval]
targets.agents = ["customer-support", "sales-agent"]  # Only test these
targets.tools = []
```

### Testing All Agents

```toml
[eval]
targets.agents = ["*"]  # Test all discovered agents
targets.tools = []
```

### Testing Multiple Cases

```toml
[eval]
description = "Comprehensive accuracy tests"
type = "accuracy"
targets.agents = ["*"]
targets.tools = []

[[eval.cases]]
prompt = "Test case 1"
output = "Expected result 1"

[[eval.cases]]
prompt = "Test case 2"
output.contains = "key phrase"

[[eval.cases]]
prompt = "Test case 3"
output = { similar = "semantic match", threshold = 0.8 }
```

## Next Steps

Now that you've created your first evaluation, explore detailed guides for each type:

### Evaluation Type Guides
- **[Accuracy](eval-accuracy.md)** - Exact matching, regex, semantic similarity, schema validation
- **[Performance](eval-performance.md)** - Latency, token usage, resource constraints
- **[Safety](eval-safety.md)** - Security testing with built-in templates
- **[Consistency](eval-consistency.md)** - Reliability testing across multiple runs
- **[LLM](eval-llm.md)** - AI-powered quality assessment
- **[Custom](eval-custom.md)** - Write your own evaluation logic in Python

### Reference Documentation
- **[Evaluations Overview](evaluations.md)** - Complete TOML schema reference
- **[Python API](../python-api.md)** - Programmatic usage (optional)

### Advanced Topics
- **[Framework Configuration](frameworks.md)** - Only needed if you're using a custom framework not already supported (LangChain, LlamaIndex, and Pydantic AI are built-in)
