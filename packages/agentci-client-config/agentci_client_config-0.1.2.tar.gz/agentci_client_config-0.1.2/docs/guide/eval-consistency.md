---
title: "Consistency Evaluations"
description: "Test output variance and behavioral reliability across multiple runs. Ensure deterministic behavior and detect regressions in agent consistency over time."
---

# Consistency Evaluations

Consistency evaluations test output variance across multiple runs of identical inputs. They ensure reliable agent behavior by measuring how much responses differ when given the same prompt multiple times.

## What Consistency Evaluations Test

Consistency evaluations measure response reliability and determinism:

- **Output variance** - How much responses differ across multiple runs
- **Deterministic behavior** - Ensuring identical inputs produce identical outputs
- **Semantic stability** - Maintaining consistent meaning even with different wording
- **Behavioral reliability** - Predictable agent responses in production
- **Regression detection** - Identifying when agents become less consistent over time

## When to Use Consistency Evaluations

Use consistency evaluations to ensure predictable behavior:

- ✅ **Production reliability** - Verify agents behave consistently for users
- ✅ **Mathematical operations** - Ensure calculations always return the same result
- ✅ **Factual queries** - Verify consistent factual information delivery
- ✅ **API responses** - Ensure tools produce reliable structured outputs
- ✅ **Quality assurance** - Detect when agents become unpredictable
- ✅ **A/B testing validation** - Ensure control groups remain consistent
- ❌ **Creative tasks** - Some variation may be desirable for creative content
- ❌ **Contextual responses** - When responses should adapt to subtle context changes

## Configuration

### Basic Configuration

```toml
[eval]
description = "Test response consistency"
type = "consistency"
targets.agents = ["*"]               # Test all agents
targets.tools = []                   # Skip tools
iterations = 5                       # Run each test case 5 times (required > 1)

[eval.consistency]
model = "openai/text-embedding-3-small"  # Optional: embedding model for similarity
```

### Supported Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | String | Yes | Brief description of the test |
| `type` | String | Yes | Must be `"consistency"` |
| `targets.agents` | Array[String] | Yes | Agents to test (`["*"]` for all) |
| `targets.tools` | Array[String] | Yes | Tools to test (`["*"]` for all) |
| `iterations` | Integer | Yes | Number of runs per test case (minimum: 2) |

> **Note:** Consistency evaluations require `iterations > 1` to measure variance across multiple runs.

## Test Cases

### Basic Test Case Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | String | No* | Input prompt for agents |
| `context` | Object | No* | Parameters for tools or agent context |
| `min_similarity` | Number | No | Minimum semantic similarity (0.0-1.0, default: 1.0) |
*Either `prompt` or `context` (or both) must be provided

### Similarity Thresholds

| Threshold | Interpretation | Example Use Case |
|-----------|---------------|------------------|
| `1.0` | Perfect consistency required (default) | Mathematical calculations |
| `0.9` | Very high consistency | Factual information, API responses |
| `0.8` | High consistency | Structured explanations |
| `0.7` | Moderate consistency | General Q&A with some flexibility |
| `0.6` | Low consistency acceptable | Creative or contextual responses |

**Note:** `min_similarity` measures how similar outputs must be (higher = more consistent), using semantic embeddings to compare responses.

## Examples

### Mathematical Consistency

```toml
[eval]
description = "Test mathematical calculation consistency"
type = "consistency"
targets.agents = ["calculator-agent"]
targets.tools = []
iterations = 10

# Calculations must be identical every time
[[eval.cases]]
prompt = "Calculate 15 * 23"
min_similarity = 1.0

[[eval.cases]]
prompt = "What is the square root of 144?"
min_similarity = 1.0

[[eval.cases]]
prompt = "Convert 100 Fahrenheit to Celsius"
min_similarity = 1.0
```

### Factual Information Consistency

```toml
[eval]
description = "Test factual knowledge consistency"
type = "consistency"
targets.agents = ["knowledge-base"]
targets.tools = []
iterations = 5

# Factual answers should be semantically consistent
[[eval.cases]]
prompt = "What is the capital of France?"
min_similarity = 0.9

[[eval.cases]]
prompt = "When was the first iPhone released?"
min_similarity = 0.9

[[eval.cases]]
prompt = "What is the boiling point of water?"
min_similarity = 1.0
```

### API Response Consistency

```toml
[eval]
description = "Test tool output consistency"
type = "consistency"
targets.agents = []
targets.tools = ["weather-api"]
iterations = 8

# API responses should have consistent structure
[[eval.cases]]
context = { city = "San Francisco", units = "metric" }
min_similarity = 0.9

[[eval.cases]]
context = { city = "London", date = "2024-01-15" }
min_similarity = 0.9
```

### Customer Support Consistency

```toml
[eval]
description = "Test customer support response consistency"
type = "consistency"
targets.agents = ["customer-support"]
targets.tools = []
iterations = 6

# Policy information should be very consistent
[[eval.cases]]
prompt = "What is your return policy?"
min_similarity = 0.9

# General help should be reasonably consistent
[[eval.cases]]
prompt = "I need help with my account"
min_similarity = 0.7

# Complex troubleshooting allows more variance
[[eval.cases]]
prompt = "My application isn't working properly. Can you help me debug this issue?"
min_similarity = 0.6
```

### Mixed Variance Requirements

```toml
[eval]
description = "Mixed consistency requirements"
type = "consistency"
targets.agents = ["general-assistant"]
targets.tools = []
iterations = 5

# Greetings can vary slightly
[[eval.cases]]
prompt = "Hello!"
min_similarity = 0.7

# Instructions should be consistent
[[eval.cases]]
prompt = "How do I reset my password?"
min_similarity = 0.8

# Calculations must be exact
[[eval.cases]]
prompt = "What is 25% of 400?"
min_similarity = 1.0
```

## Advanced Configuration

### Multi-Modal Consistency

```toml
[eval]
description = "Test consistency across different input patterns"
type = "consistency"
targets.agents = ["multi-modal-agent"]
targets.tools = []
iterations = 5

# Same question, different phrasing - should be consistent
[[eval.cases]]
prompt = "What is the weather like today?"
min_similarity = 0.8

[[eval.cases]]
prompt = "How's the weather?"
min_similarity = 0.8

[[eval.cases]]
prompt = "Tell me about today's weather conditions"
min_similarity = 0.8
```

### Tool Parameter Consistency

```toml
[eval]
description = "Test tool parameter consistency"
type = "consistency"
targets.agents = []
targets.tools = ["database-query"]
iterations = 10

# Same query should return identical results
[[eval.cases]]
context = {
  query = "SELECT COUNT(*) FROM users WHERE status = 'active'",
  connection = "primary_db"
}
min_similarity = 1.0

# Different query formats for same data
[[eval.cases]]
context = {
  table = "users",
  filter = { status = "active" },
  operation = "count"
}
min_similarity = 1.0
```

### Time-Sensitive Consistency

```toml
[eval]
description = "Test consistency for time-sensitive queries"
type = "consistency"
targets.agents = ["news-agent"]
targets.tools = []
iterations = 3

# Current events should be consistent within short timeframes
[[eval.cases]]
prompt = "What are today's top news stories?"
min_similarity = 0.7                   # Allow some variation in selection/ordering

# Historical facts should be perfectly consistent
[[eval.cases]]
prompt = "When did World War II end?"
min_similarity = 1.0
```

## Best Practices

### Choosing Appropriate Similarity Thresholds

1. **Start conservative and adjust:**
   ```toml
   # Begin with strict requirements
   [[eval.cases]]
   prompt = "Test query"
   min_similarity = 0.9

   # Relax if too restrictive
   min_similarity = 0.8
   min_similarity = 0.7
   ```

2. **Match thresholds to use cases:**
   ```toml
   # Mathematical operations: exact consistency
   min_similarity = 1.0

   # Factual information: high similarity
   min_similarity = 0.9

   # Explanations: moderate similarity
   min_similarity = 0.7
      ```

### Optimal Iteration Counts

1. **Balance statistical significance with test speed:**
   ```toml
   # Quick consistency checks
   iterations = 3

   # Standard consistency validation
   iterations = 5

   # High-confidence consistency measurement
   iterations = 10

   # Statistical analysis
   iterations = 20
   ```

2. **Consider computational cost:**
   ```toml
   # For expensive operations, use fewer iterations
   [eval]
   iterations = 3

   [[eval.cases]]
   prompt = "Complex analysis task"
   min_similarity = 0.8
   ```

### Similarity Type Selection

```toml
# Use exact matching for deterministic outputs
[[eval.cases]]
prompt = "Calculate 2 + 2"
min_similarity = 1.0

# Use semantic matching for natural language
[[eval.cases]]
prompt = "Explain photosynthesis"
min_similarity = 0.8

# Use structural matching for JSON/data outputs
[[eval.cases]]
context = { api_call = "user_info" }
min_similarity = 0.9
```

## Advanced Analysis

### Statistical Consistency Metrics

Consistency evaluations provide detailed metrics:

- **Mean variance** - Average variance across all iterations
- **Standard deviation** - Spread of variance measurements
- **Outlier detection** - Identify inconsistent individual responses
- **Trend analysis** - Detect increasing/decreasing consistency over time
- **Confidence intervals** - Statistical significance of consistency measurements

### Consistency Patterns

1. **Identify consistency patterns:**
   ```toml
   # Test different types of queries
   [[eval.cases]]
   prompt = "Simple factual question"
   min_similarity = 0.9

   [[eval.cases]]
   prompt = "Complex multi-step reasoning"
   min_similarity = 0.6                 # Complex tasks may have more variance
   ```

2. **Monitor consistency trends:**
   ```toml
   # Regression detection
   [eval]
   description = "Consistency regression monitoring"
   iterations = 10

   [[eval.cases]]
   prompt = "Baseline consistency test"
   min_similarity = 0.8
   ```

## Troubleshooting

### High Variance Issues

```toml
# If variance is higher than expected, investigate:

# 1. Check if the task is inherently variable
[[eval.cases]]
prompt = "Generate a creative story"    # Expect high variance
min_similarity = 0.6

# 2. Verify agent determinism settings
[[eval.cases]]
prompt = "Deterministic task"
min_similarity = 0.9                     # Should be high similarity

# 3. Test with more iterations for statistical significance
[eval]
iterations = 15                        # More data points
```

### Low Variance Concerns

```toml
# If variance is too low, ensure:

# 1. The agent isn't overly constrained
[[eval.cases]]
prompt = "Explain this concept in your own words"
min_similarity = 0.7                     # Allow natural variation

# 2. Test different complexity levels
[[eval.cases]]
prompt = "Simple greeting"
min_similarity = 0.8

[[eval.cases]]
prompt = "Complex explanation"
min_similarity = 0.6                     # Complex tasks can vary more
```

### Iteration Optimization

```toml
# Find optimal iteration count:

# Start with few iterations
iterations = 3

# Increase if results are unstable
iterations = 5

# Use many iterations for critical consistency
iterations = 20
```

## Production Considerations

### Consistency Monitoring

Use consistency evaluations for:

- **Deployment validation** - Ensure new versions maintain consistency
- **Performance monitoring** - Track consistency degradation over time
- **A/B testing** - Validate that control groups remain stable
- **Quality assurance** - Detect when agents become unpredictable

### Consistency vs. Flexibility Trade-offs

Balance consistency requirements with natural variation:

```toml
# Strict consistency for critical operations
[[eval.cases]]
prompt = "Security policy information"
min_similarity = 0.9

# Allow flexibility for user experience
[[eval.cases]]
prompt = "Casual conversation"
min_similarity = 0.6
```

## Next Steps

- [LLM Evaluations](eval-llm.md) - AI-powered quality assessment
- [Performance Evaluations](eval-performance.md) - Speed and resource testing
- [Configuration Overview](evaluations.md) - Complete TOML reference