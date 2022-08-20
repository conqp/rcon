"""Synchronous client."""

from socket import SOCK_STREAM

from rcon.client import BaseClient
from rcon.exceptions import SessionTimeout, WrongPassword
from rcon.source.proto import Packet, Type


__all__ = ['Client']


class Client(BaseClient, socket_type=SOCK_STREAM):
    """An RCON client."""

    _frag_detect: str | None = None

    def __init_subclass__(
            cls,
            *args,
            frag_detect: str | None = None,
            **kwargs
    ):
        """Set an optional fragmentation command
        in order to detect fragmented packets.

        This packet should produce a response, which is
        guaranteed to not be fragmented by the server.

        For details see: https://wiki.vg/RCON#Fragmentation
        """
        super().__init_subclass__(*args, **kwargs)

        if frag_detect is not None:
            cls._frag_detect = frag_detect

    def communicate(self, packet: Packet) -> Packet:
        """Send and receive a packet."""
        with self._socket.makefile('wb') as file:
            file.write(bytes(packet))

        if self._frag_detect is not None:
            with self._socket.makefile('wb') as file:
                file.write(bytes(Packet.make_command(self._frag_detect)))

        return self.read()

    def read(self) -> Packet:
        """Read a packet."""
        with self._socket.makefile('rb') as file:
            packet = Packet.read(file)

            if self._frag_detect is not None:
                while (successor := Packet.read(file)).id == packet.id:
                    packet += successor

        return packet

    def login(self, passwd: str, *, encoding: str = 'utf-8') -> bool:
        """Perform a login."""
        request = Packet.make_login(passwd, encoding=encoding)
        response = self.communicate(request)

        # Wait for SERVERDATA_AUTH_RESPONSE according to:
        # https://developer.valvesoftware.com/wiki/Source_RCON_Protocol
        while response.type != Type.SERVERDATA_AUTH_RESPONSE:
            response = self.read()

        if response.id == -1:
            raise WrongPassword()

        return True

    def run(self, command: str, *args: str, encoding: str = 'utf-8') -> str:
        """Run a command."""
        request = Packet.make_command(command, *args, encoding=encoding)
        response = self.communicate(request)

        if response.id != request.id:
            raise SessionTimeout()

        return response.payload.decode(encoding)
