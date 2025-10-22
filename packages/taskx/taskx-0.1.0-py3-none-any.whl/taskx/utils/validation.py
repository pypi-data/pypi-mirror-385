"""
Configuration and security validation for taskx.
"""

from pathlib import Path
from typing import TYPE_CHECKING, List, Set

if TYPE_CHECKING:
    from taskx.core.config import Config
    from taskx.core.task import Task


class ConfigValidator:
    """Validates taskx configuration."""

    def validate_config(self, config: "Config") -> None:
        """
        Validate entire configuration.

        Args:
            config: Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        # Check for circular dependencies
        self._check_circular_dependencies(config)

        # Validate all task references
        self._validate_task_references(config)

        # Validate task names
        self._validate_task_names(config)

    def _check_circular_dependencies(self, config: "Config") -> None:
        """Check for circular dependencies in tasks."""
        from taskx.core.dependency import DependencyResolver

        resolver = DependencyResolver(config.tasks)

        for task_name in config.tasks:
            try:
                resolver.resolve_dependencies(task_name)
            except ValueError as e:
                raise ValueError(f"Circular dependency detected: {e}") from e

    def _validate_task_references(self, config: "Config") -> None:
        """Validate that all task dependencies exist."""
        for task_name, task in config.tasks.items():
            for dep in task.depends:
                if dep not in config.tasks:
                    raise ValueError(
                        f"Task '{task_name}' depends on non-existent task '{dep}'"
                    )

    def _validate_task_names(self, config: "Config") -> None:
        """Validate task names are valid identifiers."""
        for task_name in config.tasks:
            if not task_name:
                raise ValueError("Task name cannot be empty")

            # Task names should be valid identifiers (alphanumeric + underscore/dash)
            if not all(c.isalnum() or c in "_-" for c in task_name):
                raise ValueError(
                    f"Invalid task name '{task_name}': "
                    f"must contain only alphanumeric characters, underscores, and hyphens"
                )


class SecurityValidator:
    """Security validation for taskx operations."""

    # Sensitive directories that should be blocked
    BLOCKED_PATHS = [
        "/etc",
        "/bin",
        "/sbin",
        "/usr/bin",
        "/usr/sbin",
        "/System",
        "/Windows",
        "/boot",
    ]

    # Dangerous environment variables
    DANGEROUS_ENV_VARS = [
        "LD_PRELOAD",
        "LD_LIBRARY_PATH",
        "DYLD_INSERT_LIBRARIES",
        "DYLD_LIBRARY_PATH",
    ]

    @staticmethod
    def validate_path(path: str, base_dir: Path) -> bool:
        """
        Validate that path is within base directory (prevent path traversal).

        Args:
            path: Path to validate
            base_dir: Base directory to constrain to

        Returns:
            True if path is safe, False otherwise
        """
        try:
            abs_path = Path(path).resolve()
            abs_base = base_dir.resolve()

            # Check if path is within base directory
            try:
                abs_path.relative_to(abs_base)
                return True
            except ValueError:
                return False
        except Exception:
            return False

    @staticmethod
    def is_dangerous_env_var(name: str) -> bool:
        """
        Check if environment variable is dangerous.

        Args:
            name: Environment variable name

        Returns:
            True if dangerous, False otherwise
        """
        return name in SecurityValidator.DANGEROUS_ENV_VARS

    @staticmethod
    def validate_env_vars(env: dict) -> List[str]:
        """
        Validate environment variables for security issues.

        Args:
            env: Environment variables to validate

        Returns:
            List of warnings/issues found
        """
        issues = []

        for name, value in env.items():
            if SecurityValidator.is_dangerous_env_var(name):
                issues.append(
                    f"Warning: Dangerous environment variable '{name}' detected. "
                    f"This could be a security risk."
                )

        return issues
