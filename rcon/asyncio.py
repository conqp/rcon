"""Asynchronous RCON."""

from asyncio import open_connection
from typing import IO

from rcon.proto import Packet


__all__ = ['rcon']


async def communicate(reader: IO, writer: IO, packet: Packet) -> Packet:
    """Asynchronous requests."""

    writer.write(bytes(packet))
    await writer.drain()
    return await Packet.aread(reader)


async def rcon(command: str, *arguments: str, host: str, port: int,
               passwd: str) -> str:
    """Runs a command asynchronously."""

    reader, writer = await open_connection(host, port)
    login = Packet.make_login(passwd)
    response = await communicate(reader, writer, login)

    if response.id == -1:
        raise RuntimeError('Wrong password.')

    request = Packet.make_command(command, *arguments)
    response = await communicate(reader, writer, request)

    if response.id != request.id:
        raise RuntimeError('Request ID mismatch.')

    return response.payload
