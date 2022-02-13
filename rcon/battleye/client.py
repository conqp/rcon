"""BattlEye RCon client."""

from ipaddress import IPv4Address
from typing import Union

from rcon.battleye.proto import Command, LoginRequest
from rcon.client import BaseClient


__all__ = ['Client']


Host = Union[str, IPv4Address]


class Client(BaseClient):
    """BattlEye RCon client."""

    def communicate(self, data: bytes, *, recv: int = 4096) -> bytes:
        """Sends and receives packets."""
        self._socket.send(data)
        return self._socket.recv(recv)

    def login(self, passwd: str) -> bytes:
        """Logs the user in."""
        return self.communicate(bytes(LoginRequest.from_passwd(passwd)))

    def command(self, command: str) -> bytes:
        """Executes a command."""
        return self.communicate(bytes(Command.from_command(command)))
