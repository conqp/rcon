"""BattlEye RCon client."""

from io import BufferedWriter
from logging import getLogger
from socket import SOCK_DGRAM
from typing import Callable

from rcon.battleye.proto import RESPONSE_TYPES
from rcon.battleye.proto import CommandRequest
from rcon.battleye.proto import Header
from rcon.battleye.proto import LoginRequest
from rcon.battleye.proto import Request
from rcon.battleye.proto import Response
from rcon.battleye.proto import ServerMessage
from rcon.battleye.proto import ServerMessageAck
from rcon.client import BaseClient
from rcon.exceptions import WrongPassword


__all__ = ['Client']


MessageHandler = Callable[[ServerMessage], None]


def log_message(server_message: ServerMessage) -> None:
    """Default handler, logging the server message."""

    getLogger('Server message').info(server_message.message)


class Client(BaseClient, socket_type=SOCK_DGRAM):
    """BattlEye RCon client."""

    def __init__(
            self,
            *args,
            max_length: int = 4096,
            message_handler: MessageHandler = log_message,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.max_length = max_length
        self._handle_server_message = message_handler

    def _receive(self, max_length: int) -> Response:
        """Receive a packet."""
        return RESPONSE_TYPES[
            (header := Header.from_bytes(
                (data := self._socket.recv(max_length))[:8]
            )).type
        ].from_bytes(header, data[8:])

    def receive(self, file: BufferedWriter) -> Response | str:
        """Receive a message."""
        server_messages = set()

        while isinstance(
                response := self._receive(self.max_length),
                ServerMessage
        ):
            server_messages.add(response)
            file.write(bytes(ServerMessageAck(response.seq)))
            self._handle_server_message(response)

        if not server_messages:
            return response

        return ''.join(
            msg.message for msg in
            sorted(server_messages, key=lambda msg: msg.seq)
        )

    def communicate(self, request: Request) -> Response | str:
        """Send a request and receive a response."""
        with self._socket.makefile('wb') as file:
            file.write(bytes(request))
            return self.receive(file)

    def login(self, passwd: str) -> bool:
        """Log-in the user."""
        if not self.communicate(LoginRequest(passwd)).success:
            raise WrongPassword()

        return True

    def run(self, command: str, *args: str) -> str:
        """Execute a command and return the text message."""
        return self.communicate(CommandRequest.from_command(command, *args))
