"""Asynchronous RCON."""

from asyncio import StreamReader, StreamWriter, open_connection

from rcon.exceptions import SessionTimeout, WrongPassword
from rcon.source.proto import Packet, Type


__all__ = ["Rcon"]


class Rcon:
    """
    Set's the variables needed for RCON connection
    """
    def __init__(self,
                 host: str,
                 port: int = 27015,
                 password: str = ''
                 ):

        self.host = host
        self.port = port
        self.password = password

    async def close(self, writer: StreamWriter) -> None:
        """Close socket asynchronously."""

        writer.close()
        await writer.wait_closed()

    async def communicate(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        packet: Packet,
        *,
        frag_threshold: int = 4096,
        frag_detect_cmd: str = "",
    ) -> Packet:
        """Make an asynchronous request."""

        writer.write(bytes(packet))
        await writer.drain()
        response = await Packet.aread(reader)

        if len(response.payload) < frag_threshold:
            return response

        writer.write(bytes(Packet.make_command(frag_detect_cmd)))
        await writer.drain()

        while (successor := await Packet.aread(reader)).id == response.id:
            response += successor

        return response

    async def rcon(
        self,
        command: str,
        *arguments: str,
        host: str = None,
        port: int = None,
        passwd: str = None,
        encoding: str = "utf-8",
        frag_threshold: int = 4096,
        frag_detect_cmd: str = "",
    ) -> str:
        """Run a command asynchronously."""
        try:
            host = host or self.host
            port = port or self.port
            passwd = passwd or self.password
        except AttributeError:
            return print("Make sure you declare the host, port, or password.")

        reader, writer = await open_connection(host, port)
        response = await self.communicate(
            reader,
            writer,
            Packet.make_login(passwd, encoding=encoding),
            frag_threshold=frag_threshold,
            frag_detect_cmd=frag_detect_cmd,
        )

        # Wait for SERVERDATA_AUTH_RESPONSE according to:
        # https://developer.valvesoftware.com/wiki/Source_RCON_Protocol
        while response.type != Type.SERVERDATA_AUTH_RESPONSE:
            response = await Packet.aread(reader)

        if response.id == -1:
            await self.close(writer)
            raise WrongPassword()

        request = Packet.make_command(command, *arguments, encoding=encoding)
        response = await self.communicate(reader, writer, request)
        await self.close(writer)

        if response.id != request.id:
            raise SessionTimeout()

        return response.payload.decode(encoding)
