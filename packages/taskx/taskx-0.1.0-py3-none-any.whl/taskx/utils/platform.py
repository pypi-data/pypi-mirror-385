"""
Cross-platform utilities for taskx.

Handles platform detection and platform-specific operations.
"""

import os
import platform
import sys
from pathlib import Path
from typing import Optional


class PlatformUtils:
    """Utilities for cross-platform operations."""

    @staticmethod
    def get_platform() -> str:
        """
        Get current platform name.

        Returns:
            Platform name: 'windows', 'darwin', or 'linux'
        """
        system = platform.system().lower()
        if system == "darwin":
            return "darwin"
        elif system == "windows":
            return "windows"
        else:
            return "linux"

    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return sys.platform == "win32"

    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS."""
        return sys.platform == "darwin"

    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux."""
        return sys.platform.startswith("linux")

    @staticmethod
    def get_shell() -> str:
        """
        Get the default shell for the current platform.

        Returns:
            Shell executable path or name
        """
        if PlatformUtils.is_windows():
            # On Windows, prefer PowerShell if available, fall back to cmd
            powershell = os.environ.get("POWERSHELL", "powershell.exe")
            return powershell
        else:
            # On Unix, use the user's shell or fall back to bash
            return os.environ.get("SHELL", "/bin/bash")

    @staticmethod
    def get_shell_for_command() -> Optional[str]:
        """
        Get shell to use for subprocess execution.

        Returns:
            Shell path for subprocess, or None to use default
        """
        if PlatformUtils.is_windows():
            # Windows: use cmd.exe for better compatibility
            return "cmd.exe"
        else:
            # Unix: use bash for better compatibility
            return "/bin/bash"

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize path for the current platform.

        Args:
            path: Path to normalize

        Returns:
            Normalized path string
        """
        return str(Path(path).resolve())

    @staticmethod
    def get_executable_extension() -> str:
        """
        Get executable file extension for current platform.

        Returns:
            '.exe' on Windows, '' on Unix
        """
        return ".exe" if PlatformUtils.is_windows() else ""

    @staticmethod
    def get_path_separator() -> str:
        """
        Get path separator for current platform.

        Returns:
            ';' on Windows, ':' on Unix
        """
        return ";" if PlatformUtils.is_windows() else ":"

    @staticmethod
    def get_line_ending() -> str:
        """
        Get line ending for current platform.

        Returns:
            '\\r\\n' on Windows, '\\n' on Unix
        """
        return "\r\n" if PlatformUtils.is_windows() else "\n"

    @staticmethod
    def expand_user_path(path: str) -> str:
        """
        Expand ~ in path to user home directory.

        Args:
            path: Path potentially containing ~

        Returns:
            Expanded path
        """
        return str(Path(path).expanduser())

    @staticmethod
    def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable value.

        Args:
            name: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return os.environ.get(name, default)

    @staticmethod
    def set_env_var(name: str, value: str) -> None:
        """
        Set environment variable.

        Args:
            name: Environment variable name
            value: Value to set
        """
        os.environ[name] = value

    @staticmethod
    def get_home_dir() -> Path:
        """
        Get user home directory.

        Returns:
            Path to home directory
        """
        return Path.home()

    @staticmethod
    def get_cwd() -> Path:
        """
        Get current working directory.

        Returns:
            Path to current directory
        """
        return Path.cwd()
