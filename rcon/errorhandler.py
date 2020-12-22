"""Common errors handler."""

from logging import Logger
from sys import exit    # pylint: disable=W0622
from typing import Iterable, Tuple


__all__ = ['ErrorHandler']


ErrorMap = Iterable[Tuple[Exception, str, int]]


class ErrorHandler:
    """Handles common errors and exits."""

    __slots__ = ('errors', 'logger')

    def __init__(self, errors: ErrorMap, logger: Logger):
        """Sets the logger."""
        self.errors = errors
        self.logger = logger

    def __enter__(self):
        return self

    def __exit__(self, typ, value, _):
        """Checks for connection errors and exits respectively."""
        for error, message, returncode in self.errors:
            if typ is error or isinstance(value, error):
                self.logger.error(message)
                exit(returncode)
