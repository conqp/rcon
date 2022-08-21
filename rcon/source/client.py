"""Synchronous client."""

from socket import SOCK_STREAM

from rcon.client import BaseClient
from rcon.exceptions import SessionTimeout, WrongPassword
from rcon.source.proto import Packet, Type


__all__ = ['Client']


class Client(BaseClient, socket_type=SOCK_STREAM):
    """An RCON client."""

    def __init__(
            self,
            *args,
            frag_threshold: int = 4096,
            frag_detect_cmd: str = '',
            **kwargs
    ):
        """Set an optional fragmentation threshold and
        command in order to detect fragmented packets.

        For details see: https://wiki.vg/RCON#Fragmentation
        """
        super().__init__(*args, **kwargs)
        self.frag_threshold = frag_threshold
        self.frag_detect_cmd = frag_detect_cmd

    def communicate(self, packet: Packet) -> Packet:
        """Send and receive a packet."""
        self.send(packet)
        return self.read()

    def send(self, packet: Packet) -> None:
        """Send a packet to the server."""
        with self._socket.makefile('wb') as file:
            file.write(bytes(packet))

    def read(self) -> Packet:
        """Read a packet from the server."""
        with self._socket.makefile('rb') as file:
            response = Packet.read(file)

            if len(response.payload) < self.frag_threshold:
                return response

            self.send(Packet.make_command(self.frag_detect_cmd))

            while (successor := Packet.read(file)).id == response.id:
                response += successor

        return response

    def login(self, passwd: str, *, encoding: str = 'utf-8') -> bool:
        """Perform a login."""
        self.send(Packet.make_login(passwd, encoding=encoding))

        # Wait for SERVERDATA_AUTH_RESPONSE according to:
        # https://developer.valvesoftware.com/wiki/Source_RCON_Protocol
        while (response := self.read()).type != Type.SERVERDATA_AUTH_RESPONSE:
            pass

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
