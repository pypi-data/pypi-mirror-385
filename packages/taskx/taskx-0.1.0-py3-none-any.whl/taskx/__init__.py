"""
taskx - Modern Python Task Runner

A task runner that combines the simplicity of npm scripts with the power of Make.
"""

__version__ = "0.1.0"
__author__ = "Vipin"
__all__ = ["__version__", "run_task", "load_config", "list_tasks"]

from taskx.core.config import Config
from taskx.core.runner import TaskRunner


def load_config(config_path: str = "pyproject.toml") -> Config:
    """Load taskx configuration from a file."""
    from pathlib import Path

    config = Config(Path(config_path))
    config.load()
    return config


def list_tasks(config_path: str = "pyproject.toml") -> list[str]:
    """List all available tasks."""
    config = load_config(config_path)
    return list(config.tasks.keys())


def run_task(task_name: str, config_path: str = "pyproject.toml") -> bool:
    """Run a specific task."""
    config = load_config(config_path)
    runner = TaskRunner(config)
    return runner.run(task_name)
