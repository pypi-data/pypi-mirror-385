"""
File watcher for auto-reloading tasks on file changes.

Provides watch mode functionality with debouncing and smart filtering.
"""

import asyncio
import time
from pathlib import Path
from typing import Callable, List, Optional, Set

from rich.console import Console
from watchfiles import Change, awatch

from taskx.core.task import Task


class FileWatcher:
    """
    Watches files and automatically re-executes tasks when changes are detected.

    Features:
    - Glob pattern matching for file filtering
    - Debouncing to prevent excessive re-executions
    - Graceful shutdown handling
    - Clear change reporting
    """

    def __init__(
        self,
        patterns: List[str],
        console: Optional[Console] = None,
        debounce_ms: int = 100,
    ):
        """
        Initialize file watcher.

        Args:
            patterns: List of glob patterns to watch (e.g., ["*.py", "**/*.js"])
            console: Rich console for output
            debounce_ms: Milliseconds to wait before triggering execution
        """
        self.patterns = patterns
        self.console = console or Console()
        self.debounce_ms = debounce_ms / 1000.0  # Convert to seconds
        self._last_execution = 0.0
        self._pending_changes: Set[Path] = set()

    async def watch_and_execute(
        self,
        task: Task,
        execute_callback: Callable[[], bool],
        cwd: Optional[str] = None,
    ) -> None:
        """
        Watch files and execute callback when changes are detected.

        Args:
            task: Task being watched
            execute_callback: Function to call when files change (should return success status)
            cwd: Working directory to watch
        """
        watch_dir = Path(cwd) if cwd else Path.cwd()

        self.console.print(f"[cyan]👀 Watching for changes...[/cyan]")
        self.console.print(f"[dim]Directory: {watch_dir}[/dim]")
        self.console.print(f"[dim]Patterns: {', '.join(self.patterns)}[/dim]")
        self.console.print()

        # Initial execution
        self.console.print("[yellow]▶ Running initial execution...[/yellow]")
        success = execute_callback()
        if success:
            self.console.print("[green]✓ Initial execution completed[/green]\n")
        else:
            self.console.print("[red]✗ Initial execution failed[/red]\n")

        # Watch for changes
        try:
            async for changes in awatch(str(watch_dir), recursive=True):
                # Filter changes based on patterns
                relevant_changes = self._filter_changes(changes)

                if not relevant_changes:
                    continue

                # Add to pending changes
                self._pending_changes.update(relevant_changes)

                # Debounce: wait for a short period to collect all changes
                await asyncio.sleep(self.debounce_ms)

                # Check if we should execute (respects debounce period)
                current_time = time.time()
                if current_time - self._last_execution < self.debounce_ms:
                    continue

                # Display changes
                self._display_changes(self._pending_changes)

                # Execute task
                self.console.print(f"[yellow]▶ Re-running task '{task.name}'...[/yellow]")
                success = execute_callback()

                if success:
                    self.console.print("[green]✓ Execution completed successfully[/green]\n")
                else:
                    self.console.print("[red]✗ Execution failed[/red]\n")

                # Update tracking
                self._last_execution = current_time
                self._pending_changes.clear()

        except KeyboardInterrupt:
            self.console.print("\n[yellow]⊘ Watch mode stopped by user[/yellow]")

    def _filter_changes(self, changes: Set) -> Set[Path]:
        """
        Filter changes based on watch patterns.

        Args:
            changes: Set of (Change, path) tuples from watchfiles

        Returns:
            Set of Path objects that match watch patterns
        """
        relevant = set()

        for change_type, path_str in changes:
            path = Path(path_str)

            # Skip hidden files and directories
            if any(part.startswith(".") for part in path.parts):
                continue

            # Skip common build/cache directories
            skip_dirs = {
                "__pycache__",
                "node_modules",
                ".git",
                ".venv",
                "venv",
                "dist",
                "build",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
            }
            if any(skip_dir in path.parts for skip_dir in skip_dirs):
                continue

            # Check if file matches any pattern
            for pattern in self.patterns:
                if path.match(pattern):
                    relevant.add(path)
                    break

        return relevant

    def _display_changes(self, changes: Set[Path]) -> None:
        """
        Display detected changes in a user-friendly format.

        Args:
            changes: Set of changed file paths
        """
        if not changes:
            return

        self.console.print(f"[cyan]📝 Detected {len(changes)} change(s):[/cyan]")
        for path in sorted(changes):
            self.console.print(f"   [dim]→[/dim] {path}")
        self.console.print()


def watch_task_sync(
    task: Task,
    execute_callback: Callable[[], bool],
    patterns: Optional[List[str]] = None,
    cwd: Optional[str] = None,
    console: Optional[Console] = None,
) -> None:
    """
    Synchronous wrapper for watch mode.

    Args:
        task: Task to watch
        execute_callback: Function to call when files change
        patterns: List of glob patterns to watch (defaults to task.watch)
        cwd: Working directory
        console: Rich console for output
    """
    # Use task's watch patterns if not provided
    if patterns is None:
        patterns = task.watch

    if not patterns:
        raise ValueError(f"Task '{task.name}' has no watch patterns defined")

    watcher = FileWatcher(patterns=patterns, console=console)
    asyncio.run(watcher.watch_and_execute(task, execute_callback, cwd))
