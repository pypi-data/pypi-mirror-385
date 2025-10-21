"""Unit tests for lib/params.py"""

import pytest

from lib.params import (ParameterError, convert_boolean, convert_float,
                        convert_integer, convert_string, parse_parameters,
                        substitute_parameters, validate_and_convert_parameter)


class TestTypeConverters:
    """Test type conversion functions."""

    def test_convert_string(self):
        """Test string conversion."""
        assert convert_string("hello") == "hello"
        assert convert_string(123) == "123"
        assert convert_string(None) == ""

    def test_convert_integer(self):
        """Test integer conversion."""
        assert convert_integer(42) == 42
        assert convert_integer("42") == 42
        assert convert_integer(3.14) == 3

    def test_convert_integer_invalid(self):
        """Test integer conversion with invalid input."""
        with pytest.raises(ParameterError):
            convert_integer("not a number")

    def test_convert_float(self):
        """Test float conversion."""
        assert convert_float(3.14) == 3.14
        assert convert_float("3.14") == 3.14
        assert convert_float(42) == 42.0

    def test_convert_float_invalid(self):
        """Test float conversion with invalid input."""
        with pytest.raises(ParameterError):
            convert_float("not a number")

    def test_convert_boolean(self):
        """Test boolean conversion."""
        # Boolean inputs
        assert convert_boolean(True) is True
        assert convert_boolean(False) is False

        # String inputs
        assert convert_boolean("true") is True
        assert convert_boolean("TRUE") is True
        assert convert_boolean("1") is True
        assert convert_boolean("yes") is True
        assert convert_boolean("on") is True

        assert convert_boolean("false") is False
        assert convert_boolean("0") is False
        assert convert_boolean("no") is False

        # Other inputs
        assert convert_boolean(1) is True
        assert convert_boolean(0) is False


class TestValidateAndConvertParameter:
    """Test parameter validation and conversion."""

    def test_string_parameter(self):
        """Test string parameter validation."""
        param_config = {"type": "string"}
        result = validate_and_convert_parameter("name", param_config, "Alice")
        assert result == "Alice"

    def test_string_parameter_with_choices(self):
        """Test string parameter with choices."""
        param_config = {"type": "string", "choices": ["a", "b", "c"]}

        result = validate_and_convert_parameter("mode", param_config, "b")
        assert result == "b"

    def test_string_parameter_invalid_choice(self):
        """Test error with invalid choice."""
        param_config = {"type": "string", "choices": ["a", "b", "c"]}

        with pytest.raises(ParameterError) as exc_info:
            validate_and_convert_parameter("mode", param_config, "d")

        assert "choice" in str(exc_info.value).lower()

    def test_required_parameter_missing(self):
        """Test error when required parameter is missing."""
        param_config = {"type": "string", "required": True}

        with pytest.raises(ParameterError) as exc_info:
            validate_and_convert_parameter("name", param_config, None)

        assert "required" in str(exc_info.value).lower()

    def test_parameter_with_default(self):
        """Test parameter uses default value."""
        param_config = {"type": "string", "default": "default_value"}

        result = validate_and_convert_parameter("name", param_config, None)
        assert result == "default_value"

    def test_integer_parameter(self):
        """Test integer parameter validation."""
        param_config = {"type": "integer"}

        result = validate_and_convert_parameter("count", param_config, "42")
        assert result == 42
        assert isinstance(result, int)

    def test_integer_parameter_with_min_max(self):
        """Test integer parameter with min/max constraints."""
        param_config = {"type": "integer", "min": 1, "max": 10}

        # Valid value
        result = validate_and_convert_parameter("count", param_config, 5)
        assert result == 5

        # Below minimum
        with pytest.raises(ParameterError) as exc_info:
            validate_and_convert_parameter("count", param_config, 0)
        assert "minimum" in str(exc_info.value).lower()

        # Above maximum
        with pytest.raises(ParameterError) as exc_info:
            validate_and_convert_parameter("count", param_config, 11)
        assert "maximum" in str(exc_info.value).lower()

    def test_float_parameter(self):
        """Test float parameter validation."""
        param_config = {"type": "float"}

        result = validate_and_convert_parameter("value", param_config, "3.14")
        assert result == 3.14
        assert isinstance(result, float)

    def test_float_parameter_with_constraints(self):
        """Test float parameter with min/max."""
        param_config = {"type": "float", "min": 0.0, "max": 1.0}

        result = validate_and_convert_parameter("value", param_config, 0.5)
        assert result == 0.5

        with pytest.raises(ParameterError):
            validate_and_convert_parameter("value", param_config, 1.5)

    def test_boolean_parameter(self):
        """Test boolean parameter validation."""
        param_config = {"type": "boolean"}

        result = validate_and_convert_parameter("verbose", param_config, True)
        assert result is True

        result = validate_and_convert_parameter("verbose", param_config, False)
        assert result is False

    def test_boolean_parameter_default(self):
        """Test boolean parameter defaults to False."""
        param_config = {"type": "boolean"}

        result = validate_and_convert_parameter("verbose", param_config, None)
        assert result is False


class TestSubstituteParameters:
    """Test parameter substitution in commands."""

    def test_simple_substitution(self):
        """Test simple parameter substitution."""
        command = ["echo", "Hello {name}"]
        parameters = {"name": "Alice"}

        result = substitute_parameters(command, parameters)
        assert result == ["echo", "Hello Alice"]

    def test_multiple_substitutions(self):
        """Test multiple parameters in one argument."""
        command = ["echo", "{name} has {count} apples"]
        parameters = {"name": "Bob", "count": 5}

        result = substitute_parameters(command, parameters)
        assert result == ["echo", "Bob has 5 apples"]

    def test_conditional_flag_true(self):
        """Test conditional flag when parameter is True."""
        command = ["pytest", "{verbose:--verbose}", "{cov:--cov}"]
        parameters = {"verbose": True, "cov": True}

        result = substitute_parameters(command, parameters)
        assert result == ["pytest", "--verbose", "--cov"]

    def test_conditional_flag_false(self):
        """Test conditional flag when parameter is False."""
        command = ["pytest", "{verbose:--verbose}", "{cov:--cov}"]
        parameters = {"verbose": False, "cov": False}

        result = substitute_parameters(command, parameters)
        assert result == ["pytest"]

    def test_conditional_flag_mixed(self):
        """Test mix of True and False conditional flags."""
        command = ["pytest", "{verbose:--verbose}", "tests/", "{cov:--cov}"]
        parameters = {"verbose": True, "cov": False}

        result = substitute_parameters(command, parameters)
        assert result == ["pytest", "--verbose", "tests/"]

    def test_no_parameters_to_substitute(self):
        """Test command with no parameter references."""
        command = ["echo", "hello", "world"]
        parameters = {}

        result = substitute_parameters(command, parameters)
        assert result == ["echo", "hello", "world"]

    def test_missing_parameter_value(self):
        """Test substitution when parameter value is missing."""
        command = ["echo", "Hello {name}"]
        parameters = {}

        result = substitute_parameters(command, parameters)
        # Missing parameter should be removed
        assert result == ["echo", "Hello"]

    def test_empty_arguments_removed(self):
        """Test that empty arguments are removed."""
        command = ["echo", "{missing_param}"]
        parameters = {}

        result = substitute_parameters(command, parameters)
        # Should remove the empty argument entirely
        assert result == ["echo"]

    def test_non_string_arguments(self):
        """Test handling of non-string arguments."""
        command = ["echo", 123, "test"]
        parameters = {}

        result = substitute_parameters(command, parameters)
        assert result == ["echo", "123", "test"]


class TestParseParameters:
    """Test parameter parsing from CLI args."""

    def test_parse_simple_parameters(self, mock_args):
        """Test parsing simple parameters."""
        action_config = {
            "parameters": {
                "name": {"type": "string", "required": True},
                "count": {"type": "integer", "default": 1},
            }
        }

        args = mock_args(name="Alice", count=3)
        result = parse_parameters(action_config, args)

        assert result["name"] == "Alice"
        assert result["count"] == 3

    def test_parse_with_defaults(self, mock_args):
        """Test parsing uses default values."""
        action_config = {
            "parameters": {
                "name": {"type": "string", "default": "Anonymous"},
                "count": {"type": "integer", "default": 1},
            }
        }

        args = mock_args(name=None, count=None)
        result = parse_parameters(action_config, args)

        assert result["name"] == "Anonymous"
        assert result["count"] == 1

    def test_parse_boolean_parameters(self, mock_args):
        """Test parsing boolean parameters."""
        action_config = {
            "parameters": {
                "verbose": {"type": "boolean", "default": False},
                "debug": {"type": "boolean", "default": False},
            }
        }

        args = mock_args(verbose=True, debug=None)
        result = parse_parameters(action_config, args)

        assert result["verbose"] is True
        assert result["debug"] is False

    def test_parse_missing_required_parameter(self, mock_args):
        """Test error when required parameter is missing."""
        action_config = {
            "parameters": {
                "name": {"type": "string", "required": True},
            }
        }

        args = mock_args(name=None)

        with pytest.raises(ParameterError) as exc_info:
            parse_parameters(action_config, args)

        assert "required" in str(exc_info.value).lower()

    def test_parse_no_parameters(self, mock_args):
        """Test parsing action with no parameters."""
        action_config = {}
        args = mock_args()

        result = parse_parameters(action_config, args)
        assert result == {}
