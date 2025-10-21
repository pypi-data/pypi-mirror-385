"""Dependency resolution for action execution order."""

import logging
from typing import Any, Dict, List, Set

logger = logging.getLogger("pp")


class DependencyError(Exception):
    """Dependency resolution errors."""

    pass


def resolve_dependencies(app_config: Dict[str, Any], action_name: str) -> List[str]:
    """
    Resolve dependencies for an action and return execution order.

    Uses depth-first search to perform topological sort of the dependency graph.

    Args:
        app_config: Application configuration dictionary
        action_name: Name of the action to resolve

    Returns:
        List of action names in execution order (dependencies first)

    Raises:
        DependencyError: If circular dependency or missing dependency found
    """
    actions = app_config.get("actions", {})
    visited: Set[str] = set()
    visiting: Set[str] = set()
    order: List[str] = []

    def visit(current: str, path: List[str]) -> None:
        """Visit action and its dependencies (DFS for topological sort)."""
        # Detect circular dependencies
        if current in visiting:
            cycle = " -> ".join(path + [current])
            raise DependencyError(
                f"Circular dependency detected: {cycle}\n"
                f"Remove circular dependency from your action definitions"
            )

        # Already visited this action
        if current in visited:
            return

        # Check if action exists
        if current not in actions:
            raise DependencyError(
                f"Dependency '{current}' not found\n"
                f"Available actions: {', '.join(actions.keys())}\n"
                f"Add '{current}' action or remove it from depends_on"
            )

        visiting.add(current)

        # Visit all dependencies first
        action_config = actions[current]
        dependencies = action_config.get("depends_on", [])

        if dependencies:
            logger.debug(f"Action '{current}' depends on: {', '.join(dependencies)}")

        for dep in dependencies:
            visit(dep, path + [current])

        visiting.remove(current)
        visited.add(current)
        order.append(current)

    # Start DFS from the requested action
    visit(action_name, [])
    return order


def validate_all_dependencies(app_config: Dict[str, Any]) -> List[str]:
    """
    Validate all action dependencies in the application.

    Returns:
        List of error messages (empty if all valid)
    """
    errors = []
    actions = app_config.get("actions", {})

    for action_name, action_config in actions.items():
        dependencies = action_config.get("depends_on", [])

        if not dependencies:
            continue

        # Check dependencies list type
        if not isinstance(dependencies, list):
            errors.append(
                f"Action '{action_name}': depends_on must be a list, "
                f"got {type(dependencies).__name__}"
            )
            continue

        # Check each dependency exists
        has_missing = False
        for dep in dependencies:
            if dep not in actions:
                errors.append(f"Action '{action_name}': dependency '{dep}' not found")
                has_missing = True

        # Check for circular dependencies if all deps exist
        if not has_missing:
            try:
                resolve_dependencies(app_config, action_name)
            except DependencyError as e:
                errors.append(f"Action '{action_name}': {str(e)}")

    return errors
