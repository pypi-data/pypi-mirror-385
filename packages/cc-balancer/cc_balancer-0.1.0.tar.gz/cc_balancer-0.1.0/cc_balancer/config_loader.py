"""
Configuration loader with YAML support and environment variable expansion.
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml

from cc_balancer.config import AppConfig


class ConfigError(Exception):
    """Configuration loading or validation error."""

    pass


def expand_env_vars(text: str) -> str:
    """
    Expand environment variables in format ${VAR_NAME}.

    Args:
        text: String potentially containing ${VAR_NAME} patterns

    Returns:
        String with environment variables expanded
    """

    def replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        env_value = os.environ.get(var_name)
        if env_value is None:
            # Leave unexpanded if variable doesn't exist
            return match.group(0)
        return env_value

    return re.sub(r"\$\{([^}]+)\}", replacer, text)


def expand_dict_env_vars(data: Any) -> Any:
    """
    Recursively expand environment variables in dictionary values.

    Args:
        data: Dictionary, list, or primitive value

    Returns:
        Data structure with environment variables expanded
    """
    if isinstance(data, dict):
        return {key: expand_dict_env_vars(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [expand_dict_env_vars(item) for item in data]
    elif isinstance(data, str):
        return expand_env_vars(data)
    else:
        return data


def load_config(config_path: str | Path) -> AppConfig:
    """
    Load and validate configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Validated AppConfig instance

    Raises:
        ConfigError: If file doesn't exist, is invalid YAML, or fails validation
    """
    config_file = Path(config_path)

    # Check file exists
    if not config_file.exists():
        raise ConfigError(f"Configuration file not found: {config_file}")

    # Load YAML
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {config_file}: {e}") from e
    except Exception as e:
        raise ConfigError(f"Failed to read {config_file}: {e}") from e

    if raw_data is None:
        raise ConfigError(f"Empty configuration file: {config_file}")

    # Expand environment variables
    expanded_data = expand_dict_env_vars(raw_data)

    # Validate with Pydantic
    try:
        return AppConfig(**expanded_data)
    except Exception as e:
        raise ConfigError(f"Configuration validation failed: {e}") from e


def load_config_with_defaults(config_path: str | Path | None = None) -> AppConfig:
    """
    Load configuration with fallback to default locations.

    Tries in order:
    1. Provided config_path
    2. CONFIG_FILE environment variable
    3. ./config.yaml
    4. ./config.yml

    Args:
        config_path: Optional explicit configuration path

    Returns:
        Validated AppConfig instance

    Raises:
        ConfigError: If no configuration file found or validation fails
    """
    # Try explicit path first
    if config_path:
        return load_config(config_path)

    # Try environment variable
    env_config = os.environ.get("CONFIG_FILE")
    if env_config:
        return load_config(env_config)

    # Try default locations
    default_paths = [
        Path("config.yaml"),
        Path("config.yml"),
    ]

    for path in default_paths:
        if path.exists():
            return load_config(path)

    raise ConfigError(
        "No configuration file found. Tried: "
        f"{', '.join(str(p) for p in default_paths)}. "
        "Specify via --config flag or CONFIG_FILE environment variable."
    )
