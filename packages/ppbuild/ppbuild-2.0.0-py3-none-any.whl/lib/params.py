"""Parameter handling - validation and substitution."""

import re
from typing import Any, Dict, List


class ParameterError(Exception):
    """Parameter validation errors."""

    pass


# Type converters
def convert_string(value: Any) -> str:
    """Convert value to string."""
    if value is None:
        return ""
    return str(value)


def convert_integer(value: Any) -> int:
    """Convert value to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ParameterError(f"Cannot convert '{value}' to integer")


def convert_float(value: Any) -> float:
    """Convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ParameterError(f"Cannot convert '{value}' to float")


def convert_boolean(value: Any) -> bool:
    """Convert value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)


TYPE_CONVERTERS = {
    "string": convert_string,
    "integer": convert_integer,
    "float": convert_float,
    "boolean": convert_boolean,
}


def validate_and_convert_parameter(
    param_name: str, param_config: Dict[str, Any], value: Any
) -> Any:
    """Validate and convert parameter value based on its configuration."""
    param_type = param_config.get("type", "string")
    required = param_config.get("required", False)
    default = param_config.get("default")
    choices = param_config.get("choices")
    min_val = param_config.get("min")
    max_val = param_config.get("max")

    # Handle None/missing values
    if value is None or value == "":
        if required:
            raise ParameterError(
                f"Required parameter '{param_name}' is missing.\n"
                f"Use --{param_name} <value> to provide a value."
            )
        if default is not None:
            value = default
        elif param_type == "boolean":
            value = False
        else:
            return default

    # Convert to correct type
    converter = TYPE_CONVERTERS.get(param_type)
    if not converter:
        raise ParameterError(f"Unknown parameter type: {param_type}")

    try:
        converted_value = converter(value)
    except ParameterError:
        raise
    except Exception as e:
        raise ParameterError(
            f"Invalid value for parameter '{param_name}': {value}\n"
            f"Expected type: {param_type}"
        )

    # Validate choices
    if choices and converted_value not in choices:
        raise ParameterError(
            f"Invalid choice for parameter '{param_name}': {converted_value}\n"
            f"Valid choices: {', '.join(map(str, choices))}"
        )

    # Validate numeric constraints
    if param_type in ("integer", "float"):
        if min_val is not None and converted_value < min_val:
            raise ParameterError(
                f"Parameter '{param_name}' value {converted_value} is below minimum {min_val}"
            )
        if max_val is not None and converted_value > max_val:
            raise ParameterError(
                f"Parameter '{param_name}' value {converted_value} exceeds maximum {max_val}"
            )

    return converted_value


def parse_parameters(action_config: Dict[str, Any], args) -> Dict[str, Any]:
    """Parse and validate all parameters for an action."""
    parameters = {}
    param_configs = action_config.get("parameters", {})

    for param_name, param_config in param_configs.items():
        # Get value from command line args
        value = getattr(args, param_name, None)

        # Validate and convert
        parameters[param_name] = validate_and_convert_parameter(
            param_name, param_config, value
        )

    return parameters


def substitute_parameters(command: List[str], parameters: Dict[str, Any]) -> List[str]:
    """
    Substitute parameters in command.

    Supports two syntaxes:
    - {param}: Direct substitution with parameter value
    - {param:--flag}: Conditional - includes flag only if param is True
    """
    result = []

    for arg in command:
        if not isinstance(arg, str):
            result.append(str(arg))
            continue

        # Find all parameter references in this argument
        param_refs = re.findall(r"\{([^}]+)\}", arg)

        if not param_refs:
            result.append(arg)
            continue

        # Process each parameter reference
        processed_arg = arg
        for param_ref in param_refs:
            if ":" in param_ref:
                # Conditional flag format: {param:--flag}
                param_name, flag = param_ref.split(":", 1)
                param_value = parameters.get(param_name)

                if param_value is True:
                    # Replace with the flag
                    processed_arg = processed_arg.replace(f"{{{param_ref}}}", flag)
                else:
                    # Remove the flag
                    processed_arg = processed_arg.replace(f"{{{param_ref}}}", "")
            else:
                # Direct substitution: {param}
                param_name = param_ref
                param_value = parameters.get(param_name)

                if param_value is not None:
                    processed_arg = processed_arg.replace(
                        f"{{{param_ref}}}", str(param_value)
                    )
                else:
                    # Remove the parameter reference
                    processed_arg = processed_arg.replace(f"{{{param_ref}}}", "")

        # Only add non-empty arguments
        if processed_arg.strip():
            result.append(processed_arg.strip())

    return result
