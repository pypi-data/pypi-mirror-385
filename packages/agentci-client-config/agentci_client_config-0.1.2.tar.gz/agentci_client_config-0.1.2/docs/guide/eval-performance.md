---
title: "Performance Evaluations"
description: "Measure response latency, token usage, and resource consumption with configurable thresholds. Ensure your agents meet production performance and cost requirements."
---

# Performance Evaluations

Performance evaluations measure response time, latency, and resource usage with configurable thresholds. They're critical for ensuring your agents meet production performance requirements.

## What Performance Evaluations Test

Performance evaluations measure computational efficiency and speed:

- **Response latency** - How long agents take to respond
- **Token usage** - Input and output token consumption
- **Resource constraints** - Memory and processing limits
- **Throughput** - Requests processed per unit time

## When to Use Performance Evaluations

Use performance evaluations to ensure production readiness:

- ✅ **Production deployment** - Verify agents meet SLA requirements
- ✅ **Cost optimization** - Monitor token usage and resource consumption
- ✅ **User experience** - Ensure acceptable response times
- ✅ **Load testing** - Validate performance under concurrent requests
- ✅ **Regression detection** - Catch performance degradations early
- ❌ **Functional correctness** - Use accuracy evaluations instead
- ❌ **Content quality** - Use LLM or semantic evaluations instead

## Configuration

### Basic Configuration

```toml
[eval]
description = "Test response performance"
type = "performance"
targets.agents = ["*"]               # Test all agents
targets.tools = []                   # Skip tools
```

### Supported Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | String | Yes | Brief description of the test |
| `type` | String | Yes | Must be `"performance"` |
| `targets.agents` | Array[String] | Yes | Agents to test (`["*"]` for all) |
| `targets.tools` | Array[String] | Yes | Tools to test (`["*"]` for all) |
| `iterations` | Integer | No | Times to run each test case (default: 1) |

## Test Cases

### Basic Test Case Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | String | No* | Input prompt for agents |
| `context` | Object | No* | Parameters for tools or agent context |
| `latency` | Object | No | Latency constraints and thresholds |
| `tokens` | Object | No | Token usage constraints |

*Either `prompt` or `context` (or both) must be provided

### Latency Configuration

The `latency` object supports these fields:

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `max` | Number | seconds | Maximum allowed response time |
| `max_ms` | Number | milliseconds | Maximum allowed response time |
| `min` | Number | seconds | Minimum expected response time |
| `min_ms` | Number | milliseconds | Minimum expected response time |

### Token Configuration

The `tokens` object supports these fields:

| Field | Type | Description |
|-------|------|-------------|
| `max` | Number | Maximum total tokens (input + output) |
| `min` | Number | Minimum total tokens (input + output) |
| `input_max` | Number | Maximum input tokens |
| `input_min` | Number | Minimum input tokens |
| `output_max` | Number | Maximum output tokens |
| `output_min` | Number | Minimum output tokens |

## Examples

### Basic Latency Testing

```toml
[eval]
description = "Test basic response times"
type = "performance"
targets.agents = ["*"]
targets.tools = []

# Simple questions should be fast
[[eval.cases]]
prompt = "What is 2 + 2?"
latency = { max_ms = 1000 }          # Must respond within 1 second

# Complex queries can take longer
[[eval.cases]]
prompt = "Analyze this quarterly report and provide insights"
latency = { max = 30 }               # Allow up to 30 seconds
```

### Token Usage Monitoring

```toml
[eval]
description = "Monitor token consumption"
type = "performance"
targets.agents = ["chat-assistant"]
targets.tools = []

# Short responses for simple questions
[[eval.cases]]
prompt = "Say hello"
tokens = { max = 50, output_max = 10 }

# Reasonable limits for complex tasks
[[eval.cases]]
prompt = "Explain quantum physics in simple terms"
tokens = { max = 1000, output_min = 100, output_max = 500 }
```

### Combined Performance Testing

```toml
[eval]
description = "Comprehensive performance validation"
type = "performance"
targets.agents = ["customer-support"]
targets.tools = []

# Fast, efficient responses for common questions
[[eval.cases]]
prompt = "What are your business hours?"
latency = { max_ms = 2000 }
tokens = { max = 100 }

# Reasonable performance for complex issues
[[eval.cases]]
prompt = "I'm having trouble with my account setup. Can you help me troubleshoot?"
latency = { max = 15 }
tokens = { max = 800, min = 200 }
```

### Tool Performance Testing

```toml
[eval]
description = "Test API tool performance"
type = "performance"
targets.agents = []
targets.tools = ["weather-api", "database-query"]

# API calls should be fast
[[eval.cases]]
context = { city = "San Francisco" }
latency = { max_ms = 3000 }          # API timeout

# Database queries should be efficient
[[eval.cases]]
context = { query = "SELECT * FROM users LIMIT 10" }
latency = { max_ms = 500 }
```

### Load Testing Simulation

```toml
[eval]
description = "Simulate concurrent load"
type = "performance"
targets.agents = ["api-assistant"]
targets.tools = []
iterations = 10                      # Run each test 10 times

[[eval.cases]]
prompt = "Process this data"
latency = { max = 5 }
tokens = { max = 500 }
```

### Performance Regression Testing

```toml
[eval]
description = "Detect performance regressions"
type = "performance"
targets.agents = ["*"]
targets.tools = []

# Baseline performance expectations
[[eval.cases]]
prompt = "Simple greeting"
latency = { max_ms = 800 }           # Should be very fast

[[eval.cases]]
prompt = "Medium complexity task"
latency = { max = 10 }               # Reasonable response time

[[eval.cases]]
prompt = "Complex analysis request"
latency = { max = 45 }               # Allow longer for complex tasks
```

## Best Practices

### Setting Realistic Thresholds

1. **Baseline first, then optimize:**
   ```toml
   # Start with generous limits
   [[eval.cases]]
   prompt = "Test query"
   latency = { max = 60 }

   # Tighten limits as you optimize
   latency = { max = 30 }
   latency = { max = 15 }
   ```

2. **Account for external dependencies:**
   ```toml
   # API calls need higher latency allowances
   [[eval.cases]]
   context = { external_api_call = true }
   latency = { max = 10 }             # Account for network latency

   # Local processing can be faster
   [[eval.cases]]
   prompt = "Local calculation"
   latency = { max_ms = 2000 }
   ```

### Token Optimization

1. **Monitor input efficiency:**
   ```toml
   [[eval.cases]]
   prompt = "Brief question"
   tokens = { input_max = 20, output_max = 50 }
   ```

2. **Prevent runaway outputs:**
   ```toml
   [[eval.cases]]
   prompt = "Explain this concept"
   tokens = { output_max = 300 }      # Prevent excessive responses
   ```

### Performance Testing Strategy

1. **Test different complexity levels:**
   ```toml
   # Simple tasks
   [[eval.cases]]
   prompt = "What is 1+1?"
   latency = { max_ms = 500 }

   # Medium tasks
   [[eval.cases]]
   prompt = "Summarize this paragraph"
   latency = { max = 5 }

   # Complex tasks
   [[eval.cases]]
   prompt = "Analyze and provide detailed recommendations"
   latency = { max = 30 }
   ```

2. **Use iterations for consistency:**
   ```toml
   [eval]
   iterations = 5                     # Run multiple times for average

   [[eval.cases]]
   prompt = "Performance test"
   latency = { max = 10 }
   ```

### Production Readiness Checklist

Use performance evaluations to verify:

- ✅ **95th percentile response time** under acceptable limits
- ✅ **Token costs** within budget constraints
- ✅ **No timeout failures** under normal load
- ✅ **Consistent performance** across multiple runs
- ✅ **Resource usage** stays within limits

## Advanced Configuration

### Time Unit Flexibility

```toml
# Use seconds for longer operations
latency = { max = 30 }

# Use milliseconds for precise timing
latency = { max_ms = 1500 }

# Mix units as needed
latency = { min_ms = 100, max = 5 }
```

### Range Testing

```toml
# Ensure responses aren't too fast (may indicate errors)
# or too slow (poor user experience)
[[eval.cases]]
prompt = "Standard query"
latency = { min_ms = 200, max_ms = 3000 }
tokens = { min = 10, max = 200 }
```

### Multiple Iterations for Statistics

```toml
[eval]
description = "Statistical performance analysis"
type = "performance"
iterations = 20                      # Run 20 times for statistics

[[eval.cases]]
prompt = "Benchmark query"
latency = { max = 5 }               # Average should be under 5 seconds
```

## Troubleshooting

### Common Issues

**Intermittent failures:**
```toml
# Use higher iteration counts to catch inconsistent performance
[eval]
iterations = 10

[[eval.cases]]
prompt = "Test case"
latency = { max = 15 }
```

**Cold start delays:**
```toml
# Account for cold start latency in serverless environments
[[eval.cases]]
prompt = "First request"
latency = { max = 20 }               # Allow extra time for cold starts
```

**Token counting discrepancies:**
```toml
# Be generous with token limits during initial testing
[[eval.cases]]
prompt = "Test response"
tokens = { max = 1000 }             # Start high, optimize down
```

### Performance Debugging

1. **Start with broad limits:**
   ```toml
   # Begin with generous thresholds
   latency = { max = 60 }
   tokens = { max = 2000 }
   ```

2. **Gradually tighten constraints:**
   ```toml
   # Iteratively reduce limits
   latency = { max = 30 }
   latency = { max = 15 }
   latency = { max = 10 }
   ```

3. **Use multiple test cases for different scenarios:**
   ```toml
   # Test various input complexities
   [[eval.cases]]
   prompt = "Simple"
   latency = { max = 2 }

   [[eval.cases]]
   prompt = "Complex analysis with multiple steps"
   latency = { max = 20 }
   ```

## Interpreting Results

Performance evaluation results include:

- **Average latency** across all iterations
- **95th percentile latency** for reliability assessment
- **Token usage statistics** for cost analysis
- **Success/failure rates** for reliability metrics
- **Performance trends** over time

## Next Steps

- [Safety Evaluations](eval-safety.md) - Test security and content filtering
- [Consistency Evaluations](eval-consistency.md) - Verify reliable behavior
- [Configuration Overview](evaluations.md) - Complete TOML reference