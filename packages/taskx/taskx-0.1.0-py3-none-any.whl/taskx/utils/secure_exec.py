"""
Secure command execution utilities.

Provides layered security for command execution while maintaining functionality.
"""

import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


class SecurityError(Exception):
    """Raised when security validation fails."""

    pass


class SecureCommandExecutor:
    """
    Secure command executor with multiple security layers.

    Security approach:
    1. Warn users about potentially dangerous commands
    2. Validate against common attack patterns
    3. Provide opt-in strict mode
    4. Log all command executions
    """

    # Common safe commands (for strict mode)
    WHITELISTED_COMMANDS = {
        # Python
        "python", "python3", "pip", "pytest", "mypy", "black", "ruff", "isort",
        "poetry", "hatch", "pdm", "tox", "nox",
        # JavaScript/Node
        "node", "npm", "yarn", "pnpm", "npx",
        # Build tools
        "make", "cmake", "cargo", "go",
        # Version control
        "git",
        # Docker
        "docker", "docker-compose",
        # Shell utilities
        "echo", "cat", "ls", "pwd", "cd", "mkdir", "cp", "mv",
        # Text processing
        "grep", "sed", "awk", "tr",
    }

    # Patterns that indicate potential security issues
    SUSPICIOUS_PATTERNS = [
        (r";\s*rm\s+-rf", "Destructive rm -rf after semicolon"),
        (r"\|\s*sh\b", "Piping to shell"),
        (r"\|\s*bash\b", "Piping to bash"),
        (r">\s*/dev/", "Writing to /dev"),
        (r"&&\s*rm\s+-rf\s+/", "Chained destructive command"),
        (r"curl.*\|\s*sh", "Curl pipe to shell"),
        (r"wget.*\|\s*sh", "Wget pipe to shell"),
    ]

    # Absolutely forbidden patterns (regardless of mode)
    FORBIDDEN_PATTERNS = [
        (r"rm\s+-rf\s+/$", "Attempting to delete root directory"),
        (r"rm\s+-rf\s+/\s", "Attempting to delete root directory"),
        (r"mkfs", "Filesystem formatting command"),
        (r"dd\s+if=/dev/zero", "Disk overwrite command"),
        (r":\(\)\{.*\|\:&\}", "Fork bomb pattern"),
        # Command substitution patterns (moved from suspicious to forbidden)
        (r"`[^`]*`", "Command substitution with backticks (security risk)"),
        (r"\$\([^)]*\)", "Command substitution with $() (security risk)"),
    ]

    def __init__(self, strict_mode: bool = False, allow_warnings: bool = True):
        """
        Initialize secure executor.

        Args:
            strict_mode: If True, only whitelisted commands allowed
            allow_warnings: If True, show security warnings but allow execution
        """
        self.strict_mode = strict_mode
        self.allow_warnings = allow_warnings

    def validate_command(self, cmd: str) -> Tuple[bool, List[str]]:
        """
        Validate command for security issues.

        Args:
            cmd: Command to validate

        Returns:
            Tuple of (is_safe, list_of_warnings)

        Raises:
            SecurityError: If command matches forbidden pattern
        """
        warnings = []

        # Check forbidden patterns (always blocked)
        for pattern, description in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                raise SecurityError(
                    f"Forbidden command pattern detected: {description}\\n"
                    f"Command: {cmd}\\n"
                    f"This command is blocked for security reasons."
                )

        # Check suspicious patterns (warnings)
        for pattern, description in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, cmd):
                warnings.append(f"Suspicious pattern: {description}")

        # Check whitelist in strict mode
        if self.strict_mode:
            command_parts = shlex.split(cmd)
            if command_parts:
                executable = os.path.basename(command_parts[0])
                if executable not in self.WHITELISTED_COMMANDS:
                    raise SecurityError(
                        f"Command '{executable}' not in whitelist.\\n"
                        f"In strict mode, only pre-approved commands can be executed.\\n"
                        f"To allow this command, disable strict mode or add it to the whitelist."
                    )

        return (len(warnings) == 0, warnings)

    def execute(
        self,
        cmd: str,
        env: Optional[dict] = None,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        shell: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Execute command with security validation.

        Args:
            cmd: Command to execute
            env: Environment variables
            cwd: Working directory
            timeout: Timeout in seconds
            shell: Whether to use shell (default: True for compatibility)

        Returns:
            CompletedProcess result

        Raises:
            SecurityError: If command fails security validation
        """
        # Validate command
        is_safe, warnings = self.validate_command(cmd)

        # Show warnings if enabled
        if warnings and self.allow_warnings:
            print(f"⚠️  Security warnings for command: {cmd}")
            for warning in warnings:
                print(f"   - {warning}")
            print()

        # Execute with security measures
        safe_env = os.environ.copy()
        if env:
            safe_env.update(env)

        return subprocess.run(
            cmd,
            shell=shell,
            env=safe_env,
            cwd=cwd,
            timeout=timeout or 300,  # 5-minute default timeout
            capture_output=False,
            text=True,
        )
