"""Wrapper for readline support."""

from logging import Logger
from pathlib import Path

try:
    from readline import read_history_file, write_history_file
except ModuleNotFoundError:
    read_history_file = write_history_file = lambda _: None


__all__ = ["CommandHistory"]


HIST_FILE = Path.home() / ".rconshell_history"


class CommandHistory:
    """Context manager for the command line history."""

    def __init__(self, logger: Logger, file: Path = HIST_FILE):
        """Set the logger to use."""
        self.logger = logger
        self.file = file

    def __enter__(self):
        """Load the history file."""
        try:
            read_history_file(self.file)
        except FileNotFoundError:
            self.logger.warning("Could not find history file: %s", self.file)
        except PermissionError:
            self.logger.error("Insufficient permissions to read: %s", self.file)

        return self

    def __exit__(self, *_):
        """Write to the history file."""
        try:
            write_history_file(self.file)
        except PermissionError:
            self.logger.error("Insufficient permissions to write: %s", self.file)
