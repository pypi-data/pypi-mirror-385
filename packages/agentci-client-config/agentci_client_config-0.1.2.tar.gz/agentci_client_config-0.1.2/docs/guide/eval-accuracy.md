---
title: "Accuracy Evaluations"
description: "Test agent outputs with exact matching, substring containment, regex patterns, semantic similarity, and schema validation. Essential for deterministic tasks and API responses."
---

# Accuracy Evaluations

Accuracy evaluations test whether agent or tool outputs match expected results using various matching strategies. They're essential for deterministic tasks and ensuring correct API responses.

## What Accuracy Evaluations Test

Accuracy evaluations verify that your agents produce the correct outputs for given inputs. They support multiple matching strategies:

- **Exact string matching** - Perfect matches for deterministic responses
- **Substring containment** - Verify key information appears in responses (`contains`, `contains_any`)
- **Prefix/suffix matching** - Check beginning or end of responses (`startswith`, `endswith`)
- **Regex pattern matching** - Complex pattern validation with regular expressions
- **Semantic similarity** - Verify meaning-based equivalence using embeddings
- **Schema validation** - Structured validation for tool outputs with comprehensive constraints

## When to Use Accuracy Evaluations

Use accuracy evaluations when you have clear expectations for correct outputs:

- ✅ **Mathematical calculations** - "What is 2 + 2?" should return "4"
- ✅ **Factual questions** - "Capital of France?" should contain "Paris"
- ✅ **API responses** - Tool outputs should match expected JSON structure
- ✅ **Structured data** - Validate format and required fields
- ❌ **Creative writing** - Use LLM evaluations instead
- ❌ **Subjective quality** - Use LLM or semantic evaluations instead

## Configuration

### Basic Configuration

```toml
[eval]
description = "Test response accuracy"
type = "accuracy"
targets.agents = ["*"]               # Test all agents
targets.tools = []                   # Skip tools
```

### Supported Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | String | Yes | Brief description of the test |
| `type` | String | Yes | Must be `"accuracy"` |
| `targets.agents` | Array[String] | Yes | Agents to test (`["*"]` for all) |
| `targets.tools` | Array[String] | Yes | Tools to test (`["*"]` for all) |
| `iterations` | Integer | No | Times to run each test case (default: 1) |

## Test Cases

### Basic Test Case Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | String | No* | Input prompt for agents |
| `context` | Object | No* | Parameters for tools or agent context |
| `output` | String/Object | Yes** | Expected output (string or matching strategy object) |
| `tools` | Array[Object] | No | Expected tool calls with arguments |

*Either `prompt` or `context` (or both) must be provided
**Either `output`, `output.schema`, or `tools` must be provided

## Matching Strategies

### 1. Exact String Match

```toml
[[eval.cases]]
prompt = "What is 2 + 2?"
output = "4"                         # Bare string = exact match
output.exact = "4"                   # Explicit exact match
```

### 2. Substring Containment

```toml
# Must contain specific substring
[[eval.cases]]
prompt = "What is the capital of France?"
output.contains = "Paris"

# Must contain ALL of these substrings
[[eval.cases]]
output.contains = ["Paris", "France"]

# Must contain ANY of these substrings
[[eval.cases]]
output.contains_any = ["Paris", "France", "French capital"]
```

### 3. Prefix/Suffix Matching

```toml
# Must start with text
[[eval.cases]]
output.startswith = "The answer is"

# Must start with ANY of these
[[eval.cases]]
output.startswith = ["Hi", "Hello", "Greetings"]

# Must end with text
[[eval.cases]]
output.endswith = "."

# Must end with ANY of these
[[eval.cases]]
output.endswith = ["!", "?", "."]
```

### 4. Regex Pattern Matching

```toml
[[eval.cases]]
prompt = "Format a phone number"
output.match = '''^\d{3}-\d{3}-\d{4}$''' # Must match regex pattern
```

### 5. Semantic Similarity

```toml
[[eval.cases]]
prompt = "Explain what HTTP is"
output = { similar = "HTTP is a protocol for transferring data over the web.", threshold = 0.8 }
```

### 6. Schema Validation (Tools and Structured Outputs)

For tool evaluations, validate structured outputs against TOML schemas:

```toml
[[eval.cases]]
context = { city = "San Francisco" }

[eval.cases.output.schema]
temperature = { type = "float" }
condition = { type = "str" }
humidity = { type = "int", min = 0, max = 100 }
```

See the [Schema Matching](#schema-matching) section for comprehensive schema validation options.

## Examples

### Agent Evaluations

**Mathematical calculations:**
```toml
[eval]
description = "Test basic math calculations"
type = "accuracy"
targets.agents = ["*"]
targets.tools = []

[[eval.cases]]
prompt = "Calculate 15 * 23"
output = "345"

[[eval.cases]]
prompt = "What is 100 divided by 4?"
output = "25"
```

**Factual questions:**
```toml
[eval]
description = "Test factual knowledge"
type = "accuracy"
targets.agents = ["knowledge-base"]
targets.tools = []

[[eval.cases]]
prompt = "What is the capital of Japan?"
output.contains = "Tokyo"

[[eval.cases]]
prompt = "When was the first iPhone released?"
output.contains = "2007"
```

**Semantic similarity:**
```toml
[eval]
description = "Test meaning-based matching"
type = "accuracy"
targets.agents = ["customer-support"]
targets.tools = []

[[eval.cases]]
prompt = "What's my order status for #12345?"
output = { similar = "Your order #12345 is currently being processed and will ship soon.", threshold = 0.75 }

[[eval.cases]]
prompt = "Tell me about pricing"
output.contains_any = ["$", "price", "cost", "plan"]
```

### Tool Evaluations

**API response validation:**
```toml
[eval]
description = "Test weather API tool"
type = "accuracy"
targets.agents = []
targets.tools = ["weather-api"]

[[eval.cases]]
context = { city = "New York", units = "metric" }

[eval.cases.output.schema]
temperature = { type = "float" }
condition = { type = "str" }
humidity = { type = "int", min = 0, max = 100 }
city = { type = "str" }

[[eval.cases]]
context = { city = "London", units = "imperial" }

[eval.cases.output.schema]
temperature = { type = "float" }
condition = { type = "str" }
```

**Database query validation:**
```toml
[eval]
description = "Test database queries"
type = "accuracy"
targets.agents = []
targets.tools = ["user-database"]

[[eval.cases]]
context = { query = "SELECT name FROM users WHERE id = 1" }
output.contains = "John Doe"

[[eval.cases]]
context = { query = "COUNT(*) FROM orders WHERE status = 'pending'" }
output.contains = "42"
```

### Mixed Agent and Tool Evaluation

```toml
[eval]
description = "Test order processing workflow"
type = "accuracy"
targets.agents = ["order-agent"]
targets.tools = ["order-database", "email-sender"]

[[eval.cases]]
prompt = "Process order #98765"
context = { order_id = "98765" }
output.contains = ["order", "98765", "processed"]
```

## Schema Matching

Schema matching validates structured output against defined field types and constraints. This is particularly useful for testing tools that return JSON objects or agents that produce structured data.

### Basic Field Types

```toml
[[eval.cases]]
prompt = "Get weather data"

[eval.cases.output.schema]
temperature = { type = "float" }
condition = { type = "str" }
humidity = { type = "int" }
is_raining = { type = "bool" }
```

### Field Validation Constraints

```toml
# String length constraints
[eval.cases.output.schema]
username = { type = "str", min_length = 3, max_length = 20 }

# Enum/Literal choices
status = { type = "str", enum = ["active", "inactive", "pending"] }

# Number bounds (inclusive)
age = { type = "int", min = 0, max = 120 }
percentage = { type = "float", min = 0.0, max = 100.0 }

# Optional fields and defaults
email = { type = "str", required = false }
timeout = { type = "int", default = 30 }
```

### Nested Objects

```toml
# Table syntax (recommended)
[[eval.cases]]
prompt = "Get product with pricing"

[eval.cases.output.schema]
id = { type = "int" }
name = { type = "str" }

[eval.cases.output.schema.pricing]
amount = { type = "float" }
currency = { type = "str" }
```

### Collections

```toml
# List of primitives
[eval.cases.output.schema]
tags = { type = "list[str]" }
scores = { type = "list[float]" }

# Set of unique values
unique_ids = { type = "set[int]" }

# List of objects with schema
products = { type = "list" }

[eval.cases.output.schema.products.items]
id = { type = "int" }
name = { type = "str" }
price = { type = "float" }

# Array size constraints
tags = { type = "list[str]", min_items = 1, max_items = 10 }
```

### String Matching on Field Values

Beyond type validation, you can apply string matching strategies to field values:

```toml
# Exact string match on field
[eval.cases.output.schema]
status = { type = "str", value = "operational" }

# Substring containment
error = { type = "str", value.contains = "timeout" }

# Regex pattern matching
email = { type = "str", value.match = '''^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$''' }

# Semantic similarity
message = { type = "str", value = { similar = "Welcome to our application!", threshold = 0.8 } }
```

### Complete Schema Example

```toml
[[eval.cases]]
prompt = "Create user profile"

[eval.cases.output.schema]
username = { type = "str", min_length = 3, max_length = 20 }
age = { type = "int", min = 13, max = 120 }
status = { type = "str", enum = ["active", "inactive"], default = "active" }
tags = { type = "list[str]", min_items = 1, max_items = 5 }
email = { type = "str", required = false }
```

## Best Practices

### Writing Effective Test Cases

1. **Be specific but not overly rigid:**
   ```toml
   # Good: Allows for natural language variation
   output.contains = ["Paris", "capital", "France"]

   # Better: Use semantic matching for natural language
   output = { similar = "Paris is the capital of France", threshold = 0.8 }

   # Bad: Too rigid, may fail on minor wording changes
   output = "The capital of France is Paris."
   ```

2. **Test edge cases:**
   ```toml
   [[eval.cases]]
   prompt = "What is 0 divided by 0?"
   output.contains_any = ["undefined", "indeterminate"]

   [[eval.cases]]
   prompt = "Calculate the square root of -1"
   output.contains_any = ["imaginary", "complex", "i"]
   ```

3. **Use meaningful descriptions:**
   ```toml
   [eval]
   description = "Test customer support agent handles order status inquiries correctly"
   ```

### Schema Validation Best Practices

1. **Required vs optional fields:**
   ```toml
   [eval.cases.output.schema]
   status = { type = "str" }                    # Required by default
   order_id = { type = "str" }
   estimated_delivery = { type = "str", required = false }  # Optional
   ```

2. **Validate data types and constraints:**
   ```toml
   [eval.cases.output.schema]
   temperature = { type = "float", min = -100, max = 100 }
   status = { type = "str", enum = ["sunny", "cloudy", "rainy"] }
   ```

### Performance Considerations

- Accuracy evaluations are fast and lightweight
- Schema validation adds minimal overhead
- Semantic similarity matching uses embeddings (slightly slower)
- Exact/substring matching is fastest
- Consider using multiple simple test cases rather than complex patterns

## Troubleshooting

### Common Issues

**Matching strategy selection:**
```toml
# Exact matching is case-insensitive
output = "paris"                     # Matches "Paris" or "PARIS"

# Use contains for flexibility
output.contains = "paris"            # More forgiving

# Use semantic for natural language
output = { similar = "Paris is the capital", threshold = 0.7 }
```

**Schema validation failures:**
```toml
# Make sure your schema matches the actual tool output format
# Check tool logs to see the exact structure

# Common issue: wrong type
temperature = { type = "int" }       # Tool returns 72.5 (float)
temperature = { type = "float" }     # Correct
```

### Debugging Tips

1. **Start broad and narrow down:**
   ```toml
   # Start with semantic matching
   output = { similar = "Expected meaning", threshold = 0.6 }

   # Or start with substring containment
   output.contains_any = ["key", "words"]

   # Then add more specificity
   output.contains = ["specific", "phrases"]

   # Finally, exact match if needed
   output = "exact response"
   ```

2. **Use multiple test cases for the same scenario:**
   ```toml
   # Test different phrasings
   [[eval.cases]]
   prompt = "Capital of France?"
   output.contains = "Paris"

   [[eval.cases]]
   prompt = "What city is the capital of France?"
   output.contains = "Paris"
   ```

## Next Steps

- [Performance Evaluations](eval-performance.md) - Test speed and resource usage
- [Safety Evaluations](eval-safety.md) - Validate security and content filtering
- [Configuration Overview](evaluations.md) - Complete TOML reference