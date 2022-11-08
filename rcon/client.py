"""Common base client."""

from socket import SocketKind, socket


__all__ = ['BaseClient']


class BaseClient:
    """A common RCON client."""

    def __init__(
            self, host: str, port: int, *,
            timeout: float | None = None,
            passwd: str | None = None
    ):
        """Initialize the base client."""
        self._socket = socket(type=self._socket_type)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.passwd = passwd

    def __init_subclass__(cls, *, socket_type: SocketKind | None = None):
        if socket_type is not None:
            cls._socket_type = socket_type

    def __enter__(self):
        """Attempt an auto-login if a password is set."""
        self._socket.__enter__()
        self.connect(login=True)
        return self

    def __exit__(self, typ, value, traceback):
        """Delegate to the underlying socket's exit method."""
        return self._socket.__exit__(typ, value, traceback)

    @property
    def timeout(self) -> float:
        """Return the socket timeout."""
        return self._socket.gettimeout()

    @timeout.setter
    def timeout(self, timeout: float):
        """Set the socket timeout."""
        self._socket.settimeout(timeout)

    def connect(self, login: bool = False) -> None:
        """Connect the socket and attempt a
        login if wanted and a password is set.
        """
        self._socket.connect((self.host, self.port))

        if login and self.passwd is not None:
            self.login(self.passwd)

    def close(self) -> None:
        """Close the socket connection."""
        self._socket.close()

    def login(self, passwd: str) -> bool:
        """Perform a login."""
        raise NotImplementedError()

    def run(self, command: str, *args: str) -> str:
        """Run a command."""
        raise NotImplementedError()
