"""Low-level protocol stuff."""

from __future__ import annotations
from asyncio import StreamReader
from enum import Enum
from functools import partial
from logging import getLogger
from random import randint
from typing import IO, NamedTuple


__all__ = ['LittleEndianSignedInt32', 'Type', 'Packet', 'random_request_id']


LOGGER = getLogger(__file__)
TERMINATOR = b'\x00\x00'


class LittleEndianSignedInt32(int):
    """A little-endian, signed int32."""

    MIN = -2_147_483_648
    MAX = 2_147_483_647

    def __init__(self, *_):
        """Check the boundaries."""
        super().__init__()

        if not self.MIN <= self <= self.MAX:
            raise ValueError('Signed int32 out of bounds:', int(self))

    def __bytes__(self):
        """Return the integer as signed little endian."""
        return self.to_bytes(4, 'little', signed=True)

    @classmethod
    async def aread(cls, reader: StreamReader) -> LittleEndianSignedInt32:
        """Read the integer from an asynchronous file-like object."""
        return cls.from_bytes(await reader.read(4), 'little', signed=True)

    @classmethod
    def read(cls, file: IO) -> LittleEndianSignedInt32:
        """Read the integer from a file-like object."""
        return cls.from_bytes(file.read(4), 'little', signed=True)


class Type(Enum):
    """RCON packet types."""

    SERVERDATA_AUTH = LittleEndianSignedInt32(3)
    SERVERDATA_AUTH_RESPONSE = LittleEndianSignedInt32(2)
    SERVERDATA_EXECCOMMAND = LittleEndianSignedInt32(2)
    SERVERDATA_RESPONSE_VALUE = LittleEndianSignedInt32(0)

    def __int__(self):
        """Return the actual integer value."""
        return int(self.value)

    def __bytes__(self):
        """Return the integer value as little endian."""
        return bytes(self.value)

    @classmethod
    async def aread(cls, reader: StreamReader) -> Type:
        """Read the type from an asynchronous file-like object."""
        return cls(await LittleEndianSignedInt32.aread(reader))

    @classmethod
    def read(cls, file: IO) -> Type:
        """Read the type from a file-like object."""
        return cls(LittleEndianSignedInt32.read(file))


class Packet(NamedTuple):
    """An RCON packet."""

    id: LittleEndianSignedInt32
    type: Type
    payload: bytes
    terminator: bytes = TERMINATOR

    def __add__(self, other: Packet | None):
        if other is None:
            return self

        return Packet(
            self.id,
            self.type,
            self.payload + other.payload,
            self.terminator
        )

    def __radd__(self, other: Packet):
        return other.__add__(self)

    def __bytes__(self):
        """Return the packet as bytes with prepended length."""
        payload = bytes(self.id)
        payload += bytes(self.type)
        payload += self.payload
        payload += self.terminator
        size = bytes(LittleEndianSignedInt32(len(payload)))
        return size + payload

    @classmethod
    async def aread(cls, reader: StreamReader) -> Packet:
        """Read a packet from an asynchronous file-like object."""
        size = await LittleEndianSignedInt32.aread(reader)
        id_ = await LittleEndianSignedInt32.aread(reader)
        type_ = await Type.aread(reader)
        payload = await reader.read(size - 10)
        terminator = await reader.read(2)

        if terminator != TERMINATOR:
            LOGGER.warning('Unexpected terminator: %s', terminator)

        return cls(id_, type_, payload, terminator)

    @classmethod
    def read(cls, file: IO) -> Packet:
        """Read a packet from a file-like object."""
        size = LittleEndianSignedInt32.read(file)
        id_ = LittleEndianSignedInt32.read(file)
        type_ = Type.read(file)
        payload = file.read(size - 10)
        terminator = file.read(2)

        if terminator != TERMINATOR:
            LOGGER.warning('Unexpected terminator: %s', terminator)

        return cls(id_, type_, payload, terminator)

    @classmethod
    def make_command(cls, *args: str, encoding: str = 'utf-8') -> Packet:
        """Create a command packet."""
        return cls(
            random_request_id(), Type.SERVERDATA_EXECCOMMAND,
            b' '.join(map(partial(str.encode, encoding=encoding), args))
        )

    @classmethod
    def make_login(cls, passwd: str, *, encoding: str = 'utf-8') -> Packet:
        """Create a login packet."""
        return cls(
            random_request_id(), Type.SERVERDATA_AUTH, passwd.encode(encoding)
        )


def random_request_id() -> LittleEndianSignedInt32:
    """Generate a random request ID."""

    return LittleEndianSignedInt32(randint(0, LittleEndianSignedInt32.MAX))
