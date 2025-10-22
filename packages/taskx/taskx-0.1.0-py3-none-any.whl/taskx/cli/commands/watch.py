"""
Watch command implementation.

Provides file watching and auto-restart functionality for tasks.
"""

from pathlib import Path
from typing import Dict, Optional

import click
from rich.console import Console

from taskx.core.config import Config
from taskx.core.runner import TaskRunner
from taskx.execution.watcher import watch_task_sync


@click.command()
@click.argument("task_name")
@click.option("--env", "-e", multiple=True, help="Environment variable overrides (KEY=VALUE)")
@click.option("--pattern", "-p", multiple=True, help="Additional file patterns to watch (overrides task patterns)")
@click.pass_context
def watch(
    ctx: click.Context,
    task_name: str,
    env: tuple,
    pattern: tuple,
) -> None:
    """
    Watch files and auto-restart task on changes.

    Examples:

        # Watch using task's defined patterns
        $ taskx watch dev

        # Override watch patterns
        $ taskx watch dev -p "*.py" -p "*.toml"

        # Pass environment variables
        $ taskx watch dev --env PORT=8000

    The watch command will:
    1. Run the task once initially
    2. Watch for file changes
    3. Re-run the task when changes are detected
    4. Apply debouncing to avoid excessive re-runs

    Press Ctrl+C to stop watching.
    """
    console: Console = ctx.obj["console"]
    config_path: Path = ctx.obj["config_path"]

    # Load configuration
    try:
        config = Config(config_path)
        config.load()
    except Exception as e:
        console.print(f"[red]✗ Failed to load configuration: {e}[/red]")
        ctx.exit(1)

    # Check if task exists
    if task_name not in config.tasks:
        console.print(f"[red]✗ Task '{task_name}' not found[/red]")
        console.print(f"[yellow]Available tasks: {', '.join(config.tasks.keys())}[/yellow]")
        ctx.exit(1)

    task = config.tasks[task_name]

    # Parse environment overrides
    env_overrides: Dict[str, str] = {}
    for e in env:
        if "=" in e:
            key, value = e.split("=", 1)
            env_overrides[key] = value

    # Determine watch patterns
    watch_patterns = list(pattern) if pattern else task.watch

    if not watch_patterns:
        console.print(f"[red]✗ Task '{task_name}' has no watch patterns defined[/red]")
        console.print("[yellow]Hint: Add watch patterns to your task definition:[/yellow]")
        console.print(f"[dim]  {task_name} = {{ cmd = \"...\", watch = [\"*.py\", \"*.toml\"] }}[/dim]")
        ctx.exit(1)

    # Create execution callback
    def execute_task() -> bool:
        """Execute the task with the runner."""
        runner = TaskRunner(config, console)
        return runner.run(task_name, env_overrides)

    # Start watching
    try:
        # Update task's watch patterns if overridden
        if pattern:
            task.watch = list(pattern)

        watch_task_sync(
            task=task,
            execute_callback=execute_task,
            patterns=watch_patterns,
            cwd=task.cwd,
            console=console,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]⊘ Watch mode stopped[/yellow]")
    except Exception as e:
        console.print(f"\n[red]✗ Watch failed: {e}[/red]")
        ctx.exit(1)
