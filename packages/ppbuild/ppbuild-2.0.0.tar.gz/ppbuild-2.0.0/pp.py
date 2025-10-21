#!/usr/bin/env python3
"""pp: System manager for tools and environments"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from lib import (ConfigError, DependencyError, ExecutionError, ParameterError,
                 create_argument_parser, execute_action, load_config,
                 reset_execution_tracking, resolve_dependencies)

# Configuration paths
BASE_DIR = Path(os.getenv("PP_BASE_DIR", "."))
CONFIG_FILE = os.getenv("PP_CONFIG_FILE", "pp.yaml")
ENV_FILE = os.getenv("PP_ENV_FILE", ".pp.env")

# Setup logging
LOG_LEVEL = os.getenv("PP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("pp")


def get_config_path() -> Path:
    """Get configuration file path, checking current directory then ~/.pp/"""
    # Try current directory first
    config_path = (BASE_DIR / CONFIG_FILE).resolve()
    if config_path.exists():
        return config_path

    # Fall back to ~/.pp/
    home_config = Path.home() / ".pp" / CONFIG_FILE
    if home_config.exists():
        return home_config

    # Return the local path for error message purposes
    return config_path


def load_environment() -> None:
    """Load environment variables from .env file if it exists."""
    env_path = (BASE_DIR / ENV_FILE).resolve()
    if env_path.exists():
        load_dotenv(env_path)
        logger.debug(f"Loaded environment from {env_path}")
    else:
        logger.debug(f"No .env file found at {env_path}")


def determine_action(args, app_config) -> str:
    """Determine which action to execute."""
    # Try to get action from command line
    action_name = getattr(args, "action", None)
    if action_name:
        return action_name

    # Try default action
    default_action = app_config.get("default_action")
    if default_action:
        logger.debug(f"Using default action: {default_action}")
        return default_action

    # If only one action, use it automatically
    actions = app_config.get("actions", {})
    if len(actions) == 1:
        single_action = list(actions.keys())[0]
        logger.debug(f"Using only available action: {single_action}")
        return single_action

    # No action specified and no default
    print(f"Error: No action specified and no default action defined")
    print(f"Available actions: {', '.join(actions.keys())}")
    print(f"Usage: pp {args.subcommand} <action>")
    sys.exit(1)


def main():
    """Main entry point."""
    # Load environment variables
    load_environment()

    # Load and validate configuration
    try:
        config_path = get_config_path()
        config = load_config(config_path)
        logger.debug("Configuration loaded successfully")
    except ConfigError as e:
        logger.error(str(e))
        sys.exit(1)

    # Create argument parser and parse arguments
    parser = create_argument_parser(config)
    args = parser.parse_args()

    # Show help if no subcommand
    if not args.subcommand:
        parser.print_help()
        sys.exit(1)

    try:
        # Reset execution tracking for this run
        reset_execution_tracking()

        # Get application config
        app_name = args.subcommand
        app_config = config["applications"][app_name]

        # Determine which action to run
        action_name = determine_action(args, app_config)

        # Resolve dependencies
        execution_order = resolve_dependencies(app_config, action_name)
        logger.debug(f"Execution order: {' -> '.join(execution_order)}")

        # Execute action and its dependencies
        execute_action(app_name, action_name, config, args, execution_order)

        logger.info(f"Completed {app_name}.{action_name}")

    except (ConfigError, ParameterError, DependencyError, ExecutionError) as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug("Exception details:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
