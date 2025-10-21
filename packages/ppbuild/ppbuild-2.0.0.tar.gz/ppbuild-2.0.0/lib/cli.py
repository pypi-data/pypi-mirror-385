"""Command-line interface setup."""

import argparse
from typing import Any, Dict


def create_argument_parser(config: Dict[str, Any]) -> argparse.ArgumentParser:
    """Create the main argument parser with subparsers for each application."""
    parser = argparse.ArgumentParser(
        description="pp: System manager for tools and environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Applications")

    # Create subparser for each application
    for app_name, app_config in config["applications"].items():
        create_app_parser(app_name, app_config, subparsers)

    return parser


def create_app_parser(
    app_name: str,
    app_config: Dict[str, Any],
    subparsers: argparse._SubParsersAction,
) -> None:
    """Create argument parser for a single application."""
    help_text = app_config.get("help", f"Run {app_name}")
    app_parser = subparsers.add_parser(app_name, help=help_text)

    actions = app_config["actions"]
    default_action = app_config.get("default_action")

    # Simple interface: optional action argument
    if len(actions) == 1 or (default_action and len(actions) <= 3):
        # Add action as optional argument
        action_choices = list(actions.keys())
        app_parser.add_argument(
            "action",
            nargs="?",
            choices=action_choices,
            default=default_action,
            help=(
                f"Action to perform (default: {default_action})"
                if default_action
                else "Action to perform"
            ),
        )

        # Collect all parameters from all actions
        all_parameters = {}
        for action_config in actions.values():
            parameters = action_config.get("parameters", {})
            for param_name, param_config in parameters.items():
                if param_name not in all_parameters:
                    # Make all params optional since we don't know which action will run
                    param_copy = param_config.copy()
                    param_copy["required"] = False
                    all_parameters[param_name] = param_copy

        # Add parameter arguments
        for param_name, param_config in all_parameters.items():
            add_parameter_to_parser(app_parser, param_name, param_config)

    # Complex interface: action subparsers
    else:
        action_subparsers = app_parser.add_subparsers(
            dest="action", help="Available actions", metavar="ACTION"
        )

        # Create parser for each action
        for action_name, action_config in actions.items():
            action_help = action_config.get("help", f"Run {action_name}")
            action_parser = action_subparsers.add_parser(action_name, help=action_help)

            # Add parameters specific to this action
            parameters = action_config.get("parameters", {})
            for param_name, param_config in parameters.items():
                add_parameter_to_parser(action_parser, param_name, param_config)

        # Set default action if specified
        if default_action:
            app_parser.set_defaults(action=default_action)


def add_parameter_to_parser(
    parser: argparse.ArgumentParser, param_name: str, param_config: Dict[str, Any]
) -> None:
    """Add a parameter argument to an ArgumentParser."""
    param_type = param_config.get("type", "string")
    required = param_config.get("required", False)
    default = param_config.get("default")
    help_text = param_config.get("help", f"{param_name} parameter")
    choices = param_config.get("choices")

    # Convert parameter name to CLI argument format (e.g., my_param -> --my-param)
    arg_name = f"--{param_name.replace('_', '-')}"

    kwargs = {"dest": param_name, "help": help_text}

    # Boolean parameters are flags
    if param_type == "boolean":
        kwargs["action"] = "store_true"
        if default is True:
            # If default is True, use store_false and --no-X flag
            kwargs["action"] = "store_false"
            arg_name = f"--no-{param_name.replace('_', '-')}"
    else:
        # Non-boolean parameters
        if required:
            kwargs["required"] = True
        elif default is not None:
            kwargs["default"] = default

        # Set type converter
        if param_type == "integer":
            kwargs["type"] = int
        elif param_type == "float":
            kwargs["type"] = float
        else:  # string
            kwargs["type"] = str

        # Add choices if specified
        if choices:
            kwargs["choices"] = choices

    parser.add_argument(arg_name, **kwargs)
