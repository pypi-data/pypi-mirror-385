# Advanced Framework Configuration

This guide provides detailed examples and practical workflows for creating and customizing framework configurations.

## Understanding Discovery and Execution

### How Agent Discovery Works

When AgentCI scans your code, it:
1. Searches for calls to the specified `path` (e.g., `Agent(...)` or `create_react_agent(...)`)
2. Extracts the variable name the agent is assigned to
3. Looks for the parameters specified in `args.model`, `args.prompt`, and `args.tools`
4. Captures the values passed to those parameters (extracting model names, prompt text, and tool lists)
5. Stores the source code location and extracted metadata

**Example of what gets discovered:**

```python
# Your code:
my_agent = Agent(
    llm="gpt-4",
    system_prompt="You are a helpful assistant",
    tools=[search_tool, calculator]
)

# With config:
# [[agents]]
# path = "my_framework.Agent"
# args.model = "llm"
# args.prompt = "system_prompt"
# args.tools = "tools"

# AgentCI discovers:
# - Agent name: "my_agent"
# - Model: "gpt-4"
# - System prompt: "You are a helpful assistant"
# - Tools: ["search_tool", "calculator"]
# - File location and source code
```

### How Agent Execution Works

When AgentCI runs an evaluation test case:
1. It loads the discovered agent object from your code
2. Calls the method specified in `execution.method`
3. Passes the test case prompt to the parameter named in `execution.args.prompt`

**Example:**

```toml
[[agents]]
path = "langchain.agents.AgentExecutor"
execution.method = "invoke"
execution.args.prompt = "input"
```

This configuration tells AgentCI to execute agents like:
```python
result = agent.invoke(input="What is the weather?")
```

Different frameworks use different method names and parameter names:
- LangChain: `agent.invoke(input="...")` or `agent.run(input="...")`
- LlamaIndex: `agent.chat(message="...")`
- Pydantic AI: `agent.run(user_prompt="...")`

### How Tool Discovery Works

Tool discovery behavior varies by type:
- **Decorator**: Finds functions with the specified decorator
- **Constructor**: Finds calls to the specified constructor/factory method
- **Class**: Finds classes that inherit from the specified base class
- **Function**: Finds all public (non-underscore) functions

### How Tool Execution Works

When AgentCI needs to execute a tool during evaluation:
1. It loads the discovered tool object from your code
2. Calls the method specified in `execution.method`
3. Passes the test case `context` as arguments

**Common execution patterns:**

- **`__call__`**: Direct function call (for functions and callable objects)
  ```python
  result = tool(context)  # or tool(**context) if context is a dict
  ```

- **`invoke`**: Framework-specific method (LangChain pattern)
  ```python
  result = tool.invoke(context)
  ```

- **`run`**: Alternative execution method (some frameworks)
  ```python
  result = tool.run(context)
  ```

**Context Handling:**

The test case `context` field is passed to tools differently based on its type:

```toml
# Dict context - unpacked as keyword arguments
[[eval.cases]]
context = { query = "search term", limit = 10 }
# Executes as: tool(query="search term", limit=10)

# String/primitive context - passed as single argument
[[eval.cases]]
context = "search term"
# Executes as: tool("search term")
```

If no `context` is provided but a `prompt` exists, the prompt is passed as the argument.

**Async Support:**

AgentCI automatically detects and handles async tools:
```python
async def async_tool(query: str) -> str:
    return await async_search(query)

# AgentCI will await the result automatically
```

## Variable Resolution

AgentCI can resolve variable references when extracting values:

```python
# Direct value
agent1 = Agent(llm="gpt-4")  # Extracts: "gpt-4"

# Variable reference
llm = ChatOpenAI(model="gpt-4")
agent2 = Agent(llm=llm)  # Extracts: "gpt-4" (resolves from llm variable)

# Inline call
agent3 = Agent(llm=ChatOpenAI(model="gpt-4"))  # Extracts: "gpt-4"
```

## Positional vs Keyword Arguments

AgentCI supports both positional and keyword arguments:

```python
# Keyword argument (preferred for clarity)
agent = create_agent(llm=model, prompt=system_prompt, tools=tool_list)

# Positional argument (order matters)
agent = create_agent(model, system_prompt, tool_list)
```

For positional arguments to work, AgentCI inspects the function signature of the `path` to map positions to parameter names.

## Agent Type Examples

### Constructor Pattern

Direct class instantiation:

```python
agent = Agent(llm=model, tools=tools)
agent = create_react_agent(llm=model, prompt=prompt, tools=tools)
```

```toml
[[agents]]
path = "my_framework.Agent"
type = "constructor"
args.model = "llm"
args.tools = "tools"
```

### Class Method Pattern

Static or class method that creates an agent:

```python
agent = Agent.from_tools(llm=model, tools=tools)
agent = ReActAgent.from_llm(llm=model, tools=tools)
```

```toml
[[agents]]
path = "my_framework.Agent.from_tools"
type = "class_method"  # Must be explicit for class methods
args.model = "llm"
args.tools = "tools"
```

### Function Pattern

Factory function that returns an agent:

```python
agent = create_agent(llm=model, prompt=prompt)
agent = initialize_agent(llm=model, tools=tools)
```

```toml
[[agents]]
path = "my_framework.create_agent"
type = "function"
args.model = "llm"
args.prompt = "prompt"
```

## Tool Type Examples

### Decorator Pattern

Tools created with a decorator:

```python
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search the web for information."""
    return search_api(query)
```

```toml
[[tools]]
type = "decorator"
path = "langchain_core.tools.tool"
execution.method = "invoke"
```

Discovery extracts the function name (`search`) and its implementation.

Executes as: `search.invoke(query="...")`

### Constructor Pattern

Tools created with a class method or factory function:

```python
from llama_index.core.tools import FunctionTool

search_tool = FunctionTool.from_defaults(
    fn=search_function,
    name="search",
    description="Search the web"
)
```

```toml
[[tools]]
type = "constructor"
path = "llama_index.core.tools.FunctionTool.from_defaults"
execution.method = "__call__"
```

Discovery finds calls to `FunctionTool.from_defaults` and extracts the assigned variable name.

Executes as: `search_tool(query="...")`

### Class Pattern

Tools that inherit from a base class:

```python
from langchain_core.tools import BaseTool

class SearchTool(BaseTool):
    name = "search"
    description = "Search the web"

    def _run(self, query: str) -> str:
        return search_api(query)

search_tool = SearchTool()
```

```toml
[[tools]]
type = "class"
path = "langchain_core.tools.BaseTool"
execution.method = "invoke"
```

Discovery finds classes that inherit from `BaseTool` and extracts their implementations.

Executes as: `search_tool.invoke(query="...")`

### Function Pattern

Plain Python functions used as tools (no decorator needed):

```python
def search(query: str) -> str:
    """Search the web for information."""
    return search_api(query)

def calculate(expression: str) -> float:
    """Evaluate a mathematical expression."""
    return eval(expression)
```

```toml
[[tools]]
type = "function"
# No path needed - discovers all public functions
execution.method = "__call__"
```

Discovery finds all public functions (names not starting with `_`) in files that import the framework.

Executes as: `search(query="...")` and `calculate(expression="...")`

## Practical Workflow: Creating a Custom Framework Config

Let's walk through creating a framework config for a hypothetical custom framework.

### Step 1: Identify Your Framework Patterns

Look at how your framework creates agents and tools:

```python
# Your framework code
from my_framework import Agent, tool

# Agent creation pattern
agent = Agent(
    model="gpt-4",
    system_prompt="You are helpful",
    tools=[search, calculator]
)

# Tool creation pattern
@tool
def search(query: str) -> str:
    """Search for information."""
    return search_api(query)

# Agent execution
result = agent.execute(user_input="What is the weather?")
```

### Step 2: Create the TOML Config

Create `.agentci/frameworks/my_framework.toml`:

```toml
[framework]
name = "my-framework"
dependencies = ["my-framework", "my_framework"]  # Both naming variants

# Agent discovery
[[agents]]
path = "my_framework.Agent"
type = "constructor"  # Direct instantiation: Agent(...)

# Map framework parameter names to standard fields
args.model = "model"         # Agent constructor uses 'model' parameter
args.prompt = "system_prompt"  # Agent constructor uses 'system_prompt' parameter
args.tools = "tools"         # Agent constructor uses 'tools' parameter

# Agent execution
execution.method = "execute"           # Call agent.execute(...)
execution.args.prompt = "user_input"   # Pass prompt as 'user_input' parameter

# Tool discovery
[[tools]]
type = "decorator"
path = "my_framework.tool"
execution.method = "__call__"  # Direct function call
```

### Step 3: Test Discovery

Use the Python API to verify discovery works:

```python
from pathlib import Path
from agentci.client_config import discover_frameworks

# Discover frameworks (will include your custom config)
frameworks = discover_frameworks(Path("."))

# Find your framework
my_framework = next(f for f in frameworks if f.name == "my-framework")
print(f"Found framework: {my_framework.framework.name}")
print(f"Agent patterns: {len(my_framework.agents)}")
print(f"Tool patterns: {len(my_framework.tools)}")
```

### Step 4: Verify Execution

Create a simple evaluation to test execution:

```toml
# .agentci/evals/test_framework.toml
[eval]
description = "Test custom framework integration"
type = "accuracy"

[eval.targets]
agents = ["*"]

[[eval.cases]]
prompt = "Hello"
expected.contains = "hi"
```

## Overriding Built-in Configurations

To override a built-in framework config, create a file in `.agentci/frameworks/` with the same `name`:

### Example: Customizing LangChain Config

Create `.agentci/frameworks/langchain.toml`:

```toml
[framework]
name = "langchain"  # Same name as built-in config
dependencies = ["langchain", "langchain-core"]

# Add custom agent pattern not in built-in config
[[agents]]
path = "my_custom_langchain.CustomAgent"
args.model = "llm"
args.tools = "tools"
execution.method = "run"
execution.args.prompt = "input"

# Include standard LangChain patterns you still want
[[agents]]
path = "langchain.agents.create_react_agent"
args.model = "llm"
args.prompt = "prompt"
args.tools = "tools"
execution.method = "run"
execution.args.prompt = "input"
```

Your custom configuration completely replaces the built-in one, so include any built-in patterns you still need.

## Complete Examples

### LangChain-style Framework

```toml
[framework]
name = "my-langchain-clone"
dependencies = ["my-langchain"]

# Multiple agent patterns
[[agents]]
path = "my_langchain.agents.create_react_agent"
args.model = "llm"
args.prompt = "prompt"
args.tools = "tools"
execution.method = "invoke"
execution.args.prompt = "input"

[[agents]]
path = "my_langchain.agents.AgentExecutor"
type = "constructor"
args.model = "llm"
args.tools = "tools"
execution.method = "run"
execution.args.prompt = "input"

# Multiple tool patterns
[[tools]]
type = "decorator"
path = "my_langchain.tools.tool"
execution.method = "invoke"

[[tools]]
type = "class"
path = "my_langchain.tools.BaseTool"
execution.method = "invoke"
```

### LlamaIndex-style Framework

```toml
[framework]
name = "my-llamaindex-clone"
dependencies = ["my-llamaindex", "my_llamaindex"]

# Class method agent pattern
[[agents]]
path = "my_llamaindex.agent.ReActAgent.from_tools"
type = "class_method"
args.model = "llm"
args.tools = "tools"
execution.method = "chat"
execution.args.prompt = "message"

# Constructor tool pattern
[[tools]]
type = "constructor"
path = "my_llamaindex.tools.FunctionTool.from_defaults"
execution.method = "__call__"
```

### Minimal Function-based Framework

```toml
[framework]
name = "simple-framework"
dependencies = ["simple-framework"]

# Simple function-based agents
[[agents]]
path = "simple_framework.create_agent"
type = "function"
args.model = "model"
args.prompt = "prompt"
execution.method = "run"
execution.args.prompt = "message"

# Function-based tools (no decorator)
[[tools]]
type = "function"
execution.method = "__call__"
```

## Framework Detection Deep Dive

### How Dependencies Are Checked

AgentCI reads project dependencies from multiple sources:
1. `pyproject.toml` - `[project.dependencies]` and `[tool.poetry.dependencies]`
2. `requirements.txt` - All listed packages
3. `setup.py` - `install_requires` list

For each framework config, it checks if **any** dependency in the config's `dependencies` list matches **any** installed package.

### Why Multiple Dependencies?

Frameworks often have multiple package names:
- Main package: `"langchain"`
- Core package: `"langchain-core"`
- Alternative naming: `"pydantic_ai"` vs `"pydantic-ai"`

Include all variants to ensure detection works regardless of how the user installed the framework.

### Testing Framework Detection

```python
from agentci.client_config import discover_frameworks
from pathlib import Path

# Discover all frameworks that match your project
frameworks = discover_frameworks(Path("."))

for framework in frameworks:
    print(f"Detected: {framework.framework.name}")
    print(f"  Dependencies: {framework.framework.dependencies}")
    print(f"  Agents: {len(framework.agents)}")
    print(f"  Tools: {len(framework.tools)}")
```
