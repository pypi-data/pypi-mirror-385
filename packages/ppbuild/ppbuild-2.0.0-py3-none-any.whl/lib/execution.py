"""Command execution with environment and directory setup."""

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("pp")


class ExecutionError(Exception):
    """Execution-related errors."""

    pass


def expand_path(path_str: str) -> Path:
    """Expand ~ and environment variables in path."""
    expanded = os.path.expanduser(path_str)
    expanded = os.path.expandvars(expanded)
    return Path(expanded).resolve()


def substitute_env_vars(
    env_vars: Dict[str, str], base_env: Dict[str, str]
) -> Dict[str, str]:
    """Substitute ${VAR} references in environment variables."""
    result = {}
    for key, value in env_vars.items():
        if isinstance(value, str):
            # Replace ${VAR} with environment variable values
            def replacer(match):
                var_name = match.group(1)
                return base_env.get(var_name, os.environ.get(var_name, ""))

            result[key] = re.sub(r"\$\{([^}]+)\}", replacer, value)
        else:
            result[key] = str(value)
    return result


def setup_venv_environment(
    venv_path: str, env: Dict[str, str], working_dir: Optional[Path] = None
) -> Dict[str, str]:
    """Setup virtual environment in PATH."""
    # Resolve venv path relative to working directory if needed
    if working_dir and not Path(venv_path).is_absolute():
        venv_full_path = working_dir / venv_path
    else:
        venv_full_path = expand_path(venv_path)

    if not venv_full_path.exists():
        raise ExecutionError(
            f"Virtual environment not found: {venv_full_path}\n"
            f"Create it with: python -m venv {venv_path}"
        )

    # Add venv bin to PATH
    venv_bin = venv_full_path / "bin"
    if not venv_bin.exists():
        venv_bin = venv_full_path / "Scripts"  # Windows

    env["VIRTUAL_ENV"] = str(venv_full_path)
    env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"

    return env


def setup_environment(
    app_config: Dict[str, Any], base_env: Optional[Dict[str, str]] = None
) -> tuple[Dict[str, str], Optional[Path]]:
    """
    Setup environment variables and working directory.

    Returns:
        Tuple of (environment dict, working directory path or None)
    """
    env = (base_env or os.environ).copy()
    working_dir = None

    # Handle working directory
    if "directory" in app_config:
        working_dir = expand_path(app_config["directory"])
        if not working_dir.is_dir():
            raise ExecutionError(
                f"Working directory not found: {working_dir}\n"
                f"Create it or check the 'directory' setting in your config"
            )

    # Handle custom environment variables
    if "env_vars" in app_config:
        custom_env = substitute_env_vars(app_config["env_vars"], env)
        env.update(custom_env)

    # Handle virtual environment
    if "venv" in app_config:
        env = setup_venv_environment(app_config["venv"], env, working_dir)

    return env, working_dir


def execute_command(
    command: List[str], env: Dict[str, str], working_dir: Optional[Path] = None
) -> None:
    """Execute a command with subprocess."""
    # Change directory if needed
    original_dir = None
    if working_dir:
        original_dir = Path.cwd()
        os.chdir(working_dir)
        logger.debug(f"Changed directory to {working_dir}")

    try:
        # Convert all command parts to strings
        cmd = [str(c) for c in command]
        logger.debug(f"Running command: {' '.join(cmd)}")

        # Run command
        subprocess.run(cmd, check=True, shell=False, env=env)

    except subprocess.CalledProcessError as e:
        raise ExecutionError(
            f"Command failed with exit code {e.returncode}: {' '.join(command)}\n"
            f"Check the command syntax and verify dependencies are installed"
        )
    except FileNotFoundError as e:
        raise ExecutionError(
            f"Command not found: {command[0]}\n"
            f"Install the required command or check your PATH"
        )
    finally:
        # Restore original directory
        if original_dir:
            os.chdir(original_dir)


# Track executed actions to avoid duplicate execution in dependency chains
_executed_actions: Set[str] = set()


def reset_execution_tracking():
    """Reset execution tracking (useful for testing)."""
    global _executed_actions
    _executed_actions = set()


def execute_action(
    app_name: str,
    action_name: str,
    config: Dict[str, Any],
    args,
    resolved_dependencies: List[str],
) -> None:
    """
    Execute an action and all its dependencies.

    Args:
        app_name: Name of the application
        action_name: Name of the action to execute
        config: Full configuration dictionary
        args: Parsed command-line arguments
        resolved_dependencies: List of actions in execution order (from dependency resolver)
    """
    from lib.params import parse_parameters, substitute_parameters

    app_config = config["applications"][app_name]

    # Setup environment once for the entire execution chain
    env, working_dir = setup_environment(app_config)

    # Change to working directory if specified
    if working_dir:
        os.chdir(working_dir)
        logger.debug(f"Changed directory to {working_dir}")

    # Execute all actions in dependency order
    for action_to_execute in resolved_dependencies:
        action_key = f"{app_name}:{action_to_execute}"

        # Skip if already executed
        if action_key in _executed_actions:
            logger.debug(f"Skipping already executed action: {action_to_execute}")
            continue

        logger.info(f"Executing action: {app_name}.{action_to_execute}")

        action_config = app_config["actions"][action_to_execute]
        cmd = action_config.get("command")

        if not cmd:
            logger.warning(f"Action '{action_to_execute}' has no command, skipping")
            continue

        # Parse and substitute parameters only for the main action (not dependencies)
        if action_to_execute == action_name and action_config.get("parameters"):
            parameters = parse_parameters(action_config, args)
            cmd = substitute_parameters(cmd, parameters)
            logger.debug(f"Command after parameter substitution: {cmd}")

        # Execute the command
        execute_command(cmd, env)

        # Mark as executed
        _executed_actions.add(action_key)
