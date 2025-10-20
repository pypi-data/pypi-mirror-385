"""
Test command implementation for wl tool.
"""

import subprocess
import sys
from typing import Any

from .. import Command, register_command


@register_command("test")
class TestCommand(Command):
    """Command to run tests for the project."""

    @property
    def name(self) -> str:
        """Get the command name."""
        return "test"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Run project tests"

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """
        Execute the test command.

        Args:
            *args: Positional arguments (can include pytest arguments like --cov)
            **kwargs: Keyword arguments
        """
        # Run pytest to execute tests
        try:
            # Build base command arguments
            cmd_args: list[str] = [sys.executable, "-m", "pytest", "tests/", "-v"]

            # Parse args to check if user provided their own --cov option
            has_user_cov = any(arg.startswith("--cov") for arg in args)

            # Only add default coverage if no user-defined cov and plugin is available
            if not has_user_cov:
                has_pytest_cov = self._check_pytest_cov()
                if has_pytest_cov:
                    cmd_args.extend(
                        ["--cov=py_wlcommands", "--cov-report=term-missing"]
                    )

            # Add any additional user arguments
            if args:
                filtered_args = [
                    arg for arg in args if not arg.startswith("tests/")
                ]  # Avoid duplicate test paths
                cmd_args.extend(filtered_args)

            result = subprocess.run(
                cmd_args,
                cwd=self._get_project_root(),
                check=False,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            if result.returncode != 0:
                print(f"Tests failed with return code {result.returncode}")
                sys.exit(result.returncode)
            else:
                print("All tests passed successfully!")
        except FileNotFoundError:
            print(
                "Error: pytest not found. Please install it using 'pip install pytest'"
            )
            sys.exit(1)
        except Exception as e:
            print(f"Error running tests: {e}")
            sys.exit(1)

    def _check_pytest_cov(self) -> bool:
        """
        Check if pytest-cov plugin is available.

        Returns:
            bool: True if pytest-cov is available, False otherwise
        """
        try:
            import pytest_cov

            return True
        except ImportError:
            return False

    def _get_project_root(self) -> str:
        """
        Get the project root directory.

        Returns:
            str: Path to the project root directory
        """
        import os

        # For now, assume the project root is the current working directory
        return os.getcwd()
