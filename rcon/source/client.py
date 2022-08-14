"""Synchronous client."""

from socket import SOCK_STREAM

from rcon.client import BaseClient
from rcon.exceptions import SessionTimeout, WrongPassword
from rcon.source.proto import Packet, Type


__all__ = ['Client']


class Client(BaseClient, socket_type=SOCK_STREAM):
    """An RCON client."""

    def communicate(self, packet: Packet) -> Packet:
        """Send and receive a packet."""
        with self._socket.makefile('wb') as file:
            file.write(bytes(packet))

        return self.read()

    def read(self) -> Packet:
        """Read a packet."""
        with self._socket.makefile('rb') as file:
            packet = Packet.read(file)

        if self.max_pkg_size and len(packet.payload) >= self.max_pkg_size:
            return packet + self.read_followup_packet()

        return packet

    def read_followup_packet(self) -> Packet | None:
        """Reads a potential followup packet."""
        with ChangedTimeout(self, 1) as client:
            try:
                return client.read()
            except TimeoutError:
                return None

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


class ChangedTimeout:
    """Context manager to temporarily change a client's timeout."""

    def __init__(self, client: Client, timeout: int | None):
        self.client = client
        self.timeout = timeout
        self.original_timeout = None

    def __enter__(self) -> Client:
        self.original_timeout = self.client.timeout
        self.client.timeout = self.timeout
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.timeout = self.original_timeout
