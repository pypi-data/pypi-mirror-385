"""
Deployment functionality for init command.
"""

import ctypes
import os
import platform
import shutil

try:
    from packaging.version import parse as parse_version
except ImportError:
    # 如果没有安装 packaging 库，则回退到简单的字符串比较
    def parse_version(version):
        return version


# 白名单列表：只有这些文件或文件夹会被部署
DEPLOY_WHITELIST = [
    ".uv",
    # '.cursor',
    ".lingma",
    "tools",
    "Makefile",
    ".python-version",
    "project_vendors",
]


def create_symlink(source: str, target: str) -> bool:
    """
    创建从源到目标的软链接，处理平台差异
    """
    source = os.path.abspath(source)
    target = os.path.abspath(target)

    # 如果目标文件已存在，先删除
    if os.path.exists(target):
        try:
            if os.path.islink(target):
                os.unlink(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
            elif os.path.isfile(target):
                os.remove(target)
        except Exception:
            return False

    # 确保目标目录存在
    target_dir = os.path.dirname(target)
    os.makedirs(target_dir, exist_ok=True)

    # 创建软链接（处理不同操作系统）
    try:
        if platform.system() == "Windows":
            # Windows 需要管理员权限并区分目录和文件链接
            is_directory = os.path.isdir(source)
            if is_directory:
                # Windows 10以上版本支持目录符号链接，低版本需使用junction
                os.symlink(source, target, target_is_directory=True)
            else:
                os.symlink(source, target)
        else:
            # Unix/Linux/macOS
            os.symlink(source, target)
        return True
    except OSError:
        return False


def find_py_directories() -> list[str]:
    """
    查找当前目录下所有以 py_ 开头的文件夹
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    py_dirs = []

    for item in os.listdir(current_dir):
        if item.startswith("py_") and os.path.isdir(os.path.join(current_dir, item)):
            py_dirs.append(os.path.join(current_dir, item))

    return py_dirs


def is_ignored_directory(dir_name: str) -> bool:
    """
    检查目录是否应被忽略
    """
    ignored_dirs = [".git", "__pycache__"]  # 移除了 .cursor 和 .uv
    for ignored in ignored_dirs:
        if ignored in dir_name.split(os.sep):
            return True
    return False


def is_excluded_file(file_name: str) -> bool:
    """
    检查文件是否应被排除不创建链接
    """
    excluded_files = ["README.md", ".gitignore"]  # 添加.gitignore到排除列表
    return file_name in excluded_files


def is_in_whitelist(path: str, source_dir: str) -> bool:
    """
    检查文件或目录是否在白名单中
    """
    rel_path = os.path.relpath(path, source_dir)
    if rel_path == ".":
        return False

    # 检查路径或其父目录是否在白名单中
    path_parts = rel_path.split(os.sep)
    for i in range(len(path_parts)):
        if os.sep.join(path_parts[: i + 1]) in DEPLOY_WHITELIST:
            return True
    return False


def clean_existing_symlinks(
    py_dirs: list[str], source_dir_name: str = "shared-build-system"
) -> int:
    """
    清理目标文件夹中已有的软链接
    """
    cleaned_count = 0
    source_dir_basename = os.path.basename(source_dir_name)

    for py_dir in py_dirs:
        if not os.path.exists(py_dir):
            continue

        # 递归清理子目录中的链接
        for root, dirs, files in os.walk(py_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.islink(file_path):
                    try:
                        link_target = os.readlink(file_path)
                        if source_dir_basename in link_target:
                            os.unlink(file_path)
                            cleaned_count += 1
                    except OSError:
                        pass

            # 清理目录链接
            for dir_name in dirs[:]:  # 使用副本进行迭代，因为我们可能会修改dirs
                dir_path = os.path.join(root, dir_name)
                if os.path.islink(dir_path):
                    try:
                        link_target = os.readlink(dir_path)
                        if source_dir_basename in link_target:
                            os.unlink(dir_path)
                            cleaned_count += 1
                            dirs.remove(dir_name)  # 从遍历列表中移除，避免递归进入
                    except OSError:
                        pass

    return cleaned_count


def deploy_to_py_folders() -> bool:
    """
    将 shared-build-system 中的文件部署到所有 py_ 开头的文件夹中
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(current_dir, "shared-build-system")

    if not os.path.exists(source_dir):
        return False

    py_dirs = find_py_directories()
    if not py_dirs:
        return False

    # 清理已有的软链接
    clean_existing_symlinks(py_dirs, os.path.basename(source_dir))

    # 为每个py_目录递归创建软链接
    success = True
    for py_dir in py_dirs:
        # 遍历源目录中的所有内容
        for root, dirs, files in os.walk(source_dir):
            # 忽略特定目录
            dirs[:] = [d for d in dirs if not is_ignored_directory(d)]

            # 计算相对路径
            rel_path = os.path.relpath(root, source_dir)
            if rel_path == ".":
                rel_path = ""

            # 处理当前目录中的文件
            for file in files:
                source_file = os.path.join(root, file)

                # 检查是否在白名单中
                if not is_in_whitelist(source_file, source_dir):
                    continue

                # 排除特定文件
                if rel_path == "" and is_excluded_file(file):
                    continue

                # 排除任何目录下的.gitignore文件
                if file == ".gitignore":
                    continue

                target_file = os.path.join(py_dir, rel_path, file)

                if not create_symlink(source_file, target_file):
                    success = False

            # 处理当前目录中的子目录
            for dir_name in dirs:
                source_dir_path = os.path.join(root, dir_name)

                # 检查是否在白名单中
                if not is_in_whitelist(source_dir_path, source_dir):
                    continue

                target_dir_path = os.path.join(py_dir, rel_path, dir_name)

                # 只为空目录创建链接
                if not os.listdir(source_dir_path):
                    if not create_symlink(source_dir_path, target_dir_path):
                        success = False

    return success


def run_deploy_script() -> bool:
    """
    运行内化的部署脚本功能
    """
    # 检查是否有管理员权限（Windows平台创建软链接可能需要）
    if platform.system() == "Windows":
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except AttributeError:
            # 如果在非Windows平台运行这段代码（理论上不应该发生）
            is_admin = False

        if not is_admin:
            pass  # 在实际使用中可能需要记录警告日志

    return deploy_to_py_folders()
