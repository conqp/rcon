"""Wrapper for readline support."""

from os import name
from pathlib import Path


__all__ = ['CommandHistory']


HIST_FILE = Path.home().joinpath('.rconshell_history')


if name == 'posix':
    from readline import read_history_file, write_history_file

    class CommandHistory:
        """Context manager for the command line history."""

        def __enter__(self):
            read_history_file()
            return self

        def __exit__(self, *_):
            write_history_file(HIST_FILE)
else:
    class CommandHistory:
        """Context manager for the command line history."""

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass
