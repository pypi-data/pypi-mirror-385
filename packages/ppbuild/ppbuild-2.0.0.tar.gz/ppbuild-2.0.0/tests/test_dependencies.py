"""Unit tests for lib/dependencies.py"""

import pytest

from lib.dependencies import (DependencyError, resolve_dependencies,
                              validate_all_dependencies)


class TestResolveDependencies:
    """Test dependency resolution."""

    def test_no_dependencies(self):
        """Test action with no dependencies."""
        app_config = {
            "actions": {
                "run": {"command": ["echo", "test"]},
            }
        }

        result = resolve_dependencies(app_config, "run")
        assert result == ["run"]

    def test_simple_dependency_chain(self):
        """Test simple linear dependency chain."""
        app_config = {
            "actions": {
                "build": {"command": ["echo", "build"], "depends_on": ["test"]},
                "test": {"command": ["echo", "test"], "depends_on": ["lint"]},
                "lint": {"command": ["echo", "lint"]},
            }
        }

        result = resolve_dependencies(app_config, "build")
        assert result == ["lint", "test", "build"]

    def test_diamond_dependency(self):
        """Test diamond-shaped dependency graph."""
        app_config = {
            "actions": {
                "deploy": {
                    "command": ["echo", "deploy"],
                    "depends_on": ["build", "test"],
                },
                "build": {"command": ["echo", "build"], "depends_on": ["lint"]},
                "test": {"command": ["echo", "test"], "depends_on": ["lint"]},
                "lint": {"command": ["echo", "lint"]},
            }
        }

        result = resolve_dependencies(app_config, "deploy")

        # lint should be first (common dependency)
        # build and test should come after lint
        # deploy should be last
        assert result[0] == "lint"
        assert result[-1] == "deploy"
        assert "build" in result
        assert "test" in result

    def test_multiple_dependencies(self):
        """Test action with multiple direct dependencies."""
        app_config = {
            "actions": {
                "full": {
                    "command": ["echo", "full"],
                    "depends_on": ["lint", "test", "build"],
                },
                "lint": {"command": ["echo", "lint"]},
                "test": {"command": ["echo", "test"]},
                "build": {"command": ["echo", "build"]},
            }
        }

        result = resolve_dependencies(app_config, "full")

        # All dependencies should be before 'full'
        assert result[-1] == "full"
        assert "lint" in result
        assert "test" in result
        assert "build" in result

    def test_circular_dependency_direct(self):
        """Test detection of direct circular dependency."""
        app_config = {
            "actions": {
                "a": {"command": ["echo", "a"], "depends_on": ["a"]},
            }
        }

        with pytest.raises(DependencyError) as exc_info:
            resolve_dependencies(app_config, "a")

        assert "circular" in str(exc_info.value).lower()

    def test_circular_dependency_indirect(self):
        """Test detection of indirect circular dependency."""
        app_config = {
            "actions": {
                "a": {"command": ["echo", "a"], "depends_on": ["b"]},
                "b": {"command": ["echo", "b"], "depends_on": ["c"]},
                "c": {"command": ["echo", "c"], "depends_on": ["a"]},
            }
        }

        with pytest.raises(DependencyError) as exc_info:
            resolve_dependencies(app_config, "a")

        error_msg = str(exc_info.value)
        assert "circular" in error_msg.lower()
        # Should show the cycle
        assert "a" in error_msg
        assert "b" in error_msg
        assert "c" in error_msg

    def test_missing_dependency(self):
        """Test error when dependency doesn't exist."""
        app_config = {
            "actions": {
                "build": {"command": ["echo", "build"], "depends_on": ["nonexistent"]},
            }
        }

        with pytest.raises(DependencyError) as exc_info:
            resolve_dependencies(app_config, "build")

        error_msg = str(exc_info.value)
        assert "not found" in error_msg
        assert "nonexistent" in error_msg

    def test_deep_dependency_chain(self):
        """Test deep dependency chain."""
        app_config = {
            "actions": {
                "step5": {"command": ["echo", "5"], "depends_on": ["step4"]},
                "step4": {"command": ["echo", "4"], "depends_on": ["step3"]},
                "step3": {"command": ["echo", "3"], "depends_on": ["step2"]},
                "step2": {"command": ["echo", "2"], "depends_on": ["step1"]},
                "step1": {"command": ["echo", "1"]},
            }
        }

        result = resolve_dependencies(app_config, "step5")
        assert result == ["step1", "step2", "step3", "step4", "step5"]


class TestValidateAllDependencies:
    """Test validation of all dependencies."""

    def test_all_valid_dependencies(self):
        """Test validation with all valid dependencies."""
        app_config = {
            "actions": {
                "build": {"command": ["echo", "build"], "depends_on": ["test"]},
                "test": {"command": ["echo", "test"], "depends_on": ["lint"]},
                "lint": {"command": ["echo", "lint"]},
            }
        }

        errors = validate_all_dependencies(app_config)
        assert errors == []

    def test_detect_missing_dependency(self):
        """Test detection of missing dependency."""
        app_config = {
            "actions": {
                "build": {"command": ["echo", "build"], "depends_on": ["missing"]},
                "test": {"command": ["echo", "test"]},
            }
        }

        errors = validate_all_dependencies(app_config)
        assert len(errors) == 1
        assert "build" in errors[0]
        assert "missing" in errors[0]

    def test_detect_circular_dependency(self):
        """Test detection of circular dependency."""
        app_config = {
            "actions": {
                "a": {"command": ["echo", "a"], "depends_on": ["b"]},
                "b": {"command": ["echo", "b"], "depends_on": ["a"]},
            }
        }

        errors = validate_all_dependencies(app_config)
        assert len(errors) >= 1
        # Should mention circular dependency
        assert any("circular" in err.lower() for err in errors)

    def test_multiple_errors(self):
        """Test detection of multiple errors."""
        app_config = {
            "actions": {
                "action1": {
                    "command": ["echo", "1"],
                    "depends_on": ["missing1"],
                },
                "action2": {
                    "command": ["echo", "2"],
                    "depends_on": ["missing2"],
                },
                "action3": {"command": ["echo", "3"]},
            }
        }

        errors = validate_all_dependencies(app_config)
        assert len(errors) == 2
        assert any("action1" in err and "missing1" in err for err in errors)
        assert any("action2" in err and "missing2" in err for err in errors)

    def test_invalid_depends_on_type(self):
        """Test detection of invalid depends_on type."""
        app_config = {
            "actions": {
                "build": {"command": ["echo", "build"], "depends_on": "not a list"},
            }
        }

        errors = validate_all_dependencies(app_config)
        assert len(errors) == 1
        assert "list" in errors[0].lower()

    def test_no_actions_with_dependencies(self):
        """Test validation when no actions have dependencies."""
        app_config = {
            "actions": {
                "run": {"command": ["echo", "run"]},
                "test": {"command": ["echo", "test"]},
            }
        }

        errors = validate_all_dependencies(app_config)
        assert errors == []

    def test_complex_dependency_graph(self):
        """Test validation of complex dependency graph."""
        app_config = {
            "actions": {
                "deploy": {
                    "command": ["echo", "deploy"],
                    "depends_on": ["build", "test"],
                },
                "build": {"command": ["echo", "build"], "depends_on": ["lint"]},
                "test": {
                    "command": ["echo", "test"],
                    "depends_on": ["lint", "fixtures"],
                },
                "lint": {"command": ["echo", "lint"]},
                "fixtures": {"command": ["echo", "fixtures"]},
            }
        }

        errors = validate_all_dependencies(app_config)
        assert errors == []
