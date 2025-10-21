"""Integration tests - test full workflow with real configs."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from lib import (execute_action, load_config, reset_execution_tracking,
                 resolve_dependencies)


class TestBasicExecution:
    """Test basic command execution."""

    def test_simple_command_execution(self, temp_dir, simple_config, mock_args):
        """Test executing a simple command."""
        # Create config file
        config_path = temp_dir / "pp.yaml"
        with open(config_path, "w") as f:
            yaml.dump(simple_config, f)

        # Load config
        config = load_config(config_path)

        # Setup args
        args = mock_args(action="run")

        # Resolve dependencies
        execution_order = resolve_dependencies(
            config["applications"]["test_app"], "run"
        )

        # Execute
        reset_execution_tracking()
        with patch("subprocess.run") as mock_run:
            execute_action("test_app", "run", config, args, execution_order)
            mock_run.assert_called_once()
            assert mock_run.call_args[0][0] == ["echo", "Hello"]

    def test_config_from_examples_directory(self):
        """Test loading actual example configs."""
        examples_dir = Path("examples")
        if not examples_dir.exists():
            pytest.skip("examples directory not found")

        # Test basic_config.yaml
        basic_config_path = examples_dir / "basic_config.yaml"
        if basic_config_path.exists():
            config = load_config(basic_config_path)
            assert "applications" in config
            assert len(config["applications"]) > 0


class TestParameterIntegration:
    """Test parameter handling end-to-end."""

    def test_parameter_substitution(self, temp_dir, config_with_params, mock_args):
        """Test parameter substitution in commands."""
        # Create config file
        config_path = temp_dir / "pp.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_with_params, f)

        # Load config
        config = load_config(config_path)

        # Setup args with parameters
        args = mock_args(action="run", name="Alice", count=3, verbose=True)

        # Execute
        reset_execution_tracking()
        execution_order = resolve_dependencies(config["applications"]["app"], "run")

        with patch("subprocess.run") as mock_run:
            execute_action("app", "run", config, args, execution_order)

            # Check parameter substitution
            cmd = mock_run.call_args[0][0]
            assert "name=Alice" in cmd
            assert "count=3" in cmd
            assert "--verbose" in cmd

    def test_boolean_flag_false(self, temp_dir, config_with_params, mock_args):
        """Test boolean parameter when False."""
        config_path = temp_dir / "pp.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_with_params, f)

        config = load_config(config_path)
        args = mock_args(action="run", name="Bob", count=1, verbose=False)

        reset_execution_tracking()
        execution_order = resolve_dependencies(config["applications"]["app"], "run")

        with patch("subprocess.run") as mock_run:
            execute_action("app", "run", config, args, execution_order)

            # Check verbose flag is NOT present
            cmd = mock_run.call_args[0][0]
            assert "--verbose" not in cmd

    def test_parameter_defaults(self, temp_dir, config_with_params, mock_args):
        """Test parameter default values."""
        config_path = temp_dir / "pp.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_with_params, f)

        config = load_config(config_path)
        args = mock_args(action="run", name="Charlie", count=None, verbose=None)

        reset_execution_tracking()
        execution_order = resolve_dependencies(config["applications"]["app"], "run")

        with patch("subprocess.run") as mock_run:
            execute_action("app", "run", config, args, execution_order)

            # Should use default count=1
            cmd = mock_run.call_args[0][0]
            assert "count=1" in cmd


class TestDependencyIntegration:
    """Test dependency resolution end-to-end."""

    def test_dependency_execution_order(
        self, temp_dir, config_with_dependencies, mock_args
    ):
        """Test actions execute in correct dependency order."""
        config_path = temp_dir / "pp.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_with_dependencies, f)

        config = load_config(config_path)
        args = mock_args(action="full")

        reset_execution_tracking()
        execution_order = resolve_dependencies(config["applications"]["ci"], "full")

        # Verify order: lint -> test -> build -> full
        assert execution_order == ["lint", "test", "build", "full"]

        with patch("subprocess.run") as mock_run:
            execute_action("ci", "full", config, args, execution_order)

            # Verify all 4 actions executed
            assert mock_run.call_count == 4

            # Verify execution order
            calls = [call[0][0] for call in mock_run.call_args_list]
            assert calls[0] == ["echo", "Linting"]
            assert calls[1] == ["echo", "Testing"]
            assert calls[2] == ["echo", "Building"]
            assert calls[3] == ["echo", "Full pipeline complete"]

    def test_circular_dependency_detection(self, temp_dir, mock_args):
        """Test circular dependency is detected."""
        circular_config = {
            "applications": {
                "app": {
                    "help": "Test app",
                    "actions": {
                        "a": {"command": ["echo", "a"], "depends_on": ["b"]},
                        "b": {"command": ["echo", "b"], "depends_on": ["c"]},
                        "c": {"command": ["echo", "c"], "depends_on": ["a"]},
                    },
                }
            }
        }

        config_path = temp_dir / "pp.yaml"
        with open(config_path, "w") as f:
            yaml.dump(circular_config, f)

        config = load_config(config_path)

        # Should raise DependencyError
        from lib.dependencies import DependencyError

        with pytest.raises(DependencyError) as exc_info:
            resolve_dependencies(config["applications"]["app"], "a")

        assert "circular" in str(exc_info.value).lower()


class TestEnvironmentSetup:
    """Test environment and directory setup."""

    def test_environment_variables(self, temp_dir, mock_args):
        """Test custom environment variables are set."""
        config = {
            "applications": {
                "app": {
                    "help": "Test app",
                    "env_vars": {
                        "MY_VAR": "test_value",
                        "ANOTHER_VAR": "another_value",
                    },
                    "actions": {
                        "run": {"command": ["echo", "test"]},
                    },
                }
            }
        }

        config_path = temp_dir / "pp.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        config = load_config(config_path)
        args = mock_args(action="run")

        reset_execution_tracking()
        execution_order = resolve_dependencies(config["applications"]["app"], "run")

        with patch("subprocess.run") as mock_run:
            execute_action("app", "run", config, args, execution_order)

            # Check environment variables were passed
            env = mock_run.call_args[1]["env"]
            assert env["MY_VAR"] == "test_value"
            assert env["ANOTHER_VAR"] == "another_value"


class TestErrorHandling:
    """Test error handling."""

    def test_missing_config_file(self, temp_dir):
        """Test error when config file doesn't exist."""
        from lib.config import ConfigError

        config_path = temp_dir / "nonexistent.yaml"

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_path)

        assert "not found" in str(exc_info.value)

    def test_invalid_yaml(self, temp_dir):
        """Test error with invalid YAML."""
        from lib.config import ConfigError

        config_path = temp_dir / "invalid.yaml"
        with open(config_path, "w") as f:
            f.write("invalid: yaml: content: [")

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_path)

        assert "invalid" in str(exc_info.value).lower()

    def test_missing_required_parameter(self, temp_dir, config_with_params, mock_args):
        """Test error when required parameter is missing."""
        from lib.params import ParameterError

        config_path = temp_dir / "pp.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_with_params, f)

        config = load_config(config_path)
        args = mock_args(action="run", name=None)  # Missing required 'name'

        reset_execution_tracking()
        execution_order = resolve_dependencies(config["applications"]["app"], "run")

        with pytest.raises(ParameterError) as exc_info:
            execute_action("app", "run", config, args, execution_order)

        assert "required" in str(exc_info.value).lower()
        assert "name" in str(exc_info.value)
