"""
Build dist command for WL Commands.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from ...exceptions import CommandError
from ...utils.logging import log_error, log_info
from .. import Command, register_command


@register_command("build dist")
class BuildDistCommand(Command):
    """Command to build distribution packages."""

    @property
    def name(self) -> str:
        """Return the command name."""
        return "dist"

    @property
    def help(self) -> str:
        """Return the command help text."""
        return "Build distribution packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Execute the build dist command."""
        # Determine the platform and run the appropriate build command
        try:
            log_info("Building distribution packages...")

            # Check if we are in a uv workspace
            is_workspace = self._detect_uv_workspace()
            python_executable = None
            if is_workspace:
                log_info("✓ uv workspace environment detected")
                # In a workspace, check if .venv exists
                if not Path(".venv").exists():
                    log_info("No .venv found, creating virtual environment...")
                    # Create virtual environment
                    self._create_venv()

                # Set python executable path for maturin
                if sys.platform.startswith("win"):
                    python_executable = ".venv\\Scripts\\python.exe"
                else:
                    python_executable = ".venv/bin/python"
            else:
                log_info("Not in uv workspace environment")

            # Use maturin to build the distribution packages
            # Directly use maturin from PATH
            command = ["maturin", "build", "--release", "--out", "dist"]
            # If we have a python executable, use it for the build
            if python_executable:
                command.extend(["-i", python_executable])

            log_info(f"Trying to build with: {' '.join(command)}")
            subprocess.run(
                command,
                check=True,
                capture_output=False,
                text=True,
            )

            # If in workspace, remove the .venv directory
            if is_workspace and Path(".venv").exists():
                log_info("In uv workspace, removing .venv directory...")
                shutil.rmtree(".venv")
                log_info("✓ .venv directory removed")

            log_info("✓ Distribution packages built successfully")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to build distribution packages: {e}")
            raise CommandError(f"Build dist failed with return code {e.returncode}")
        except FileNotFoundError:
            log_error(
                "Maturin command not found. Please ensure maturin is installed and in PATH."
            )
            raise CommandError("Maturin command not found")
        except Exception as e:
            log_error(f"Unexpected error during build dist: {e}")
            raise CommandError(f"Build dist failed: {e}")

    def _detect_uv_workspace(self) -> bool:
        """Detect if we are in a uv workspace."""
        try:
            # Method 1: Check for uv.lock file which indicates a workspace
            if Path("uv.lock").exists():
                log_info("Debug: uv.lock file found, workspace detected")
                return True

            # Method 2: Use uv tree command to check for multiple root packages
            result = subprocess.run(
                ["uv", "tree"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            # Check for a workspace by counting root packages
            # In a workspace, there would be multiple top-level packages
            lines = result.stdout.split("\n")
            root_packages = []
            for line in lines:
                # Root package lines:
                # 1. Are not indented (don't start with space)
                # 2. Are not "Resolved" lines
                # 3. Are not "(*)" lines
                if (
                    not line.startswith(" ")
                    and line.strip()
                    and not line.startswith("Resolved")
                    and not line.startswith("(*)")
                ):
                    # Check if this is a root package - either without version or with version
                    # Root packages with versions look like "package-name v1.2.3"
                    if " v" in line and not line.startswith("v"):
                        # Check if it's a root package with version by verifying the format
                        parts = line.split(" v", 1)  # Split only on first occurrence
                        if len(parts) == 2:
                            package_name = parts[0]
                            version = parts[1]
                            # Verify that package name doesn't start with special chars and version is valid
                            if (
                                package_name
                                and not package_name.startswith(("├", "└", "│"))
                                and version.replace(".", "").replace("-", "").isalnum()
                            ):
                                root_packages.append(line)
                    elif line and not line.startswith(
                        ("├", "└", "│")
                    ):  # Plain root package without version
                        root_packages.append(line)

            log_info(f"Debug: uv tree root packages: {root_packages}")
            log_info(f"Debug: root packages count: {len(root_packages)}")

            # There should be more than one root package in a workspace
            if len(root_packages) > 1:
                log_info("Debug: Multiple root packages found, workspace detected")
                return True

        except Exception as e:
            log_info(f"Debug: Workspace detection error: {e}")
            pass  # Ignore errors in workspace detection

        log_info("Debug: No workspace detected")
        return False

    def _create_venv(self) -> None:
        """Create virtual environment using uv."""
        try:
            # Use uv to create virtual environment
            cmd = ["uv", "venv"]
            subprocess.run(
                cmd,
                check=True,
                capture_output=False,
                text=True,
            )
            log_info("✓ Virtual environment created successfully")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to create virtual environment: {e}")
            raise CommandError(f"Failed to create virtual environment: {e}")
        except Exception as e:
            log_error(f"Unexpected error creating virtual environment: {e}")
            raise CommandError(f"Failed to create virtual environment: {e}")
