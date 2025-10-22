"""
Task model and related data structures.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    """
    Represents a task definition.

    A task can be a simple command string or a complex configuration with
    dependencies, environment variables, hooks, and more.

    Attributes:
        name: Unique task identifier
        cmd: Command to execute (can contain ${VAR} placeholders)
        description: Human-readable description
        depends: List of task names that must run before this task
        parallel: List of commands to run in parallel (mutually exclusive with cmd)
        env: Task-specific environment variables
        cwd: Working directory for command execution
        shell: Explicitly specify shell to use
        timeout: Maximum execution time in seconds
        retry: Number of retry attempts on failure
        retry_delay: Delay between retries in seconds
        on_error: Command to run if task fails
        on_success: Command to run if task succeeds
        pre: Command to run before main task
        post: Command to run after main task
        watch: File patterns to watch for auto-reload
        prompt: Variable name to prompt user for
        confirm: Confirmation message before execution
        if_platform: Only run on specific platforms (windows, darwin, linux)
        if_env: Only run if environment variable is set
        silent: Suppress output
        ignore_errors: Continue even if task fails
    """

    name: str
    cmd: str = ""
    description: Optional[str] = None
    depends: List[str] = field(default_factory=list)
    parallel: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    cwd: Optional[str] = None
    shell: Optional[str] = None
    timeout: Optional[int] = None
    retry: int = 0
    retry_delay: int = 1
    on_error: Optional[str] = None
    on_success: Optional[str] = None
    pre: Optional[str] = None
    post: Optional[str] = None
    watch: List[str] = field(default_factory=list)
    prompt: Optional[str] = None
    confirm: Optional[str] = None
    if_platform: Optional[str] = None
    if_env: Optional[str] = None
    silent: bool = False
    ignore_errors: bool = False

    def __post_init__(self) -> None:
        """Validate task definition after initialization."""
        if not self.name:
            raise ValueError("Task name cannot be empty")

        if not self.cmd and not self.parallel:
            raise ValueError(f"Task '{self.name}' must have either 'cmd' or 'parallel' defined")

        if self.cmd and self.parallel:
            raise ValueError(
                f"Task '{self.name}' cannot have both 'cmd' and 'parallel' defined"
            )

        if self.timeout and self.timeout <= 0:
            raise ValueError(f"Task '{self.name}' timeout must be positive")

        if self.retry < 0:
            raise ValueError(f"Task '{self.name}' retry count cannot be negative")

        if self.retry_delay < 0:
            raise ValueError(f"Task '{self.name}' retry_delay cannot be negative")

        # Normalize cwd to Path
        if self.cwd:
            self.cwd = str(Path(self.cwd))

    @property
    def is_parallel(self) -> bool:
        """Check if this is a parallel task."""
        return bool(self.parallel)

    @property
    def has_dependencies(self) -> bool:
        """Check if task has dependencies."""
        return bool(self.depends)

    @property
    def has_hooks(self) -> bool:
        """Check if task has any hooks."""
        return any([self.pre, self.post, self.on_error, self.on_success])

    @property
    def has_watch(self) -> bool:
        """Check if task has watch patterns."""
        return bool(self.watch)

    def should_run_on_platform(self, current_platform: str) -> bool:
        """
        Check if task should run on the current platform.

        Args:
            current_platform: Current platform name (windows, darwin, linux)

        Returns:
            True if task should run, False otherwise
        """
        if not self.if_platform:
            return True
        return current_platform.lower() == self.if_platform.lower()

    def should_run_with_env(self, env_vars: Dict[str, str]) -> bool:
        """
        Check if task should run given environment variables.

        Args:
            env_vars: Current environment variables

        Returns:
            True if task should run, False otherwise
        """
        if not self.if_env:
            return True
        return self.if_env in env_vars

    def __repr__(self) -> str:
        """String representation of task."""
        if self.is_parallel:
            return f"Task({self.name}, parallel={len(self.parallel)} commands)"
        return f"Task({self.name}, cmd={self.cmd[:30]}...)"


@dataclass
class ExecutionResult:
    """
    Result of task execution.

    Attributes:
        task_name: Name of the executed task
        success: Whether execution succeeded
        exit_code: Process exit code
        duration: Execution duration in seconds
        stdout: Standard output
        stderr: Standard error
        error: Exception if execution failed
    """

    task_name: str
    success: bool
    exit_code: int = 0
    duration: float = 0.0
    stdout: str = ""
    stderr: str = ""
    error: Optional[Exception] = None

    @property
    def failed(self) -> bool:
        """Check if execution failed."""
        return not self.success

    def __repr__(self) -> str:
        """String representation of result."""
        status = "✓" if self.success else "✗"
        return f"ExecutionResult({status} {self.task_name}, {self.duration:.2f}s)"


@dataclass
class Hook:
    """
    Represents a task hook.

    Hooks are commands that run at specific points in the task lifecycle.

    Attributes:
        name: Hook name (pre, post, on_error, on_success)
        cmd: Command to execute
        task_name: Name of the task this hook belongs to
    """

    name: str
    cmd: str
    task_name: str

    def __post_init__(self) -> None:
        """Validate hook definition."""
        valid_hooks = ["pre", "post", "on_error", "on_success"]
        if self.name not in valid_hooks:
            raise ValueError(f"Invalid hook name: {self.name}. Must be one of {valid_hooks}")

        if not self.cmd:
            raise ValueError(f"Hook '{self.name}' for task '{self.task_name}' has no command")

    def __repr__(self) -> str:
        """String representation of hook."""
        return f"Hook({self.name}, task={self.task_name})"
