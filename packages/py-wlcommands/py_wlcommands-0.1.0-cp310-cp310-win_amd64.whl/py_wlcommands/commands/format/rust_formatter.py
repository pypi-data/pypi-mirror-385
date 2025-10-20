"""
Rust code formatting utilities.
"""

import subprocess
import sys
from pathlib import Path

from ...utils.logging import log_info


def format_rust_code(rust_dir: str, env: dict, quiet: bool) -> None:
    """Format Rust code if rust directory exists."""
    rust_path = Path(rust_dir)
    if rust_path.exists():
        # Fix encoding issues on Windows
        environment = env.copy() if env else {}
        if sys.platform.startswith("win"):
            # Set environment variables to ensure proper UTF-8 handling
            environment["PYTHONIOENCODING"] = "utf-8"
            environment["PYTHONLEGACYWINDOWSFSENCODING"] = "1"

        if not quiet:
            log_info(f"Formatting Rust code in {rust_dir}...")
            log_info(f"格式化 {rust_dir} 中的 Rust 代码...", lang="zh")

        # Save current directory and change to rust directory
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(rust_dir)
            _run_format_command(["cargo", "fmt"], environment, quiet)
        except Exception as e:
            if not quiet:
                log_info(f"Warning: Failed to format Rust code: {e}")
                log_info(f"警告：格式化 Rust 代码失败: {e}", lang="zh")
            else:
                print(f"Warning: Failed to format Rust code: {e}")
        finally:
            # Always return to original directory
            os.chdir(original_cwd)
    else:
        if not quiet:
            log_info("Rust directory not found, skipping Rust code formatting")
            log_info("未找到 Rust 目录，跳过 Rust 代码格式化", lang="zh")
        else:
            print("Rust directory not found, skipping Rust code formatting")


def _run_format_command(command: list, env: dict, quiet: bool) -> None:
    """Run a formatting command with proper output handling."""
    # Prepare environment variables
    environment = env.copy() if env else {}

    # Fix encoding issues on Windows
    if sys.platform.startswith("win"):
        # Set environment variables to ensure proper UTF-8 handling
        environment["PYTHONIOENCODING"] = "utf-8"
        environment["PYTHONLEGACYWINDOWSFSENCODING"] = "1"

    # Check for execution of untrusted input - not applicable here as we're running
    # trusted formatting tools with trusted paths
    if quiet:
        # In quiet mode, capture output to suppress it
        result = subprocess.run(
            command,
            env=environment,
            capture_output=True,
            text=True,
            # Explicitly set encoding for Windows systems
            encoding="utf-8" if sys.platform.startswith("win") else None,
        )
        if result.returncode != 0:
            raise Exception(
                f"Command failed with return code {result.returncode}: {result.stderr}"
            )
    else:
        # In normal mode, let the command output directly to stdout/stderr
        result = subprocess.run(
            command,
            env=environment,
            # Explicitly set encoding for Windows systems
            encoding="utf-8" if sys.platform.startswith("win") else None,
        )
        if result.returncode != 0:
            raise Exception(f"Command failed with return code {result.returncode}")
