"""RCON client library."""

from warnings import warn

from rcon.source import rcon as _rcon
from rcon.source import Client as _Client


class Client(_Client):
    """Backwards compatibility."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warn(
            'rcon.Client() is deprecated. Use rcon.source.Client() instead.',
            DeprecationWarning
        )


async def rcon(*args, **kwargs) -> str:
    """Backwards compatibility."""

    warn(
        'rcon.rcon() is deprecated. Use rcon.source.rcon() instead.',
        DeprecationWarning
    )
    return await _rcon(*args, **kwargs)
