"""
Hook execution system for taskx.

Handles pre/post/error/success hooks.
"""

import subprocess
from typing import Optional

from rich.console import Console

from taskx.core.task import Hook, Task
from taskx.utils.secure_exec import SecureCommandExecutor, SecurityError


class HookExecutor:
    """Executes task hooks."""

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize hook executor.

        Args:
            console: Rich console for output
        """
        self.console = console or Console()
        self.secure_executor = SecureCommandExecutor()

    def execute_hook(
        self,
        hook: Hook,
        env: dict,
        cwd: Optional[str] = None,
    ) -> bool:
        """
        Execute a single hook.

        Args:
            hook: Hook to execute
            env: Environment variables
            cwd: Working directory

        Returns:
            True if hook succeeded, False otherwise
        """
        self.console.print(f"[dim]→ Running {hook.name} hook: {hook.cmd}[/dim]")

        try:
            result = self.secure_executor.execute(
                cmd=hook.cmd,
                env=env,
                cwd=cwd,
                shell=True,
            )

            return result.returncode == 0

        except SecurityError as e:
            self.console.print(f"[red]✗ Hook '{hook.name}' blocked by security: {e}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]✗ Hook '{hook.name}' failed: {e}[/red]")
            return False

    def execute_hooks_for_task(
        self,
        task: Task,
        hook_type: str,
        env: dict,
    ) -> bool:
        """
        Execute hooks of a specific type for a task.

        Args:
            task: Task to execute hooks for
            hook_type: Type of hook ('pre', 'post', 'on_error', 'on_success')
            env: Environment variables

        Returns:
            True if all hooks succeeded, False otherwise
        """
        hook_cmd = None

        if hook_type == "pre":
            hook_cmd = task.pre
        elif hook_type == "post":
            hook_cmd = task.post
        elif hook_type == "on_error":
            hook_cmd = task.on_error
        elif hook_type == "on_success":
            hook_cmd = task.on_success

        if not hook_cmd:
            return True  # No hook to execute

        hook = Hook(name=hook_type, cmd=hook_cmd, task_name=task.name)
        return self.execute_hook(hook, env, task.cwd)
