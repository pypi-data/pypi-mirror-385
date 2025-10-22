"""
Configuration loading and parsing.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from taskx.core.task import Task
from taskx.utils.validation import ConfigValidator


class ConfigError(Exception):
    """Raised when configuration is invalid."""

    pass


class Config:
    """
    Load and parse taskx configuration from pyproject.toml.

    The configuration is loaded from the [tool.taskx] section of pyproject.toml.

    Example configuration:
        [tool.taskx.env]
        APP_NAME = "myapp"
        VERSION = "1.0.0"

        [tool.taskx.tasks]
        test = "pytest"
        dev = { cmd = "uvicorn app:app --reload", env = { PORT = "8000" } }
        deploy = { depends = ["test", "build"], cmd = "deploy.sh" }

    Attributes:
        config_path: Path to the configuration file
        tasks: Dictionary of task names to Task objects
        env: Global environment variables
        settings: Global settings
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file (default: pyproject.toml)
        """
        self.config_path = config_path or Path("pyproject.toml")
        self.tasks: Dict[str, Task] = {}
        self.env: Dict[str, str] = {}
        self.settings: Dict[str, Any] = {}
        self._raw_data: Dict[str, Any] = {}

    def load(self) -> None:
        """
        Load configuration from file.

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ConfigError: If configuration is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Hint: Run 'taskx init' to create a configuration file"
            )

        try:
            with open(self.config_path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            raise ConfigError(f"Failed to parse {self.config_path}: {e}") from e

        # Get taskx config section
        tool_section = data.get("tool", {})
        taskx_config = tool_section.get("taskx", {})

        if not taskx_config:
            raise ConfigError(
                f"No [tool.taskx] section found in {self.config_path}\n"
                f"Hint: Run 'taskx init' to create a configuration file"
            )

        self._raw_data = taskx_config

        # Load environment variables
        self.env = taskx_config.get("env", {})
        self._validate_env(self.env)

        # Load settings
        self.settings = taskx_config.get("settings", {})

        # Load tasks
        tasks_data = taskx_config.get("tasks", {})
        if not tasks_data:
            raise ConfigError(
                f"No tasks defined in {self.config_path}\n"
                f"Hint: Add tasks under [tool.taskx.tasks]"
            )

        for name, task_def in tasks_data.items():
            try:
                self.tasks[name] = self._parse_task(name, task_def)
            except Exception as e:
                raise ConfigError(f"Failed to parse task '{name}': {e}") from e

        # Validate configuration
        validator = ConfigValidator()
        validator.validate_config(self)

    def _validate_env(self, env: Dict[str, str]) -> None:
        """
        Validate environment variables.

        Args:
            env: Environment variables to validate

        Raises:
            ConfigError: If environment variables are invalid
        """
        for key, value in env.items():
            if not isinstance(key, str):
                raise ConfigError(f"Environment variable key must be string, got {type(key)}")
            if not isinstance(value, str):
                raise ConfigError(
                    f"Environment variable '{key}' value must be string, got {type(value)}"
                )
            if not key.replace("_", "").isalnum():
                raise ConfigError(
                    f"Invalid environment variable name: '{key}'. "
                    f"Must contain only alphanumeric characters and underscores"
                )

    def _parse_task(self, name: str, task_def: Any) -> Task:
        """
        Parse task definition into Task object.

        Args:
            name: Task name
            task_def: Task definition (string or dict)

        Returns:
            Parsed Task object

        Raises:
            ConfigError: If task definition is invalid
        """
        if isinstance(task_def, str):
            # Simple string command
            return Task(name=name, cmd=task_def)

        elif isinstance(task_def, dict):
            # Complex task definition
            task_dict = task_def.copy()

            # Handle 'alias' field (reference to another task)
            if "alias" in task_dict:
                alias_name = task_dict["alias"]
                if alias_name not in self.tasks:
                    raise ConfigError(
                        f"Task '{name}' aliases non-existent task '{alias_name}'"
                    )
                # Copy the aliased task
                aliased_task = self.tasks[alias_name]
                return Task(
                    name=name,
                    cmd=aliased_task.cmd,
                    description=task_dict.get("description", aliased_task.description),
                    depends=aliased_task.depends,
                    env=aliased_task.env,
                )

            # Extract and validate fields
            cmd = task_dict.get("cmd", "")
            parallel = task_dict.get("parallel", [])

            if not cmd and not parallel:
                raise ConfigError(f"Task '{name}' must have 'cmd' or 'parallel' field")

            if cmd and parallel:
                raise ConfigError(f"Task '{name}' cannot have both 'cmd' and 'parallel'")

            return Task(
                name=name,
                cmd=cmd,
                description=task_dict.get("description"),
                depends=task_dict.get("depends", []),
                parallel=parallel,
                env=task_dict.get("env", {}),
                cwd=task_dict.get("cwd"),
                shell=task_dict.get("shell"),
                timeout=task_dict.get("timeout"),
                retry=task_dict.get("retry", 0),
                retry_delay=task_dict.get("retry_delay", 1),
                on_error=task_dict.get("on_error"),
                on_success=task_dict.get("on_success"),
                pre=task_dict.get("pre"),
                post=task_dict.get("post"),
                watch=task_dict.get("watch", []),
                prompt=task_dict.get("prompt"),
                confirm=task_dict.get("confirm"),
                if_platform=task_dict.get("if_platform"),
                if_env=task_dict.get("if_env"),
                silent=task_dict.get("silent", False),
                ignore_errors=task_dict.get("ignore_errors", False),
            )

        else:
            raise ConfigError(
                f"Invalid task definition for '{name}': "
                f"must be string or table, got {type(task_def)}"
            )

    def get_task(self, name: str) -> Optional[Task]:
        """
        Get task by name.

        Args:
            name: Task name

        Returns:
            Task object if found, None otherwise
        """
        return self.tasks.get(name)

    def has_task(self, name: str) -> bool:
        """
        Check if task exists.

        Args:
            name: Task name

        Returns:
            True if task exists, False otherwise
        """
        return name in self.tasks

    def task_names(self) -> list[str]:
        """
        Get list of all task names.

        Returns:
            Sorted list of task names
        """
        return sorted(self.tasks.keys())

    def __repr__(self) -> str:
        """String representation of config."""
        return f"Config({len(self.tasks)} tasks, {len(self.env)} env vars)"
