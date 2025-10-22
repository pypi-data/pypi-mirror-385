"""
Main CLI entry point for taskx.

Copyright (c) 2025 taskx Project
Licensed under Proprietary License - See LICENSE file

This software is free to use but cannot be modified, copied, or redistributed.
License notices must be preserved in all uses. See LICENSE file for full terms.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from taskx import __version__
from taskx.cli.commands.graph import graph
from taskx.cli.commands.watch import watch
from taskx.core.config import Config, ConfigError
from taskx.core.runner import TaskRunner
from taskx.formatters.console import ConsoleFormatter


@click.group(invoke_without_command=True)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default="pyproject.toml",
    help="Path to configuration file",
)
@click.option("--version", "-v", is_flag=True, help="Show version and exit")
@click.pass_context
def cli(ctx: click.Context, config: str, version: bool) -> None:
    """
    taskx - Modern Python Task Runner

    npm scripts for Python. Simple task automation that just works.
    """
    # Store config path in context
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = Path(config)
    ctx.obj["console"] = Console()
    ctx.obj["formatter"] = ConsoleFormatter(ctx.obj["console"])

    # Show version if requested
    if version:
        click.echo(f"taskx version {__version__}")
        ctx.exit(0)

    # If no subcommand, show available tasks
    if ctx.invoked_subcommand is None:
        try:
            cfg = Config(ctx.obj["config_path"])
            cfg.load()
            ctx.obj["formatter"].print_task_list(cfg.tasks)
        except (FileNotFoundError, ConfigError) as e:
            ctx.obj["formatter"].print_error(str(e))
            click.echo("\nHint: Run 'taskx init' to create a configuration file")
            ctx.exit(1)


@cli.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List all available tasks."""
    try:
        cfg = Config(ctx.obj["config_path"])
        cfg.load()
        ctx.obj["formatter"].print_task_list(cfg.tasks)
    except (FileNotFoundError, ConfigError) as e:
        ctx.obj["formatter"].print_error(str(e))
        ctx.exit(1)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument("task_name")
@click.option("--env", "-e", multiple=True, help="Set environment variable (KEY=VALUE)")
@click.pass_context
def run(ctx: click.Context, task_name: str, env: tuple) -> None:
    """Run a specific task."""
    try:
        # Load configuration
        cfg = Config(ctx.obj["config_path"])
        cfg.load()

        # Check if task exists
        if task_name not in cfg.tasks:
            ctx.obj["formatter"].print_error(f"Task '{task_name}' not found")
            click.echo(f"\nAvailable tasks: {', '.join(sorted(cfg.tasks.keys()))}")
            ctx.exit(1)

        # Parse environment overrides
        env_overrides = {}
        for e in env:
            if "=" in e:
                key, value = e.split("=", 1)
                env_overrides[key] = value

        # Run task
        runner = TaskRunner(cfg, ctx.obj["console"])
        success = runner.run(task_name, env_overrides)

        if not success:
            ctx.exit(1)

    except (FileNotFoundError, ConfigError) as e:
        ctx.obj["formatter"].print_error(str(e))
        ctx.exit(1)
    except KeyboardInterrupt:
        ctx.obj["formatter"].print_warning("\nTask interrupted by user")
        ctx.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        ctx.obj["formatter"].print_error(f"Unexpected error: {e}")
        ctx.exit(1)


@cli.command()
@click.option("--name", "-n", prompt="Project name", help="Project name")
@click.option(
    "--examples/--no-examples",
    default=True,
    help="Add example tasks",
)
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize taskx configuration in current directory."""
    config_path = Path("pyproject.toml")

    if config_path.exists():
        if not click.confirm(f"{config_path} already exists. Overwrite?"):
            ctx.obj["formatter"].print_warning("Initialization cancelled")
            ctx.exit(0)

    # Create basic pyproject.toml with taskx section
    content = f"""[project]
name = "{ctx.params.get('name', 'myproject')}"
version = "0.1.0"

[tool.taskx.env]
PROJECT_NAME = "{ctx.params.get('name', 'myproject')}"

[tool.taskx.tasks]
"""

    if ctx.params.get("examples", True):
        content += """# Development tasks
dev = { cmd = "echo 'Development server would start here'", description = "Start development server" }
test = { cmd = "pytest tests/", description = "Run test suite" }
lint = { cmd = "ruff check .", description = "Run linting" }
format = { cmd = "black . && isort .", description = "Format code" }

# Build tasks
build = { cmd = "python -m build", description = "Build distribution packages" }
clean = { cmd = "rm -rf dist build *.egg-info", description = "Clean build artifacts" }

# Composite task with dependencies
check = { depends = ["lint", "test"], cmd = "echo 'All checks passed!'", description = "Run all checks" }
"""
    else:
        content += """hello = "echo 'Hello from taskx!'"
"""

    config_path.write_text(content)
    ctx.obj["formatter"].print_success(f"Created {config_path} with taskx configuration")
    click.echo("\nNext steps:")
    click.echo("  1. Edit pyproject.toml to add your tasks")
    click.echo("  2. Run 'taskx list' to see available tasks")
    click.echo("  3. Run 'taskx <task-name>' to execute a task")


# Register additional commands
cli.add_command(watch)
cli.add_command(graph)


# Register task names as dynamic commands
@cli.command(name="__dynamic__", hidden=True, add_help_option=False)
@click.argument("task_name", required=False)
@click.pass_context
def dynamic_task(ctx: click.Context, task_name: Optional[str]) -> None:
    """Handle dynamic task execution."""
    if task_name:
        ctx.invoke(run, task_name=task_name)


def main() -> int:
    """Main entry point."""
    try:
        cli(obj={})
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        console = Console()
        console.print(f"[red]Fatal error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
