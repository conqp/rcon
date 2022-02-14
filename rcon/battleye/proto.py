"""Low-level protocol stuff."""

from typing import NamedTuple, Union
from zlib import crc32


__all__ = [
    'RESPONSE_TYPES',
    'Header',
    'LoginRequest',
    'LoginResponse',
    'Command',
    'CommandResponse',
    'ServerMessage',
    'Request',
    'Response'
]


PREFIX = 'BE'
SUFFIX = 0xff


class Header(NamedTuple):
    """Packet header."""

    prefix: str
    crc32: int
    suffix: int

    def __bytes__(self):
        return b''.join((
            self.prefix.encode('ascii'),
            self.crc32.to_bytes(4, 'little'),
            self.suffix.to_bytes(1, 'little')
        ))

    @classmethod
    def from_payload(cls, payload: bytes):
        """Creates a header for the given payload."""
        return cls(
            PREFIX,
            crc32(SUFFIX.to_bytes(1, 'little') + payload),
            SUFFIX
        )

    @classmethod
    def from_bytes(cls, payload: bytes):
        """Creates a header from the given bytes."""
        return cls(
            payload[:2].decode('ascii'),
            int.from_bytes(payload[2:5], 'little'),
            int.from_bytes(payload[5:6], 'little')
        )


class LoginRequest(NamedTuple):
    """Login request packet."""

    type: int
    passwd: str

    def __bytes__(self):
        return bytes(self.header) + self.payload

    @property
    def payload(self) -> bytes:
        """Returns the payload."""
        return self.type.to_bytes(1, 'little') + self.passwd.encode('ascii')

    @property
    def header(self) -> Header:
        """Returns the appropriate header."""
        return Header.from_payload(self.payload)

    @classmethod
    def from_passwd(cls, passwd: str):
        """Creates a login request with the given password."""
        return cls(0x00, passwd)


class LoginResponse(NamedTuple):
    """A login response."""

    header: Header
    type: int
    success: bool

    @classmethod
    def from_bytes(cls, header: Header, payload: bytes):
        """Creates a login response from the given bytes."""
        return cls(
            header,
            int.from_bytes(payload[:1], 'little'),
            bool(int.from_bytes(payload[2:3], 'little'))
        )


class Command(NamedTuple):
    """Command packet."""

    type: int
    seq: int
    command: str

    def __bytes__(self):
        return bytes(self.header) + self.payload

    @property
    def payload(self) -> bytes:
        """Returns the payload."""
        return b''.join((
            self.type.to_bytes(1, 'little'),
            self.seq.to_bytes(1, 'little'),
            self.command.encode('ascii')
        ))

    @property
    def header(self) -> Header:
        """Returns the appropriate header."""
        return Header.from_payload(self.payload)

    @classmethod
    def from_string(cls, command: str):
        """Creates a command packet from the given string."""
        return cls(0x01, 0x00, command)

    @classmethod
    def from_command(cls, command: str, *args: str):
        """Creates a command packet from the command and arguments."""
        return cls.from_string(' '.join([command, *args]))


class CommandResponse(NamedTuple):
    """A command response."""

    header: Header
    type: int
    seq: int
    payload: bytes

    @classmethod
    def from_bytes(cls, header: Header, payload: bytes):
        """Creates a command response from the given bytes."""
        return cls(
            header,
            int.from_bytes(payload[:1], 'little'),
            int.from_bytes(payload[1:2], 'little'),
            payload[2:]
        )

    @property
    def message(self) -> str:
        """Returns the text message."""
        return self.payload.decode('ascii')


class ServerMessage(NamedTuple):
    """A message from the server."""

    header: Header
    type: int
    seq: int
    payload: bytes

    @classmethod
    def from_bytes(cls, header: Header, payload: bytes):
        """Creates a server message from the given bytes."""
        return cls(
            header,
            int.from_bytes(payload[:1], 'little'),
            int.from_bytes(payload[1:2], 'little'),
            payload[2:]
        )

    @property
    def message(self) -> str:
        """Returns the text message."""
        return self.payload.decode('ascii')


Request = Union[LoginRequest, Command]
Response = Union[LoginResponse, CommandResponse, ServerMessage]

RESPONSE_TYPES = {
    0x00: LoginResponse,
    0x01: CommandResponse,
    0x02: ServerMessage
}
