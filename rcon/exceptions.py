"""RCON exceptions."""


__all__ = ['InvalidConfig', 'RequestIdMismatch', 'WrongPassword']


class InvalidConfig(ValueError):
    """Indicates invalid credentials."""


class RequestIdMismatch(Exception):
    """Indicates that the sent and received request IDs do not match."""

    def __init__(self, sent: int, received: int):
        """Sets the sent and received request IDs."""
        super().__init__(sent, received)
        self.sent = sent
        self.received = received


class WrongPassword(Exception):
    """Indicates a wrong RCON password."""
