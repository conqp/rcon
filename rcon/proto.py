"""Low-level protocol stuff."""

from __future__ import annotations
from enum import Enum
from logging import getLogger
from random import randint
from socket import SOCK_STREAM, socket
from typing import NamedTuple

from rcon.exceptions import RequestIdMismatch
from rcon.exceptions import WrongPassword


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
            raise ValueError('Signed int32 out of bounds:', self)

    def __bytes__(self):
        """Returns the integer as signed little endian."""
        return self.to_bytes(4, 'little', signed=True)

    @classmethod
    def from_bytes(cls, bytes_: bytes) -> LittleEndianSignedInt32:
        """Creates the integer from the given bytes."""
        return super().from_bytes(bytes_, 'little', signed=True)


class Type(Enum):
    """Available packet types."""

    LOGIN = 3
    COMMAND = 2
    RESPONSE = 0

    def __int__(self):
        """Returns the actual integer value."""
        return self.value

    def __bytes__(self):
        """Returns the integer value as little endian."""
        return int(self).to_bytes(4, 'little', signed=True)

    @classmethod
    def from_bytes(cls, bytes_: bytes) -> Type:
        """Creates a type from the given bytes."""
        return cls(int.from_bytes(bytes_, 'little', signed=True))


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
        size = len(payload).to_bytes(4, 'little', signed=True)
        return size + payload

    @classmethod
    def from_bytes(cls, bytes_: bytes) -> Packet:
        """Creates a packet from the respective bytes."""
        id_ = LittleEndianSignedInt32.from_bytes(bytes_[:4])
        type_ = Type.from_bytes(bytes_[4:8])
        payload = bytes_[8:-2].decode()

        if (terminator := bytes_[-2:].decode()) != TERMINATOR:
            LOGGER.warning('Unexpected terminator: %s', terminator)

        return cls(id_, type_, payload, terminator)

    @classmethod
    def from_args(cls, *args: str) -> Packet:
        """Creates a command packet."""
        return cls(random_request_id(), Type.COMMAND, ' '.join(args))

    @classmethod
    def from_login(cls, passwd: str) -> Packet:
        """Creates a login packet."""
        return cls(random_request_id(), Type.LOGIN, passwd)


class Client:
    """An RCON client."""

    __slots__ = ('_socket', 'host', 'port', 'timeout', 'passwd')

    def __init__(self, host: str, port: int, *, timeout: float = None,
                 passwd: str = None):
        """Initializes the base client with the SOCK_STREAM socket type."""
        self._socket = socket(type=SOCK_STREAM)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.passwd = passwd

    def __enter__(self):
        """Attempts an auto-login if a password is set."""
        self._socket.__enter__()
        self._socket.settimeout(self.timeout)
        self._socket.connect((self.host, self.port))

        if self.passwd is not None:
            self.login(self.passwd)

        return self

    def __exit__(self, typ, value, traceback):
        """Delegates to the underlying socket's exit method."""
        return self._socket.__exit__(typ, value, traceback)

    def communicate(self, packet: Packet) -> Packet:
        """Sends and receives a packet."""
        self._socket.send(bytes(packet))
        header = self._socket.recv(4)
        length = int.from_bytes(header, 'little')
        payload = self._socket.recv(length)
        response = Packet.from_bytes(payload)

        if response.id == packet.id:
            return response

        raise RequestIdMismatch(packet.id, response.id)

    def login(self, passwd: str) -> bool:
        """Performs a login."""
        packet = Packet.from_login(passwd)

        try:
            self.communicate(packet)
        except RequestIdMismatch as mismatch:
            if mismatch.received == -1:
                raise WrongPassword() from None

            raise

        return True

    def run(self, command: str, *arguments: str, raw: bool = False) -> str:
        """Runs a command."""
        packet = Packet.from_args(command, *arguments)

        try:
            response = self.communicate(packet)
        except RequestIdMismatch:
            if self.passwd is not None:  # Re-authenticate and retry command.
                self.login(self.passwd)
                return self.run(command, *arguments)

            raise

        return response if raw else response.payload
