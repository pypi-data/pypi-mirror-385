"""Configuration loading and validation."""

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger("pp")


class ConfigError(Exception):
    """Configuration-related errors."""

    pass


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load and validate YAML configuration."""
    try:
        if not config_path.exists():
            raise ConfigError(
                f"Configuration file not found: {config_path}\n"
                f"Create a pp.yaml file or check PP_CONFIG_FILE environment variable"
            )

        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        validate_config(config)
        return config

    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {config_path}: {e}")


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration structure."""
    if "applications" not in config:
        raise ConfigError("Config must have 'applications' key")

    apps = config["applications"]
    if not isinstance(apps, dict):
        raise ConfigError("'applications' must be a dictionary")

    for app_name, app_config in apps.items():
        validate_app(app_name, app_config)


def validate_app(app_name: str, app_config: Dict[str, Any]) -> None:
    """Validate application configuration."""
    if not isinstance(app_config, dict):
        raise ConfigError(f"Application '{app_name}' config must be a dictionary")

    if "actions" not in app_config:
        raise ConfigError(f"Application '{app_name}' must have 'actions'")

    actions = app_config["actions"]
    if not isinstance(actions, dict) or not actions:
        raise ConfigError(
            f"Application '{app_name}' actions must be a non-empty dictionary"
        )

    # Validate default_action exists if specified
    default_action = app_config.get("default_action")
    if default_action and default_action not in actions:
        raise ConfigError(
            f"Application '{app_name}' default_action '{default_action}' not found in actions"
        )

    # Validate each action
    for action_name, action_config in actions.items():
        validate_action(app_name, action_name, action_config)


def validate_action(
    app_name: str, action_name: str, action_config: Dict[str, Any]
) -> None:
    """Validate action configuration."""
    if not isinstance(action_config, dict):
        raise ConfigError(
            f"Action '{app_name}.{action_name}' config must be a dictionary"
        )

    if "command" not in action_config:
        raise ConfigError(f"Action '{app_name}.{action_name}' must have 'command'")

    cmd = action_config["command"]
    if not isinstance(cmd, list) or not cmd:
        raise ConfigError(
            f"Action '{app_name}.{action_name}' command must be a non-empty list"
        )

    # Validate depends_on if specified
    depends_on = action_config.get("depends_on")
    if depends_on is not None:
        if not isinstance(depends_on, list):
            raise ConfigError(
                f"Action '{app_name}.{action_name}' depends_on must be a list"
            )
        if not all(isinstance(dep, str) for dep in depends_on):
            raise ConfigError(
                f"Action '{app_name}.{action_name}' depends_on must contain only strings"
            )

    # Validate parameters if specified
    params = action_config.get("parameters")
    if params:
        if not isinstance(params, dict):
            raise ConfigError(
                f"Action '{app_name}.{action_name}' parameters must be a dictionary"
            )
        for param_name, param_config in params.items():
            validate_parameter(app_name, action_name, param_name, param_config)


def validate_parameter(
    app_name: str, action_name: str, param_name: str, param_config: Dict[str, Any]
) -> None:
    """Validate parameter configuration."""
    if not isinstance(param_config, dict):
        raise ConfigError(
            f"Parameter '{param_name}' in '{app_name}.{action_name}' must be a dictionary"
        )

    param_type = param_config.get("type", "string")
    valid_types = {"string", "integer", "float", "boolean"}

    if param_type not in valid_types:
        raise ConfigError(
            f"Parameter '{param_name}' has invalid type '{param_type}'. "
            f"Valid types: {', '.join(valid_types)}"
        )

    # Validate numeric constraints
    if param_type in ("integer", "float"):
        min_val = param_config.get("min")
        max_val = param_config.get("max")
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ConfigError(
                f"Parameter '{param_name}' min ({min_val}) > max ({max_val})"
            )

    # Validate choices
    choices = param_config.get("choices")
    if choices and not isinstance(choices, list):
        raise ConfigError(f"Parameter '{param_name}' choices must be a list")

    # Validate default value
    default = param_config.get("default")
    if default is not None and choices and default not in choices:
        raise ConfigError(
            f"Parameter '{param_name}' default '{default}' not in choices"
        )
