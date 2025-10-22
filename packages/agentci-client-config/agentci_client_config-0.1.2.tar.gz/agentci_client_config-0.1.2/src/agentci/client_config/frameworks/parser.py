from __future__ import annotations
from pathlib import Path
import tomllib

from agentci.client_config import config
from agentci.client_config.frameworks.schema import FrameworkConfig


DISCOVER_EXTENSIONS: list[str] = [
    "toml",
]


def discover_frameworks(repository_path: Path | None = None) -> list[FrameworkConfig]:
    """Discover all framework configurations.

    Discovers framework configurations from two sources:
    1. Built-in configs (bundled with the library in frameworks/configs/)
    2. User-defined configs (in repository's .agentci/frameworks/)

    User-defined configs with the same name as built-in configs will override the built-in versions.

    Args:
        repository_path: Root path of the repository. If None, only built-in configs are returned.

    Returns:
        List of parsed FrameworkConfig objects, with user configs overriding built-in configs by name.

    Raises:
        ValueError: If any framework configuration file fails to parse or validate.
    """
    frameworks_by_name: dict[str, FrameworkConfig] = {}

    # First, discover built-in configs
    builtin_configs_path = Path(__file__).parent / "configs"
    for extension in DISCOVER_EXTENSIONS:
        for config_file in builtin_configs_path.glob(f"*.{extension}"):
            # Use a placeholder path for built-in configs
            parsed_framework = parse_framework_config_toml(config_file, builtin_configs_path.parent)
            frameworks_by_name[parsed_framework.name] = parsed_framework

    # Then, discover user configs (if repository path provided)
    if repository_path is not None:
        framework_path = repository_path / config.framework_path_name

        if framework_path.exists():
            for extension in DISCOVER_EXTENSIONS:
                for config_file in framework_path.glob(f"*.{extension}"):
                    parsed_framework = parse_framework_config_toml(config_file, repository_path)
                    # User config overrides built-in config with same name
                    frameworks_by_name[parsed_framework.name] = parsed_framework

    return list(frameworks_by_name.values())


def parse_framework_config_toml(toml_path: Path, repository_path: Path) -> FrameworkConfig:
    """Parse a single TOML framework configuration file.

    Reads a TOML file containing a framework configuration, validates its structure,
    and returns a fully populated FrameworkConfig object. The function automatically
    derives the framework name from the filename and calculates the relative file path.

    Args:
        toml_path: Absolute path to the TOML configuration file.
        repository_path: Root path of the repository, used to calculate relative file paths.

    Returns:
        FrameworkConfig: Validated framework configuration object.

    Raises:
        ValueError: If the TOML file is missing the required 'framework' section or if
                   validation fails for any configuration fields.

    Example:
        >>> from pathlib import Path
        >>> framework_config = parse_framework_config_toml(
        ...     Path("/repo/.agentci/frameworks/langchain.toml"),
        ...     Path("/repo")
        ... )
        >>> print(framework_config.name)  # 'langchain'
        >>> print(framework_config.file_path)  # '.agentci/frameworks/langchain.toml'
    """
    try:
        with open(toml_path, "rb") as f:
            toml_data = tomllib.load(f)

        if "framework" not in toml_data:
            raise ValueError(f"Missing 'framework' section in {toml_path}")

        # Add metadata to the config data
        toml_data["name"] = toml_path.stem
        toml_data["file_path"] = str(toml_path.relative_to(repository_path))

        return FrameworkConfig(**toml_data)

    except Exception as e:
        raise ValueError(f"Failed to parse framework config {toml_path}: {str(e)}")
