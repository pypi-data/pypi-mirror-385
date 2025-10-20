"""Configuration manager utility."""

import json
import os
from pathlib import Path
from typing import Any


class ConfigManager:
    """Manager for loading and managing configuration."""

    def __init__(self, config_file: str = "config.json") -> None:
        self.config_file = config_file
        self.config: dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file or environment variables."""
        # Load from config file if exists
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception:
                # If file loading fails, continue with empty config
                self.config = {}

        # Override with environment variables
        self._load_from_env()

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Example environment variable loading
        python_version = os.environ.get("PYTHON_VERSION")
        if python_version:
            self.config["python_version"] = python_version

        venv_path = os.environ.get("VENV_PATH")
        if venv_path:
            self.config["venv_path"] = venv_path

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        self.config[key] = value

    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to save configuration: {e}")
