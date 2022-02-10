"""Common errors handler."""

from logging import Logger
from socket import timeout

from rcon.exceptions import ConfigReadError, RequestIdMismatch, WrongPassword


__all__ = ['ErrorHandler']


class ErrorHandler:
    """Handles common errors and exits."""

    __slots__ = ('logger', 'exit_code')

    def __init__(self, logger: Logger):
        """Sets the logger."""
        self.logger = logger
        self.exit_code = 0

    def __enter__(self):
        return self

    def __exit__(self, _, value, __):
        """Checks for connection errors and exits respectively."""
        if isinstance(value, ConnectionRefusedError):
            self.logger.error('Connection refused.')
            self.exit_code = 3
        elif isinstance(value, (TimeoutError, timeout)):
            self.logger.error('Connection timed out.')
            self.exit_code = 4
        elif isinstance(value, WrongPassword):
            self.logger.error('Wrong password.')
            self.exit_code = 5
        elif isinstance(value, RequestIdMismatch):
            self.logger.error('Session timed out.')
            self.exit_code = 6
        elif isinstance(value, ConfigReadError):
            self.exit_code = value.exit_code
        else:
            return None

        return True
