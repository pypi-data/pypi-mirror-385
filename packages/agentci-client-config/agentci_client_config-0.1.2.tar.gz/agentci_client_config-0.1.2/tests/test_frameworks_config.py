"""Tests for framework configuration parsing and validation."""

import pytest
from pathlib import Path

from agentci.client_config.frameworks.schema import (
    FrameworkConfig,
    AgentType,
    ToolType,
    AgentConfig,
    ToolConfig,
    FrameworkMetadata,
    AgentDiscoveryArgs,
    AgentExecutionArgs,
    ExecutionConfig,
)
from agentci.client_config.frameworks.parser import parse_framework_config_toml


class TestFrameworkMetadata:
    """Test framework metadata validation."""

    def test_valid_metadata(self):
        """Test valid framework metadata."""
        metadata = FrameworkMetadata(
            name="test-framework",
            dependencies=["lib1", "lib2"],
        )
        assert metadata.name == "test-framework"
        assert metadata.dependencies == ["lib1", "lib2"]


class TestAgentDiscoveryArgs:
    """Test agent discovery arguments validation."""

    def test_valid_with_model(self):
        """Test valid discovery args with just model."""
        args = AgentDiscoveryArgs(model="llm")
        assert args.model == "llm"
        assert args.prompt is None
        assert args.tools is None

    def test_valid_with_all_args(self):
        """Test valid discovery args with all fields."""
        args = AgentDiscoveryArgs(model="llm", prompt="system_prompt", tools="tools")
        assert args.model == "llm"
        assert args.prompt == "system_prompt"
        assert args.tools == "tools"

    def test_requires_at_least_one_arg(self):
        """Test that at least one arg must be specified."""
        with pytest.raises(ValueError, match="At least one of"):
            AgentDiscoveryArgs()


class TestAgentExecutionArgs:
    """Test agent execution arguments validation."""

    def test_valid_execution_args(self):
        """Test valid execution args."""
        args = AgentExecutionArgs(prompt="user_input")
        assert args.prompt == "user_input"


class TestExecutionConfig:
    """Test execution configuration validation."""

    def test_execution_with_method_only(self):
        """Test execution config with just method."""
        exec_config = ExecutionConfig(method="run")
        assert exec_config.method == "run"
        assert exec_config.args is None

    def test_execution_with_args(self):
        """Test execution config with args mapping."""
        exec_args = AgentExecutionArgs(prompt="user_input")
        exec_config = ExecutionConfig(
            method="invoke",
            args=exec_args,
        )
        assert exec_config.method == "invoke"
        assert exec_config.args.prompt == "user_input"


class TestAgentConfig:
    """Test agent configuration validation."""

    def test_valid_agent_config(self):
        """Test valid agent configuration."""
        agent = AgentConfig(
            path="langchain.agents.Agent",
            args=AgentDiscoveryArgs(model="llm", prompt="system_prompt"),
            execution=ExecutionConfig(
                method="run",
                args=AgentExecutionArgs(prompt="input"),
            ),
        )
        assert agent.path == "langchain.agents.Agent"
        assert agent.type is None  # Optional
        assert agent.args.model == "llm"
        assert agent.args.prompt == "system_prompt"
        assert agent.execution.method == "run"
        assert agent.execution.args.prompt == "input"

    def test_agent_with_explicit_type(self):
        """Test agent with explicit type."""
        agent = AgentConfig(
            path="llama_index.Agent.from_tools",
            type=AgentType.CLASS_METHOD,
            args=AgentDiscoveryArgs(model="llm"),
            execution=ExecutionConfig(method="chat"),
        )
        assert agent.type == AgentType.CLASS_METHOD

    def test_agent_all_types(self):
        """Test all agent type enum values."""
        for agent_type in AgentType:
            # Use appropriate path format for class_method type
            path = "test.Agent.from_tools" if agent_type == AgentType.CLASS_METHOD else "test.Agent"
            agent = AgentConfig(
                path=path,
                type=agent_type,
                args=AgentDiscoveryArgs(model="llm"),
                execution=ExecutionConfig(method="run"),
            )
            assert agent.type == agent_type

    def test_agent_empty_path_fails(self):
        """Test that agent path cannot be empty."""
        with pytest.raises(ValueError, match="Agent path cannot be empty"):
            AgentConfig(
                path="",
                args=AgentDiscoveryArgs(model="llm"),
                execution=ExecutionConfig(method="run"),
            )

    def test_agent_whitespace_path_fails(self):
        """Test that agent path cannot be only whitespace."""
        with pytest.raises(ValueError, match="Agent path cannot be empty"):
            AgentConfig(
                path="   ",
                args=AgentDiscoveryArgs(model="llm"),
                execution=ExecutionConfig(method="run"),
            )

    def test_agent_class_method_requires_two_parts(self):
        """Test that class_method type requires path with Class.method format."""
        with pytest.raises(ValueError, match="requires path with at least 2 parts"):
            AgentConfig(
                path="Agent",
                type=AgentType.CLASS_METHOD,
                args=AgentDiscoveryArgs(model="llm"),
                execution=ExecutionConfig(method="run"),
            )

    def test_agent_class_method_valid_path(self):
        """Test that class_method accepts valid Class.method path."""
        agent = AgentConfig(
            path="llama_index.Agent.from_tools",
            type=AgentType.CLASS_METHOD,
            args=AgentDiscoveryArgs(model="llm"),
            execution=ExecutionConfig(method="run"),
        )
        assert agent.path == "llama_index.Agent.from_tools"
        assert agent.type == AgentType.CLASS_METHOD


class TestToolConfig:
    """Test tool configuration validation."""

    def test_tool_decorator(self):
        """Test decorator tool configuration."""
        tool = ToolConfig(
            type=ToolType.DECORATOR,
            path="langchain_core.tools.tool",
            execution=ExecutionConfig(method="invoke"),
        )
        assert tool.type == ToolType.DECORATOR
        assert tool.path == "langchain_core.tools.tool"

    def test_tool_function(self):
        """Test function tool configuration."""
        tool = ToolConfig(
            type=ToolType.FUNCTION,
            execution=ExecutionConfig(method="__call__"),
        )
        assert tool.type == ToolType.FUNCTION
        assert tool.path is None  # Not needed for functions

    def test_tool_all_types(self):
        """Test all tool type enum values."""
        for tool_type in ToolType:
            tool = ToolConfig(
                type=tool_type,
                path="test.Tool" if tool_type != ToolType.FUNCTION else None,
                execution=ExecutionConfig(method="run"),
            )
            assert tool.type == tool_type

    def test_tool_decorator_requires_path(self):
        """Test that decorator tools require a path."""
        with pytest.raises(ValueError, match="requires a path"):
            ToolConfig(
                type=ToolType.DECORATOR,
                execution=ExecutionConfig(method="invoke"),
            )

    def test_tool_constructor_requires_path(self):
        """Test that constructor tools require a path."""
        with pytest.raises(ValueError, match="requires a path"):
            ToolConfig(
                type=ToolType.CONSTRUCTOR,
                execution=ExecutionConfig(method="invoke"),
            )

    def test_tool_class_requires_path(self):
        """Test that class tools require a path."""
        with pytest.raises(ValueError, match="requires a path"):
            ToolConfig(
                type=ToolType.CLASS,
                execution=ExecutionConfig(method="invoke"),
            )


class TestFrameworkConfig:
    """Test complete framework configuration."""

    def test_minimal_framework_config(self):
        """Test minimal valid framework configuration."""
        config = FrameworkConfig(
            name="test",
            file_path=".agentci/frameworks/test.toml",
            framework=FrameworkMetadata(name="test", dependencies=["test-lib"]),
            agents=[
                AgentConfig(
                    path="test.Agent",
                    args=AgentDiscoveryArgs(model="llm"),
                    execution=ExecutionConfig(method="run"),
                )
            ],
        )
        assert config.name == "test"
        assert config.framework.name == "test"
        assert len(config.agents) == 1
        assert config.tools == []

    def test_framework_with_agents_and_tools(self):
        """Test framework with agents and tools."""
        config = FrameworkConfig(
            name="full",
            file_path=".agentci/frameworks/full.toml",
            framework=FrameworkMetadata(name="full", dependencies=["lib"]),
            agents=[
                AgentConfig(
                    path="lib.Agent",
                    args=AgentDiscoveryArgs(model="llm"),
                    execution=ExecutionConfig(method="run"),
                )
            ],
            tools=[
                ToolConfig(
                    type=ToolType.FUNCTION,
                    execution=ExecutionConfig(method="__call__"),
                )
            ],
        )
        assert len(config.agents) == 1
        assert len(config.tools) == 1

    def test_framework_requires_agents_or_tools(self):
        """Test that framework must have at least agents or tools."""
        with pytest.raises(ValueError, match="must define at least one agent or tool"):
            FrameworkConfig(
                name="empty",
                file_path=".agentci/frameworks/empty.toml",
                framework=FrameworkMetadata(name="empty", dependencies=["lib"]),
                agents=[],
                tools=[],
            )

    def test_framework_requires_dependencies(self):
        """Test that framework must have at least one dependency."""
        with pytest.raises(ValueError, match="must specify at least one dependency"):
            FrameworkConfig(
                name="no_deps",
                file_path=".agentci/frameworks/no_deps.toml",
                framework=FrameworkMetadata(name="no_deps", dependencies=[]),
                agents=[
                    AgentConfig(
                        path="lib.Agent",
                        args=AgentDiscoveryArgs(model="llm"),
                        execution=ExecutionConfig(method="run"),
                    )
                ],
            )


class TestTOMLParsing:
    """Test TOML file parsing."""

    @pytest.fixture
    def builtin_configs_path(self):
        """Get path to built-in framework configs."""
        return Path(__file__).parent.parent / "src" / "agentci" / "client_config" / "frameworks" / "configs"

    def test_parse_langchain_toml(self, builtin_configs_path):
        """Test parsing langchain configuration."""
        toml_path = builtin_configs_path / "langchain.toml"
        config = parse_framework_config_toml(toml_path, builtin_configs_path.parent)

        assert config.name == "langchain"
        assert config.framework.name == "langchain"
        assert "langchain" in config.framework.dependencies

        # Should have multiple agents
        assert len(config.agents) >= 3

        # Check one of the agents
        react_agent = next(
            (a for a in config.agents if "create_react_agent" in a.path),
            None,
        )
        assert react_agent is not None
        assert react_agent.args.model is not None or react_agent.args.model == "model"
        assert react_agent.execution.method in ["invoke", "run"]

        # Should have multiple tools
        assert len(config.tools) >= 3

        # Check tool types
        tool_types = {tool.type for tool in config.tools}
        assert ToolType.DECORATOR in tool_types
        assert ToolType.CONSTRUCTOR in tool_types
        assert ToolType.CLASS in tool_types

    def test_parse_llamaindex_toml(self, builtin_configs_path):
        """Test parsing llamaindex configuration."""
        toml_path = builtin_configs_path / "llamaindex.toml"
        config = parse_framework_config_toml(toml_path, builtin_configs_path.parent)

        assert config.name == "llamaindex"
        assert config.framework.name == "llamaindex"
        assert any("llama" in dep.lower() for dep in config.framework.dependencies)

        # Should have agents
        assert len(config.agents) >= 2

        # Check for explicit agent types
        agent_types = {agent.type for agent in config.agents if agent.type}
        assert len(agent_types) > 0

        # Should have tools
        assert len(config.tools) >= 2

    def test_parse_pydantic_ai_toml(self, builtin_configs_path):
        """Test parsing pydantic-ai configuration."""
        toml_path = builtin_configs_path / "pydantic_ai.toml"
        config = parse_framework_config_toml(toml_path, builtin_configs_path.parent)

        assert config.name == "pydantic_ai"
        assert config.framework.name == "pydantic-ai"
        assert any("pydantic" in dep.lower() for dep in config.framework.dependencies)

        # Should have at least one agent
        assert len(config.agents) >= 1

        # Check agent structure
        agent = config.agents[0]
        assert agent.path == "pydantic_ai.Agent"
        assert agent.args.model is not None

        # Should have at least one tool
        assert len(config.tools) >= 1

    def test_parse_custom_framework_toml(self, tmp_path):
        """Test parsing a custom framework configuration."""
        toml_path = tmp_path / "custom.toml"
        toml_path.write_text(
            """
[framework]
name = "my-framework"
dependencies = ["my-lib", "my-lib-core"]

[[agents]]
path = "my_lib.CustomAgent"
type = "constructor"
args.model = "llm"
args.prompt = "system_prompt"
args.tools = "tools"
execution.method = "execute"
execution.args.prompt = "user_input"

[[tools]]
type = "decorator"
path = "my_lib.tool"
execution.method = "run"

[[tools]]
type = "function"
execution.method = "__call__"
        """
        )

        config = parse_framework_config_toml(toml_path, tmp_path)

        assert config.name == "custom"
        assert config.framework.name == "my-framework"
        assert config.framework.dependencies == ["my-lib", "my-lib-core"]

        assert len(config.agents) == 1
        agent = config.agents[0]
        assert agent.path == "my_lib.CustomAgent"
        assert agent.type == AgentType.CONSTRUCTOR
        assert agent.args.model == "llm"
        assert agent.args.prompt == "system_prompt"
        assert agent.args.tools == "tools"
        assert agent.execution.method == "execute"
        assert agent.execution.args.prompt == "user_input"

        assert len(config.tools) == 2
        assert config.tools[0].type == ToolType.DECORATOR
        assert config.tools[1].type == ToolType.FUNCTION

    def test_invalid_toml_missing_framework_section(self, tmp_path):
        """Test parsing fails with missing framework section."""
        toml_path = tmp_path / "invalid.toml"
        toml_path.write_text(
            """
# Missing [framework] section
[[agents]]
path = "test.Agent"
        """
        )

        with pytest.raises(ValueError, match="Missing 'framework' section"):
            parse_framework_config_toml(toml_path, tmp_path)

    def test_metadata_populated_correctly(self, tmp_path):
        """Test that name and file_path metadata are populated."""
        toml_path = tmp_path / "test_framework.toml"
        toml_path.write_text(
            """
[framework]
name = "test"
dependencies = ["test-lib"]

[[agents]]
path = "test.Agent"
args.model = "llm"
execution.method = "run"
        """
        )

        config = parse_framework_config_toml(toml_path, tmp_path)

        # Name should come from filename
        assert config.name == "test_framework"
        # file_path should be relative to repository_path
        assert config.file_path == "test_framework.toml"
