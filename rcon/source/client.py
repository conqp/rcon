"""Synchronous client."""

from socket import SOCK_STREAM

from rcon.client import BaseClient
from rcon.exceptions import SessionTimeout, WrongPassword
from rcon.source.proto import Packet, Type


__all__ = ['Client']


class Client(BaseClient, socket_type=SOCK_STREAM):
    """An RCON client."""

    def __init_subclass__(
            cls,
            *args,
            frag_threshold: int = 4096,
            frag_detect_cmd: str = '',
            **kwargs
    ):
        """Set an optional fragmentation command
        in order to detect fragmented packets.

        This packet should produce a response, which is
        guaranteed to not be fragmented by the server.

        For details see: https://wiki.vg/RCON#Fragmentation
        """
        super().__init_subclass__(*args, **kwargs)
        cls.frag_threshold = frag_threshold
        cls.frag_detect_cmd = frag_detect_cmd

    def communicate(self, packet: Packet) -> Packet:
        """Send and receive a packet."""
        self.send(packet)

        if len((response := self.read()).payload) < self.frag_threshold:
            return response

        self.send(Packet.make_command(self.frag_detect_cmd))

        while (successor := self.read()).id == response.id:
            response += successor

        return response

    def send(self, packet: Packet) -> None:
        """Send a packet to the server."""
        with self._socket.makefile('wb') as file:
            file.write(bytes(packet))

    def read(self) -> Packet:
        """Read a packet from the server."""
        with self._socket.makefile('rb') as file:
            return Packet.read(file)

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
