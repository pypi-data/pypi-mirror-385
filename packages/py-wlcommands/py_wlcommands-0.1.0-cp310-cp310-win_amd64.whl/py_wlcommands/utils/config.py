"""
Configuration management utilities for WL Commands.
"""

import json
import os
from typing import Any


class ConfigManager:
    """Manage application configuration."""

    def __init__(self, config_file: str | None = None) -> None:
        """
        Initialize configuration manager.

        Args:
            config_file (str, optional): Path to configuration file.
        """
        self.config_file = config_file or self._get_default_config_path()
        self._config = {}
        self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        # Try to get from environment variable first
        config_path = os.environ.get("WL_CONFIG_PATH")
        if config_path:
            return config_path

        # Use home directory
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".wl", "config.json")

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            # Create default config directory if needed
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            self._config = self._get_default_config()
            self._save_config()
            return

        try:
            with open(self.config_file, encoding="utf-8") as f:
                self._config = json.load(f)
        except (OSError, json.JSONDecodeError):
            # Fallback to default config if file is corrupted
            self._config = self._get_default_config()

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except OSError:
            # Silently fail if can't write to config file
            pass

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        return {
            "log_level": "INFO",
            "log_file": None,
            "log_console": False,  # 控制是否在控制台显示结构化日志
            "language": "auto",  # 语言设置: "en", "zh", 或 "auto"
            "aliases": {},
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key (str): Configuration key.
            default (Any, optional): Default value if key not found.

        Returns:
            Any: Configuration value.
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key (str): Configuration key.
            value (Any): Configuration value.
        """
        self._config[key] = value
        self._save_config()

    def get_all(self) -> dict[str, Any]:
        """
        Get all configuration.

        Returns:
            Dict[str, Any]: All configuration.
        """
        return self._config.copy()

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()


# Global configuration manager instance
_config_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """
    Get global configuration manager instance.

    Returns:
        ConfigManager: Global configuration manager.
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config(key: str, default: Any = None) -> Any:
    """
    Get configuration value from global manager.

    Args:
        key (str): Configuration key.
        default (Any, optional): Default value if key not found.

    Returns:
        Any: Configuration value.
    """
    return get_config_manager().get(key, default)
