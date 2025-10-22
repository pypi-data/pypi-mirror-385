"""
Environment variable management for taskx.
"""

import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import dotenv_values

from taskx.utils.shell import EnvironmentExpander


class EnvironmentManager:
    """Manages environment variables for task execution."""

    def __init__(self, global_env: Optional[Dict[str, str]] = None):
        """
        Initialize environment manager.

        Args:
            global_env: Global environment variables from config
        """
        self.global_env = global_env or {}
        self.dotenv_vars: Dict[str, str] = {}

    def load_dotenv(self, dotenv_path: Optional[Path] = None) -> None:
        """
        Load environment variables from .env file.

        Args:
            dotenv_path: Path to .env file (default: .env in current directory)
        """
        if dotenv_path is None:
            dotenv_path = Path(".env")

        if dotenv_path.exists():
            self.dotenv_vars = dict(dotenv_values(dotenv_path))

    def get_env_for_task(
        self,
        task_env: Optional[Dict[str, str]] = None,
        override_env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Build complete environment for task execution.

        Priority (highest to lowest):
        1. override_env (CLI flags)
        2. task_env (task-specific env)
        3. global_env (from config)
        4. dotenv_vars (from .env file)
        5. os.environ (system environment)

        Args:
            task_env: Task-specific environment variables
            override_env: Override environment variables (from CLI)

        Returns:
            Complete environment dictionary
        """
        # Start with system environment
        env = os.environ.copy()

        # Add .env variables
        env.update(self.dotenv_vars)

        # Add global environment from config
        env.update(self.global_env)

        # Add task-specific environment
        if task_env:
            env.update(task_env)

        # Add override environment (highest priority)
        if override_env:
            env.update(override_env)

        return env

    def expand_command(self, cmd: str, env: Dict[str, str]) -> str:
        """
        Expand environment variables in command.

        Args:
            cmd: Command with ${VAR} placeholders
            env: Environment variables to use for expansion

        Returns:
            Command with expanded variables
        """
        return EnvironmentExpander.expand_variables(cmd, env)

    def validate_required_vars(
        self, cmd: str, env: Dict[str, str]
    ) -> tuple[bool, list[str]]:
        """
        Check if all required variables are available.

        Args:
            cmd: Command to check
            env: Available environment variables

        Returns:
            Tuple of (all_available, missing_vars)
        """
        required_vars = EnvironmentExpander.find_variables(cmd)
        missing = [var for var in required_vars if var not in env]
        return (len(missing) == 0, missing)
