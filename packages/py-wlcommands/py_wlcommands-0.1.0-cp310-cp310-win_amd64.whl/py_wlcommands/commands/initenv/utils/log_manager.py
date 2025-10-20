"""Log manager utility for initenv module."""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from ....utils.logging import log_info


class LogManager:
    """Manager for logging with levels and performance monitoring."""

    def __init__(self, name: str = "initenv") -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Prevent adding multiple handlers if class is instantiated multiple times
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_level(self, level: int) -> None:
        """Set logging level."""
        self.logger.setLevel(level)

    def info(self, message: str, lang: str = "en") -> None:
        """Log info message."""
        if lang == "zh":
            # For Chinese messages, we might want to handle them differently
            # but for now, we just log them normally
            self.logger.info(message)
        else:
            self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)


def performance_monitor(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to monitor function execution time."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        log_info(f"Starting {func.__name__}...")
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        log_info(f"Finished {func.__name__} in {execution_time:.2f} seconds")
        return result

    return wrapper
