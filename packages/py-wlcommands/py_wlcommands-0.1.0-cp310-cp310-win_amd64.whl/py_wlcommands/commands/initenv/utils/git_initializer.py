"""Git initializer utility."""

import subprocess
from pathlib import Path

from ....utils.logging import log_info
from .exceptions import GitInitializationError
from .log_manager import performance_monitor


class GitInitializer:
    """Git repository initializer."""

    def __init__(self, env: dict[str, str]) -> None:
        self.env = env

    @performance_monitor
    def initialize(self) -> None:
        """Initialize Git repository if it doesn't exist."""
        if not Path(".git").exists():
            log_info("Initializing Git repository...")
            log_info("初始化Git仓库...", lang="zh")
            try:
                subprocess.run(
                    ["git", "init"], check=True, capture_output=False, env=self.env
                )
                log_info("✓ Git repository initialized")
                log_info("✓ Git仓库初始化完成", lang="zh")
            except subprocess.CalledProcessError as e:
                log_info("Warning: Failed to initialize Git repository")
                log_info("警告: 初始化Git仓库失败", lang="zh")
                raise GitInitializationError(
                    f"Failed to initialize Git repository: {e}"
                )
        else:
            log_info("Git repository already exists, skipping initialization")
            log_info("Git仓库已存在，跳过初始化", lang="zh")
