"""
Command-line interface for WL Commands.
"""

import argparse
import functools
import sys
from typing import Any, cast

from .commands import Command


def load_commands() -> dict:
    """
    Load all registered commands dynamically.

    Returns:
        dict: A dictionary of command names and their classes.
    """
    # Import command modules to register commands
    from .commands import list_commands  # noqa: F401
    from .commands.buildcommands import BuildCommand  # noqa: F401
    from .commands.clean import CleanCommand  # noqa: F401
    from .commands.format.format_command import FormatCommand  # noqa: F401
    from .commands.format.python_formatter import (  # noqa: F401
        format_examples,
        format_tools_scripts,
        format_with_python_tools,
        generate_type_stubs,
    )
    from .commands.format.rust_formatter import format_rust_code  # noqa: F401
    from .commands.initenv import InitCommand  # noqa: F401
    from .commands.lint.lint import LintCommand  # noqa: F401
    from .commands.self import SelfCommand  # noqa: F401

    return list_commands()


def setup_self_command(
    subparsers: argparse._SubParsersAction, command_class: type[Command]
) -> None:
    """
    Setup self command with subcommands.

    Args:
        subparsers: The subparsers object from argparse.
        command_class: The SelfCommand class.
    """
    self_cmd = command_class()
    self_parser = subparsers.add_parser(self_cmd.name, help=self_cmd.help)
    self_subparsers = self_parser.add_subparsers(
        dest="subcommand", help="Self management subcommands"
    )

    # Self update command
    update_parser = self_subparsers.add_parser("update", help="Update wl command")
    update_parser.set_defaults(func=self_cmd.execute)


def setup_regular_command(
    subparsers: argparse._SubParsersAction, name: str, command_class: type[Command]
) -> None:
    """
    Setup a regular command.

    Args:
        subparsers: The subparsers object from argparse.
        name (str): The command name.
        command_class: The command class.
    """
    cmd = command_class()

    # Split the command name to handle subcommands
    # e.g., "build dist" becomes ["build", "dist"]
    command_parts = name.split()

    if len(command_parts) == 1:
        # Regular single command
        cmd_parser = subparsers.add_parser(cmd.name, help=cmd.help)
    else:
        # Handle subcommands by finding or creating parent parser
        parent_name = command_parts[0]
        subcommand_name = command_parts[1]

        # Check if parent parser already exists
        parent_parser = subparsers.choices.get(parent_name)

        if parent_parser is None:
            # Create parent parser if it doesn't exist
            # For now, we'll create a simple placeholder parent command
            parent_parser = subparsers.add_parser(
                parent_name, help=f"{parent_name} commands"
            )
            parent_subparsers = parent_parser.add_subparsers(dest="subcommand")
        else:
            # Find existing subparsers in parent parser
            parent_subparsers = None
            for action in parent_parser._actions:
                if isinstance(action, argparse._SubParsersAction):
                    parent_subparsers = action
                    break
            if parent_subparsers is None:
                parent_subparsers = parent_parser.add_subparsers(dest="subcommand")

        # Add subcommand to parent parser
        cmd_parser = parent_subparsers.add_parser(subcommand_name, help=cmd.help)

    # Add command-specific arguments if the command has add_arguments method
    if hasattr(command_class, "add_arguments"):
        command_class_with_args = cast(Any, command_class)
        command_class_with_args.add_arguments(cmd_parser)

    cmd_parser.set_defaults(func=cmd.execute)


@functools.lru_cache(maxsize=1)
def get_parser() -> argparse.ArgumentParser:
    """
    Create and return the argument parser with all commands.
    Uses lru_cache to avoid recreating the parser on repeated calls.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    # Get log level from configuration
    from .utils.config import get_config

    get_config("log_level", "INFO")

    parser = argparse.ArgumentParser(
        prog="wl",
        description="WL Commands - Project management CLI tool",
        epilog="Commands to manage the project environment and workflow",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Load all registered commands dynamically
    commands = load_commands()

    # Setup parsers for all commands
    for name, command_class in commands.items():
        if name == "self":
            setup_self_command(subparsers, command_class)
        else:
            setup_regular_command(subparsers, name, command_class)

    return parser


def main() -> None:
    """
    Main entry point for the WL Commands.
    """
    from .exceptions import CommandError
    from .utils.logging import log_error

    parser = get_parser()
    args = parser.parse_args()

    # Handle command aliases
    if hasattr(args, "command") and args.command:
        from .commands import resolve_command_name

        args.command = resolve_command_name(args.command)

    try:
        if hasattr(args, "func"):
            # Pass arguments to the command's execute function
            func_args = {
                k: v for k, v in vars(args).items() if k not in ["func", "command"]
            }
            if func_args:
                args.func(**func_args)
            else:
                args.func()
        else:
            parser.print_help()
    except CommandError as e:
        log_error(str(e))
        sys.exit(getattr(e, "error_code", 1))


if __name__ == "__main__":
    main()
