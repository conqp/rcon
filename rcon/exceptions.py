"""Common exceptions."""

__all__ = [
    'ConfigReadError',
    'EmptyResponse',
    'SessionTimeout',
    'UserAbort',
    'WrongPassword'
]


class ConfigReadError(Exception):
    """Indicates an error while reading the configuration."""


class EmptyResponse(Exception):
    """Indicates an empty response from the server."""


class SessionTimeout(Exception):
    """Indicates that the session timed out."""


class UserAbort(Exception):
    """Indicates that a required action has been aborted by the user."""


class WrongPassword(Exception):
    """Indicates a wrong password."""
