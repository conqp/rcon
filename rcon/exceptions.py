"""RCON exceptions."""

__all__ = ['RequestIdMismatch', 'WrongPassword']


class RequestIdMismatch(Exception):
    """Indicates a mismatch in request IDs."""

    def __init__(self, sent: int, received: int):
        """Sets the sent and received IDs."""
        super().__init__()
        self.sent = sent
        self.received = received


class WrongPassword(Exception):
    """Indicates a wrong password."""
