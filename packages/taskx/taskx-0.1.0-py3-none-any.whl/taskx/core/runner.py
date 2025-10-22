"""
Task execution engine.

Orchestrates task execution with dependencies, hooks, and error handling.
"""

import asyncio
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional

from rich.console import Console

from taskx.core.config import Config
from taskx.core.dependency import DependencyResolver
from taskx.core.env import EnvironmentManager
from taskx.core.hooks import HookExecutor
from taskx.core.task import ExecutionResult, Task
from taskx.execution.parallel import ParallelExecutor
from taskx.utils.platform import PlatformUtils
from taskx.utils.secure_exec import SecureCommandExecutor, SecurityError
from taskx.utils.shell import ShellValidator


class TaskRunner:
    """Executes tasks with dependency resolution and hooks."""

    def __init__(self, config: Config, console: Optional[Console] = None):
        """
        Initialize task runner.

        Args:
            config: Task configuration
            console: Rich console for output
        """
        self.config = config
        self.console = console or Console()
        self.env_manager = EnvironmentManager(config.env)
        self.hook_executor = HookExecutor(self.console)
        self.dependency_resolver = DependencyResolver(config.tasks)
        self.secure_executor = SecureCommandExecutor(
            strict_mode=config.settings.get("strict_mode", False),
            allow_warnings=config.settings.get("allow_security_warnings", True),
        )
        self.parallel_executor = ParallelExecutor(
            console=self.console,
            max_concurrent=config.settings.get("max_parallel_tasks", 10),
            strict_mode=config.settings.get("strict_mode", False),
        )

        # Load .env file if it exists
        self.env_manager.load_dotenv()

    def run(self, task_name: str, override_env: Optional[Dict[str, str]] = None) -> bool:
        """
        Run a task and all its dependencies.

        Args:
            task_name: Name of task to run
            override_env: Environment variable overrides from CLI

        Returns:
            True if task and all dependencies succeeded, False otherwise
        """
        # Resolve dependencies
        try:
            task_chain = self.dependency_resolver.resolve_dependencies(task_name)
        except Exception as e:
            self.console.print(f"[red]✗ Dependency resolution failed: {e}[/red]")
            return False

        # Execute tasks in dependency order
        for task in task_chain:
            result = self._execute_single_task(task, override_env)
            if not result.success:
                # Stop on first failure unless ignore_errors is set
                task_obj = self.config.tasks[task]
                if not task_obj.ignore_errors:
                    self.console.print(
                        f"[red]✗ Task chain failed at '{task}'. Stopping execution.[/red]"
                    )
                    return False

        return True

    def _execute_single_task(
        self, task_name: str, override_env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute a single task without dependencies.

        Args:
            task_name: Task to execute
            override_env: Environment overrides

        Returns:
            Execution result
        """
        task = self.config.tasks[task_name]

        # Check platform compatibility
        current_platform = PlatformUtils.get_platform()
        if not task.should_run_on_platform(current_platform):
            self.console.print(
                f"[yellow]⊘ Skipping '{task_name}': not compatible with {current_platform}[/yellow]"
            )
            return ExecutionResult(task_name=task_name, success=True, exit_code=0)

        # Build environment
        env = self.env_manager.get_env_for_task(task.env, override_env)

        # Check environment requirements
        if task.if_env and not task.should_run_with_env(env):
            self.console.print(
                f"[yellow]⊘ Skipping '{task_name}': environment condition not met[/yellow]"
            )
            return ExecutionResult(task_name=task_name, success=True, exit_code=0)

        # Execute pre hook
        if task.pre:
            if not self.hook_executor.execute_hooks_for_task(task, "pre", env):
                self.console.print(f"[yellow]Warning: Pre-hook failed for '{task_name}'[/yellow]")

        # Execute main task
        start_time = time.time()

        if not task.silent:
            self.console.print(f"[cyan]→ Running:[/cyan] {task_name}")

        try:
            # Check if this is a parallel task
            if task.parallel:
                result = self._run_parallel(task, env)
            else:
                result = self._run_command(task, env)

            duration = time.time() - start_time

            if result.success:
                if not task.silent:
                    self.console.print(
                        f"[green]✓ Completed:[/green] {task_name} ({duration:.2f}s)"
                    )

                # Execute success hook
                if task.on_success:
                    self.hook_executor.execute_hooks_for_task(task, "on_success", env)

                # Execute post hook
                if task.post:
                    self.hook_executor.execute_hooks_for_task(task, "post", env)

            else:
                if not task.silent:
                    self.console.print(
                        f"[red]✗ Failed:[/red] {task_name} "
                        f"(exit code: {result.exit_code}, {duration:.2f}s)"
                    )

                # Execute error hook
                if task.on_error:
                    self.hook_executor.execute_hooks_for_task(task, "on_error", env)

            return ExecutionResult(
                task_name=task_name,
                success=result.success,
                exit_code=result.exit_code,
                duration=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            self.console.print(f"[red]✗ Error executing '{task_name}': {e}[/red]")

            # Execute error hook
            if task.on_error:
                self.hook_executor.execute_hooks_for_task(task, "on_error", env)

            return ExecutionResult(
                task_name=task_name,
                success=False,
                exit_code=-1,
                duration=duration,
                error=e,
            )

    def _run_command(self, task: Task, env: dict) -> ExecutionResult:
        """
        Run task command.

        Args:
            task: Task to run
            env: Environment variables

        Returns:
            Execution result
        """
        # Get command to execute
        cmd = task.cmd

        # Validate RAW command before expansion (security fix)
        if not ShellValidator.is_safe_command(cmd):
            return ExecutionResult(
                task_name=task.name,
                success=False,
                exit_code=-1,
                error=ValueError(f"Dangerous command detected (before expansion): {cmd}"),
            )

        # Expand environment variables
        cmd = self.env_manager.expand_command(cmd, env)

        # Validate EXPANDED command is also safe (defense in depth)
        if not ShellValidator.is_safe_command(cmd):
            return ExecutionResult(
                task_name=task.name,
                success=False,
                exit_code=-1,
                error=ValueError(f"Dangerous command detected (after expansion): {cmd}"),
            )

        # Sanitize command
        cmd = ShellValidator.sanitize_command(cmd)

        # Determine working directory
        cwd = task.cwd or str(Path.cwd())

        # Execute command securely
        try:
            result = self.secure_executor.execute(
                cmd=cmd,
                env=env,
                cwd=cwd,
                timeout=task.timeout,
                shell=True,  # Required for pipes, redirects, etc.
            )

            return ExecutionResult(
                task_name=task.name,
                success=result.returncode == 0,
                exit_code=result.returncode,
            )

        except SecurityError as e:
            self.console.print(f"[red]✗ Security Error:[/red] {e}")
            return ExecutionResult(
                task_name=task.name,
                success=False,
                exit_code=-1,
                error=e,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                task_name=task.name,
                success=False,
                exit_code=-1,
                error=TimeoutError(f"Task '{task.name}' timed out after {task.timeout}s"),
            )
        except Exception as e:
            return ExecutionResult(
                task_name=task.name,
                success=False,
                exit_code=-1,
                error=e,
            )

    def _run_parallel(self, task: Task, env: dict) -> ExecutionResult:
        """
        Run parallel tasks.

        Args:
            task: Task with parallel commands
            env: Environment variables

        Returns:
            Aggregated execution result
        """
        # Validate and expand environment variables in all commands
        commands = []
        for cmd in task.parallel:
            # Validate RAW command before expansion (security fix)
            if not ShellValidator.is_safe_command(cmd):
                return ExecutionResult(
                    task_name=task.name,
                    success=False,
                    exit_code=-1,
                    error=ValueError(f"Dangerous command detected (before expansion): {cmd}"),
                )

            # Expand environment variables
            expanded_cmd = self.env_manager.expand_command(cmd, env)

            # Validate EXPANDED command is also safe (defense in depth)
            if not ShellValidator.is_safe_command(expanded_cmd):
                return ExecutionResult(
                    task_name=task.name,
                    success=False,
                    exit_code=-1,
                    error=ValueError(f"Dangerous command detected (after expansion): {expanded_cmd}"),
                )

            # Sanitize command
            sanitized_cmd = ShellValidator.sanitize_command(expanded_cmd)
            commands.append(sanitized_cmd)

        # Determine working directory
        cwd = task.cwd or str(Path.cwd())

        # Execute commands in parallel
        try:
            results = asyncio.run(
                self.parallel_executor.run_parallel(
                    commands=commands,
                    env=env,
                    cwd=cwd,
                    timeout=task.timeout,
                )
            )

            # Aggregate results
            all_success = all(r.success for r in results.values())
            failed_cmds = [cmd for cmd, r in results.items() if not r.success]

            if not all_success:
                error_msg = f"Parallel execution failed for commands: {', '.join(failed_cmds)}"
                return ExecutionResult(
                    task_name=task.name,
                    success=False,
                    exit_code=-1,
                    error=ValueError(error_msg),
                )

            return ExecutionResult(
                task_name=task.name,
                success=True,
                exit_code=0,
            )

        except Exception as e:
            return ExecutionResult(
                task_name=task.name,
                success=False,
                exit_code=-1,
                error=e,
            )
