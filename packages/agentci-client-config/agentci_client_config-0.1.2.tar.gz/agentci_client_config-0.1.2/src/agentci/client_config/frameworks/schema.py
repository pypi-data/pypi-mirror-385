from __future__ import annotations
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "FrameworkConfig",
    "AgentType",
    "ToolType",
    "NameExtraction",
    "AgentDiscoveryArgs",
    "AgentExecutionArgs",
    "ExecutionConfig",
    "AgentConfig",
    "ToolConfig",
    "FrameworkMetadata",
]


class AgentType(str, Enum):
    """Types of agent discovery patterns."""

    CONSTRUCTOR = "constructor"
    CLASS_METHOD = "class_method"
    FUNCTION = "function"


class ToolType(str, Enum):
    """Types of tool discovery patterns."""

    FUNCTION = "function"
    DECORATOR = "decorator"
    CONSTRUCTOR = "constructor"
    CLASS = "class"


class NameExtraction(BaseModel):
    """Configuration for extracting names from AST nodes."""

    from_: str = Field(
        alias="from",
        description="Where to extract the name from: 'args', 'variable', 'function'",
    )
    param: Optional[str] = Field(
        None,
        description="If from='args', which parameter name to extract",
    )


class AgentDiscoveryArgs(BaseModel):
    """Arguments for discovering agents in source code."""

    model: Optional[str] = Field(
        None,
        description="Framework parameter name for model (e.g., 'model', 'llm')",
    )
    prompt: Optional[str] = Field(
        None,
        description="Framework parameter name for system prompt (e.g., 'prompt', 'system_prompt')",
    )
    tools: Optional[str] = Field(
        None,
        description="Framework parameter name for tools list (e.g., 'tools')",
    )

    @model_validator(mode="after")
    def validate_at_least_one_arg(self):
        """Ensure at least one argument is specified."""
        if not any([self.model, self.prompt, self.tools]):
            raise ValueError("At least one of 'model', 'prompt', or 'tools' must be specified")
        return self


class AgentExecutionArgs(BaseModel):
    """Arguments for executing agents at runtime."""

    prompt: str = Field(
        description="Parameter name for user prompt during execution (e.g., 'messages', 'input', 'user_prompt')"
    )


class ExecutionConfig(BaseModel):
    """Configuration for executing discovered objects."""

    method: str = Field(description="Method name to call on the object")
    args: Optional[AgentExecutionArgs] = Field(None, description="Arguments for runtime execution")


class AgentConfig(BaseModel):
    """Configuration for discovering and executing agents."""

    path: str = Field(description="Fully qualified Python path to the agent constructor")
    type: Optional[AgentType] = Field(
        None,
        description="Discovery type: 'constructor', 'class_method', 'function' (optional, auto-detected if not specified)",
    )
    args: AgentDiscoveryArgs = Field(description="Mapping of our schema fields to framework parameter names")
    execution: ExecutionConfig = Field(description="How to execute this agent")

    @model_validator(mode="after")
    def validate_path_format(self):
        """Validate path format matches the agent type."""
        if not self.path or not self.path.strip():
            raise ValueError("Agent path cannot be empty")

        parts = self.path.split(".")

        if self.type == AgentType.CLASS_METHOD and len(parts) < 2:
            raise ValueError(
                f"Agent type 'class_method' requires path with at least 2 parts (Class.method), got: {self.path}"
            )

        return self


class ToolConfig(BaseModel):
    """Configuration for discovering and executing tools."""

    type: ToolType = Field(description="Discovery type: 'decorator', 'constructor', 'class', 'function'")
    path: Optional[str] = Field(
        None,
        description="Fully qualified Python path (not needed for type='function')",
    )
    execution: ExecutionConfig = Field(description="How to execute this tool")

    @model_validator(mode="after")
    def validate_path_requirements(self):
        """Validate that path is provided when required for tool type."""
        if self.type != ToolType.FUNCTION and self.path is None:
            raise ValueError(f"Tool type '{self.type.value}' requires a path")
        return self


class FrameworkMetadata(BaseModel):
    """Framework metadata."""

    name: str = Field(description="Framework identifier")
    dependencies: List[str] = Field(description="List of package names to detect framework presence")


class FrameworkConfig(BaseModel):
    """Complete framework configuration loaded from TOML."""

    # Metadata (populated during parsing)
    name: str = Field(description="Framework name derived from filename")
    file_path: str = Field(description="Path to source configuration file")

    # Configuration content
    framework: FrameworkMetadata = Field(description="Framework metadata")
    agents: List[AgentConfig] = Field(
        default_factory=list,
        description="Agent discovery and execution configurations",
    )
    tools: List[ToolConfig] = Field(
        default_factory=list,
        description="Tool discovery and execution configurations",
    )

    @model_validator(mode="after")
    def validate_has_agents_or_tools(self):
        """Ensure framework defines at least agents or tools."""
        if not self.agents and not self.tools:
            raise ValueError("Framework must define at least one agent or tool configuration")
        return self

    @model_validator(mode="after")
    def validate_dependencies_not_empty(self):
        """Ensure framework has at least one dependency."""
        if not self.framework.dependencies:
            raise ValueError("Framework must specify at least one dependency")
        return self
