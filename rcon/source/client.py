"""Synchronous client."""

from socket import SOCK_STREAM

from rcon.client import BaseClient
from rcon.exceptions import SessionTimeout, WrongPassword
from rcon.source.proto import Packet, Type

__all__ = ["Client"]


class Client(BaseClient, socket_type=SOCK_STREAM):
    """An RCON client."""

    def __init__(self, *args, frag_threshold: int = 4096, **kwargs):
        """Set an optional fragmentation threshold and
        command in order to detect fragmented packets.

        For details see: https://wiki.vg/RCON#Fragmentation
        """
        super().__init__(*args, **kwargs)
        self.frag_threshold = frag_threshold

    def communicate(
        self, packet: Packet, raise_unexpected_terminator: bool = False
    ) -> Packet:
        """Send and receive a packet."""
        self.send(packet)
        return self.read(raise_unexpected_terminator)

    def send(self, packet: Packet) -> None:
        """Send a packet to the server."""
        with self._socket.makefile("wb") as file:
            file.write(bytes(packet))

    def read(self, raise_unexpected_terminator: bool = False) -> Packet:
        """Read a packet from the server."""
        with self._socket.makefile("rb") as file:
            response = Packet.read(file, raise_unexpected_terminator)

            if len(response.payload) < self.frag_threshold:
                return response

            self.send(Packet.make_empty_response())

            while (successor := Packet.read(file)).id == response.id:
                response += successor

        return response

    def login(self, passwd: str, *, encoding: str = "utf-8") -> bool:
        """Perform a login."""
        self.send(Packet.make_login(passwd, encoding=encoding))

        # Wait for SERVERDATA_AUTH_RESPONSE according to:
        # https://developer.valvesoftware.com/wiki/Source_RCON_Protocol
        while (response := self.read()).type != Type.SERVERDATA_AUTH_RESPONSE:
            pass

        if response.id == -1:
            raise WrongPassword()

        return True

    def run(
        self,
        command: str,
        *args: str,
        encoding: str = "utf-8",
        enforce_id: bool = True,
        raise_unexpected_terminator: bool = False,
    ) -> str:
        """Run a command."""
        request = Packet.make_command(command, *args, encoding=encoding)
        response = self.communicate(request, raise_unexpected_terminator)

        if enforce_id and response.id != request.id:
            raise SessionTimeout("packet ID mismatch")

        return response.payload.decode(encoding)
