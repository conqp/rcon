"""Test the BattlEye protocol."""

from unittest import TestCase

from rcon.battleye.proto import Header


HEADER = Header(920575337, 0x00)
BYTES = b'BEi\xdd\xde6\xff\x00'


class TestHeader(TestCase):
    """Test header object."""

    def test_header_from_bytes(self):
        """Tests header object parsing."""
        self.assertEqual(Header.from_bytes(BYTES), HEADER)

    def test_header_to_bytes(self):
        """Tests header object parsing."""
        self.assertEqual(bytes(HEADER), BYTES)
