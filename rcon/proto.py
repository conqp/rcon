"""Low-level protocol stuff."""

from __future__ import annotations
from enum import Enum
from logging import getLogger
from random import randint
from socket import SOCK_STREAM, socket
from typing import IO, NamedTuple, Optional


__all__ = [
    'LittleEndianSignedInt32',
    'Type',
    'Packet',
    'Client',
    'random_request_id'
]


LOGGER = getLogger(__file__)
TERMINATOR = '\x00\x00'


def random_request_id() -> LittleEndianSignedInt32:
    """Generates a random request ID."""

    return LittleEndianSignedInt32(randint(0, LittleEndianSignedInt32.MAX))


class LittleEndianSignedInt32(int):
    """A little-endian, signed int32."""

    MIN = -2_147_483_648
    MAX = 2_147_483_647

    def __init__(self, *_):
        """Checks the boundaries."""
        super().__init__()

        if not self.MIN <= self <= self.MAX:
            raise ValueError('Signed int32 out of bounds:', int(self))

    def __bytes__(self):
        """Returns the integer as signed little endian."""
        return self.to_bytes(4, 'little', signed=True)

    @classmethod
    def read(cls, file: IO) -> LittleEndianSignedInt32:
        """Creates the integer from the given bytes."""
        return super().from_bytes(file.read(4), 'little', signed=True)


class Type(Enum):
    """RCON packet types."""

    SERVERDATA_AUTH = LittleEndianSignedInt32(3)
    SERVERDATA_AUTH_RESPONSE = LittleEndianSignedInt32(2)
    SERVERDATA_EXECCOMMAND = LittleEndianSignedInt32(2)
    SERVERDATA_RESPONSE_VALUE = LittleEndianSignedInt32(0)

    def __int__(self):
        """Returns the actual integer value."""
        return int(self.value)

    def __bytes__(self):
        """Returns the integer value as little endian."""
        return bytes(self.value)

    @classmethod
    def read(cls, file: IO) -> Type:
        """Creates a type from the given bytes."""
        return cls(LittleEndianSignedInt32.read(file))


class Packet(NamedTuple):
    """An RCON packet."""

    id: LittleEndianSignedInt32
    type: Type
    payload: str
    terminator: str = TERMINATOR

    def __bytes__(self):
        """Returns the packet as bytes with prepended length."""
        payload = bytes(self.id)
        payload += bytes(self.type)
        payload += self.payload.encode()
        payload += self.terminator.encode()
        size = bytes(LittleEndianSignedInt32(len(payload)))
        return size + payload

    @classmethod
    def read(cls, file: IO) -> Packet:
        """Reads a packet from a file-like object."""
        size = LittleEndianSignedInt32.read(file)
        id_ = LittleEndianSignedInt32.read(file)
        type_ = Type.read(file)
        payload = file.read(size - 10).decode()
        terminator = file.read(2).decode()

        if terminator != TERMINATOR:
            LOGGER.warning('Unexpected terminator: %s', terminator)

        return cls(id_, type_, payload, terminator)

    @classmethod
    def make_command(cls, *args: str) -> Packet:
        """Creates a command packet."""
        return cls(random_request_id(), Type.SERVERDATA_EXECCOMMAND,
                   ' '.join(args))

    @classmethod
    def make_login(cls, passwd: str) -> Packet:
        """Creates a login packet."""
        return cls(random_request_id(), Type.SERVERDATA_AUTH, passwd)


class Client:
    """An RCON client."""

    __slots__ = ('_socket', 'host', 'port', 'passwd')

    def __init__(self, host: str, port: int, *,
                 timeout: Optional[float] = None,
                 passwd: Optional[str] = None):
        """Initializes the base client with the SOCK_STREAM socket type."""
        self._socket = socket(type=SOCK_STREAM)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.passwd = passwd

    def __enter__(self):
        """Attempts an auto-login if a password is set."""
        self._socket.__enter__()
        self.connect(login=True)
        return self

    def __exit__(self, typ, value, traceback):
        """Delegates to the underlying socket's exit method."""
        return self._socket.__exit__(typ, value, traceback)

    @property
    def timeout(self) -> float:
        """Returns the socket timeout."""
        return self._socket.gettimeout()

    @timeout.setter
    def timeout(self, timeout: float):
        """Sets the socket timeout."""
        self._socket.settimeout(timeout)

    def connect(self, login: bool = False) -> None:
        """Connects the socket and attempts a
        login if wanted and a password is set.
        """
        self._socket.connect((self.host, self.port))

        if login and self.passwd is not None:
            self.login(self.passwd)

    def close(self) -> None:
        """Closes the socket connection."""
        self._socket.close()

    def communicate(self, packet: Packet) -> Packet:
        """Sends and receives a packet."""
        with self._socket.makefile('wb') as file:
            file.write(bytes(packet))

        with self._socket.makefile('rb') as file:
            return Packet.read(file)

    def login(self, passwd: str) -> bool:
        """Performs a login."""
        response = self.communicate(Packet.make_login(passwd))

        if response.id == -1:
            raise RuntimeError('Wrong password.')

        return True

    def run(self, command: str, *arguments: str, raw: bool = False) -> str:
        """Runs a command."""
        request = Packet.make_command(command, *arguments)
        response = self.communicate(request)

        if response.id != request.id:
            if self.passwd is not None:
                if self.login(self.passwd):
                    return self.run(command, *arguments)

            raise RuntimeError('Request ID mismatch.')

        return response if raw else response.payload
