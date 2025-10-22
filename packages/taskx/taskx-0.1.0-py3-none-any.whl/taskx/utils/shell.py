"""
Shell command utilities with security features.

Provides safe command execution and validation.
"""

import re
import shlex
from typing import List, Optional


class ShellValidator:
    """Validates and sanitizes shell commands."""

    # Dangerous shell metacharacters that could enable injection
    DANGEROUS_CHARS = [";", "&", "|", "`", "$", "(", ")", "<", ">", "\n", "\\"]

    # Dangerous commands that should be blocked
    DANGEROUS_COMMANDS = [
        "rm -rf /",
        "mkfs",
        "dd if=/dev/zero",
        ":(){ :|:& };:",  # Fork bomb
        "chmod -R 777 /",
    ]

    @staticmethod
    def is_safe_command(cmd: str) -> bool:
        """
        Check if command is safe to execute.

        Args:
            cmd: Command to validate

        Returns:
            True if safe, False if potentially dangerous
        """
        # Check for dangerous command patterns
        cmd_lower = cmd.lower().strip()
        for dangerous in ShellValidator.DANGEROUS_COMMANDS:
            if dangerous.lower() in cmd_lower:
                return False

        return True

    @staticmethod
    def sanitize_command(cmd: str) -> str:
        """
        Sanitize command for safe execution.

        Args:
            cmd: Command to sanitize

        Returns:
            Sanitized command

        Note:
            This is basic sanitization. For production use,
            consider using parameterized execution instead.
        """
        # Remove null bytes
        cmd = cmd.replace("\x00", "")

        # Normalize whitespace
        cmd = " ".join(cmd.split())

        return cmd


class CommandBuilder:
    """Builds safe shell commands."""

    @staticmethod
    def build_command(
        cmd: str,
        args: Optional[List[str]] = None,
        shell: bool = True,
    ) -> str:
        """
        Build a safe command string.

        Args:
            cmd: Base command
            args: Optional arguments
            shell: Whether to build for shell execution

        Returns:
            Built command string
        """
        if not shell and args:
            # For non-shell execution, properly quote arguments
            quoted_args = [shlex.quote(arg) for arg in args]
            return f"{cmd} {' '.join(quoted_args)}"

        return cmd

    @staticmethod
    def escape_argument(arg: str) -> str:
        """
        Escape argument for safe shell execution.

        Args:
            arg: Argument to escape

        Returns:
            Escaped argument
        """
        return shlex.quote(arg)


class EnvironmentExpander:
    """Expands environment variables in commands."""

    @staticmethod
    def expand_variables(cmd: str, env: dict) -> str:
        """
        Expand ${VAR} placeholders in command with proper escaping.

        Args:
            cmd: Command with placeholders
            env: Environment variables dict

        Returns:
            Command with expanded and properly escaped variables
        """
        # Pattern to match ${VAR} or $VAR
        pattern = r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)"

        def replace(match: re.Match) -> str:
            var_name = match.group(1) or match.group(2)
            value = env.get(var_name, match.group(0))
            # SECURITY: Properly quote value to prevent command injection
            return shlex.quote(str(value))

        return re.sub(pattern, replace, cmd)

    @staticmethod
    def find_variables(cmd: str) -> List[str]:
        """
        Find all variable references in command.

        Args:
            cmd: Command to search

        Returns:
            List of variable names found
        """
        pattern = r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)"
        matches = re.findall(pattern, cmd)
        return [m[0] or m[1] for m in matches]
