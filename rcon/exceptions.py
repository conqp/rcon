"""RCON exceptions."""

__all__ = ['ConfigReadError', 'RequestIdMismatch', 'WrongPassword']


class ConfigReadError(Exception):
    """Indicates an error while reading the configuration."""

    def __init__(self, exit_code: int):
        super().__init__()
        self.exit_code = exit_code


class RequestIdMismatch(Exception):
    """Indicates a mismatch in request IDs."""

    def __init__(self, sent: int, received: int):
        """Sets the sent and received IDs."""
        super().__init__()
        self.sent = sent
        self.received = received


class WrongPassword(Exception):
    """Indicates a wrong password."""
