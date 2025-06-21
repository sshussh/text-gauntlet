"""Logging utilities and configuration for Text Gauntlet."""

import logging
import logging.handlers
from typing import Optional

from config.settings import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        """Format the log record with colors."""
        # Apply color to log level
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )

        return super().format(record)


class Logger:
    """Custom logger class for Text Gauntlet application."""

    _instance: Optional["Logger"] = None
    _logger: logging.Logger | None = None

    def __new__(cls) -> "Logger":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize logger if not already initialized."""
        if self._logger is None:
            self._setupLogger()

    def _setupLogger(self) -> None:
        """Set up the logger with appropriate handlers and formatters."""
        self._logger = logging.getLogger("TextGauntlet")
        self._logger.setLevel(getattr(logging, settings.logging.level.upper()))

        # Prevent duplicate logging by setting propagate to False
        self._logger.propagate = False

        # Clear existing handlers
        self._logger.handlers.clear()

        # Create colored formatter for console
        console_formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create plain formatter for file (no colors in files)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(getattr(logging, settings.logging.level.upper()))
        consoleHandler.setFormatter(console_formatter)
        self._logger.addHandler(consoleHandler)

        # File handler (if enabled)
        if settings.logging.enableFileLogging:
            logFile = settings.logsPath / "text_gauntlet.log"

            if settings.logging.logRotation:
                fileHandler = logging.handlers.RotatingFileHandler(
                    logFile,
                    maxBytes=settings.logging.maxLogSize,
                    backupCount=settings.logging.backupCount,
                )
            else:
                fileHandler = logging.FileHandler(logFile)

            fileHandler.setLevel(getattr(logging, settings.logging.level.upper()))
            fileHandler.setFormatter(file_formatter)
            self._logger.addHandler(fileHandler)

    @classmethod
    def configure_root_logger(cls) -> None:
        """Configure the root logger to match our custom formatting."""
        root_logger = logging.getLogger()

        # Clear any existing handlers to avoid conflicts
        root_logger.handlers.clear()

        root_logger.setLevel(logging.INFO)

        # Create colored formatter for console
        console_formatter = ColoredFormatter(
            "%(asctime)s - TextGauntlet - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        if self._logger:
            self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        if self._logger:
            self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        if self._logger:
            self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        if self._logger:
            self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        if self._logger:
            self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        if self._logger:
            self._logger.exception(message, *args, **kwargs)


# Global logger instance
logger = Logger()
