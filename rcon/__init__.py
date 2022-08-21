"""RCON client library."""

from typing import Any, Coroutine
from warnings import warn

from rcon.exceptions import EmptyResponse, SessionTimeout, WrongPassword
from rcon.source import rcon as _rcon
from rcon.source import Client as _Client


__all__ = [
    'EmptyResponse',
    'SessionTimeout',
    'WrongPassword',
    'Client',
    'rcon'
]


class Client(_Client):
    """Wrapper for the rcon.source.Client for backwards compatibility."""

    def __init__(self, *args, **kwargs):
        warn(
            'rcon.Client() is deprecated. Use rcon.source.Client() instead.',
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


def rcon(*args, **kwargs) -> Coroutine[Any, Any, str]:
    """Wrapper for rcon.source.rcon() for backwards compatibility."""

    warn(
        'rcon.rcon() is deprecated. Use rcon.source.rcon() instead.',
        DeprecationWarning,
        stacklevel=2
    )
    return _rcon(*args, **kwargs)
