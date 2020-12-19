"""RCON server configuration."""

from __future__ import annotations
from configparser import ConfigParser, SectionProxy
from logging import getLogger
from pathlib import Path
from typing import Dict, Iterator, NamedTuple, Tuple

from rcon.exceptions import InvalidConfig


__all__ = ['servers']


CONFIG = ConfigParser()
CONFIG_FILE = Path('/etc/rcon.conf')
LOGGER = getLogger('RCON Config')


class Config(NamedTuple):
    """Represents server configuration."""

    host: str
    port: int
    passwd: str = None
    prompt: str = 'RCON> '

    @classmethod
    def from_string(cls, string: str) -> Config:
        """Reads the credentials from the given string."""
        try:
            host, port = string.split(':')
        except ValueError:
            raise InvalidConfig(f'Invalid socket: {string}.') from None

        try:
            port = int(port)
        except ValueError:
            raise InvalidConfig(f'Not an integer: {port}.') from None

        try:
            passwd, host = host.rsplit('@', maxsplit=1)
        except ValueError:
            passwd = None

        return cls(host, port, passwd)

    @classmethod
    def from_config_section(cls, section: SectionProxy) -> Config:
        """Creates a credentials tuple from
        the respective config section.
        """
        host = section['host']
        port = section.getint('port')
        passwd = section.get('passwd')
        prompt = section.get('prompt')
        return cls(host, port, passwd, prompt)


def entries(config_parser: ConfigParser) -> Iterator[Tuple[str, Config]]:
    """Yields entries."""

    for section in config_parser.sections():
        yield (section, Config.from_config_section(config_parser[section]))


def servers() -> Dict[str, Config]:
    """Returns a dictionary of servers."""

    CONFIG.read(CONFIG_FILE)
    return dict(entries(CONFIG))
