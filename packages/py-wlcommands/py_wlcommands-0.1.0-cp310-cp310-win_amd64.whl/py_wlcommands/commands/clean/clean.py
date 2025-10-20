"""
Utilities for cleaning project artifacts.
"""

import glob
import os
import shutil
from pathlib import Path

from py_wlcommands.utils.logging import log_info


def clean_build_artifacts() -> None:
    """
    Clean build artifacts and temporary files
    清理构建产物和临时文件
    """
    # List of directories to remove
    # 需要删除的目录列表
    dirs_to_remove = [
        "build",
        "dist",
        "results",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "logs",
        "todos",
    ]

    # List of files to remove
    # 需要删除的文件列表
    files_to_remove = [".coverage"]

    # Remove specific directories
    # 删除指定目录
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                log_info(f"Removed directory: {dir_name}", lang="en")
                log_info(f"已删除目录: {dir_name}", lang="zh")
            except Exception as e:
                log_info(f"Failed to remove directory {dir_name}: {e}", lang="en")
                log_info(f"删除目录 {dir_name} 失败: {e}", lang="zh")

    # Remove specific files
    # 删除指定文件
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                log_info(f"Removed file: {file_name}", lang="en")
                log_info(f"已删除文件: {file_name}", lang="zh")
            except Exception as e:
                log_info(f"Failed to remove file {file_name}: {e}", lang="en")
                log_info(f"删除文件 {file_name} 失败: {e}", lang="zh")

    # Remove log files
    # 删除日志文件
    try:
        for log_file in glob.glob("*.log"):
            os.remove(log_file)
            log_info(f"Removed log file: {log_file}", lang="en")
            log_info(f"已删除日志文件: {log_file}", lang="zh")
    except Exception as e:
        log_info(f"Failed to remove log files: {e}", lang="en")
        log_info(f"删除日志文件失败: {e}", lang="zh")

    # Remove __pycache__ directories only in project directory (not in venv)
    # 只删除项目目录中的__pycache__目录（不删除虚拟环境中的）
    try:
        project_root = Path(".").resolve()
        for pycache_dir in project_root.rglob("__pycache__"):
            # Skip pycache directories in virtual environments
            # 跳过虚拟环境中的pycache目录
            if ".venv" in str(pycache_dir) or "venv" in str(pycache_dir):
                continue

            if pycache_dir.is_dir():
                shutil.rmtree(pycache_dir)
                log_info(f"Removed pycache directory: {pycache_dir}", lang="en")
                log_info(f"已删除pycache目录: {pycache_dir}", lang="zh")
    except Exception as e:
        log_info(f"Failed to remove pycache directories: {e}", lang="en")
        log_info(f"删除pycache目录失败: {e}", lang="zh")

    # Remove egg-info directories only in project directory
    # 只删除项目目录中的egg-info目录
    try:
        project_root = Path(".").resolve()
        for egg_info_dir in project_root.rglob("*.egg-info"):
            # Skip egg-info directories in virtual environments
            # 跳过虚拟环境中的egg-info目录
            if ".venv" in str(egg_info_dir) or "venv" in str(egg_info_dir):
                continue

            if egg_info_dir.is_dir():
                shutil.rmtree(egg_info_dir)
                log_info(f"Removed egg-info directory: {egg_info_dir}", lang="en")
                log_info(f"已删除egg-info目录: {egg_info_dir}", lang="zh")
    except Exception as e:
        log_info(f"Failed to remove egg-info directories: {e}", lang="en")
        log_info(f"删除egg-info目录失败: {e}", lang="zh")


def clean_all_artifacts() -> None:
    """
    Clean all artifacts including virtual environment
    清理所有产物，包括虚拟环境
    """
    # First do regular cleaning
    # 首先执行常规清理
    clean_build_artifacts()

    # Remove virtual environment
    # 删除虚拟环境
    venv_dirs = [".venv", "venv"]
    for venv_dir in venv_dirs:
        if os.path.exists(venv_dir):
            try:
                shutil.rmtree(venv_dir)
                log_info(f"Removed virtual environment: {venv_dir}", lang="en")
                log_info(f"已删除虚拟环境: {venv_dir}", lang="zh")
            except Exception as e:
                log_info(
                    f"Failed to remove virtual environment {venv_dir}: {e}", lang="en"
                )
                log_info(f"删除虚拟环境 {venv_dir} 失败: {e}", lang="zh")

    # Remove auto-activation scripts
    # 删除自动激活脚本
    auto_activate_scripts = ["auto_activate_venv.bat", "auto_activate_venv.sh"]
    for script in auto_activate_scripts:
        if os.path.exists(script):
            try:
                os.remove(script)
                log_info(f"Removed auto-activation script: {script}", lang="en")
                log_info(f"已删除自动激活脚本: {script}", lang="zh")
            except Exception as e:
                log_info(
                    f"Failed to remove auto-activation script {script}: {e}", lang="en"
                )
                log_info(f"删除自动激活脚本 {script} 失败: {e}", lang="zh")


def clean_rust_artifacts() -> None:
    """
    Clean Rust build artifacts
    清理Rust构建产物
    """
    # Check if Rust is enabled and directory exists
    # 检查是否启用了Rust且目录存在
    rust_dir = "rust"
    if os.path.exists(rust_dir):
        rust_target_dir = os.path.join(rust_dir, "target")
        if os.path.exists(rust_target_dir):
            try:
                shutil.rmtree(rust_target_dir)
                log_info(f"Removed Rust target directory: {rust_target_dir}", lang="en")
                log_info(f"已删除Rust target目录: {rust_target_dir}", lang="zh")
            except Exception as e:
                log_info(
                    f"Failed to remove Rust target directory {rust_target_dir}: {e}",
                    lang="en",
                )
                log_info(f"删除Rust target目录 {rust_target_dir} 失败: {e}", lang="zh")
        else:
            log_info("Rust target directory does not exist, skipping...", lang="en")
            log_info("Rust target目录不存在，跳过...", lang="zh")
    else:
        log_info("Rust directory does not exist, skipping...", lang="en")
        log_info("Rust目录不存在，跳过...", lang="zh")


"""
Clean project command.
"""

import sys

from py_wlcommands.commands import Command, register_command, validate_command_args

from .clean_utils import (
    clean_all_artifacts,
    clean_build_artifacts,
    clean_rust_artifacts,
)


@register_command("clean")
class CleanCommand(Command):
    """Command to clean project build artifacts."""

    @property
    def name(self) -> str:
        return "clean"

    @property
    def help(self) -> str:
        return "Clean project build artifacts"

    @classmethod
    def add_arguments(cls, parser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "target",
            nargs="?",
            default="build",
            choices=["build", "all", "rust"],
            help="Target to clean (build, all, rust)",
        )

    @validate_command_args()
    def execute(self, target: str = "build") -> None:
        """
        Clean project - equivalent to make clean
        清理项目 - 等效于 make clean
        """
        from py_wlcommands.utils.logging import log_info

        # Use simple logging instead of structured logging for user-facing messages
        if target == "all":
            log_info("Cleaning all project artifacts including virtual environment...")
            log_info("正在清理所有项目产物，包括虚拟环境...", lang="zh")
        elif target == "rust":
            log_info("Cleaning Rust build artifacts...")
            log_info("正在清理Rust构建产物...", lang="zh")
        else:
            log_info("Cleaning project build artifacts...")
            log_info("正在清理项目构建产物...", lang="zh")

        try:
            # Clean based on target
            # 根据目标清理
            if target == "all":
                clean_all_artifacts()
            elif target == "rust":
                clean_rust_artifacts()
            else:
                clean_build_artifacts()

            # Use simple logging for user-facing messages
            if target == "all":
                log_info("Complete project cleaning completed successfully!")
                log_info("完整项目清理成功完成！", lang="zh")
            elif target == "rust":
                log_info("Rust cleaning completed successfully!")
                log_info("Rust清理成功完成！", lang="zh")
            else:
                log_info("Project cleaning completed successfully!")
                log_info("项目清理成功完成！", lang="zh")
        except Exception as e:
            log_info(f"Error cleaning project: {e}", lang="en")
            log_info(f"错误：清理项目失败: {e}", lang="zh")
            sys.exit(1)
