"""Unit tests for lib/config.py"""

import pytest
import yaml

from lib.config import (ConfigError, load_config, validate_action,
                        validate_app, validate_config, validate_parameter)


class TestLoadConfig:
    """Test config loading."""

    def test_load_valid_config(self, temp_dir, simple_config):
        """Test loading a valid config file."""
        config_path = temp_dir / "pp.yaml"
        with open(config_path, "w") as f:
            yaml.dump(simple_config, f)

        config = load_config(config_path)

        assert "applications" in config
        assert "test_app" in config["applications"]

    def test_load_nonexistent_file(self, temp_dir):
        """Test error when file doesn't exist."""
        config_path = temp_dir / "missing.yaml"

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_path)

        assert "not found" in str(exc_info.value)

    def test_load_invalid_yaml(self, temp_dir):
        """Test error with malformed YAML."""
        config_path = temp_dir / "bad.yaml"
        with open(config_path, "w") as f:
            f.write("invalid: [unclosed")

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_path)

        assert "invalid" in str(exc_info.value).lower()


class TestValidateConfig:
    """Test configuration validation."""

    def test_validate_valid_config(self, simple_config):
        """Test validation of valid config."""
        # Should not raise
        validate_config(simple_config)

    def test_missing_applications_key(self):
        """Test error when 'applications' key is missing."""
        config = {"other_key": "value"}

        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)

        assert "applications" in str(exc_info.value)

    def test_applications_not_dict(self):
        """Test error when 'applications' is not a dictionary."""
        config = {"applications": ["not", "a", "dict"]}

        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)

        assert "dictionary" in str(exc_info.value)


class TestValidateApp:
    """Test application validation."""

    def test_validate_valid_app(self):
        """Test validation of valid app config."""
        app_config = {
            "help": "Test app",
            "actions": {
                "run": {"command": ["echo", "test"]},
            },
        }

        # Should not raise
        validate_app("test_app", app_config)

    def test_app_config_not_dict(self):
        """Test error when app config is not a dict."""
        with pytest.raises(ConfigError) as exc_info:
            validate_app("test_app", "not a dict")

        assert "dictionary" in str(exc_info.value)

    def test_missing_actions(self):
        """Test error when actions are missing."""
        app_config = {"help": "Test app"}

        with pytest.raises(ConfigError) as exc_info:
            validate_app("test_app", app_config)

        assert "actions" in str(exc_info.value)

    def test_actions_not_dict(self):
        """Test error when actions is not a dict."""
        app_config = {"actions": ["not", "a", "dict"]}

        with pytest.raises(ConfigError) as exc_info:
            validate_app("test_app", app_config)

        assert "dictionary" in str(exc_info.value)

    def test_actions_empty(self):
        """Test error when actions is empty."""
        app_config = {"actions": {}}

        with pytest.raises(ConfigError) as exc_info:
            validate_app("test_app", app_config)

        assert "non-empty" in str(exc_info.value)

    def test_invalid_default_action(self):
        """Test error when default_action doesn't exist."""
        app_config = {
            "default_action": "nonexistent",
            "actions": {
                "run": {"command": ["echo", "test"]},
            },
        }

        with pytest.raises(ConfigError) as exc_info:
            validate_app("test_app", app_config)

        assert "default_action" in str(exc_info.value)
        assert "nonexistent" in str(exc_info.value)


class TestValidateAction:
    """Test action validation."""

    def test_validate_valid_action(self):
        """Test validation of valid action."""
        action_config = {
            "help": "Run the app",
            "command": ["echo", "hello"],
        }

        # Should not raise
        validate_action("test_app", "run", action_config)

    def test_action_config_not_dict(self):
        """Test error when action config is not a dict."""
        with pytest.raises(ConfigError) as exc_info:
            validate_action("test_app", "run", "not a dict")

        assert "dictionary" in str(exc_info.value)

    def test_missing_command(self):
        """Test error when command is missing."""
        action_config = {"help": "Run the app"}

        with pytest.raises(ConfigError) as exc_info:
            validate_action("test_app", "run", action_config)

        assert "command" in str(exc_info.value)

    def test_command_not_list(self):
        """Test error when command is not a list."""
        action_config = {"command": "not a list"}

        with pytest.raises(ConfigError) as exc_info:
            validate_action("test_app", "run", action_config)

        assert "list" in str(exc_info.value)

    def test_command_empty_list(self):
        """Test error when command is an empty list."""
        action_config = {"command": []}

        with pytest.raises(ConfigError) as exc_info:
            validate_action("test_app", "run", action_config)

        assert "non-empty" in str(exc_info.value)

    def test_invalid_depends_on_type(self):
        """Test error when depends_on is not a list."""
        action_config = {
            "command": ["echo", "test"],
            "depends_on": "not a list",
        }

        with pytest.raises(ConfigError) as exc_info:
            validate_action("test_app", "run", action_config)

        assert "depends_on" in str(exc_info.value)
        assert "list" in str(exc_info.value)

    def test_depends_on_non_string_items(self):
        """Test error when depends_on contains non-strings."""
        action_config = {
            "command": ["echo", "test"],
            "depends_on": ["valid", 123, "another"],
        }

        with pytest.raises(ConfigError) as exc_info:
            validate_action("test_app", "run", action_config)

        assert "depends_on" in str(exc_info.value)
        assert "strings" in str(exc_info.value)


class TestValidateParameter:
    """Test parameter validation."""

    def test_validate_valid_parameter(self):
        """Test validation of valid parameter."""
        param_config = {
            "type": "string",
            "required": True,
            "help": "A parameter",
        }

        # Should not raise
        validate_parameter("test_app", "run", "param1", param_config)

    def test_parameter_config_not_dict(self):
        """Test error when parameter config is not a dict."""
        with pytest.raises(ConfigError) as exc_info:
            validate_parameter("test_app", "run", "param1", "not a dict")

        assert "dictionary" in str(exc_info.value)

    def test_invalid_parameter_type(self):
        """Test error with invalid parameter type."""
        param_config = {"type": "invalid_type"}

        with pytest.raises(ConfigError) as exc_info:
            validate_parameter("test_app", "run", "param1", param_config)

        assert "invalid type" in str(exc_info.value)

    def test_numeric_min_max_validation(self):
        """Test error when min > max for numeric types."""
        param_config = {
            "type": "integer",
            "min": 10,
            "max": 5,
        }

        with pytest.raises(ConfigError) as exc_info:
            validate_parameter("test_app", "run", "count", param_config)

        assert "min" in str(exc_info.value)
        assert "max" in str(exc_info.value)

    def test_choices_not_list(self):
        """Test error when choices is not a list."""
        param_config = {
            "type": "string",
            "choices": "not a list",
        }

        with pytest.raises(ConfigError) as exc_info:
            validate_parameter("test_app", "run", "mode", param_config)

        assert "choices" in str(exc_info.value)
        assert "list" in str(exc_info.value)

    def test_invalid_default_in_choices(self):
        """Test error when default is not in choices."""
        param_config = {
            "type": "string",
            "choices": ["a", "b", "c"],
            "default": "d",
        }

        with pytest.raises(ConfigError) as exc_info:
            validate_parameter("test_app", "run", "mode", param_config)

        assert "default" in str(exc_info.value)
        assert "choices" in str(exc_info.value)
