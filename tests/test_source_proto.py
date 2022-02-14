"""Testing of the proto module."""

from functools import partial
from io import BytesIO
from random import randint
from unittest import TestCase

from rcon.source.proto import LittleEndianSignedInt32
from rcon.source.proto import Packet
from rcon.source.proto import Type
from rcon.source.proto import random_request_id


class TestRandomRequestId(TestCase):
    """Tests the random_request_id function."""

    def _test_type(self, request_id: LittleEndianSignedInt32):
        """Tests the type of a request id."""
        self.assertIsInstance(request_id, LittleEndianSignedInt32)

    def _test_value(self, request_id: LittleEndianSignedInt32):
        """Tests the value of a request id."""
        self.assertTrue(0 <= request_id <= LittleEndianSignedInt32.MAX)

    def _test_request_id(self, request_id: LittleEndianSignedInt32):
        """Tests a request id."""
        self._test_type(request_id)
        self._test_value(request_id)

    def test_random_request_ids(self):
        """Tests for valid values."""
        for _ in range(1000):
            self._test_request_id(random_request_id())


class TestLittleEndianSignedInt32(TestCase):
    """Tests the LittleEndianSignedInt32 type."""

    def test_min(self):
        """Tests the minimum value."""
        self.assertEqual(
            LittleEndianSignedInt32(LittleEndianSignedInt32.MIN),
            LittleEndianSignedInt32.MIN
        )

    def test_max(self):
        """Tests the maximum value."""
        self.assertEqual(
            LittleEndianSignedInt32(LittleEndianSignedInt32.MAX),
            LittleEndianSignedInt32.MAX
        )

    def test_below_min(self):
        """Tests a value below the minimum value."""
        self.assertRaises(
            ValueError,
            partial(LittleEndianSignedInt32, LittleEndianSignedInt32.MIN - 1)
        )

    def test_above_max(self):
        """Tests a value above the maximum value."""
        self.assertRaises(
            ValueError,
            partial(LittleEndianSignedInt32, LittleEndianSignedInt32.MAX + 1)
        )

    def test_random(self):
        """Tests random LittleEndianSignedInt32 values."""
        for _ in range(1000):
            random = randint(
                LittleEndianSignedInt32.MIN,
                LittleEndianSignedInt32.MAX + 1
            )
            self.assertEqual(LittleEndianSignedInt32(random), random)


class TestType(TestCase):
    """Tests the Type enum."""

    def test_serverdata_auth_value(self):
        """Tests the SERVERDATA_AUTH value."""
        self.assertEqual(Type.SERVERDATA_AUTH.value, 3)
        self.assertEqual(int(Type.SERVERDATA_AUTH), 3)

    def test_serverdata_auth_bytes(self):
        """Tests the SERVERDATA_AUTH bytes."""
        self.assertEqual(
            bytes(Type.SERVERDATA_AUTH),
            (3).to_bytes(4, 'little')
        )

    def test_serverdata_auth_read(self):
        """Tests reading of SERVERDATA_AUTH."""
        self.assertIs(
            Type.read(BytesIO((3).to_bytes(4, 'little'))),
            Type.SERVERDATA_AUTH
        )

    def test_serverdata_auth_response_value(self):
        """Tests the SERVERDATA_AUTH_RESPONSE value."""
        self.assertEqual(Type.SERVERDATA_AUTH_RESPONSE.value, 2)
        self.assertEqual(int(Type.SERVERDATA_AUTH_RESPONSE), 2)

    def test_serverdata_auth_response_bytes(self):
        """Tests the SERVERDATA_AUTH_RESPONSE bytes."""
        self.assertEqual(
            bytes(Type.SERVERDATA_AUTH_RESPONSE),
            (2).to_bytes(4, 'little')
        )

    def test_serverdata_auth_response_read(self):
        """Tests the reading of SERVERDATA_AUTH_RESPONSE."""
        self.assertIs(
            Type.read(BytesIO((2).to_bytes(4, 'little'))),
            Type.SERVERDATA_AUTH_RESPONSE
        )

    def test_serverdata_execcommand_value(self):
        """Tests the SERVERDATA_EXECCOMMAND value."""
        self.assertEqual(Type.SERVERDATA_EXECCOMMAND.value, 2)
        self.assertEqual(int(Type.SERVERDATA_EXECCOMMAND), 2)

    def test_serverdata_execcommand_bytes(self):
        """Tests the SERVERDATA_EXECCOMMAND bytes."""
        self.assertEqual(
            bytes(Type.SERVERDATA_EXECCOMMAND),
            (2).to_bytes(4, 'little')
        )

    def test_serverdata_execcommand_read(self):
        """Tests the reading of SERVERDATA_EXECCOMMAND."""
        self.assertIs(
            Type.read(BytesIO((2).to_bytes(4, 'little'))),
            Type.SERVERDATA_EXECCOMMAND
        )

    def test_serverdata_response_value_value(self):
        """Tests the SERVERDATA_RESPONSE_VALUE value."""
        self.assertEqual(Type.SERVERDATA_RESPONSE_VALUE.value, 0)
        self.assertEqual(int(Type.SERVERDATA_RESPONSE_VALUE), 0)

    def test_serverdata_response_value_bytes(self):
        """Tests the SERVERDATA_RESPONSE_VALUE bytes."""
        self.assertEqual(
            bytes(Type.SERVERDATA_RESPONSE_VALUE),
            (0).to_bytes(4, 'little')
        )

    def test_serverdata_response_value_read(self):
        """Tests the reading SERVERDATA_RESPONSE_VALUE."""
        self.assertIs(
            Type.read(BytesIO((0).to_bytes(4, 'little'))),
            Type.SERVERDATA_RESPONSE_VALUE
        )


class TestPacket(TestCase):
    """Tests the Packet named tuple."""

    def setUp(self):
        """Creates a packet."""
        self.packet = Packet(
            random_request_id(),
            Type.SERVERDATA_EXECCOMMAND,
            'Lorem ipsum sit amet...'.encode()
        )

    def test_bytes_rw(self):
        """Tests recovering from bytes."""
        self.assertEqual(Packet.read(BytesIO(bytes(self.packet))), self.packet)
