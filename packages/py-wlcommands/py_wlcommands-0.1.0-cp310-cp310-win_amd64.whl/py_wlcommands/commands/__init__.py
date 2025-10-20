"""
Command registration and management module.
"""

import functools
from collections.abc import Callable
from typing import Any, Dict, Type

from ..exceptions import CommandError

# Command registry
_COMMANDS: dict[str, type["Command"]] = {}
_ALIASES: dict[str, str] = {}
_DEPENDENCY_RESOLVERS: dict[str, Callable[[], Any]] = {}


class ErrorCode:
    """Error codes for command operations."""

    SUCCESS = 0
    COMMAND_NOT_FOUND = 1
    COMMAND_EXECUTION_FAILED = 2
    INVALID_ARGUMENT = 3
    MISSING_DEPENDENCY = 4


class Command:
    """
    Base class for all commands.
    """

    def __init__(self, **dependencies: Any) -> None:
        """
        Initialize the command with dependencies.

        Args:
            **dependencies: Dependencies to inject into the command
        """
        self._dependencies = dependencies

    @property
    def name(self) -> str:
        """
        Get the command name.

        Returns:
            str: The command name
        """
        raise NotImplementedError("Command subclasses must implement name property")

    @property
    def help(self) -> str:
        """
        Get the command help text.

        Returns:
            str: The command help text
        """
        raise NotImplementedError("Command subclasses must implement help property")

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """
        Execute the command.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        raise NotImplementedError("Command subclasses must implement execute method")


def register_command(name: str) -> Callable[[type[Command]], type[Command]]:
    """
    Decorator to register a command.

    Args:
        name (str): The name to register the command under

    Returns:
        Callable[[Type[Command]], Type[Command]]: The decorator function
    """

    def decorator(command_class: type[Command]) -> type[Command]:
        _COMMANDS[name] = command_class
        return command_class

    return decorator


def register_alias(alias: str, command_name: str) -> None:
    """
    Register an alias for a command.

    Args:
        alias (str): The alias to register
        command_name (str): The name of the command to alias
    """
    _ALIASES[alias] = command_name


def resolve_command_name(name: str) -> str:
    """
    Resolve a command name, handling aliases.

    Args:
        name (str): The command name or alias

    Returns:
        str: The resolved command name
    """
    return _ALIASES.get(name, name)


def list_commands() -> dict[str, type[Command]]:
    """
    List all registered commands.

    Returns:
        Dict[str, Type[Command]]: A dictionary of command names and their classes
    """
    return _COMMANDS.copy()


def get_command(name: str) -> Command:
    """
    Get an instance of a registered command.

    Args:
        name (str): The name of the command to get

    Returns:
        Command: An instance of the requested command

    Raises:
        ValueError: If the command is not found
    """
    resolved_name = resolve_command_name(name)
    if resolved_name not in _COMMANDS:
        raise ValueError(f"Command '{name}' not found")

    command_class = _COMMANDS[resolved_name]
    dependencies = resolve_dependencies(**command_class.__init__.__annotations__)
    return command_class(**dependencies)


def validate_command_args(**validators: Callable[[Any], bool]) -> Callable:
    """
    Decorator to validate command arguments.

    Args:
        **validators: A dictionary of argument names and validation functions

    Returns:
        Callable: The decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for arg_name, validator in validators.items():
                if arg_name in kwargs:
                    if not validator(kwargs[arg_name]):
                        raise ValueError(f"Invalid value for {arg_name}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def register_dependency(name: str, resolver: Callable[[], Any]) -> None:
    """
    Register a dependency resolver.

    Args:
        name (str): The name of the dependency
        resolver (Callable[[], Any]): A function that returns the dependency instance
    """
    _DEPENDENCY_RESOLVERS[name] = resolver


def resolve_dependencies(**annotations: Any) -> dict[str, Any]:
    """
    Resolve dependencies based on annotations.

    Args:
        **annotations: Annotations to resolve dependencies for

    Returns:
        Dict[str, Any]: A dictionary of dependency names and their instances
    """
    dependencies = {}
    for arg_name, _arg_type in annotations.items():
        if arg_name in _DEPENDENCY_RESOLVERS:
            dependencies[arg_name] = _DEPENDENCY_RESOLVERS[arg_name]()
    return dependencies


# Import command modules to register commands
from . import (
    buildcommands,
    clean,
    config,
    format,
    initenv,
    lint,
    self,
    testcommands,  # Added testcommands import
)

# Register common aliases
register_alias("i", "init")
register_alias("b", "build")
register_alias("t", "test")  # Added test alias
register_alias("f", "format")
register_alias("l", "lint")
register_alias("c", "clean")
