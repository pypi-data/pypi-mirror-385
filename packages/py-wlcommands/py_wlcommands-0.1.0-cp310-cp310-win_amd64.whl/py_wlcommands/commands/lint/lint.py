"""
Lint command.
"""

from ...commands import Command, register_command, validate_command_args


@register_command("lint")
class LintCommand(Command):
    """Command to lint code."""

    @property
    def name(self) -> str:
        return "lint"

    @property
    def help(self) -> str:
        return "Lint code with ruff - equivalent to make lint"

    @classmethod
    def add_arguments(cls, parser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "-q", "--quiet", action="store_true", help="Suppress detailed output"
        )
        parser.add_argument(
            "--fix", action="store_true", help="Automatically fix lint errors"
        )

    @validate_command_args()
    def execute(self, quiet: bool = False, fix: bool = False, **kwargs) -> None:
        """
        Lint code - equivalent to make lint
        代码静态检查 - 等效于 make lint
        """
        import subprocess
        import sys
        from pathlib import Path

        from ...utils.logging import log_info

        # 忽略传递的额外参数，例如'command'
        # Ignore extra arguments passed, such as 'command'

        if not quiet:
            log_info("Linting code...")
            log_info("正在进行代码静态检查...", lang="zh")

        try:
            # Get project root directory
            project_root = Path(__file__).parent.parent.parent.parent.parent

            # Prepare ruff command
            cmd = ["ruff", "check", "."]

            # Add fix flag if requested
            if fix:
                cmd.append("--fix")

            # Add quiet flag if requested
            if quiet:
                cmd.append("--quiet")

            # Execute ruff command
            # 在 subprocess.run 调用中忽略 S603 警告，因为我们执行的是受信任的命令
            if quiet:
                # In quiet mode, capture output to suppress it
                result = subprocess.run(  # nosec B603
                    cmd,
                    cwd=str(project_root),
                    capture_output=True,
                    text=True,
                    # Explicitly set encoding for Windows systems
                    encoding="utf-8" if sys.platform.startswith("win") else None,
                )

                if result.returncode != 0 and not quiet:
                    log_info("Linting completed with issues:")
                    log_info("代码静态检查发现以下问题:")
                    if result.stdout:
                        print(result.stdout)
                    if result.stderr:
                        print(result.stderr)
                elif result.returncode == 0 and not quiet:
                    log_info("Code linting completed successfully!")
                    log_info("代码静态检查成功完成！", lang="zh")
            else:
                # In normal mode, let ruff output directly to stdout/stderr to preserve colors
                result = subprocess.run(
                    cmd,
                    cwd=str(project_root),
                    # Explicitly set encoding for Windows systems
                    encoding="utf-8" if sys.platform.startswith("win") else None,
                )  # nosec B603

                if result.returncode == 0:
                    log_info("Code linting completed successfully!")
                    log_info("代码静态检查成功完成！", lang="zh")

            # 如果有错误，退出码非0
            if result.returncode != 0:
                sys.exit(result.returncode)

        except FileNotFoundError:
            if not quiet:
                log_info("Error: ruff is not installed or not found in PATH")
                log_info("错误：未安装 ruff 或在 PATH 中找不到", lang="zh")
            sys.exit(1)
        except Exception as e:
            if not quiet:
                log_info(f"Error during linting: {e}", lang="en")
                log_info(f"错误：静态检查期间出错: {e}", lang="zh")
            sys.exit(1)
