"""BattlEye RCon client."""

from collections import defaultdict
from logging import getLogger
from socket import SOCK_DGRAM
from typing import Callable

from rcon.battleye.proto import HEADER_SIZE
from rcon.battleye.proto import RESPONSE_TYPES
from rcon.battleye.proto import CommandRequest
from rcon.battleye.proto import CommandResponse
from rcon.battleye.proto import Header
from rcon.battleye.proto import LoginRequest
from rcon.battleye.proto import LoginResponse
from rcon.battleye.proto import Request
from rcon.battleye.proto import Response
from rcon.battleye.proto import ServerMessage
from rcon.battleye.proto import ServerMessageAck
from rcon.client import BaseClient
from rcon.exceptions import WrongPassword


__all__ = ["Client"]


MessageHandler = Callable[[ServerMessage], None]


def log_message(server_message: ServerMessage) -> None:
    """Default handler, logging the server message."""

    getLogger("Server message").info(server_message.message)


class Client(BaseClient, socket_type=SOCK_DGRAM):
    """BattlEye RCon client."""

    def __init__(
        self,
        *args,
        max_length: int = 4096,
        message_handler: MessageHandler = log_message,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.max_length = max_length
        self.message_handler = message_handler

    def handle_server_message(self, message: ServerMessage) -> None:
        """Handle the respective server message."""
        with self._socket.makefile("wb") as file:
            file.write(bytes(ServerMessageAck(message.seq)))

        self.message_handler(message)

    def receive(self) -> Response:
        """Receive a packet."""
        return RESPONSE_TYPES[
            (
                header := Header.from_bytes(
                    (data := self._socket.recv(self.max_length))[:HEADER_SIZE]
                )
            ).type
        ].from_bytes(header, data[HEADER_SIZE:])

    def communicate(self, request: Request) -> Response | str:
        """Send a request and receive a response."""
        acknowledged = defaultdict(set)
        command_responses = []
        first = False

        with self._socket.makefile("wb") as file:
            file.write(bytes(request))

        while True:
            try:
                response = self.receive()
            except TimeoutError:
                if first:
                    raise
                else:
                    break

            first = False

            if isinstance(response, LoginResponse):
                return response

            seq = response.seq

            if isinstance(response, CommandResponse):
                # Collect fragmented command responses with the same seq
                command_responses.append(response)
            else:
                if seq in acknowledged[response_type := type(response)]:
                    break
                else:
                    acknowledged[response_type].add(seq)

            if isinstance(response, ServerMessage):
                self.handle_server_message(response)

        return "".join(
            command_response.message
            for command_response in sorted(command_responses, key=lambda cr: cr.seq)
        )

    def login(self, passwd: str) -> bool:
        """Log-in the user."""
        if not self.communicate(LoginRequest(passwd)).success:
            raise WrongPassword()

        return True

    def run(self, command: str, *args: str) -> str:
        """Execute a command and return the text message."""
        return self.communicate(CommandRequest.from_command(command, *args))
