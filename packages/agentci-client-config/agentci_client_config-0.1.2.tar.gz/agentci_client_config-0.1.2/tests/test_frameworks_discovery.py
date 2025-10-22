"""Tests for framework discovery functionality."""

import pytest
from pathlib import Path

from agentci.client_config import config
from agentci.client_config.frameworks.parser import discover_frameworks
from agentci.client_config.frameworks.schema import AgentType, ToolType


class TestFrameworkDiscovery:
    """Test framework discovery functionality."""

    @pytest.fixture
    def repo_with_frameworks(self, tmp_path):
        """Create a temporary repository with custom framework configs."""
        # Create the framework directory structure using config
        frameworks_dir = tmp_path / config.framework_path_name
        frameworks_dir.mkdir(parents=True)

        # Create a custom framework config
        custom_toml = frameworks_dir / "custom_framework.toml"
        custom_toml.write_text(
            """
[framework]
name = "custom_framework"
dependencies = ["custom-lib"]

[[agents]]
path = "custom_lib.Agent"
args.model = "model"
args.prompt = "prompt"
execution.method = "run"
execution.args.prompt = "input"

[[tools]]
type = "function"
execution.method = "__call__"
        """
        )

        return tmp_path

    @pytest.fixture
    def repo_with_override(self, tmp_path):
        """Create a repository that overrides a built-in framework config."""
        frameworks_dir = tmp_path / config.framework_path_name
        frameworks_dir.mkdir(parents=True)

        # Override langchain config with custom version
        override_toml = frameworks_dir / "langchain.toml"
        override_toml.write_text(
            """
[framework]
name = "langchain"
dependencies = ["langchain-custom"]

[[agents]]
path = "langchain_custom.CustomAgent"
args.model = "llm"
args.prompt = "system_prompt"
execution.method = "execute"
execution.args.prompt = "user_input"
        """
        )

        return tmp_path

    @pytest.fixture
    def empty_repo(self, tmp_path):
        """Create a temporary repository without framework configs."""
        return tmp_path

    def test_discover_builtin_frameworks(self):
        """Test discovery of built-in framework configurations."""
        frameworks = discover_frameworks()

        # Should find at least the 3 built-in configs
        assert len(frameworks) >= 3

        framework_names = {fw.name for fw in frameworks}
        assert "langchain" in framework_names
        assert "llamaindex" in framework_names
        assert "pydantic_ai" in framework_names

    def test_discover_builtin_framework_structure(self):
        """Test that built-in frameworks have correct structure."""
        frameworks = discover_frameworks()

        langchain = next((fw for fw in frameworks if fw.name == "langchain"), None)
        assert langchain is not None
        assert langchain.framework.name == "langchain"
        assert "langchain" in langchain.framework.dependencies
        assert len(langchain.agents) > 0
        assert len(langchain.tools) > 0

        # Check agent structure
        assert all(agent.path for agent in langchain.agents)
        assert all(agent.args for agent in langchain.agents)
        assert all(agent.execution for agent in langchain.agents)

        # Check tool structure
        assert all(tool.type for tool in langchain.tools)
        assert all(tool.execution for tool in langchain.tools)

    def test_discover_with_custom_framework(self, repo_with_frameworks):
        """Test discovery with custom user-defined framework."""
        frameworks = discover_frameworks(repo_with_frameworks)

        # Should include built-in + custom
        framework_names = {fw.name for fw in frameworks}
        assert "langchain" in framework_names
        assert "llamaindex" in framework_names
        assert "pydantic_ai" in framework_names
        assert "custom_framework" in framework_names

        # Verify custom framework
        custom = next((fw for fw in frameworks if fw.name == "custom_framework"), None)
        assert custom is not None
        assert custom.framework.dependencies == ["custom-lib"]
        assert len(custom.agents) == 1
        assert custom.agents[0].path == "custom_lib.Agent"

    def test_user_config_overrides_builtin(self, repo_with_override):
        """Test that user-defined configs override built-in configs by name."""
        frameworks = discover_frameworks(repo_with_override)

        # Should still have all framework names
        framework_names = {fw.name for fw in frameworks}
        assert "langchain" in framework_names
        assert "llamaindex" in framework_names
        assert "pydantic_ai" in framework_names

        # But langchain should be the overridden version
        langchain = next((fw for fw in frameworks if fw.name == "langchain"), None)
        assert langchain is not None
        assert langchain.framework.dependencies == ["langchain-custom"]
        assert len(langchain.agents) == 1
        assert langchain.agents[0].path == "langchain_custom.CustomAgent"
        assert langchain.agents[0].execution.method == "execute"

    def test_discover_empty_repo_returns_builtins(self, empty_repo):
        """Test that empty repo still returns built-in frameworks."""
        frameworks = discover_frameworks(empty_repo)

        # Should return built-in frameworks even without user configs
        framework_names = {fw.name for fw in frameworks}
        assert "langchain" in framework_names
        assert "llamaindex" in framework_names
        assert "pydantic_ai" in framework_names

    def test_discover_no_frameworks_directory(self, tmp_path):
        """Test discovery when frameworks directory doesn't exist."""
        frameworks = discover_frameworks(tmp_path)

        # Should still return built-in frameworks
        assert len(frameworks) >= 3
        framework_names = {fw.name for fw in frameworks}
        assert "langchain" in framework_names

    def test_framework_agent_types(self):
        """Test that agent types are parsed correctly."""
        frameworks = discover_frameworks()

        langchain = next((fw for fw in frameworks if fw.name == "langchain"), None)
        assert langchain is not None

        # Langchain agents don't explicitly specify type (auto-detected)
        for agent in langchain.agents:
            # Type is optional and may be None for auto-detection
            if agent.type is not None:
                assert isinstance(agent.type, AgentType)

        llamaindex = next((fw for fw in frameworks if fw.name == "llamaindex"), None)
        assert llamaindex is not None

        # LlamaIndex has explicit types
        agent_types = {agent.type for agent in llamaindex.agents if agent.type}
        assert AgentType.CONSTRUCTOR in agent_types or AgentType.CLASS_METHOD in agent_types

    def test_framework_tool_types(self):
        """Test that tool types are parsed correctly."""
        frameworks = discover_frameworks()

        langchain = next((fw for fw in frameworks if fw.name == "langchain"), None)
        assert langchain is not None

        tool_types = {tool.type for tool in langchain.tools}
        assert ToolType.DECORATOR in tool_types
        assert ToolType.CONSTRUCTOR in tool_types
        assert ToolType.CLASS in tool_types

    def test_framework_execution_configs(self):
        """Test that execution configurations are valid."""
        from agentci.client_config.frameworks.schema import AgentExecutionArgs

        frameworks = discover_frameworks()

        for framework in frameworks:
            # Check agent execution configs
            for agent in framework.agents:
                assert agent.execution.method
                # execution.args is optional
                if agent.execution.args:
                    assert isinstance(agent.execution.args, AgentExecutionArgs)
                    assert agent.execution.args.prompt  # Should have prompt field

            # Check tool execution configs
            for tool in framework.tools:
                assert tool.execution.method
                # Tools don't have execution args (args is only for agents)
                if tool.execution.args:
                    assert isinstance(tool.execution.args, AgentExecutionArgs)

    def test_multiple_user_frameworks(self, tmp_path):
        """Test discovery with multiple user-defined frameworks."""
        frameworks_dir = tmp_path / config.framework_path_name
        frameworks_dir.mkdir(parents=True)

        # Create two custom frameworks
        for i in range(1, 3):
            custom_toml = frameworks_dir / f"custom_{i}.toml"
            custom_toml.write_text(
                f"""
[framework]
name = "custom_{i}"
dependencies = ["custom-lib-{i}"]

[[agents]]
path = "custom_{i}.Agent"
args.model = "model"
execution.method = "run"
            """
            )

        frameworks = discover_frameworks(tmp_path)

        # Should have built-ins + 2 custom
        framework_names = {fw.name for fw in frameworks}
        assert "custom_1" in framework_names
        assert "custom_2" in framework_names
        assert "langchain" in framework_names

    def test_invalid_framework_config_raises_error(self, tmp_path):
        """Test that invalid framework config raises ValueError."""
        frameworks_dir = tmp_path / config.framework_path_name
        frameworks_dir.mkdir(parents=True)

        invalid_toml = frameworks_dir / "invalid.toml"
        invalid_toml.write_text(
            """
[framework]
# Missing name - should cause validation error
dependencies = ["some-lib"]
        """
        )

        with pytest.raises(ValueError, match="Failed to parse framework config"):
            discover_frameworks(tmp_path)
