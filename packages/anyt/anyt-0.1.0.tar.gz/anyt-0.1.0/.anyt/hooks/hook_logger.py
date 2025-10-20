#!/usr/bin/env python3
"""
Shared logging utility for Claude Code hooks.
Provides centralized logging functionality for all hook scripts.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

# Define paths
PROJECT_ROOT = Path("/Users/bsheng/work/AnyTaskBackend")
LOGS_DIR = PROJECT_ROOT / ".anyt" / "hooks" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class HookLogger:
    """Logger for Claude Code hooks with structured logging."""

    def __init__(self, hook_name: str):
        """Initialize logger for a specific hook.

        Args:
            hook_name: Name of the hook (e.g., 'UserPromptSubmit', 'Notification')
        """
        self.hook_name = hook_name
        self.log_file = LOGS_DIR / f"{hook_name.lower()}.log"
        self.all_events_log = LOGS_DIR / "all_events.log"

        # Setup logging
        self._setup_logger()

    def _setup_logger(self):
        """Setup logging configuration."""
        # Create logger
        self.logger = logging.getLogger(f"hook.{self.hook_name}")
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # File handler for specific hook
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)

        # File handler for all events
        all_events_handler = logging.FileHandler(self.all_events_log)
        all_events_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        all_events_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(all_events_handler)

    def log_event(self, event_data: Dict[str, Any], level: str = "info"):
        """Log a hook event with structured data.

        Args:
            event_data: Dictionary containing event data
            level: Log level (debug, info, warning, error)
        """
        log_func = getattr(self.logger, level.lower(), self.logger.info)

        # Create structured log message
        message = f"Event: {self.hook_name}"
        if event_data:
            message += f" | Data: {json.dumps(event_data, indent=None)}"

        log_func(message)

    def log_hook_input(self, hook_input: Dict[str, Any]):
        """Log the input received by the hook.

        Args:
            hook_input: The input data received by the hook
        """
        self.logger.info(f"Hook input received: {json.dumps(hook_input, indent=2)}")

    def log_hook_output(self, output: Dict[str, Any]):
        """Log the output returned by the hook.

        Args:
            output: The output data returned by the hook
        """
        self.logger.info(f"Hook output: {json.dumps(output, indent=2)}")

    def log_error(self, error_msg: str, exception: Exception = None):
        """Log an error that occurred during hook execution.

        Args:
            error_msg: Error message
            exception: Optional exception object
        """
        if exception:
            self.logger.error(f"{error_msg}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(error_msg)

    def debug(self, msg: str):
        """Log debug message."""
        self.logger.debug(msg)

    def info(self, msg: str):
        """Log info message."""
        self.logger.info(msg)

    def warning(self, msg: str):
        """Log warning message."""
        self.logger.warning(msg)

    def error(self, msg: str):
        """Log error message."""
        self.logger.error(msg)


def get_logger(hook_name: str) -> HookLogger:
    """Get a logger instance for a specific hook.

    Args:
        hook_name: Name of the hook

    Returns:
        HookLogger instance
    """
    return HookLogger(hook_name)
