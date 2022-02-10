"""RCON exceptions."""

__all__ = [
    'ConfigReadError',
    'RequestIdMismatch',
    'UserAbort',
    'WrongPassword'
]


class ConfigReadError(Exception):
    """Indicates an error while reading the configuration."""


class RequestIdMismatch(Exception):
    """Indicates a mismatch in request IDs."""

    def __init__(self, sent: int, received: int):
        """Sets the IDs that have been sent and received."""
        super().__init__()
        self.sent = sent
        self.received = received


class UserAbort(Exception):
    """Indicates that a required action has been aborted by the user."""


class WrongPassword(Exception):
    """Indicates a wrong password."""
