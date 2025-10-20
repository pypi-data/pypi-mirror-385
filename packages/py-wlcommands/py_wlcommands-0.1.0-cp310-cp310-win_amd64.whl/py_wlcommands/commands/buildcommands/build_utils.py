"""
Build utilities for WL Commands.
"""

import os
import sys

from ...exceptions import CommandError
from ...utils.logging import log_error, log_info
from ...utils.subprocess import run_command


def is_rust_enabled() -> bool:
    """
    Check if Rust is enabled for this project.

    Returns:
        bool: True if Rust is enabled, False otherwise.
    """
    rust_dir = os.path.join(os.getcwd(), "rust")
    cargo_toml = os.path.join(rust_dir, "Cargo.toml")
    return os.path.exists(cargo_toml)


def build_windows() -> None:
    """Build the project on Windows."""
    rust_enabled = is_rust_enabled()

    try:
        if rust_enabled:
            log_info("Using maturin develop to build and install editable package...")
            log_info("使用 maturin develop 构建和安装可编辑包...", lang="zh")
            run_command(["maturin", "develop"], capture_output=False)
        else:
            log_info(
                "Pure Python project, using uv pip install -e . for installation..."
            )
            log_info("纯 Python 项目，使用 uv pip install -e . 进行安装...", lang="zh")
            run_command(
                ["uv", "pip", "install", "--link-mode=copy", "-e", "."],
                capture_output=False,
            )

        log_info("✓ Build completed successfully")
        log_info("✓ 构建成功完成", lang="zh")
    except CommandError as e:
        log_error(f"Build failed: {e}")
        log_error(f"构建失败: {e}", lang="zh")
        raise
    except Exception as e:
        log_error(f"Unexpected error during build: {e}")
        log_error(f"构建过程中出现意外错误: {e}", lang="zh")
        raise CommandError(f"Build failed: {e}")


def build_unix() -> None:
    """Build the project on Unix-like systems."""
    rust_enabled = is_rust_enabled()

    try:
        if rust_enabled:
            log_info("Using maturin develop to build and install editable package...")
            log_info("使用 maturin develop 构建和安装可编辑包...", lang="zh")
            run_command(["maturin", "develop"], capture_output=False)
        else:
            log_info(
                "Pure Python project, using uv pip install -e . for installation..."
            )
            log_info("纯 Python 项目，使用 uv pip install -e . 进行安装...", lang="zh")
            run_command(
                ["uv", "pip", "install", "--link-mode=copy", "-e", "."],
                capture_output=False,
            )

        log_info("✓ Build completed successfully")
        log_info("✓ 构建成功完成", lang="zh")
    except CommandError as e:
        log_error(f"Build failed: {e}")
        log_error(f"构建失败: {e}", lang="zh")
        raise
    except Exception as e:
        log_error(f"Unexpected error during build: {e}")
        log_error(f"构建过程中出现意外错误: {e}", lang="zh")
        raise CommandError(f"Build failed: {e}")


def build_project() -> None:
    """
    Build the project based on the current platform.

    Raises:
        CommandError: If the build fails.
    """
    # Determine if we're on Windows or Unix-like system
    if sys.platform.startswith("win"):
        build_windows()
    else:
        build_unix()
