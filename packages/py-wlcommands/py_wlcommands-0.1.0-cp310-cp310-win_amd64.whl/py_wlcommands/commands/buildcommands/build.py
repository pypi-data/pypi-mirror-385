"""
Build command for WL Commands.
"""

from typing import Any

from .. import Command, register_command
from .build_utils import build_project


@register_command("build")
class BuildCommand(Command):
    """Command to build the project."""

    @property
    def name(self) -> str:
        """Return the command name."""
        return "build"

    @property
    def help(self) -> str:
        """Return the command help text."""
        return "Build the project"

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Execute the build command."""
        build_project()
