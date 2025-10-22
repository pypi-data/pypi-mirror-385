"""
Console output formatting using Rich.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Dict

from taskx.core.task import Task


class ConsoleFormatter:
    """Formats output for the console using Rich."""

    def __init__(self, console: Console = None):
        """Initialize formatter."""
        self.console = console or Console()

    def print_task_list(self, tasks: Dict[str, Task]) -> None:
        """
        Print a formatted list of tasks.

        Args:
            tasks: Dictionary of task names to Task objects
        """
        table = Table(title="Available Tasks", show_header=True)
        table.add_column("Task", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Dependencies", style="yellow")

        for name in sorted(tasks.keys()):
            task = tasks[name]
            deps = ", ".join(task.depends) if task.depends else "-"
            desc = task.description or "(no description)"
            table.add_row(name, desc, deps)

        self.console.print(table)

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[red]✗ Error:[/red] {message}")

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"[green]✓ Success:[/green] {message}")

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]⚠ Warning:[/yellow] {message}")

    def print_info(self, message: str) -> None:
        """Print an info message."""
        self.console.print(f"[blue]ℹ Info:[/blue] {message}")
