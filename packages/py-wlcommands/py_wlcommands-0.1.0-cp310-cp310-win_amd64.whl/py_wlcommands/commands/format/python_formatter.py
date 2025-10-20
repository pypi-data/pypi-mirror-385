"""
Python code formatting utilities for WL Commands.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from ...utils.logging import log_info


def format_with_python_tools(target: str, env: dict, quiet: bool) -> None:
    """Format code with isort, black and ruff."""
    if not quiet:
        log_info(f"Formatting {target} with isort...")
        log_info(f"使用 isort 格式化 {target}...", lang="zh")
    try:
        _run_format_command(["uv", "run", "isort", target], env, quiet)
    except Exception as e:
        if not quiet:
            log_info(f"Warning: isort failed: {e}")
            log_info(f"警告：isort 失败: {e}", lang="zh")
        else:
            print(f"Warning: isort failed: {e}")

    if not quiet:
        log_info(f"Formatting {target} with black...")
        log_info(f"使用 black 格式化 {target}...", lang="zh")
    try:
        _run_format_command(["uv", "run", "black", target], env, quiet)
    except Exception as e:
        if not quiet:
            log_info(f"Warning: black failed: {e}")
            log_info(f"警告：black 失败: {e}", lang="zh")
        else:
            print(f"Warning: black failed: {e}")

    if not quiet:
        log_info(f"Checking and fixing {target} with ruff...")
        log_info(f"使用 ruff 检查并修复 {target}...", lang="zh")
    try:
        _run_format_command(["uv", "run", "ruff", "check", "--fix", target], env, quiet)
    except Exception as e:
        if not quiet:
            log_info(f"Warning: ruff check failed: {e}")
            log_info(f"警告：ruff 检查失败: {e}", lang="zh")
        else:
            print(f"Warning: ruff check failed: {e}")


def format_tools_scripts(tools_dir: str, env: dict, quiet: bool) -> None:
    """Format Python files in tools directory."""
    tools_path = Path(tools_dir)
    if not quiet:
        log_info(f"Formatting Python files in {tools_dir}...")
        log_info(f"格式化 {tools_dir} 中的 Python 文件...", lang="zh")

    # Find all Python files in tools directory
    python_files = list(tools_path.glob("**/*.py"))
    if python_files:
        # Format tools Python files with isort
        try:
            _run_format_command(
                ["uv", "run", "isort"] + [str(f) for f in python_files], env, quiet
            )
        except Exception as e:
            if not quiet:
                log_info(f"Warning: isort failed for tools scripts: {e}")
                log_info(f"警告：tools 脚本 isort 失败: {e}", lang="zh")
            else:
                print(f"Warning: isort failed for tools scripts: {e}")

        # Format tools Python files with black
        try:
            _run_format_command(
                ["uv", "run", "black"] + [str(f) for f in python_files], env, quiet
            )
        except Exception as e:
            if not quiet:
                log_info(f"Warning: black failed for tools scripts: {e}")
                log_info(f"警告：tools 脚本 black 失败: {e}", lang="zh")
            else:
                print(f"Warning: black failed for tools scripts: {e}")

        # Fix issues in tools Python files with ruff
        try:
            _run_format_command(
                ["uv", "run", "ruff", "check", "--fix"]
                + [str(f) for f in python_files],
                env,
                quiet,
            )
        except Exception as e:
            if not quiet:
                log_info(f"Warning: ruff check failed for tools scripts: {e}")
                log_info(f"警告：tools 脚本 ruff 检查失败: {e}", lang="zh")
            else:
                print(f"Warning: ruff check failed for tools scripts: {e}")
    else:
        if not quiet:
            log_info("No Python files found in tools directory")
            log_info("在 tools 目录中未找到 Python 文件", lang="zh")
        else:
            print("No Python files found in tools directory")


def format_examples(examples_dir: str, env: dict, quiet: bool) -> None:
    """Format examples directory."""
    if not quiet:
        log_info(f"Formatting {examples_dir}...")
        log_info(f"格式化 {examples_dir}...", lang="zh")

    # Format examples with isort
    try:
        _run_format_command(["uv", "run", "isort", examples_dir], env, quiet)
    except Exception as e:
        if not quiet:
            log_info(f"Warning: isort failed for examples: {e}")
            log_info(f"警告：examples 的 isort 失败: {e}", lang="zh")
        else:
            print(f"Warning: isort failed for examples: {e}")

    # Format examples with black
    try:
        _run_format_command(["uv", "run", "black", examples_dir], env, quiet)
    except Exception as e:
        if not quiet:
            log_info(f"Warning: black failed for examples: {e}")
            log_info(f"警告：examples 的 black 失败: {e}", lang="zh")
        else:
            print(f"Warning: black failed for examples: {e}")

    # Fix issues in examples with ruff (with unsafe fixes)
    try:
        _run_format_command(
            ["uv", "run", "ruff", "check", "--fix", examples_dir, "--unsafe-fixes"],
            env,
            quiet,
        )
    except Exception as e:
        if not quiet:
            log_info(f"Warning: ruff check failed for examples: {e}")
            log_info(f"警告：examples 的 ruff 检查失败: {e}", lang="zh")
        else:
            print(f"Warning: ruff check failed for examples: {e}")


def generate_type_stubs(src_dir: str, typings_dir: str, env: dict, quiet: bool) -> None:
    """Generate type stubs."""
    if not quiet:
        log_info(f"Generating type stubs for {src_dir}...")
        log_info(f"为 {src_dir} 生成类型提示...", lang="zh")

    # Ensure typings directory exists
    typings_path = Path(typings_dir)
    typings_path.mkdir(parents=True, exist_ok=True)

    try:
        # Try to run stubgen through uv
        _run_format_command(
            ["uv", "run", "stubgen", src_dir, "-o", typings_dir], env, quiet
        )
    except Exception:
        # If that fails, try direct execution as fallback
        try:
            # First check if stubgen is available
            result = subprocess.run(
                ["python", "-c", "import mypy.stubgen"],
                capture_output=True,
                text=True,
                shell=False,
            )

            if result.returncode == 0:
                # stubgen is available, use it directly
                _run_format_command(
                    ["python", "-m", "mypy.stubgen", src_dir, "-o", typings_dir],
                    env,
                    quiet,
                )
            else:
                # Try to find stubgen executable
                stubgen_path = shutil.which("stubgen")
                if stubgen_path:
                    _run_format_command(
                        [stubgen_path, src_dir, "-o", typings_dir], env, quiet
                    )
                else:
                    if not quiet:
                        log_info(
                            "Warning: stubgen not found, skipping type stub generation"
                        )
                        log_info("警告：未找到 stubgen，跳过类型提示生成", lang="zh")
                    else:
                        print(
                            "Warning: stubgen not found, skipping type stub generation"
                        )
        except Exception as fallback_e:
            if not quiet:
                log_info(f"Warning: Failed to generate type stubs: {fallback_e}")
                log_info(f"警告：生成类型提示失败: {fallback_e}", lang="zh")
            else:
                print(f"Warning: Failed to generate type stubs: {fallback_e}")


def _is_running_in_uv_tool() -> bool:
    """Check if we are running in a uv tool environment."""
    # Check if we're in a uv tool environment by looking for uv specific paths
    import sys

    # Get the current executable path
    executable_path = sys.executable.lower()

    # Check if we're in a uv tool environment
    # UV tool environments typically have paths like:
    # Windows: C:\Users\{user}\AppData\Roaming\uv\tools\{tool_name}\...
    # Unix: ~/.local/share/uv/tools/{tool_name}/...
    return "uv\\tools\\" in executable_path or "uv/tools/" in executable_path


def _run_format_command(command: list, env: dict, quiet: bool) -> None:
    """Run a formatting command with proper output handling."""
    # Prepare environment variables
    environment = env.copy() if env else {}

    # Fix encoding issues on Windows
    if sys.platform.startswith("win"):
        # Set environment variables to ensure proper UTF-8 handling
        environment["PYTHONIOENCODING"] = "utf-8"
        environment["PYTHONLEGACYWINDOWSFSENCODING"] = "1"

    # Special handling for uv run commands when running in uv tool environment
    if (
        len(command) >= 2
        and command[0] == "uv"
        and command[1] == "run"
        and _is_running_in_uv_tool()
    ):
        # When running in uv tool environment, try to run tools directly
        # instead of using uv run to avoid file locking issues
        direct_command = command[2:]  # Remove "uv run" from the command
        try:
            # Try running the command directly first
            _run_command_with_fallback(direct_command, environment, quiet)
            return
        except Exception:
            # If direct execution fails, fall back to uv run
            pass

    # Check for execution of untrusted input - not applicable here as we're running
    # trusted formatting tools with trusted paths
    _run_command_with_fallback(command, environment, quiet)


def _run_command_with_fallback(command: list, env: dict, quiet: bool) -> None:
    """Run command with fallback handling."""
    if quiet:
        # In quiet mode, capture output to suppress it
        result = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True,
            shell=False,
            # Explicitly set encoding for Windows systems
            encoding="utf-8" if sys.platform.startswith("win") else None,
        )  # nosec B603
        # Even if the command fails, we continue execution to make formatting more robust
        if result.returncode != 0:
            # Log the error but don't raise exception to avoid stopping the whole formatting process
            error_msg = f"Command failed with return code {result.returncode}"
            if result.stderr:
                error_msg += f": {result.stderr.strip()}"
            raise Exception(error_msg)
    else:
        # In normal mode, let the command output directly to stdout/stderr
        result = subprocess.run(
            command,
            env=env,
            shell=False,
            # Explicitly set encoding for Windows systems
            encoding="utf-8" if sys.platform.startswith("win") else None,
        )  # nosec B603
        # Even if the command fails, we continue execution to make formatting more robust
        if result.returncode != 0:
            # Log the error but don't raise exception to avoid stopping the whole formatting process
            raise Exception(f"Command failed with return code {result.returncode}")
