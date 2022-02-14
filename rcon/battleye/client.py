"""BattlEye RCon client."""

from ipaddress import IPv4Address
from socket import SOCK_DGRAM
from typing import Union

from rcon.battleye.proto import Command
from rcon.battleye.proto import CommandResponse
from rcon.battleye.proto import Header
from rcon.battleye.proto import LoginRequest
from rcon.battleye.proto import LoginResponse
from rcon.client import BaseClient
from rcon.exceptions import WrongPassword


__all__ = ['Client']


Host = Union[str, IPv4Address]


class Client(BaseClient, socket_type=SOCK_DGRAM):
    """BattlEye RCon client."""

    def send(self, data: bytes) -> None:
        """Sends bytes."""
        with self._socket.makefile('wb') as file:
            file.write(data)

    def _login(self, login_request: LoginRequest) -> LoginResponse:
        """Logs the user in."""
        self.send(bytes(login_request))

        with self._socket.makefile('rb') as file:
            return LoginResponse.read(file)

    def login(self, passwd: str) -> bool:
        """Logs the user in."""
        if not self._login(LoginRequest.from_passwd(passwd)).success:
            raise WrongPassword()

        return True

    def _run(self, command: Command) -> CommandResponse:
        """Executes a command."""
        self.send(bytes(command))

        with self._socket.makefile('rb') as file:
            header = Header.read(file)

        # TODO: Can we determine the packet size?
        remainder = self._socket.recv(4096)
        return CommandResponse.from_bytes(header, remainder)

    def run(self, command: str, *args: str) -> str:
        """Executes a command."""
        return self._run(Command.from_command(command, *args)).message
