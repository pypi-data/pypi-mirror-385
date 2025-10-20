"""Custom exceptions for initenv commands."""

import subprocess
from pathlib import Path

from ....utils.logging import log_info
from .exceptions import RustInitializationError
from .log_manager import performance_monitor


class RustInitializer:
    """Rust environment initializer."""

    def __init__(self) -> None:
        pass

    @performance_monitor
    def initialize(self) -> None:
        """Initialize Rust environment."""
        rust_dir = Path("rust")

        # Create rust directory if it doesn't exist
        if not rust_dir.exists():
            log_info("Creating rust directory...")
            log_info("创建rust目录...", lang="zh")
            rust_dir.mkdir(exist_ok=True)

        # Check if Cargo.toml exists
        cargo_toml_path = rust_dir / "Cargo.toml"
        if cargo_toml_path.exists():
            log_info("Cargo.toml already exists, skipping creation")
            log_info("Cargo.toml 已存在，跳过创建", lang="zh")
            return

        log_info("Initializing Rust project with cargo...")
        log_info("使用cargo初始化Rust项目...", lang="zh")
        try:
            result = subprocess.run(
                ["cargo", "init", "--lib"],
                cwd=rust_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                log_info("✓ Rust project initialized successfully")
                log_info("✓ Rust项目初始化成功", lang="zh")
            else:
                raise RustInitializationError(
                    f"Failed to initialize Rust project: {result.stderr}"
                )
        except subprocess.CalledProcessError as e:
            raise RustInitializationError(f"Failed to initialize Rust project: {e}")
        except FileNotFoundError:
            raise RustInitializationError(
                "Cargo not found. Please install Rust toolchain first."
            )
