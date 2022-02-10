"""Common errors handler."""

from logging import Logger
from socket import timeout

from rcon.exceptions import ConfigReadError
from rcon.exceptions import RequestIdMismatch
from rcon.exceptions import UserAbort
from rcon.exceptions import WrongPassword


__all__ = ['ErrorHandler']


ERRORS = {
    UserAbort: 1,
    ConfigReadError: 2,
    ConnectionRefusedError: 3,
    (TimeoutError, timeout): 4,
    WrongPassword: 5,
    RequestIdMismatch: 6
}


class ErrorHandler:
    """Handles common errors and exits."""

    __slots__ = ('logger', 'exit_code')

    def __init__(self, logger: Logger):
        """Sets the logger."""
        self.logger = logger
        self.exit_code = 0

    def __enter__(self):
        return self

    def __exit__(self, _, value: Exception, __):
        """Checks for connection errors and exits respectively."""
        for typ, exit_code in ERRORS.items():
            if isinstance(value, typ):
                self.exit_code = exit_code
                return True

        return None
