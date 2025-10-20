"""
Logging utilities for WL Commands.
"""

import datetime
import json
import locale
import os
import sys
from functools import partial
from typing import Any


class LogLevel:
    """Log levels."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogFilter:
    """Filter logs based on context."""

    def __init__(self, **context) -> None:
        self.context = context

    def filter(self, record: dict[str, Any]) -> bool:
        """Filter log records based on context."""
        for key, value in self.context.items():
            if key in record and record[key] != value:
                return False
        return True


class LogRotator:
    """Simple log rotator that manages log file size."""

    def __init__(
        self, filename: str, max_size: int = 10 * 1024 * 1024
    ) -> None:  # 10MB default
        """
        Initialize log rotator.

        Args:
            filename (str): Log file name.
            max_size (int): Maximum file size in bytes before rotation.
        """
        self.filename = filename
        self.max_size = max_size

    def should_rotate(self) -> bool:
        """Check if log file should be rotated."""
        if not os.path.exists(self.filename):
            return False
        return os.path.getsize(self.filename) >= self.max_size

    def do_rotate(self) -> None:
        """Perform log rotation."""
        if os.path.exists(self.filename):
            backup_name = f"{self.filename}.1"
            if os.path.exists(backup_name):
                os.remove(backup_name)
            os.rename(self.filename, backup_name)


class StructuredLogger:
    """A structured logger that outputs JSON formatted logs."""

    def __init__(
        self, name: str, min_level: int = LogLevel.INFO, log_file: str = None
    ) -> None:
        """
        Initialize structured logger.

        Args:
            name (str): Logger name.
            min_level (int): Minimum log level.
            log_file (str): Log file path.
        """
        self.name = name
        self.min_level = min_level
        self.filters = []
        self.log_file = log_file
        self.log_rotator = LogRotator(log_file) if log_file else None

        # Check configuration for console output setting
        try:
            from .config import get_config

            self.enable_console = get_config("log_console", False)
        except ImportError:
            self.enable_console = False

    def add_filter(self, filter_func) -> None:
        """Add a filter function."""
        self.filters.append(filter_func)

    def _should_log(self, level: int, **kwargs) -> bool:
        """Check if log should be processed based on level and filters."""
        if level < self.min_level:
            return False

        record = {
            "level": level,
            "timestamp": datetime.datetime.now().isoformat(),
            **kwargs,
        }
        return all(f(record) for f in self.filters)

    def _write_log(self, message: str) -> None:
        """Write log message to appropriate output."""
        # Always write to file if specified
        if self.log_file and self.log_rotator:
            # Handle log rotation
            if self.log_rotator.should_rotate():
                self.log_rotator.do_rotate()

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")

        # Write to console only if enabled
        if self.enable_console:
            target = (
                sys.stdout
                if "ERROR" not in message and "CRITICAL" not in message
                else sys.stderr
            )
            print(message, file=target)

    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal logging method."""
        if not self._should_log(level, message=message, **kwargs):
            return

        record = {
            "logger": self.name,
            "level": level,
            "level_name": self._get_level_name(level),
            "timestamp": datetime.datetime.now().isoformat(),
            "message": message,
            **kwargs,
        }

        self._write_log(json.dumps(record))

    def _get_level_name(self, level: int) -> str:
        """Convert level number to name."""
        level_names = {
            LogLevel.DEBUG: "DEBUG",
            LogLevel.INFO: "INFO",
            LogLevel.WARNING: "WARNING",
            LogLevel.ERROR: "ERROR",
            LogLevel.CRITICAL: "CRITICAL",
        }
        return level_names.get(level, "UNKNOWN")

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, **kwargs)


def _is_system_chinese() -> bool:
    """
    Check if the system language is Chinese.

    Returns:
        bool: True if system language is Chinese, False otherwise
    """
    try:
        # Try different locale-related environment variables
        lang = (
            os.environ.get("LANG", "")
            or os.environ.get("LANGUAGE", "")
            or os.environ.get("LC_ALL", "")
            or os.environ.get("LC_MESSAGES", "")
            or locale.getdefaultlocale()[0]
            or ""
        )

        # Check if any of the locale identifiers contain Chinese language codes
        return any(chinese_lang in lang.lower() for chinese_lang in ["zh", "chinese"])
    except Exception:
        # If we can't determine the language, default to English
        return False


# Default simple logging functions (backward compatibility)
def _should_display_language(lang: str) -> bool:
    """
    Check if message in specified language should be displayed.

    Args:
        lang (str): Language of the message ("en" or "zh")

    Returns:
        bool: True if message should be displayed
    """
    try:
        from .config import get_config

        language_setting = get_config("language", "auto")

        # If language is set to auto, display based on system language
        if language_setting == "auto":
            # If system language is Chinese, only show Chinese messages
            # Otherwise, show English messages
            is_system_chinese = _is_system_chinese()
            return (lang == "zh" and is_system_chinese) or (
                lang == "en" and not is_system_chinese
            )

        # If language is set to specific language, only display that language
        return language_setting == lang
    except ImportError:
        # Default to showing English if config is not available
        return lang == "en"


def log_info(message, lang="en") -> None:
    """
    Log an informational message.

    Args:
        message (str): Message to log.
        lang (str, optional): Language of the message. Defaults to "en".
    """
    if _should_display_language(lang):
        if lang == "en":
            print(f"INFO: {message}")
        elif lang == "zh":
            print(f"信息: {message}")


def log_error(message, lang="en") -> None:
    """
    Log an error message.

    Args:
        message (str): Message to log.
        lang (str, optional): Language of the message. Defaults to "en".
    """
    if _should_display_language(lang):
        if lang == "en":
            print(f"ERROR: {message}", file=sys.stderr)
        elif lang == "zh":
            print(f"错误: {message}", file=sys.stderr)


# Create a default structured logger (console output controlled by config)
default_logger = StructuredLogger("wl")


# Convenience functions for the default logger
log_debug = partial(default_logger.debug)
log_warning = partial(default_logger.warning)
log_critical = partial(default_logger.critical)
log_info_structured = partial(default_logger.info)
