"""
Config command.

Usage:
    wl config list                  # List all configuration values
    wl config get <key>             # Get a specific configuration value
    wl config set <key> <value>     # Set a configuration value
    wl config reset                 # Reset configuration to default values

Examples:
    wl config list
    wl config get log_level
    wl config set log_level DEBUG
    wl config set log_console true
    wl config set language en       # Only show English messages
    wl config set language zh       # Only show Chinese messages
    wl config set language auto     # Show messages based on system language (default)
"""

from ...commands import Command, register_command, validate_command_args


@register_command("config")
class ConfigCommand(Command):
    """Command to manage wl configuration."""

    @property
    def name(self) -> str:
        return "config"

    @property
    def help(self) -> str:
        return "Manage wl configuration"

    @classmethod
    def add_arguments(cls, parser) -> None:
        """Add command-specific arguments."""
        subparsers = parser.add_subparsers(dest="config_action", help="Config actions")

        # Get subcommand
        get_parser = subparsers.add_parser("get", help="Get configuration value")
        get_parser.add_argument("key", help="Configuration key to get")

        # Set subcommand
        set_parser = subparsers.add_parser("set", help="Set configuration value")
        set_parser.add_argument("key", help="Configuration key to set")
        set_parser.add_argument("value", help="Configuration value to set")

        # List subcommand
        subparsers.add_parser("list", help="List all configuration values")

        # Reset subcommand
        subparsers.add_parser("reset", help="Reset configuration to default")

    @validate_command_args()
    def execute(
        self, config_action: str = None, key: str = None, value: str = None, **kwargs
    ) -> None:
        """
        Manage wl configuration.
        管理wl配置。
        """
        from ...utils.config import get_config_manager

        config_manager = get_config_manager()

        if config_action == "get":
            if not key:
                print("Error: key is required for get action")
                return

            value = config_manager.get(key)
            if value is not None:
                print(f"{key} = {value}")
            else:
                print(f"{key} is not set")

        elif config_action == "set":
            if not key or value is None:
                print("Error: both key and value are required for set action")
                return

            # Special handling for language setting
            if key == "language" and value not in ["en", "zh", "auto"]:
                print("Error: language must be one of 'en', 'zh', or 'auto'")
                return

            # Convert string values to appropriate types
            converted_value = self._convert_value(value)
            config_manager.set(key, converted_value)
            print(f"Set {key} = {converted_value}")

        elif config_action == "list":
            all_config = config_manager.get_all()
            if all_config:
                print("Current configuration:")
                for k, v in all_config.items():
                    print(f"  {k} = {v}")
            else:
                print("No configuration values set")

        elif config_action == "reset":
            # Reset to default configuration
            default_config = config_manager._get_default_config()
            for key in config_manager.get_all():
                if key not in default_config:
                    config_manager.set(key, None)  # Remove extra keys

            for key, value in default_config.items():
                config_manager.set(key, value)

            print("Configuration reset to default values")

        else:
            print("Error: config action required. Use 'get', 'set', 'list', or 'reset'")

    def _convert_value(self, value: str):
        """
        Convert string value to appropriate type.

        Args:
            value (str): String value to convert

        Returns:
            Converted value
        """
        # Handle None value
        if value.lower() in ("none", "null"):
            return None

        # Try to convert to boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Try to convert to integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string if no other conversion works
        return value
