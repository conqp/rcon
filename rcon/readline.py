"""Wrapper for readline support."""

from logging import Logger
from pathlib import Path

try:
    from readline import read_history_file, write_history_file
except ModuleNotFoundError:
    read_history_file = write_history_file = lambda _: None


__all__ = ['CommandHistory']


HIST_FILE = Path.home().joinpath('.rconshell_history')


class CommandHistory:
    """Context manager for the command line history."""

    __slots__ = ('logger',)

    def __init__(self, logger: Logger):
        """Set the logger to use."""
        self.logger = logger

    def __enter__(self):
        """Load the history file."""
        try:
            read_history_file(HIST_FILE)
        except FileNotFoundError:
            self.logger.warning(
                'Could not find history file: %s', HIST_FILE
            )
        except PermissionError:
            self.logger.error(
                'Insufficient permissions to read: %s', HIST_FILE
            )

        return self

    def __exit__(self, *_):
        """Write to the history file."""
        try:
            write_history_file(HIST_FILE)
        except PermissionError:
            self.logger.error(
                'Insufficient permissions to write: %s', HIST_FILE
            )
