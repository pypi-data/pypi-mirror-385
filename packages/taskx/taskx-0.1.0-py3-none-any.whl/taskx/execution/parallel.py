"""
Parallel task execution system.

Provides async execution of multiple tasks concurrently with progress tracking.
"""

import asyncio
import time
from typing import Dict, List, Optional

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from taskx.core.task import ExecutionResult, Task
from taskx.utils.secure_exec import SecureCommandExecutor, SecurityError


class ParallelExecutor:
    """
    Executes multiple tasks in parallel using asyncio.

    Features:
    - Concurrent task execution
    - Progress tracking with Rich
    - Error handling and aggregation
    - Secure command execution
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        max_concurrent: int = 10,
        strict_mode: bool = False,
    ):
        """
        Initialize parallel executor.

        Args:
            console: Rich console for output
            max_concurrent: Maximum number of concurrent tasks
            strict_mode: Enable strict security mode
        """
        self.console = console or Console()
        self.max_concurrent = max_concurrent
        self.secure_executor = SecureCommandExecutor(
            strict_mode=strict_mode,
            allow_warnings=True,
        )

    async def run_parallel(
        self,
        commands: List[str],
        env: dict,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, ExecutionResult]:
        """
        Run multiple commands in parallel.

        Args:
            commands: List of commands to execute
            env: Environment variables
            cwd: Working directory
            timeout: Timeout for each command

        Returns:
            Dictionary mapping command to execution result
        """
        # Create semaphore to limit concurrent executions
        semaphore = asyncio.Semaphore(self.max_concurrent)

        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            # Create progress tasks for each command
            overall_task = progress.add_task(
                f"[cyan]Running {len(commands)} tasks in parallel...",
                total=len(commands),
            )

            # Create tasks for each command
            tasks = []
            for cmd in commands:
                task = self._execute_with_progress(
                    cmd=cmd,
                    env=env,
                    cwd=cwd,
                    timeout=timeout,
                    semaphore=semaphore,
                    progress=progress,
                    overall_task=overall_task,
                )
                tasks.append(task)

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        result_dict = {}
        for i, cmd in enumerate(commands):
            result = results[i]
            if isinstance(result, Exception):
                result_dict[cmd] = ExecutionResult(
                    task_name=cmd,
                    success=False,
                    exit_code=-1,
                    error=result,
                )
            else:
                result_dict[cmd] = result

        return result_dict

    async def _execute_with_progress(
        self,
        cmd: str,
        env: dict,
        cwd: Optional[str],
        timeout: Optional[int],
        semaphore: asyncio.Semaphore,
        progress: Progress,
        overall_task: int,
    ) -> ExecutionResult:
        """
        Execute a single command with progress tracking.

        Args:
            cmd: Command to execute
            env: Environment variables
            cwd: Working directory
            timeout: Timeout in seconds
            semaphore: Semaphore for limiting concurrency
            progress: Progress display
            overall_task: Progress task ID for overall progress

        Returns:
            Execution result
        """
        async with semaphore:
            # Create task-specific progress
            task_id = progress.add_task(
                f"[yellow]{cmd[:50]}...",
                total=None,
            )

            try:
                start_time = time.time()

                # Run command in thread pool (subprocess is blocking)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._execute_sync,
                    cmd,
                    env,
                    cwd,
                    timeout,
                )

                duration = time.time() - start_time

                # Update progress
                if result.success:
                    progress.update(
                        task_id,
                        description=f"[green]✓ {cmd[:50]}",
                        completed=True,
                    )
                else:
                    progress.update(
                        task_id,
                        description=f"[red]✗ {cmd[:50]}",
                        completed=True,
                    )

                progress.update(overall_task, advance=1)

                return ExecutionResult(
                    task_name=cmd,
                    success=result.success,
                    exit_code=result.exit_code,
                    duration=duration,
                )

            except Exception as e:
                progress.update(
                    task_id,
                    description=f"[red]✗ {cmd[:50]} (error)",
                    completed=True,
                )
                progress.update(overall_task, advance=1)

                return ExecutionResult(
                    task_name=cmd,
                    success=False,
                    exit_code=-1,
                    error=e,
                )

    def _execute_sync(
        self,
        cmd: str,
        env: dict,
        cwd: Optional[str],
        timeout: Optional[int],
    ) -> ExecutionResult:
        """
        Execute command synchronously (for use in thread pool).

        Args:
            cmd: Command to execute
            env: Environment variables
            cwd: Working directory
            timeout: Timeout in seconds

        Returns:
            Execution result
        """
        try:
            result = self.secure_executor.execute(
                cmd=cmd,
                env=env,
                cwd=cwd,
                timeout=timeout,
                shell=True,
            )

            return ExecutionResult(
                task_name=cmd,
                success=result.returncode == 0,
                exit_code=result.returncode,
            )

        except SecurityError as e:
            return ExecutionResult(
                task_name=cmd,
                success=False,
                exit_code=-1,
                error=e,
            )

        except Exception as e:
            return ExecutionResult(
                task_name=cmd,
                success=False,
                exit_code=-1,
                error=e,
            )


def run_parallel_sync(
    commands: List[str],
    env: dict,
    cwd: Optional[str] = None,
    timeout: Optional[int] = None,
    console: Optional[Console] = None,
) -> Dict[str, ExecutionResult]:
    """
    Synchronous wrapper for parallel execution.

    Args:
        commands: List of commands to execute
        env: Environment variables
        cwd: Working directory
        timeout: Timeout for each command
        console: Rich console for output

    Returns:
        Dictionary mapping command to execution result
    """
    executor = ParallelExecutor(console=console)
    return asyncio.run(executor.run_parallel(commands, env, cwd, timeout))
