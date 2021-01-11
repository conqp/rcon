"""Common errors handler."""

from logging import Logger
from socket import timeout
from sys import exit    # pylint: disable=W0622

from rcon.exceptions import RequestIdMismatch, WrongPassword


__all__ = ['ErrorHandler']


class ErrorHandler:
    """Handles common errors and exits."""

    __slots__ = ('logger',)

    def __init__(self, logger: Logger):
        """Sets the logger."""
        self.logger = logger

    def __enter__(self):
        return self

    def __exit__(self, _, value, __):
        """Checks for connection errors and exits respectively."""
        if isinstance(value, ConnectionRefusedError):
            self.logger.error('Connection refused.')
            exit(3)

        if isinstance(value, (TimeoutError, timeout)):
            self.logger.error('Connection timed out.')
            exit(4)

        if isinstance(value, WrongPassword):
            self.logger.error('Wrong password.')
            exit(5)

        if isinstance(value, RequestIdMismatch):
            self.logger.error('Session timed out.')
            exit(5)
