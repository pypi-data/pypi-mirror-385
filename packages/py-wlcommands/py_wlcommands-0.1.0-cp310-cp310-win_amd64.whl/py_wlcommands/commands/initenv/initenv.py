"""Initialize project command."""

from typing import Any

from ...exceptions import CommandError
from ...utils.logging import log_error, log_info
from .. import Command, register_command
from .utils.exceptions import InitEnvError
from .utils.initializer import Initializer
from .utils.platform_adapter import PlatformAdapter


@register_command("init")
class InitCommand(Command):
    """Command to initialize project environment."""

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        """Return the command name."""
        return "init"

    @property
    def help(self) -> str:
        """Return the command help text."""
        return "Initialize project environment"

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize project - equivalent to make init
        初始化项目 - 等效于 make init
        """
        log_info("=== Starting initialization of project environment ===")
        log_info("=== 开始初始化项目环境 ===", lang="zh")

        try:
            # Detect platform
            is_windows = PlatformAdapter.is_windows()
            env = PlatformAdapter.get_env()

            # Create initializer
            initializer = Initializer(env)

            # Check if uv is installed
            initializer.check_uv_installed()

            # Initialize Git repository
            initializer.init_git()

            # Generate pyproject.toml if needed
            initializer.generate_pyproject()

            # Setup project structure
            initializer.setup_project_structure()

            # Initialize Rust if needed
            initializer.init_rust()

            # Sync Cargo.toml with pyproject.toml
            initializer.sync_cargo_toml()

            # Create virtual environment
            initializer.create_venv(is_windows)

            # Platform-specific finalization
            if is_windows:
                self._finalize_windows()
            else:
                self._finalize_unix()

            log_info("Project environment initialization completed!")
            log_info("项目环境初始化完成!", lang="zh")
        except InitEnvError as e:
            log_error(f"Initialization error: {e}")
            log_error(f"初始化错误: {e}", lang="zh")
            raise CommandError(f"Project initialization failed: {e}")
        except Exception as e:
            log_error(f"Error initializing project: {e}")
            log_error(f"错误：初始化项目失败: {e}", lang="zh")
            raise CommandError(f"Project initialization failed: {e}")

    def _finalize_windows(self) -> None:
        """Finalize Windows-specific steps."""
        log_info("Environment initialization completed!")
        log_info("环境初始化完成!", lang="zh")
        log_info("To activate the environment, please run:")
        log_info("要激活环境，请运行:", lang="zh")
        log_info("  .venv\\Scripts\\Activate.ps1")
        log_info(
            "After activating the environment, please run 'uv pip install -e .' to install project dependencies."
        )
        log_info(
            "激活环境后，请运行 'uv pip install -e .' 来安装项目依赖包。", lang="zh"
        )

    def _finalize_unix(self) -> None:
        """Finalize Unix-specific steps."""
        log_info("Project environment initialization completed!")
        log_info("项目环境初始化完成!", lang="zh")
        log_info("Next steps:")
        log_info("下一步:", lang="zh")
        log_info("  1. Activate environment: source ./.venv/bin/activate")
        log_info("  1. 激活环境: source ./.venv/bin/activate", lang="zh")
        log_info(
            "  2. Use uv to automatically manage dependencies without manual installation"
        )
        log_info("  2. 使用 uv 自动管理依赖，无需手动安装", lang="zh")
