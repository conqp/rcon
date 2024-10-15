from unittest import TestCase
from socket import socket, AF_INET

import pytest

from rcon.source import Client

HOST: str = "localhost"
PORT: int = 25575


class TestLocalMinecraftServer(TestCase):
    def setUp(self):
        self.client = Client(HOST, PORT, passwd="test")

    @pytest.mark.skipif(
        socket(AF_INET).connect_ex((HOST, PORT)) != 0,
        reason="requires a local Minecraft server to be running",
    )
    def test_list_empty(self):
        with self.client as client:
            response = client.run("list")

        self.assertEqual(response, "There are 0 of a max of 20 players " "online: ")
