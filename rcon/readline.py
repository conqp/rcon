"""Wrapper for readline support."""

from logging import Logger
from os import name
from pathlib import Path


__all__ = ['CommandHistory']


HIST_FILE = Path.home().joinpath('.rconshell_history')


if name == 'posix':
    from readline import read_history_file, write_history_file

    class CommandHistory:
        """Context manager for the command line history."""

        def __init__(self, logger: Logger):
            self.logger = logger

        def __enter__(self):
            try:
                read_history_file(HIST_FILE)
            except FileNotFoundError:
                self.logger.warning('Could not find history file: %s',
                                    HIST_FILE)
            except PermissionError:
                self.logger.error('Insufficient permissions to read: %s',
                                  HIST_FILE)

            return self

        def __exit__(self, *_):
            try:
                write_history_file(HIST_FILE)
            except PermissionError:
                self.logger.error('Insufficient permissions to write: %s',
                                  HIST_FILE)
else:
    class CommandHistory:
        """Context manager mockup for non-posix systems."""

        def __init__(self, logger: Logger):
            logger.warning('Command line history unavailable on this system.')

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass
