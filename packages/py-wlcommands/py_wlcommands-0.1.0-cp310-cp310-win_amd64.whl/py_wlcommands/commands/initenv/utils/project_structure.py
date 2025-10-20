"""Project structure setup utility."""

from pathlib import Path

from ....utils.logging import log_info
from .log_manager import performance_monitor


class ProjectStructureSetup:
    """Project structure setup handler."""

    def __init__(self) -> None:
        pass

    @performance_monitor
    def setup(self, project_name: str) -> None:
        """Setup project structure."""
        # Create main project structure
        directories = [
            "src",
            f"src/{project_name}",
            f"src/{project_name}/lib",  # 添加lib目录以支持Rust扩展
            "tests",
            "docs",
            "examples",
            "rust",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            # Create __init__.py files for Python packages
            if directory.startswith("src/") or directory == "tests":
                init_file = Path(directory) / "__init__.py"
                if not init_file.exists():
                    init_file.touch()

        # Create README.md if it doesn't exist or is empty
        readme_file = Path("README.md")
        should_create_readme = not readme_file.exists() or readme_file.read_text().strip() == ""
        if should_create_readme:
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(f"# {project_name}\n")
            log_info(f"✓ Created README.md with project name: {project_name}")
            log_info(f"✓ 创建 README.md，项目名: {project_name}", lang="zh")

        log_info("✓ Project structure created successfully")
        log_info("✓ 项目结构创建成功", lang="zh")


def setup_project_structure(project_name: str) -> None:
    """Setup project structure manually."""
    try:
        # Normalize project name
        normalized_name = project_name.replace("-", "_")

        # Define required directories
        required_dirs = [
            Path("src"),
            Path("src") / normalized_name,
            Path("src") / normalized_name / "lib",  # 添加lib目录以支持Rust扩展
            Path("rust"),
            Path("tests"),
            Path("docs"),
            Path("examples"),
            Path("dist"),
        ]

        log_info(f"Setting up project structure for '{project_name}'...")
        log_info(f"为 '{project_name}' 设置项目结构...", lang="zh")

        # Create directories
        for dir_path in required_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            log_info(f"  ✓ Created directory: {dir_path}")
            log_info(f"  ✓ 创建目录: {dir_path}", lang="zh")

        # Create required __init__.py files
        required_inits = [
            Path("src") / normalized_name / "__init__.py",
            Path("tests") / "__init__.py",
        ]

        for init_file in required_inits:
            if init_file.parent.exists():
                init_file.touch(exist_ok=True)
                log_info(f"  ✓ Created file: {init_file}")
                log_info(f"  ✓ 创建文件: {init_file}", lang="zh")

        # Create README.md if it doesn't exist or is empty
        readme_file = Path("README.md")
        should_create_readme = not readme_file.exists() or readme_file.read_text().strip() == ""
        if should_create_readme:
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(f"# {project_name}\n")
            log_info(f"  ✓ Created README.md with project name: {project_name}")
            log_info(f"  ✓ 创建 README.md，项目名: {project_name}", lang="zh")

        log_info("✓ Project structure set up successfully")
        log_info("✓ 项目结构设置成功", lang="zh")
    except Exception as e:
        log_info(f"Warning: Failed to setup project structure: {e}")
        log_info(f"警告: 设置项目结构失败: {e}", lang="zh")