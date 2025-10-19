"""
Logging functionality.

This module provides a singleton logger with:
- Colored console output with relative timestamps
- Optional file logging with absolute timestamps
- Thread-safe initialization
- Module-level access through a proxy object
"""

from __future__ import annotations

import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lithi.core.core import singleton


def get_utc_timestamp() -> str:
    """Generate UTC timestamp string for log filenames (safe for all OS)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


class ColoredFormatter(logging.Formatter):
    """
    A custom formatter for adding colors to log messages.

    This formatter adds:
    - Color codes based on log level (DEBUG=cyan, INFO=green, etc.)
    - Relative timestamps (seconds since program start)
    - Reset codes to return terminal to normal colors
    """

    # Reference start time for calculating relative timestamps
    _start_time = time.monotonic()

    COLORS: dict[str, str] = {
        "RESET": "\u001b[0m",
        "DEBUG": "\u001b[0;36m",  # Cyan
        "INFO": "\u001b[0;32m",  # Green
        "WARNING": "\u001b[0;33m",  # Yellow
        "ERROR": "\u001b[0;31m",  # Red
        "CRITICAL": "\u001b[1;31m",  # Bold Red
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the object."""
        super().__init__(*args, **kwargs)
        # Detect non-TTY to disable colors automatically
        self.enable_colors = sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """
        Override the format method to add color codes to the log messages.

        Adds these custom fields to the log record:
        - rel_secs: relative time since program start (e.g., "12.3456s")
        - color: ANSI color code for the log level
        - reset: ANSI reset code to return to normal colors
        """
        # Total width 10 including 's', right-aligned for neat columns
        record.rel_secs = (
            f"{time.monotonic() - ColoredFormatter._start_time:.4f}s".rjust(10)
        )
        if self.enable_colors:
            record.color = self.COLORS.get(record.levelname, "")
            record.reset = self.COLORS["RESET"]
        else:
            record.color = ""
            record.reset = ""
        return super().format(record)


@singleton
class Logger(logging.Logger):
    """
    Custom logger class implementing the Singleton pattern.

    Why singleton? We want one consistent logger throughout the entire
    application that maintains the same configuration
    (handlers, formatters, etc.) regardless of where it's accessed from.

    The logger provides:
    - Console output: Colored, with relative timestamps
    - File output: Plain text, with absolute timestamps (optional)
    """

    def __init__(
        self,
        name: str = __name__,
        level: int = logging.NOTSET,
        directory: Path | None = None,
    ) -> None:
        """
        Initialize the Logger with console and optional file handlers.

        Args:
            name: Logger name (appears in log messages)
            level: Minimum log level to display on console
            directory: Optional directory path for log file output
        """
        # Initialize the parent Logger class
        # Set logger to DEBUG so all messages reach handlers
        # Individual handlers will filter at their own levels
        super().__init__(name, logging.DEBUG)

        # Only add handlers if none exist (prevents duplicate handlers)
        if not self.handlers:
            # Console handler
            # Shows colored output in terminal/console with relative
            # timestamps
            self.c_handler = logging.StreamHandler()
            self.c_handler.setLevel(
                level
            )  # Console respects the level setting
            c_format = ColoredFormatter(
                "[%(color)s%(levelname)-8s%(reset)s]: %(rel_secs)s "
                "%(filename)20s:%(lineno)d - "
                "%(message)s"
            )
            self.c_handler.setFormatter(c_format)
            self.addHandler(self.c_handler)

            # Build file path if directory is provided
            log_filepath = None
            if directory is not None:
                if isinstance(directory, Path):
                    filename = f"{name}_{get_utc_timestamp()}.log"
                    log_filepath = directory / filename
                else:
                    raise TypeError(
                        f"directory must be Path or None, got "
                        f"{type(directory).__name__} ({directory})"
                    )

            # File handler (optional)
            # Saves plain text logs to file with absolute timestamps
            if log_filepath:
                # Create log directory if it doesn't exist
                log_filepath.parent.mkdir(parents=True, exist_ok=True)

                self.f_handler = logging.FileHandler(
                    log_filepath, encoding="utf-8"
                )
                self.f_handler.setLevel(
                    logging.NOTSET
                )  # File gets ALL log levels
                f_format = logging.Formatter(
                    "[%(levelname)-8s]: %(asctime)s "
                    "%(filename)20s:%(lineno)d | "
                    "%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                self.f_handler.setFormatter(f_format)
                self.addHandler(self.f_handler)

    def setLevel(self, level: int | str) -> None:
        """
        Override setLevel to only update the console handler level.

        The logger itself stays at a low level to ensure all messages reach
        handlers.
        Only the console handler level is changed to control console output.
        The file handler always receives all log levels.
        """
        # Don't change the logger's own level

        # Only update the console handler level
        if hasattr(self, "c_handler"):
            self.c_handler.setLevel(level)

    @classmethod
    def get(cls, *args: Any, **kwargs: Any) -> Logger:
        """Stub method - will be replaced by singleton decorator."""
        raise NotImplementedError(
            "This method is replaced by the singleton decorator"
        )


# === PROXY PATTERN FOR MODULE-LEVEL ACCESS ===
class _GlobalLoggerProxy:
    """
    Proxy object that forwards all method calls to the singleton Logger.

    Why use a proxy?
    - Allows modules to import 'logger' and use it like logger.info("message")
    - Handles the case where logger isn't initialized yet with a helpful error
    - Provides a clean, simple interface: just import and use

    How it works:
    - Any attribute access (like logger.info) gets forwarded to
      Logger.getLogger()
    - If logger isn't initialized yet, provides a helpful error message
    """

    # pylint: disable=too-few-public-methods
    def __getattr__(self, attr: str) -> Any:
        """
        Forward all attribute access to the singleton Logger instance.

        This magic method is called whenever someone tries to access an
        attribute that doesn't exist on this proxy object
        (like logger.info, logger.debug, etc.)
        """
        try:
            return getattr(Logger.get(), attr)
        except ValueError as e:
            raise RuntimeError(
                "Logger not initialized. "
                "Call Logger(name='your_logger_name') first."
            ) from e


# === MODULE-LEVEL INTERFACE ===
# This is what other modules import and use
# Usage: from your_module import logger; logger.info("Hello!")
logger = _GlobalLoggerProxy()
