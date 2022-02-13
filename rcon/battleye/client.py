"""BattlEye RCon client."""

from ipaddress import IPv4Address
from socket import SOCK_DGRAM
from typing import Union

from rcon.battleye.proto import Command, LoginRequest
from rcon.client import BaseClient


__all__ = ['Client']


Host = Union[str, IPv4Address]


class Client(BaseClient, socket_type=SOCK_DGRAM):
    """BattlEye RCon client."""

    def communicate(self, data: bytes, *, size: int = 4096) -> bytes:
        """Sends and receives packets."""
        self._socket.send(data)
        return self._socket.recv(size)

    def login(self, passwd: str) -> bytes:
        """Logs the user in."""
        return self.communicate(bytes(LoginRequest.from_passwd(passwd)))

    def run(self, command: str, *args: str) -> str:
        """Executes a command."""
        packet = Command.from_command(command, *args)
        _ = self.communicate(bytes(packet))
        # TODO: Process response
        return ''
