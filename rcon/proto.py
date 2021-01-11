"""Low-level protocol stuff."""

from __future__ import annotations
from enum import Enum
from logging import getLogger
from random import randint
from typing import IO, NamedTuple


__all__ = ['LittleEndianSignedInt32', 'Type', 'Packet', 'random_request_id']


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
    async def aread(cls, file: IO) -> LittleEndianSignedInt32:
        """Reads the integer from an ansynchronous file-like object."""
        return cls.from_bytes(await file.read(4), 'little', signed=True)

    @classmethod
    def read(cls, file: IO) -> LittleEndianSignedInt32:
        """Reads the integer from a file-like object."""
        return cls.from_bytes(file.read(4), 'little', signed=True)


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
    async def aread(cls, file: IO) -> Type:
        """Reads the type from an asynchronous file-like object."""
        return cls(await LittleEndianSignedInt32.aread(file))

    @classmethod
    def read(cls, file: IO) -> Type:
        """Reads the type from a file-like object."""
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
    async def aread(cls, file: IO) -> Packet:
        """Reads a packet from an asynchronous file-like object."""
        size = await LittleEndianSignedInt32.aread(file)
        id_ = await LittleEndianSignedInt32.aread(file)
        type_ = await Type.aread(file)
        payload = await file.read(size - 10)
        terminator = await file.read(2)

        if (terminator := terminator.decode()) != TERMINATOR:
            LOGGER.warning('Unexpected terminator: %s', terminator)

        return cls(id_, type_, payload.decode(), terminator)

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
